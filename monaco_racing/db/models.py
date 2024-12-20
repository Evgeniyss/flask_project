from peewee import Model, CharField, SqliteDatabase, ForeignKeyField
from playhouse.pool import PooledSqliteDatabase


db = PooledSqliteDatabase(
    'racing.db',
    max_connections=32,
    stale_timeout=300,
)


class BaseModel(Model):
    class Meta:
        database = db


class Report(BaseModel):
    driver_name = CharField()
    team = CharField()
    timestamp = CharField()


class Driver(BaseModel):
    code = CharField(unique=True)
    driver_name = CharField()
    team = CharField()
    report = ForeignKeyField(Report, backref='drivers')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'driver_name': self.driver_name,
            'team': self.team
        }
