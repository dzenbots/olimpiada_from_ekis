from peewee import Model, TextField

from database import db


class BaseModel(Model):
    class Meta:
        database = db


class OlimpField(BaseModel):
    filename = TextField()
    comment = TextField()


def initialize_db():
    db.connect()
    db.create_tables(
        [
            OlimpField
        ],
        safe=True
    )


def close_db():
    db.close()
