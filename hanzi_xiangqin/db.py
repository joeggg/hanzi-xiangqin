from functools import cache

from redis.asyncio import Redis


@cache
def get_async_redis() -> Redis:
    return Redis(host="redis", max_connections=20)
