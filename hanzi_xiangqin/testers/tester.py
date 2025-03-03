import json
from abc import ABC, abstractmethod
from typing import Generator

from ..data_types import Hanzi


class Tester(ABC):
    def __init__(self, chars: list[Hanzi]) -> None:
        self.chars = chars
        self.name = "Tester"

    @abstractmethod
    def characters(self) -> Generator[Hanzi, bool, None]:
        """Yields characters until the test is over"""

    @abstractmethod
    def estimate_count(self) -> int:
        """Estimates the number of characters known by the user"""

    @abstractmethod
    def get_breakdown(self) -> dict:
        """Returns a breakdown of the test results"""

    def print_debug_info(self) -> None:
        print("\n****Breakdown****\n")
        print(json.dumps(self.get_breakdown(), indent=2))
        print("\n***************\n")
