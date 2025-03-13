import logging

from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from .db import Base, get_setup_engine


def set_up_database() -> None:
    engine = get_setup_engine()

    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE DATABASE hx"))
        except ProgrammingError:
            logging.info("Database already exists")

    Base.metadata.create_all(engine)
    logging.info("Database tables created")
