from ..db import TestType
from .simple import SimpleTester
from .tester import Breakdown, GuessResults, Tester

TESTERS = {
    TestType.SIMPLE: SimpleTester,
}

__all__ = [
    "Breakdown",
    "GuessResults",
    "SimpleTester",
    "Tester",
]
