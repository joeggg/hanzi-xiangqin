import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ...db import Channel, Test, TestDone, TestNotFound, TestResults
from ...testers import TestType
from ..dependencies import channel
from .schemas import AnswerBody, NextCharacterResponse, StartTestResponse

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("/start")
async def start_test(
    channel: Annotated[Channel, Depends(channel)], test_type: TestType | None = None
) -> StartTestResponse:
    test = Test(test_type or TestType.SIMPLE)
    logging.info("Queueing test %s", test.test_id)
    await channel.queue_test(test)
    return StartTestResponse(test_id=test.test_id)


@router.get("/{test_id}/next")
async def get_next_character(
    channel: Annotated[Channel, Depends(channel)], test_id: str
) -> NextCharacterResponse:
    try:
        character = await channel.next_character(test_id)
    except TestDone:
        return NextCharacterResponse(done=True)
    except TestNotFound:
        raise HTTPException(404, "Test not found")

    if character is None:
        raise HTTPException(429, "waiting for next character")

    return NextCharacterResponse(character=character)


@router.post("/{test_id}/answer")
async def post_answer(
    channel: Annotated[Channel, Depends(channel)], test_id: str, answer: AnswerBody
) -> None:
    await channel.put_answer(test_id, answer.answer)


@router.get("/{test_id}/results")
async def get_results(channel: Annotated[Channel, Depends(channel)], test_id: str) -> TestResults:
    if results := await channel.get_results(test_id):
        return results
    raise HTTPException(404, "Results not found")
