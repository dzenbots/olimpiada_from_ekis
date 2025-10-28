from peewee import Model, TextField, CharField

from database import db


class BaseModel(Model):
    class Meta:
        database = db


class OlimpField(BaseModel):
    date = CharField()
    subject = CharField()
    students_list_link = TextField()
    classes = CharField()
    protocols_link = TextField()


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
