import uuid

from fastapi import APIRouter, Depends
from redis.asyncio import Redis

from hanzi_xiangqin.api.dependencies import async_redis

from .schemas import StartTestResponse

router = APIRouter(prefix="/tests", tags=["tests"])


@router.get("/start")
async def start_test(redis: Redis = Depends(async_redis)) -> StartTestResponse:
    test_id = uuid.uuid4()
    await redis.lpush("tests", str(test_id))
    return StartTestResponse(test_id=test_id)
