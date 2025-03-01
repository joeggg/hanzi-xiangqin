import logging
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["OK"] = "OK"


@router.get("/health")
async def health() -> HealthResponse:
    logging.info("Health check")
    return HealthResponse()
