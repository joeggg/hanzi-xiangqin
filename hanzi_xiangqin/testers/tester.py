import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator

import numpy as np

from ..data_types import Hanzi
from .estimators import Estimator, Model


@dataclass
class Breakdown:
    model: Model
    # Bin upper limit to ratio of characters guessed correctly
    data: list[tuple[int, float]]
    curve: list[float]

    def to_dict(self) -> dict:
        return {"model": self.model.to_dict(), "data": self.data, "curve": self.curve}

    @classmethod
    def from_dict(cls, data: dict) -> "Breakdown":
        return Breakdown(Model.from_dict(data["model"]), data["data"], data["curve"])


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
    """
    Serves characters and ingests yes/no answers via its `characters` generator. Will record the
    number of characters gotten correct or incorrect within each frequency bin characters were
    served from.

    Encapsulates an estimator class which it will use to get the count of known characters
    """

    def __init__(self, chars: list[Hanzi]) -> None:
        self.chars = chars
        self.name = "Tester"
        self.estimator: Estimator
        self.answers: dict[tuple[int, int], GuessResults] = {}

    @abstractmethod
    def characters(self) -> Generator[Hanzi, bool, None]:
        """Yields characters and receives answers until the test is over"""

    def estimate_count(self) -> int:
        """Estimates the number of characters known by the user"""
        count = self.estimator.estimate_count(self.answers, len(self.chars))
        # Prevent negative estimates
        return int(np.max([count, np.float64(0)]).round(-2))

    def get_breakdown(self) -> Breakdown:
        """Returns a breakdown of the test results"""
        model = self.estimator.get_model()
        return Breakdown(
            model,
            [(bin_interval[1], result.ratio()) for bin_interval, result in self.answers.items()],
            [
                float(y)
                for y in model.evaluate_range(np.linspace(1, 10_000, 10_000, dtype=np.float64))
            ],
        )

    def print_debug_info(self) -> None:
        print("\n****Breakdown****\n")
        print(json.dumps(self.get_breakdown(), indent=2))
        print("\n***************\n")
