import traceback

from sqlalchemy import delete, update

from ..db import Test, TestResults, TestStatus, get_async_engine


async def update_test_results(test_id: int, results: TestResults) -> None:
    async with get_async_engine().begin() as conn:
        await conn.execute(
            update(Test)
            .where(Test.test_id == test_id)
            .values(status=TestStatus.DONE, results=results)
        )


async def delete_test(test_id: int) -> None:
    async with get_async_engine().begin() as conn:
        await conn.execute(delete(Test).where(Test.test_id == test_id))


async def set_test_in_progress(test_id: int) -> None:
    async with get_async_engine().begin() as conn:
        await conn.execute(
            update(Test).where(Test.test_id == test_id).values(status=TestStatus.IN_PROGRESS)
        )


async def set_test_errored(test_id: int) -> None:
    async with get_async_engine().begin() as conn:
        await conn.execute(
            update(Test)
            .where(Test.test_id == test_id)
            .values(status=TestStatus.ERROR, error=traceback.format_exc())
        )
