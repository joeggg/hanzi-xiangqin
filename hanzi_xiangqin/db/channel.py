from dataclasses import asdict, dataclass

import orjson

from ..config import get_config
from ..data_types import Hanzi
from .client import get_async_redis
from .models import TestType


@dataclass
class TestJob:
    test_id: int
    test_type: TestType


class Channel:
    def __init__(self) -> None:
        self.redis = get_async_redis()
        self.config = get_config()
        self.queue_name = "test_queue"
        self._char_queue_key = "{}_char_queue"
        self._answer_queue_key = "{}_answer_queue"
        self._char_cache_key = "{}_char_cache"

    def char_queue_key(self, test_id: int) -> str:
        return self._char_queue_key.format(test_id)

    def answer_queue_key(self, test_id: int) -> str:
        return self._answer_queue_key.format(test_id)

    def char_cache_key(self, test_id: int) -> str:
        return self._char_cache_key.format(test_id)

    async def queue_test(self, test: TestJob) -> None:
        await self.redis.lpush(self.queue_name, orjson.dumps(asdict((test))))

    async def pop_test(self) -> TestJob | None:
        test = await self.redis.rpop(self.queue_name)
        if test is None:
            return None

        return TestJob(**orjson.loads(test))

    # Worker methods - have access to Test object

    async def put_character(self, test_id: int, hanzi: Hanzi) -> None:
        async with self.redis.pipeline() as pipe:
            await pipe.lpush(
                self.char_queue_key(test_id),
                orjson.dumps(hanzi.model_dump()),
            )
            await pipe.expire(self.char_queue_key(test_id), self.config.test_inactivity_timeout)
            await pipe.execute()

    async def next_answer(self, test_id: int) -> bool | None:
        answer = await self.redis.rpop(self.answer_queue_key(test_id))
        if answer is None:
            return None

        await self.redis.expire(self.answer_queue_key(test_id), self.config.test_inactivity_timeout)
        return answer == "1"

    # API methods - have access to just test_id

    async def next_character(self, test_id: int) -> Hanzi | None:
        result = await self.redis.rpop(self.char_queue_key(test_id))
        if result is None:
            result = await self.redis.get(self.char_cache_key(test_id))
            if result is None:
                return None

        async with self.redis.pipeline() as pipe:
            await pipe.set(self.char_cache_key(test_id), result)
            await pipe.expire(self.char_cache_key(test_id), self.config.test_inactivity_timeout)
            await pipe.expire(self.char_queue_key(test_id), self.config.test_inactivity_timeout)
            await pipe.execute()

        return Hanzi(**orjson.loads(result))

    async def put_answer(self, test_id: int, answer: bool) -> None:
        async with self.redis.pipeline() as pipe:
            await pipe.lpush(self.answer_queue_key(test_id), "1" if answer else "0")
            await pipe.delete(self.char_cache_key(test_id))
            await pipe.expire(self.answer_queue_key(test_id), self.config.test_inactivity_timeout)
            await pipe.execute()
