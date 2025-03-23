import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import AfterValidator
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import Channel, Test, TestJob, TestResults, TestStatus, TestType
from ..dependencies import channel, db_session
from .crud import create_test, get_test_by_uid, get_test_id_and_status, get_test_results
from .schemas import AnswerBody, NextCharacterResponse, StartTestResponse, TestRespone

router = APIRouter(prefix="/tests", tags=["tests"])


def validate_uuid(uid: str) -> str:
    return str(UUID(uid))


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


@router.get("/{uid}", response_model=TestRespone)
async def get_test(
    session: Annotated[AsyncSession, Depends(db_session)],
    uid: Annotated[str, AfterValidator(validate_uuid)],
) -> Test:
    return await get_test_by_uid(session, uid)


@router.get("/{uid}/next")
async def get_next_character(
    session: Annotated[AsyncSession, Depends(db_session)],
    channel: Annotated[Channel, Depends(channel)],
    uid: Annotated[str, AfterValidator(validate_uuid)],
) -> NextCharacterResponse:
    test_id, status = await get_test_id_and_status(session, uid)

    if status == TestStatus.DONE:
        return NextCharacterResponse(done=True)
    elif status == TestStatus.ERROR:
        raise HTTPException(500, "Test errored")

    character = await channel.next_character(test_id)
    if character is None:
        raise HTTPException(429, "waiting for next character")

    return NextCharacterResponse(character=character)


@router.post("/{uid}/answer")
async def post_answer(
    session: Annotated[AsyncSession, Depends(db_session)],
    channel: Annotated[Channel, Depends(channel)],
    uid: Annotated[str, AfterValidator(validate_uuid)],
    answer: AnswerBody,
) -> None:
    test_id, status = await get_test_id_and_status(session, uid)

    if status == TestStatus.IN_PROGRESS:
        await channel.put_answer(test_id, answer.answer)


@router.get("/{uid}/results")
async def get_results(
    session: Annotated[AsyncSession, Depends(db_session)],
    uid: Annotated[str, AfterValidator(validate_uuid)],
) -> TestResults:
    results = await get_test_results(session, uid)
    if results is None:
        raise HTTPException(404, "Results not found")

    return results
