import asyncio
import logging

import pytest
from pytest_mock import MockerFixture

from hanzi_xiangqin.db import Channel, TestJob, TestType
from hanzi_xiangqin.worker.worker import Worker, WorkerConfig


@pytest.fixture
def worker() -> Worker:
    return Worker(WorkerConfig(max_tasks=1, timer_poll_interval_s=0.1))


@pytest.mark.asyncio(loop_scope="session")
async def test_cancel_tasks(channel: Channel, worker: Worker, mocker: MockerFixture):
    spy = mocker.spy(logging, "error")

    await channel.queue_test(TestJob(1, TestType.SIMPLE))

    worker_task = asyncio.create_task(worker.run())
    await asyncio.sleep(0.1)

    worker.shut_down()
    await worker_task

    assert spy.call_count == 1
    assert spy.call_args[0] == ("Test %s was cancelled!", 1)


@pytest.mark.asyncio(loop_scope="session")
async def test_max_jobs(channel: Channel, worker: Worker, mocker: MockerFixture):
    spy = mocker.spy(logging, "warning")

    await channel.queue_test(TestJob(1, TestType.SIMPLE))
    await channel.queue_test(TestJob(2, TestType.SIMPLE))

    worker_task = asyncio.create_task(worker.run())
    await asyncio.sleep(0.5)

    assert spy.call_count == 1
    assert spy.call_args[0] == ("Too many tasks, cancelling new test",)
    assert len(worker.jobs) == 1

    worker.shut_down()
    await worker_task
