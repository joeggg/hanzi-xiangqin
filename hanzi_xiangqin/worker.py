import asyncio
import logging
import signal
import time

from .data_types import load_character_list
from .db import TestChannel, get_async_redis, pop_test
from .testers import TESTERS, Tester


async def worker() -> None:
    logging.info("Starting worker")
    redis = get_async_redis()
    shutting_down = False

    def handle_shutdown(*_) -> None:
        nonlocal shutting_down
        shutting_down = True

    signal.signal(signal.SIGINT, handle_shutdown)

    chars = load_character_list()

    start = time.time()
    while not shutting_down:
        test = await pop_test(redis)
        if test:
            channel = TestChannel(redis, test.test_id)
            tester = TESTERS[test.test_type]
            await run_test(channel, tester(chars))
            continue

        await asyncio.sleep(0.2)

        if time.time() - start > 60:
            logging.info("Worker heartbeat")
            start = time.time()


async def run_test(channel: TestChannel, tester: Tester) -> None: ...
