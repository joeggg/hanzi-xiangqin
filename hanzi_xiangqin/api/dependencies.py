from typing import AsyncIterator, Iterator

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession

from ..db import Channel, get_async_engine


def channel() -> Iterator[Channel]:
    yield Channel()


async def db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(get_async_engine(), expire_on_commit=False) as session:
        try:
            yield session
            await session.commit()
        except Exception as exc:
            await session.rollback()
            raise exc


async def db_connection() -> AsyncIterator[AsyncConnection]:
    async with get_async_engine().connect() as conn:
        yield conn
