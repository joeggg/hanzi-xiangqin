from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from ...data_types import Hanzi
from ...db import TestStatus
from ...testers import TestType


class StartTestResponse(BaseModel):
    test_id: str


class TestRespone(BaseModel):
    uid: UUID
    status: TestStatus
    test_type: TestType
    created_time: datetime
    start_time: datetime | None = None
    end_time: datetime | None = None

    model_config = {"from_attributes": True}


class NextCharacterResponse(BaseModel):
    done: bool = False
    character: Hanzi | None = None


class AnswerBody(BaseModel):
    answer: bool
