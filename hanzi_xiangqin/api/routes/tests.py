from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis

from ...db import Test, TestChannel, TestDone, TestResults, queue_test
from ...testers import TestType
from ..dependencies import async_redis
from .schemas import NextCharacterResponse, StartTestResponse

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("/start")
async def start_test(redis: Annotated[Redis, Depends(async_redis)]) -> StartTestResponse:
    test = Test(TestType.SIMPLE)
    await queue_test(redis, test)
    return StartTestResponse(test_id=test.test_id)


@router.get("/{test_id}/next")
async def get_next_character(
    test_id: str, redis: Annotated[Redis, Depends(async_redis)]
) -> NextCharacterResponse:
    channel = TestChannel(redis, test_id)
    try:
        character = await channel.next_character()
    except TestDone:
        return NextCharacterResponse(done=True)

    if character is None:
        raise HTTPException(429, "waiting for next character")

    return NextCharacterResponse(character=character)


@router.post("/{test_id}/answer")
async def post_answer(
    test_id: str, answer: bool, redis: Annotated[Redis, Depends(async_redis)]
) -> None:
    channel = TestChannel(redis, test_id)
    await channel.put_answer(answer)


@router.get("/{test_id}/results")
async def get_results(test_id: str, redis: Annotated[Redis, Depends(async_redis)]) -> TestResults:
    channel = TestChannel(redis, test_id)
    if results := await channel.get_results():
        return results
    raise HTTPException(404, "Results not found")
