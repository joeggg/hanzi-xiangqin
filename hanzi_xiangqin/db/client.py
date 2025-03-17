from functools import cache

from pydantic_settings import BaseSettings
from redis.asyncio import Redis
from sqlalchemy import Engine, NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from ..config import get_config


class PostgresConfig(BaseSettings):
    pguser: str = ""
    pgpassword: str = ""
    root_pgpassword: str = ""
    pghost: str = "localhost"
    pgport: int = 5432
    pgdatabase: str = ""


@cache
def get_async_redis() -> Redis:
    config = get_config()
    return Redis(host="redis", max_connections=config.redis_pool_size, decode_responses=True)


@cache
def get_engine() -> Engine:
    config = get_config()
    return create_engine(get_db_url(), pool_size=config.pg_pool_size)


@cache
def get_async_engine() -> AsyncEngine:
    config = get_config()
    return create_async_engine(get_db_url(), pool_size=config.pg_pool_size)


def get_setup_engine(postgres_db: bool) -> Engine:
    return create_engine(
        get_db_url(root=True, postgres_db=postgres_db),
        poolclass=NullPool,
        isolation_level="AUTOCOMMIT",
    )


def get_db_url(root: bool = False, postgres_db: bool = False) -> str:
    config = PostgresConfig()
    return "postgresql+psycopg://{}:{}@{}:{}/{}".format(
        "postgres" if root else config.pguser,
        config.root_pgpassword if root else config.pgpassword,
        config.pghost,
        config.pgport,
        "postgres" if postgres_db else config.pgdatabase,
    )
