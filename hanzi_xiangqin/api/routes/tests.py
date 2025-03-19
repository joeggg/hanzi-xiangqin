import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import Channel, Test, TestJob, TestResults, TestStatus
from ...testers import TestType
from ..dependencies import channel, db_session
from .crud import create_test, get_test_by_uid, get_test_id_and_status, get_test_results
from .schemas import AnswerBody, NextCharacterResponse, StartTestResponse, TestRespone

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/start")
async def start_test(
    session: Annotated[AsyncSession, Depends(db_session)],
    channel: Annotated[Channel, Depends(channel)],
    test_type: TestType | None = None,
) -> StartTestResponse:
    test = await create_test(session, test_type)

    logging.info("Queueing test %s", test.test_id)
    await channel.queue_test(TestJob(test.test_id, test.test_type))

    return StartTestResponse(test_id=str(test.uid))


@router.get("/{test_id}", response_model=TestRespone)
async def get_test(session: Annotated[AsyncSession, Depends(db_session)], test_id: str) -> Test:
    return await get_test_by_uid(session, test_id)


@router.get("/{test_id}/next")
async def get_next_character(
    session: Annotated[AsyncSession, Depends(db_session)],
    channel: Annotated[Channel, Depends(channel)],
    test_id: str,
) -> NextCharacterResponse:
    uid, status = await get_test_id_and_status(session, test_id)

    if status == TestStatus.DONE:
        return NextCharacterResponse(done=True)
    elif status == TestStatus.ERROR:
        raise HTTPException(500, "Test errored")

    character = await channel.next_character(uid)
    if character is None:
        raise HTTPException(429, "waiting for next character")

    return NextCharacterResponse(character=character)


@router.post("/{test_id}/answer")
async def post_answer(
    session: Annotated[AsyncSession, Depends(db_session)],
    channel: Annotated[Channel, Depends(channel)],
    test_id: str,
    answer: AnswerBody,
) -> None:
    uid, status = await get_test_id_and_status(session, test_id)

    if status == TestStatus.IN_PROGRESS:
        await channel.put_answer(uid, answer.answer)


@router.get("/{test_id}/results")
async def get_results(
    session: Annotated[AsyncSession, Depends(db_session)], test_id: str
) -> TestResults:
    results = await get_test_results(session, test_id)
    if results is None:
        raise HTTPException(404, "Results not found")

    return results
