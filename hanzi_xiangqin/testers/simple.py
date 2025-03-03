import itertools
import random
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Generator

from ..data_types import Hanzi
from .tester import Tester


@dataclass
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
        correct_ratios = {
            bin: results.correct / (results.correct + results.incorrect)
            for bin, results in self.answers.items()
        }
        max_bin = max(self.answers.keys())

        # Get the last bin with a ratio over 50% and the first bin with a non-zero ratio below 50%
        last_over_50, last_below_50 = 0, max_bin + 1
        for bin, ratio in correct_ratios.items():
            if ratio >= 0.5:
                last_over_50 = bin
            elif ratio > 0:
                last_below_50 = bin

        # Get the number of chars up to each bin and the diff between the 2
        last_over_50_chars = (last_over_50 + 1) * self.bin_size
        last_below_50_chars = (last_below_50 + 1) * self.bin_size
        diff = last_below_50_chars - last_over_50_chars

        # Get the midpoint between the latest max and bin ratios
        last_over_50_ratio = correct_ratios[last_over_50]
        last_below_50_ratio = correct_ratios.get(last_below_50, 0)
        ratio_midpoint = (last_over_50_ratio + last_below_50_ratio) / 2
        # Multipy ratio midpoint by the diff to estimate characters known above the last over 50% bin
        extra_chars = ratio_midpoint * diff

        # Assume all chars before last over 50% bin are known
        # Use the ratio to get characters known in that last bin
        # Add the extra chars estimated above that last bin
        return round((last_over_50 + last_over_50_ratio) * self.bin_size) + round(extra_chars)

    def get_breakdown(self) -> dict:
        breakdown = {}
        for bin, results in self.answers.items():
            breakdown[f"{(bin * self.bin_size) + 1}-{(bin + 1) * self.bin_size}"] = asdict(results)
        return breakdown
