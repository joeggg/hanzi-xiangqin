from ..db import TestType
from .simple import SimpleTester
from .tester import GuessResults, Tester

TESTERS = {
    TestType.SIMPLE: SimpleTester,
}

__all__ = [
    "GuessResults",
    "SimpleTester",
    "Tester",
]
