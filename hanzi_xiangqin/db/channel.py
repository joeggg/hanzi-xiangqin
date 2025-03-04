import logging
import uuid
from dataclasses import asdict, dataclass, field

import orjson
from pydantic import BaseModel
from redis.asyncio import Redis

from ..config import get_config
from ..data_types import Hanzi
from ..testers import TestType


class TestResults(BaseModel):
    count: int
    breakdown: dict


@dataclass
class Test:
    test_type: TestType
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class TestDone(Exception):
    pass


async def queue_test(redis: Redis, data: Test) -> None:
    logging.info("Queueing test %s", data.test_id)
    config = get_config()
    async with redis.pipeline() as pipe:
        await pipe.lpush("test_queue", orjson.dumps(asdict(data)))
        await pipe.setex(data.test_id, config.test_timeout, "1")
        await pipe.execute()


async def pop_test(redis: Redis) -> Test | None:
    result = await redis.rpop("test_queue")
    if result is None:
        return None

    data = Test(**orjson.loads(result))
    logging.info("Got new job for test: %s", data.test_id)
    return data


class TestChannel:
    def __init__(self, redis: Redis, test_id: str) -> None:
        self.redis = redis
        self.test_id = test_id

        self.char_queue_key = f"{self.test_id}_char_queue"
        self.answer_queue_key = f"{self.test_id}_answer_queue"
        self.results_key = f"{self.test_id}_results"
        self.config = get_config()

    async def end(self) -> None:
        await self.redis.delete(self.test_id)

    async def put_character(self, hanzi: Hanzi) -> None:
        await self.redis.lpush(self.char_queue_key, orjson.dumps(hanzi.model_dump()))
        await self.redis.expire(self.char_queue_key, self.config.test_timeout)

    async def put_answer(self, answer: bool) -> None:
        await self.redis.lpush(self.answer_queue_key, "1" if answer else "0")
        await self.redis.expire(self.answer_queue_key, self.config.test_timeout)

    async def next_character(self) -> Hanzi | None:
        result = await self.redis.rpop(self.char_queue_key)
        if result is None:
            if await self.redis.exists(self.test_id):
                return None
            raise TestDone("Test is complete")

        return Hanzi(**orjson.loads(result))

    async def next_answer(self) -> bool | None:
        answer = await self.redis.rpop(self.answer_queue_key)
        if answer is None:
            return None
        return answer == "1"

    async def put_results(self, result: TestResults) -> None:
        config = get_config()
        await self.redis.setex(
            self.results_key, config.result_cache_ttl, orjson.dumps(result.model_dump())
        )

    async def get_results(self) -> TestResults | None:
        results = await self.redis.get(self.results_key)
        if results is None:
            return None

        data = orjson.loads(results)
        return TestResults(**data)
