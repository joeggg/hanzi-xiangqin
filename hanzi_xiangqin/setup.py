import logging

from sqlalchemy import Connection, text
from sqlalchemy.exc import ProgrammingError

from .db import Base, PostgresConfig, get_setup_engine


def set_up_database() -> None:
    """
    Create database and tables using postgres user, then create a separate user for the API so it's
    unable to drop anything
    """
    pg_config = PostgresConfig()

    create_database(pg_config)
    create_user_and_tables(pg_config)


def create_database(pg_config: PostgresConfig) -> None:
    engine = get_setup_engine(postgres_db=True)

    with engine.connect() as conn:
        create_if_not_exists(conn, "DATABASE", pg_config.pgdatabase)

    logging.info("Database created")


def create_user_and_tables(pg_config: PostgresConfig) -> None:
    engine = get_setup_engine(postgres_db=False)
    schemas = [table.schema for table in Base.metadata.tables.values() if table.schema]

    # Create all unique schemas
    with engine.connect() as conn:
        for schema in schemas:
            create_if_not_exists(conn, "SCHEMA", schema)
            logging.info("Schema %s created", schema)

    Base.metadata.create_all(bind=engine)
    logging.info("Database tables created")

    with engine.connect() as conn:
        create_if_not_exists(conn, "USER", pg_config.pguser)
        create_user_permissions(
            conn, pg_config.pgdatabase, schemas, pg_config.pguser, pg_config.pgpassword
        )
    logging.info("User created")


def create_if_not_exists(conn: Connection, obj_type: str, obj_name: str) -> None:
    try:
        conn.execute(text(f"CREATE {obj_type} {obj_name}"))
    except ProgrammingError:
        logging.info("%s already exists", obj_type.capitalize())


def create_user_permissions(
    conn: Connection, database: str, schemas: list[str], user: str, password: str
) -> None:
    conn.execute(text(f"ALTER USER {user} WITH PASSWORD '{password}'"))
    conn.execute(text(f"GRANT ALL PRIVILEGES ON DATABASE {database} TO {user}"))

    for schema in schemas:
        conn.execute(text(f"GRANT USAGE ON SCHEMA {schema} TO {user}"))

    conn.execute(text(f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA main TO {user}"))
    conn.execute(text(f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA main TO {user}"))
