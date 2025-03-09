from dataclasses import asdict

import orjson

from ..config import get_config
from ..data_types import Hanzi
from .data_types import Test, TestDone, TestNotFound, TestResults
from .setup import get_async_redis


class Channel:
    def __init__(self) -> None:
        self.redis = get_async_redis()
        self.config = get_config()
        self.queue_name = "test_queue"

    async def queue_test(self, data: Test) -> None:
        await self.redis.lpush(self.queue_name, orjson.dumps(asdict(data)))

    async def pop_test(self) -> Test | None:
        result = await self.redis.rpop(self.queue_name)
        if result is None:
            return None

        data = Test(**orjson.loads(result))
        await self.redis.setex(data.test_id, self.config.test_timeout, result)
        return data

    async def test_by_id(self, test_id: str) -> Test:
        result = await self.redis.get(test_id)
        if result is None:
            raise TestNotFound

        return Test(**orjson.loads(result))

    # Worker methods - have access to Test object

    async def put_character(self, test: Test, hanzi: Hanzi) -> None:
        async with self.redis.pipeline() as pipe:
            await pipe.setex(
                test.char_key, self.config.test_timeout, orjson.dumps(hanzi.model_dump())
            )
            await pipe.expire(test.test_id, self.config.test_timeout)
            await pipe.execute()

    async def next_answer(self, test: Test) -> bool | None:
        answer = await self.redis.getdel(test.answer_key)
        if answer is None:
            return None
        return answer == "1"

    async def end_test(self, test: Test, results: TestResults) -> None:
        """Sets results, deletes communication keys, and sets state to DONE"""
        test.done = True
        async with self.redis.pipeline() as pipe:
            await self.redis.setex(
                test.results_key, self.config.result_cache_ttl, orjson.dumps(asdict(results))
            )
            await self.redis.setex(
                test.test_id, self.config.result_cache_ttl, orjson.dumps(asdict(test))
            )
            for key in [test.char_key, test.answer_key]:
                await self.redis.delete(key)

            await pipe.execute()

    async def cancel_test(self, test: Test) -> None:
        """Deletes all test keys"""
        async with self.redis.pipeline() as pipe:
            for key in [test.test_id, test.char_key, test.answer_key, test.results_key]:
                await pipe.delete(key)
            await pipe.execute()

    # API methods - have access to just test_id

    async def next_character(self, test_id: str) -> Hanzi | None:
        test = await self.test_by_id(test_id)
        result = await self.redis.get(test.char_key)

        if result is None:
            if test.done:
                raise TestDone
            return None

        return Hanzi(**orjson.loads(result))

    async def put_answer(self, test_id: str, answer: bool) -> None:
        test = await self.test_by_id(test_id)

        async with self.redis.pipeline() as pipe:
            await pipe.delete(test.char_key)
            await pipe.setex(test.answer_key, self.config.test_timeout, "1" if answer else "0")
            await pipe.expire(test.test_id, self.config.test_timeout)
            await pipe.execute()

    async def get_results(self, test_id: str) -> TestResults | None:
        test = await self.test_by_id(test_id)

        results = await self.redis.get(test.results_key)
        if results is None:
            return None

        return TestResults(**orjson.loads(results))
