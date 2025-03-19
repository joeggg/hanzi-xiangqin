import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import ClassVar, TypedDict

from sqlalchemy import BigInteger, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from ..testers import TestType


class TestStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ERROR = "error"


class TestResults(TypedDict):
    count: int
    breakdown: dict


class TestError(TypedDict):
    message: str
    traceback: str


class Base(MappedAsDataclass, DeclarativeBase):
    type_annotation_map: ClassVar[dict] = {
        datetime: postgresql.TIMESTAMP(timezone=True),
        uuid.UUID: postgresql.UUID,
        TestResults: postgresql.JSONB,
        TestError: postgresql.JSONB,
    }


class Test(Base):
    __tablename__ = "tests"
    __table_args__ = {"schema": "main"}  # noqa: RUF012

    test_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, init=False
    )
    uid: Mapped[uuid.UUID] = mapped_column(
        init=False, server_default=text("gen_random_uuid()"), index=True
    )
    test_type: Mapped[TestType]
    status: Mapped[TestStatus] = mapped_column(default=TestStatus.PENDING, index=True)
    created_time: Mapped[datetime] = mapped_column(
        default_factory=lambda: datetime.now(UTC), index=True
    )
    start_time: Mapped[datetime | None] = mapped_column(default=None)
    end_time: Mapped[datetime | None] = mapped_column(default=None)
    results: Mapped[TestResults | None] = mapped_column(default=None)
    error: Mapped[str | None] = mapped_column(default=None)
