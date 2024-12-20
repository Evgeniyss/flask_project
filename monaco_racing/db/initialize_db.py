from retry import retry
from .models import db, Report, Driver
from .parser import fill_db


@retry(tries=3, delay=1)
def initialize_database():
    db.create_tables([Report, Driver], safe=True)
    fill_db()
