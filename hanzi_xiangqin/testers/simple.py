import itertools
import random
from collections import defaultdict
from typing import Generator

from ..data_types import Hanzi
from .estimators import Estimator, LeastSquaresEstimator
from .tester import GuessResults, Tester


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
        estimator: type[Estimator] = LeastSquaresEstimator,
    ) -> None:
        super().__init__(chars)
        self.name = "simple"

        self.bin_size = bin_size
        self.chars_per_level = chars_per_level
        self.max_level_repeats = max_level_repeats
        self.estimator = estimator()

        self.seen_chars: set[Hanzi] = set()
        self.answers: dict[tuple[int, int], GuessResults] = defaultdict(GuessResults)
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
                bin_interval = (current_bin * self.bin_size, (current_bin + 1) * self.bin_size)
                self.answers[bin_interval] += current_results

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
