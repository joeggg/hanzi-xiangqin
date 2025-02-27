import itertools
import random
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Generator, Iterator

from .data_types import Hanzi


class Tester(ABC):
    def __init__(self, chars: list[Hanzi]) -> None:
        self.chars = chars
        self.name = "Tester"

    @abstractmethod
    def characters(self) -> Iterator[Hanzi]:
        """Yields characters until the test is over"""

    @abstractmethod
    def estimate_count(self) -> int:
        """Estimates the number of characters known by the user"""

    @abstractmethod
    def print_debug_info(self) -> None:
        """Prints detailed information about the test"""


@dataclass()
class GuessResults:
    correct: int = 0
    incorrect: int = 0


class SimpleTester(Tester):
    def __init__(self, chars: list[Hanzi], bin_size: int = 500) -> None:
        super().__init__(chars)
        self.bin_size = bin_size
        self.answers: dict[int, GuessResults] = defaultdict(GuessResults)
        self.name = "simple"

    def characters(self) -> Generator[Hanzi, bool, None]:
        bins = list(itertools.batched(self.chars, 500))

        current_bin = 0
        times_visited: dict[int, int] = defaultdict(int)
        char = random.choice(bins[current_bin])

        while True:
            answer = yield char

            if answer is None:
                continue

            times_visited[current_bin] += 1

            if answer:
                self.answers[current_bin].correct += 1
                if current_bin != len(bins) - 1:
                    current_bin += 1
            else:
                self.answers[current_bin].incorrect += 1
                if current_bin != 0:
                    current_bin -= 1

            if times_visited[current_bin] == 4:
                break

            char = random.choice(bins[current_bin])

    def estimate_count(self) -> int:
        return 0

    def print_debug_info(self):
        print("\n****Results****\n")
        for bin, results in self.answers.items():
            print(f"{(bin * self.bin_size) + 1}-{(bin + 1) * self.bin_size}", asdict(results))
        print()
