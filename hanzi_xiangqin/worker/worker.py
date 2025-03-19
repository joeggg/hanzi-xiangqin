import asyncio
import logging
import signal
import time
from dataclasses import dataclass
from typing import Callable

from ..config import get_config
from ..data_types import load_character_list
from ..db import Channel, TestResults
from ..testers import TESTERS, Tester
from .queries import delete_test, set_test_errored, set_test_in_progress, update_test_results


async def run_worker() -> None:
    worker = Worker()

    def handle_shutdown(*_) -> None:
        logging.info("Shutting down worker")
        worker.shut_down()

    signal.signal(signal.SIGTERM, handle_shutdown)

    await worker.run()


@dataclass
class Job:
    test_id: int
    task: asyncio.Task


class Worker:
    TASK_CLEANUP_INTERVAL = 5
    HEARTBEAT_INTERVAL = 60
    POLL_INTERVAL = 0.2
    TIMER_POLL_INTERVAL = 5
    MAX_TASKS = 100

    def __init__(self) -> None:
        self.channel = Channel()
        self.shutting_down = False

        self.jobs: list[Job] = []
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
            await asyncio.sleep(self.POLL_INTERVAL)

            try:
                test = await self.channel.pop_test()
                if not test:
                    continue

                if len(self.jobs) > self.MAX_TASKS:
                    logging.warning("Too many tasks, cancelling new test")
                    await delete_test(test.test_id)
                    continue

                tester = TESTERS[test.test_type](load_character_list())
                self.jobs.append(
                    Job(
                        test.test_id,
                        asyncio.create_task(run_test(self.channel, tester, test.test_id)),
                    )
                )

            except Exception:
                logging.exception("An unexpected error occurred in worker")

        for job in self.jobs:
            job.task.cancel()
            try:
                await job.task
            except asyncio.CancelledError:
                logging.error("Test %s was cancelled!", job.test_id)
                await set_test_errored(job.test_id)

        await asyncio.gather(*self.timer_tasks)

    async def timer_task(self, task: Callable[[], None], interval: int) -> None:
        start = time.time()
        while not self.shutting_down:
            await asyncio.sleep(self.TIMER_POLL_INTERVAL)

            if time.time() - start > interval:
                task()
                start = time.time()

    def shut_down(self) -> None:
        self.shutting_down = True

    def cleanup_tasks(self) -> None:
        self.jobs = [job for job in self.jobs if not job.task.done()]


async def run_test(channel: Channel, tester: Tester, test_id: int) -> None:
    logging.info("[%s] Starting test", test_id)
    await set_test_in_progress(test_id)
    characters = tester.characters()

    try:
        for character in characters:
            await channel.put_character(test_id, character)

            answer = await get_answer(channel, test_id)
            if answer is None:
                await delete_test(test_id)
                return
            logging.info("[%s] Got answer: %s", test_id, answer)

            try:
                characters.send(answer)
            except StopIteration:
                pass

        await update_test_results(
            test_id, TestResults(count=tester.estimate_count(), breakdown=tester.get_breakdown())
        )
        logging.info("[%s] Completed test", test_id)

    except Exception:
        logging.exception("[%s] An unexpected error occurred in test", test_id)
        await set_test_errored(test_id)


async def get_answer(channel: Channel, test_id: int) -> bool | None:
    config = get_config()
    start = time.time()
    while True:
        answer = await channel.next_answer(test_id)
        if answer is not None:
            return answer

        await asyncio.sleep(0.2)

        if time.time() - start > config.test_inactivity_timeout:
            return None
