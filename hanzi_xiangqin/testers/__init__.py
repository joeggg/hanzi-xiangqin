from ..db import TestType
from .least_squares import LeastSquaresTester
from .simple import SimpleTester
from .tester import Tester

TESTERS = {
    TestType.SIMPLE: SimpleTester,
    TestType.LEAST_SQUARES: LeastSquaresTester,
}

__all__ = [
    "LeastSquaresTester",
    "SimpleTester",
    "Tester",
]
