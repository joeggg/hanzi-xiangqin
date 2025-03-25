import json
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Generator

from ..data_types import Hanzi
from .estimators import Estimator


@dataclass
class GuessResults:
    correct: int = 0
    incorrect: int = 0

    def __add__(self, other: "GuessResults") -> "GuessResults":
        return GuessResults(
            correct=self.correct + other.correct, incorrect=self.incorrect + other.incorrect
        )

    def ratio(self) -> float:
        return self.correct / (self.correct + self.incorrect)


class Tester(ABC):
    def __init__(self, chars: list[Hanzi]) -> None:
        self.chars = chars
        self.name = "Tester"
        self.estimator: Estimator
        self.answers: dict[int, GuessResults] = {}

    @abstractmethod
    def characters(self) -> Generator[Hanzi, bool, None]:
        """Yields characters until the test is over"""

    def estimate_count(self) -> int:
        """Estimates the number of characters known by the user"""
        return self.estimator.estimate_count(self.answers)

    def get_breakdown(self) -> dict:
        return {freq_level: asdict(results) for freq_level, results in self.answers.items()}

    def print_debug_info(self) -> None:
        print("\n****Breakdown****\n")
        print(json.dumps(self.get_breakdown(), indent=2))
        print("\n***************\n")
