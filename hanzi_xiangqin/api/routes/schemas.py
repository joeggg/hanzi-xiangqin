import uuid

from pydantic import BaseModel

from ...data_types import Hanzi


class StartTestResponse(BaseModel):
    test_id: uuid.UUID


class NextCharactorResponse(BaseModel):
    done: bool = False
    character: Hanzi | None = None
