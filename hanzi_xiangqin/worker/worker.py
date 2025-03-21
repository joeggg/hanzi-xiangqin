import asyncio
import logging
import signal
import time
from dataclasses import dataclass
from typing import Callable

from pydantic_settings import BaseSettings

from ..config import get_config
from ..data_types import load_character_list
from ..db import Channel, TestJob, TestResults
from ..testers import TESTERS
from .queries import delete_test, set_test_errored, set_test_in_progress, update_test_results


async def run_worker() -> None:
    worker = Worker()

    def handle_shutdown(*_) -> None:
        logging.info("Shutting down worker")
        worker.shut_down()

    signal.signal(signal.SIGTERM, handle_shutdown)

    await worker.run()


class WorkerConfig(BaseSettings):
    task_cleanup_interval_s: float = 5
    heartbeat_interval_s: float = 60
    poll_interval_s: float = 0.2
    timer_poll_interval_s: float = 5
    max_tasks: int = 100


@dataclass
class Job:
    test_id: int
    task: asyncio.Task


class Worker:
    def __init__(self, config: WorkerConfig | None = None) -> None:
        self.config = config or WorkerConfig()
        self.channel = Channel()
        self.shutting_down = False

        self.jobs: list[Job] = []
        self.timer_tasks: list[asyncio.Task] = []

    async def run(self) -> None:
        logging.info("Starting worker")

        self.timer_tasks = [
            asyncio.create_task(
                self.timer_task(
                    lambda: logging.info("Worker heartbeat"), self.config.task_cleanup_interval_s
                )
            ),
            asyncio.create_task(
                self.timer_task(self.cleanup_tasks, self.config.task_cleanup_interval_s)
            ),
        ]

        while not self.shutting_down:
            await asyncio.sleep(self.config.poll_interval_s)

            try:
                test = await self.channel.pop_test()
                if not test:
                    continue

                if len(self.jobs) >= self.config.max_tasks:
                    logging.warning("Too many tasks, cancelling new test")
                    await delete_test(test.test_id)
                    continue

                self.jobs.append(
                    Job(test.test_id, asyncio.create_task(run_test(self.channel, test)))
                )

            except Exception:
                logging.exception("An unexpected error occurred in worker")

        await self.cancel_tasks()

    async def cancel_tasks(self) -> None:
        for job in self.jobs:
            job.task.cancel()
            try:
                await job.task
            except asyncio.CancelledError:
                logging.error("Test %s was cancelled!", job.test_id)
                await set_test_errored(job.test_id)

        await asyncio.gather(*self.timer_tasks)

    async def timer_task(self, task: Callable[[], None], interval: float) -> None:
        start = time.time()
        while not self.shutting_down:
            await asyncio.sleep(self.config.timer_poll_interval_s)

            if time.time() - start > interval:
                task()
                start = time.time()

    def shut_down(self) -> None:
        self.shutting_down = True

    def cleanup_tasks(self) -> None:
        self.jobs = [job for job in self.jobs if not job.task.done()]


async def run_test(channel: Channel, test: TestJob) -> None:
    test_id = test.test_id
    tester = TESTERS[test.test_type](load_character_list())
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
