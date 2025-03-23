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

    def __add__(self, other: "GuessResults") -> "GuessResults":
        return GuessResults(
            correct=self.correct + other.correct, incorrect=self.incorrect + other.incorrect
        )

    def ratio(self) -> float:
        return self.correct / (self.correct + self.incorrect)


class SimpleTester(Tester):
    """
    Splits character into bins based on how common they are, and begins with the first bin

    Will serve `chars_per_level` characters from the current bin before advancing to the next bin

    Once the first bin is reached where none are correct, it will reduce the bin by 1, then will
    enter a state where it will either increase the bin or decrease the bin after each set of
    characters based on if the ratio of correct answers is above or below 50%.

    Will repeat this process until it has revisited the same bin `max_level_repeats` times
    """

    def __init__(
        self,
        chars: list[Hanzi],
        bin_size: int = 500,
        chars_per_level: int = 4,
        max_level_repeats: int = 2,
    ) -> None:
        super().__init__(chars)
        self.name = "simple"

        self.bin_size = bin_size
        self.chars_per_level = chars_per_level
        self.max_level_repeats = max_level_repeats

        self.seen_chars: set[Hanzi] = set()
        self.answers: dict[int, GuessResults] = defaultdict(GuessResults)
        self.bins = list(itertools.batched(self.chars, self.bin_size))
        self.second_stage = False

    def characters(self) -> Generator[Hanzi, bool, None]:
        """Serve characters and receive answers using a generator until the test is over"""
        current_bin, char_no = 0, 0
        current_results = GuessResults()
        times_visited: dict[int, int] = defaultdict(int)

        char = self._get_character(current_bin)

        while True:
            answer = yield char

            if answer is None:
                continue

            char_no += 1

            if answer:
                current_results.correct += 1
            else:
                current_results.incorrect += 1

            # Change level once number of characters reached
            if char_no % self.chars_per_level == 0:
                self.answers[current_bin] += current_results

                if self.second_stage:
                    # In 2nd stage inc/decr bin based on ratio, break if bin visited too many times
                    times_visited[current_bin] += 1
                    if times_visited[current_bin] == self.max_level_repeats:
                        break

                    if current_results.ratio() >= 0.5:
                        current_bin = self._incr_bin(current_bin)
                    else:
                        current_bin = self._decr_bin(current_bin)

                else:
                    # In 1st stage, inc bin each time until none correct or reached last bin
                    if current_results.correct == 0 or current_bin == len(self.bins) - 1:
                        self.second_stage = True
                    else:
                        current_bin = self._incr_bin(current_bin)

                current_results = GuessResults()

            char = self._get_character(current_bin)

    def _incr_bin(self, current_bin: int) -> int:
        """Increment bin if below the maximum"""
        if current_bin == len(self.bins) - 1:
            return current_bin
        return current_bin + 1

    def _decr_bin(self, current_bin: int) -> int:
        """Decrease bin if above the minimum"""
        if current_bin == 0:
            return current_bin
        return current_bin - 1

    def _get_character(self, bin: int) -> Hanzi:
        """Get a unique random character from the given bin"""
        while (char := random.choice(self.bins[bin])) in self.seen_chars:
            ...
        self.seen_chars.add(char)
        return char

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
        # Multipy ratio midpoint by the diff to estimate characters known above the last over 50%
        # bin
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
