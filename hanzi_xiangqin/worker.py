import asyncio
import logging
import signal
import time

from .db import get_async_redis


async def worker() -> None:
    logging.info("Starting worker")
    redis = get_async_redis()
    shutting_down = False

    def handle_shutdown(*_) -> None:
        nonlocal shutting_down
        shutting_down = True

    signal.signal(signal.SIGINT, handle_shutdown)

    start = time.time()
    while not shutting_down:
        test_id = await redis.rpop("tests")
        if test_id:
            logging.info("Got test %s", test_id)
            continue

        await asyncio.sleep(0.2)

        if time.time() - start > 60:
            logging.info("Worker heartbeat")
            start = time.time()
