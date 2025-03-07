import asyncio
import logging
import signal
import time

from ..config import get_config
from ..data_types import load_character_list
from ..db import TestChannel, TestResults, get_async_redis, pop_test
from ..testers import TESTERS, Tester


async def run_worker() -> None:
    logging.info("Starting worker")
    redis = get_async_redis()
    shutting_down = False

    def handle_shutdown(*_) -> None:
        nonlocal shutting_down
        logging.info("Shutting down worker")
        shutting_down = True

    signal.signal(signal.SIGTERM, handle_shutdown)

    chars = load_character_list()

    tasks: list[asyncio.Task] = []
    max_tasks = 100

    task_check_interval = 5
    heartbeat_interval = 60
    last_heartbeat = time.time()
    last_task_check = time.time()

    while not shutting_down:
        test = await pop_test(redis)
        if test:
            channel = TestChannel(redis, test.test_id)
            if len(tasks) <= max_tasks:
                tester = TESTERS[test.test_type]
                tasks.append(asyncio.create_task(run_test(channel, tester(chars))))
            else:
                logging.warning("Too many tasks, cancelling test")
                await channel.end()
            continue

        await asyncio.sleep(0.2)

        if time.time() - last_heartbeat > heartbeat_interval:
            logging.info("Worker heartbeat")
            last_heartbeat = time.time()

        if time.time() - last_task_check > task_check_interval:
            tasks = [task for task in tasks if not task.done()]
            last_task_check = time.time()

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks)


async def run_test(channel: TestChannel, tester: Tester) -> None:
    test = tester.characters()
    for character in test:
        await channel.put_character(character)

        answer = await get_answer(channel)
        if answer is None:
            await channel.end()
            return
        logging.info("[%s] Got answer: %s", channel.test_id, answer)

        try:
            test.send(answer)
        except StopIteration:
            pass

    await channel.end()
    count = tester.estimate_count()
    await channel.put_results(TestResults(count=count, breakdown=tester.get_breakdown()))


async def get_answer(channel: TestChannel) -> bool | None:
    config = get_config()
    start = time.time()
    while True:
        answer = await channel.next_answer()
        if answer is not None:
            return answer
        await asyncio.sleep(0.2)
        if time.time() - start > config.answer_timeout:
            await channel.end()
            return None
