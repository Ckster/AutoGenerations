from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from database.config import DATABASE_URL

Base = declarative_base()


def make_engine():
    return create_engine(DATABASE_URL)