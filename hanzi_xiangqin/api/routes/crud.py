from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import Test, TestResults, TestStatus, TestType


async def create_test(session: AsyncSession, test_type: TestType | None = None) -> Test:
    test = Test(test_type or TestType.SIMPLE)
    session.add(test)
    await session.commit()
    return test


async def get_test_by_uid(session: AsyncSession, test_id: str) -> Test:
    try:
        return (await session.scalars(select(Test).where(Test.uid == test_id))).one()
    except NoResultFound:
        raise HTTPException(404, "Test not found")


async def get_test_results(session: AsyncSession, test_id: str) -> TestResults | None:
    return (await session.scalars(select(Test.results).where(Test.uid == test_id))).one()


async def get_test_id_and_status(session: AsyncSession, test_id: str) -> tuple[int, TestStatus]:
    try:
        return (
            (await session.execute(select(Test.test_id, Test.status).where(Test.uid == test_id)))
            .tuples()
            .one()
        )
    except NoResultFound:
        raise HTTPException(404, "Test not found")
