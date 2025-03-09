import uuid
from dataclasses import dataclass, field
from functools import cached_property

from ..testers import TestType


class TestDone(Exception): ...


class TestNotFound(Exception): ...


@dataclass
class TestResults:
    count: int
    breakdown: dict


@dataclass
class Test:
    test_type: TestType
    test_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    done: bool = False

    @cached_property
    def char_key(self) -> str:
        return f"{self.test_id}_char_queue"

    @cached_property
    def answer_key(self) -> str:
        return f"{self.test_id}_answer_queue"

    @cached_property
    def results_key(self) -> str:
        return f"{self.test_id}_results"

    @cached_property
    def state_key(self) -> str:
        return f"{self.test_id}_state"
