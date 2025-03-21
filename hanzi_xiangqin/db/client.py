from functools import cache

from pydantic_settings import BaseSettings
from redis import Redis
from redis.asyncio import Redis as AsyncRedis
from sqlalchemy import Engine, NullPool, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class PostgresConfig(BaseSettings):
    pguser: str = ""
    pgpassword: str = ""
    root_pgpassword: str = ""
    pghost: str = "localhost"
    pgport: int = 5432
    pgdatabase: str = ""
    pg_pool_size: int = 20


class RedisConfig(BaseSettings):
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_pool_size: int = 20


@cache
def get_redis() -> Redis:
    config = RedisConfig()
    return Redis(
        host=config.redis_host,
        port=config.redis_port,
        max_connections=config.redis_pool_size,
        decode_responses=True,
    )


@cache
def get_async_redis() -> AsyncRedis:
    config = RedisConfig()
    return AsyncRedis(
        host=config.redis_host,
        port=config.redis_port,
        max_connections=config.redis_pool_size,
        decode_responses=True,
    )


@cache
def get_postgres_config() -> PostgresConfig:
    return PostgresConfig()


@cache
def get_engine() -> Engine:
    config = get_postgres_config()
    return create_engine(get_db_url(), pool_size=config.pg_pool_size)


@cache
def get_async_engine() -> AsyncEngine:
    config = get_postgres_config()
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
