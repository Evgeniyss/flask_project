from typing import Dict
from retry import retry
from ..api.utils import get_report_build
from .models import db, Report, Driver
from src.report.constants import (ABBREVIATIONS_FILE_PATH as file_path,
                                  START_LOG_FILE_PATH as start_log_path,
                                  END_LOG_FILE_PATH as end_log_path)
from src.report.report import read_racers_data


DELIMITER_FORMAT = '------------------------------------------------------------------------'


@retry(tries=3, delay=1)
def parse_report_result_to_db():
    """
    Parse the raw report result and insert data into the 'Report' table.

    Retrieves a raw report result using the get_report_build function and splits it into rows.
    Excludes rows with the specified delimiter format. For each valid row, extracts information
    such as 'driver_name', 'team', and 'timestamp' and inserts this data into the 'Report' table.

    Returns:
    - None
    """
    report_result: str = get_report_build(
        path=str(file_path),
        order='asc',
        driver='',
        start_log=str(start_log_path),
        end_log=str(end_log_path
                    ))

    rows: list = report_result.split('\n')

    result = []

    for row in rows:
        if DELIMITER_FORMAT in row:
            continue
        row_data = row.split('|')

        result.append({
            'driver_name': row_data[0][row_data[0].index('.') + 1:].strip(),
            'team': row_data[1].strip(),
            'timestamp': row_data[2].strip()
        })

    return result


@retry(tries=3, delay=1)
def parse_driver_list_to_db():
    """
    Parse racer data and insert into the 'Driver' table.

    Retrieves racer data using the read_racers_data function.
    Iterates through the data, extracting information such as 'code', 'driver_name', and 'team',
    and inserts this data into the 'Driver' table.

    Returns:
    - None
    """
    drivers: Dict[str, Dict[str, str]] = read_racers_data(
        file_path=file_path)

    result = []
    for code in drivers:
        result.append({'code': code,
                       'driver_name': drivers.get(code)['racer'],
                       'team': drivers.get(code).get('team'),
                       'report': 1})

    return result


@retry(tries=3, delay=1)
def fill_db():
    """
    Fill the 'Report' and 'Driver' tables with parsed data.

    Uses parse_report_result_to_db and parse_driver_list_to_db functions to retrieve parsed data
    and inserts the data into the 'Report' and 'Driver' tables respectively.

    Returns:
    - None
    """
    report_data = parse_report_result_to_db()
    driver_data = parse_driver_list_to_db()

    with db.atomic():
        Report.insert_many(report_data).execute()
        Driver.insert_many(driver_data).execute()
