from ..db import TestType
from .simple import SimpleTester
from .tester import Tester

TESTERS = {
    TestType.SIMPLE: SimpleTester,
}

__all__ = [
    "SimpleTester",
    "Tester",
]
