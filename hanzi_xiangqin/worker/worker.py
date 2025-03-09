import asyncio
import logging
import signal
import time
from typing import Callable

from ..config import get_config
from ..data_types import load_character_list
from ..db import Channel, Test, TestResults
from ..testers import TESTERS


async def run_worker() -> None:
    worker = Worker()

    def handle_shutdown(*_) -> None:
        logging.info("Shutting down worker")
        worker.shut_down()

    signal.signal(signal.SIGTERM, handle_shutdown)

    await worker.run()


class Worker:
    TASK_CLEANUP_INTERVAL = 5
    HEARTBEAT_INTERVAL = 60
    POLL_INTERVAL = 0.2
    TIMER_POLL_INTERVAL = 5
    MAX_TASKS = 100

    def __init__(self) -> None:
        self.channel = Channel()
        self.shutting_down = False

        self.tasks: list[asyncio.Task] = []
        self.timer_tasks: list[asyncio.Task] = []

    async def run(self) -> None:
        logging.info("Starting worker")

        self.timer_tasks = [
            asyncio.create_task(
                self.timer_task(lambda: logging.info("Worker heartbeat"), self.HEARTBEAT_INTERVAL)
            ),
            asyncio.create_task(self.timer_task(self.cleanup_tasks, self.TASK_CLEANUP_INTERVAL)),
        ]

        while not self.shutting_down:
            test = await self.channel.pop_test()
            if test:
                if len(self.tasks) <= self.MAX_TASKS:
                    self.tasks.append(asyncio.create_task(Runner(self.channel, test).run_test()))
                else:
                    logging.warning("Too many tasks, cancelling new test")
                    await self.channel.cancel_test(test)

            await asyncio.sleep(self.POLL_INTERVAL)

        for task in self.tasks:
            task.cancel()

        await asyncio.gather(*self.tasks, *self.timer_tasks)

    async def timer_task(self, task: Callable[[], None], interval: int) -> None:
        start = time.time()
        while not self.shutting_down:
            await asyncio.sleep(self.TIMER_POLL_INTERVAL)

            if time.time() - start > interval:
                task()
                start = time.time()

    async def run_test(self, test: Test) -> None: ...

    def shut_down(self) -> None:
        self.shutting_down = True

    def cleanup_tasks(self) -> None:
        self.tasks = [task for task in self.tasks if not task.done()]


class Runner:
    def __init__(self, channel: Channel, test: Test) -> None:
        self.channel = channel
        self.test = test

    async def run_test(self) -> None:
        logging.info("[%s] Starting test", self.test.test_id)
        tester = TESTERS[self.test.test_type](load_character_list())
        characters = tester.characters()

        for character in characters:
            await self.channel.put_character(self.test, character)

            answer = await self.get_answer()
            if answer is None:
                await self.channel.cancel_test(self.test)
                return
            logging.info("[%s] Got answer: %s", self.test.test_id, answer)

            try:
                characters.send(answer)
            except StopIteration:
                pass

        count = tester.estimate_count()
        await self.channel.end_test(
            self.test, TestResults(count=count, breakdown=tester.get_breakdown())
        )
        logging.info("[%s] Completed test: %s", self.test.test_id)

    async def get_answer(self) -> bool | None:
        config = get_config()
        start = time.time()
        while True:
            answer = await self.channel.next_answer(self.test)
            if answer is not None:
                return answer
            await asyncio.sleep(0.2)
            if time.time() - start > config.answer_timeout:
                await self.channel.cancel_test(self.test)
                return None
