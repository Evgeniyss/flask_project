import dicttoxml
from typing import Dict, Optional, Union
from flask import make_response, jsonify
from peewee import ModelSelect
from src.report.constants import (ABBREVIATIONS_FILE_PATH as file_path,
                                  START_LOG_FILE_PATH as start_log_path,
                                  END_LOG_FILE_PATH as end_log_path)
from src.report.report import build_report


def get_report_build(path: str = file_path,
                     order: str = 'asc',
                     driver: str = '',
                     start_log: str = start_log_path,
                     end_log: str = end_log_path) -> str:
    """Returns report of Monaco 2018 racing.

    Parameters:
    - path (str): File path for the report. Defaults to ABBREVIATIONS_FILE_PATH.
    - order (str): Sorting order for the report. Defaults to 'asc'.
    - driver (str): Driver information for the report. Defaults to an empty string.
    - start_log (str): Start log file path. Defaults to START_LOG_FILE_PATH.
    - end_log (str): End log file path. Defaults to END_LOG_FILE_PATH.

    Returns:
    - str: The generated report as a string.
    """
    if not isinstance(path, str) or not path.endswith('.txt'):
        raise TypeError("Invalid file path provided for 'path' parameter.")

    if not isinstance(start_log, str) or not start_log.endswith('.log'):
        raise TypeError(
            "Invalid file path provided for 'start_log' parameter.")

    if not isinstance(end_log, str) or not end_log.endswith('.log'):
        raise TypeError("Invalid file path provided for 'end_log' parameter.")

    if order not in ['asc', 'desc']:
        raise TypeError(
            "Invalid value for 'order' parameter. Should be 'asc' or 'desc'.")

    return build_report(file_path=path,
                        order=order,
                        driver=driver,
                        start_log_path=start_log,
                        end_log_path=end_log)


def output_xml(data: Dict, code: int, headers: Optional[Dict] = None) -> make_response:
    xml_data = dicttoxml.dicttoxml(data)
    try:
        xml_string = xml_data.decode('utf-8')
    except UnicodeDecodeError as e:
        error_message = f'Error decoding XML: {e}'
        return make_response({'error': error_message}, 500)

    response = make_response(xml_string, code)
    response.headers['Content-Type'] = 'application/xml'
    return response


def output_format(data: Dict, code: int, repr_format: str) -> Union[make_response, jsonify]:
    """Output the response in the specified format"""
    handler = output_xml if repr_format.lower() == 'xml' else jsonify
    if isinstance(data, ModelSelect):
        data = list(data.dicts())
    return handler({'response': data}, code)
