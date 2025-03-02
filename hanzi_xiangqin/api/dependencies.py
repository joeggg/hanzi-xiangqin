from typing import Iterator

from redis.asyncio import Redis

from ..db import get_async_redis


def async_redis() -> Iterator[Redis]:
    yield get_async_redis()
