from datetime import datetime
from typing import ClassVar

from sqlalchemy import BigInteger
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from ..testers import TestType
from .data_types import TestStatus


class Base(MappedAsDataclass, DeclarativeBase):
    type_annotation_map: ClassVar[dict] = {
        datetime: postgresql.TIMESTAMP(timezone=True),
        dict: postgresql.JSONB,
    }


class Test(Base):
    __tablename__ = "tests"
    __table_args__ = {"schema": "main"}  # noqa: RUF012

    test_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, init=False
    )
    test_type: Mapped[TestType]
    status: Mapped[TestStatus]
    start_time: Mapped[datetime | None]
    end_time: Mapped[datetime | None]
    results: Mapped[dict | None]
