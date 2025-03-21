import logging
import os
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.orm import Session

from hanzi_xiangqin.api.app import create_app
from hanzi_xiangqin.db import Base, Channel, get_engine, get_redis
from hanzi_xiangqin.setup import set_up_database


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def session() -> Iterator[Session]:
    engine = get_engine()
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def channel() -> Channel:
    return Channel()


@pytest.fixture(scope="session", autouse=True)
def load_env() -> None:
    if os.getenv("GITHUB_ACTIONS") == "true":
        os.environ["PGHOST"] = "db"
        os.environ["REDIS_HOST"] = "redis"

    os.environ["PGUSER"] = "hx"
    os.environ["PGPASSWORD"] = "postgres"
    os.environ["ROOT_PGPASSWORD"] = "postgres"
    os.environ["PGPORT"] = "5432"
    os.environ["PGDATABASE"] = "hx"


@pytest.fixture(autouse=True)
def clear_db(session: Session) -> Iterator[None]:
    yield
    for table in Base.metadata.tables.values():
        logging.info("Clearing table %s", table.name)
        session.execute(delete(table))
    session.commit()


@pytest.fixture(autouse=True)
def clear_redis() -> Iterator[None]:
    yield
    get_redis().flushall()


@pytest.fixture(scope="session", autouse=True)
def set_up_db() -> Iterator[None]:
    set_up_database()
    yield
