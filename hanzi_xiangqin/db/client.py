from functools import cache

from pydantic_settings import BaseSettings
from redis.asyncio import Redis
from sqlalchemy import Engine, NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class DbConfig(BaseSettings):
    username: str = "postgres"
    password: str = "postgres"
    host: str = "db"
    port: int = 5432
    database: str = "hx"


@cache
def get_async_redis() -> Redis:
    return Redis(host="redis", max_connections=20, decode_responses=True)


@cache
def get_engine() -> Engine:
    return create_engine(get_db_url(), pool_size=20)


@cache
def get_async_engine() -> AsyncEngine:
    return create_async_engine(get_db_url(), pool_size=20)


@cache
def get_setup_engine() -> Engine:
    return create_engine(get_db_url(), poolclass=NullPool, isolation_level="AUTOCOMMIT")


@cache
def get_db_url() -> str:
    config = DbConfig()
    return (
        f"postgresql+psycopg://{config.username}:{config.password}@{config.host}:{config.port}"
        f"/{config.database}"
    )
