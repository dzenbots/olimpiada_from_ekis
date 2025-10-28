from peewee import SqliteDatabase

from config import config

db = SqliteDatabase(config.database.filename)

from database.models import OlimpField, initialize_db, close_db

__all__ = [
    "OlimpField",
    "initialize_db",
    "close_db",
    "db"
]
