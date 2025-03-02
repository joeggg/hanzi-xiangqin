import uuid

from pydantic import BaseModel


class StartTestResponse(BaseModel):
    test_id: uuid.UUID
