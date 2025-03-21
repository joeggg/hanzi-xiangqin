import logging
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from hanzi_xiangqin.data_types import Definition, Hanzi
from hanzi_xiangqin.db import Channel, Test, TestStatus
from hanzi_xiangqin.testers import TestType


@pytest.fixture
def test(session: Session) -> Test:
    test = Test(test_type=TestType.SIMPLE)
    session.add(test)
    session.commit()
    return test


@pytest.mark.asyncio(loop_scope="session")
async def test_start_test(async_client: AsyncClient, session: Session):
    response = (await async_client.post("/tests/start")).raise_for_status()
    data = response.json()

    tests = session.scalars(select(Test)).all()

    assert len(tests) == 1
    assert str(tests[0].uid) == data["test_id"]


@pytest.mark.asyncio(loop_scope="session")
async def test_next_character_bad_id(async_client: AsyncClient):
    response = await async_client.get("/tests/blah/next")
    assert response.status_code == 422


@pytest.mark.asyncio(loop_scope="session")
async def test_next_character_bad_no_test(async_client: AsyncClient):
    response = await async_client.get(f"/tests/{uuid4()}/next")
    assert response.status_code == 404


@pytest.mark.asyncio(loop_scope="session")
async def test_next_character_not_available(async_client: AsyncClient, test: Test):
    logging.warning("HIHIH %s", test.uid)
    response = await async_client.get(f"/tests/{test.uid}/next")
    assert response.status_code == 429


@pytest.mark.asyncio(loop_scope="session")
async def test_next_character(async_client: AsyncClient, channel: Channel, test: Test):
    hanzi = Hanzi(
        simplified="",
        traditional="Test",
        rank=1,
        definitions=[Definition(pinyin="test", text="test")],
    )
    await channel.put_character(test.test_id, hanzi)

    # Run twice to check if caching is working
    for _ in range(2):
        response = (await async_client.get(f"/tests/{test.uid}/next")).raise_for_status()
        data = response.json()

        assert data["character"] == hanzi.model_dump()


@pytest.mark.asyncio(loop_scope="session")
async def test_post_answer_not_started(async_client: AsyncClient, channel: Channel, test: Test):
    (await async_client.post(f"/tests/{test.uid}/answer", json={"answer": True})).raise_for_status()

    assert await channel.next_answer(test.test_id) is None


@pytest.mark.asyncio(loop_scope="session")
async def test_post_answer(
    async_client: AsyncClient, session: Session, channel: Channel, test: Test
):
    session.execute(update(Test).where(Test.uid == test.uid).values(status=TestStatus.IN_PROGRESS))
    session.commit()

    (await async_client.post(f"/tests/{test.uid}/answer", json={"answer": True})).raise_for_status()

    assert await channel.next_answer(test.test_id) is True

    # After answer is posted should 429 until next character is available
    response = await async_client.get(f"/tests/{test.uid}/next")
    assert response.status_code == 429


@pytest.mark.asyncio(loop_scope="session")
async def test_next_character_done(async_client: AsyncClient, session: Session, test: Test):
    session.execute(update(Test).where(Test.uid == test.uid).values(status=TestStatus.DONE))
    session.commit()

    response = (await async_client.get(f"/tests/{test.uid}/next")).raise_for_status()
    data = response.json()

    assert data == {"done": True, "character": None}
