import itertools
from typing import Iterable

import pytest

from hanzi_xiangqin.data_types import Hanzi, load_character_list
from hanzi_xiangqin.testers import LeastSquaresTester, SimpleTester, Tester


@pytest.fixture
def simple_tester() -> SimpleTester:
    return SimpleTester(load_character_list(), bin_size=500, chars_per_level=2, max_level_repeats=4)


@pytest.fixture
def lq_tester() -> SimpleTester:
    return LeastSquaresTester(
        load_character_list(), bin_size=500, chars_per_level=5, max_level_repeats=2
    )


def run_answer_sequence(tester: Tester, answers: Iterable[bool]) -> list[Hanzi]:
    characters = tester.characters()
    answers_iter = iter(answers)

    results = []
    for char in characters:
        results.append(char)
        try:
            characters.send(next(answers_iter))
        except StopIteration:
            break

    return results


def test_first_stage_next_bin(simple_tester: SimpleTester):
    chars = run_answer_sequence(simple_tester, [True, False, True, False])

    for i, char in enumerate(chars):
        lower_rank = (i // simple_tester.chars_per_level) * simple_tester.bin_size
        higher_rank = lower_rank + simple_tester.bin_size

        assert lower_rank <= char.rank < higher_rank

    assert simple_tester.second_stage is False


def test_all_correct(simple_tester: SimpleTester):
    chars = run_answer_sequence(simple_tester, itertools.repeat(True))
    assert len(chars) == simple_tester.chars_per_level * (
        simple_tester.max_level_repeats + len(simple_tester.bins)
    )
    assert simple_tester.second_stage is True


def test_all_incorrect(simple_tester: SimpleTester):
    chars = run_answer_sequence(simple_tester, itertools.repeat(False))
    assert len(chars) == simple_tester.chars_per_level * (simple_tester.max_level_repeats + 1)
    assert simple_tester.second_stage is True
