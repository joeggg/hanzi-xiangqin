import logging

from sqlalchemy import Connection, text
from sqlalchemy.exc import ProgrammingError

from .db import Base, get_setup_engine


def set_up_database() -> None:
    """
    Create database and tables using postgres user, then create a separate user for the API so it's
    unable to drop anything
    """
    engine = get_setup_engine()

    with engine.connect() as conn:
        create_if_not_exists(conn, "CREATE DATABASE hx", "Database")
        create_if_not_exists(conn, "CREATE USER hx", "User")
        create_user_permissions(conn)

    Base.metadata.create_all(engine)
    logging.info("Database tables created")


def create_if_not_exists(conn: Connection, query: str, obj_name: str) -> None:
    try:
        conn.execute(text(query))
    except ProgrammingError:
        logging.info("%s already exists", obj_name)


def create_user_permissions(conn: Connection) -> None:
    conn.execute(text("GRANT ALL PRIVILEGES ON DATABASE hx TO hx"))
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hx"))
    conn.execute(text("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hx"))
