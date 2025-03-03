from enum import StrEnum

from .simple import SimpleTester
from .tester import Tester


class TestType(StrEnum):
    SIMPLE = "simple"


TESTERS = {TestType.SIMPLE: SimpleTester}

__all__ = ["SimpleTester", "Tester"]
