import os
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pytest

from hanzi_xiangqin.data_types import load_character_list
from hanzi_xiangqin.testers import GuessResults
from hanzi_xiangqin.testers.estimators import LeastSquaresEstimator

DOMAIN = list((x, x + 500) for x in range(0, 8500, 500))
COPY_TO = "/mnt/c/Users/Joe/Desktop/plots"

TEST_CASES: dict[str, dict[tuple[int, int], GuessResults]] = {
    "flat_high": {x: GuessResults(1, 0) for x in DOMAIN},
    "flat_low": {x: GuessResults(0, 1) for x in DOMAIN},
    "single_low": {x: GuessResults(0, 1) for x in [(0, 500)]},
    "linear_decreasing": {x: GuessResults(len(DOMAIN) - i, i) for i, x in enumerate(DOMAIN, 1)},
    "slow_linear_decreasing": {
        x: GuessResults(3 * len(DOMAIN) - i, i) for i, x in enumerate(DOMAIN, 1)
    },
    "fast_linear_decreasing": {
        x: GuessResults(max(0, len(DOMAIN) - 2 * i), 2 * i) for i, x in enumerate(DOMAIN, 1)
    },
    "realistic_medium": {
        (0, 500): GuessResults(4, 0),
        (500, 1000): GuessResults(4, 0),
        (1000, 1500): GuessResults(3, 1),
        (1500, 2000): GuessResults(1, 3),
        (2000, 2500): GuessResults(5, 3),
        (2500, 3000): GuessResults(3, 8),
        (3000, 3500): GuessResults(0, 4),
    },
    "realistic_low": {
        (0, 500): GuessResults(4, 0),
        (500, 1000): GuessResults(5, 3),
        (1000, 1500): GuessResults(2, 10),
        (1500, 2000): GuessResults(1, 7),
    },
    "realistic_very_low": {
        (0, 500): GuessResults(3, 1),
        (500, 1000): GuessResults(3, 5),
        (1000, 1500): GuessResults(1, 3),
    },
    "realistic_high": {
        (0, 500): GuessResults(4, 0),
        (500, 1000): GuessResults(4, 0),
        (1000, 1500): GuessResults(4, 0),
        (1500, 2000): GuessResults(3, 1),
        (2000, 2500): GuessResults(3, 1),
        (2500, 3000): GuessResults(2, 2),
        (3000, 3500): GuessResults(5, 3),
        (3500, 4000): GuessResults(3, 9),
        (4000, 4500): GuessResults(1, 7),
    },
    "astrid": {
        (0, 500): GuessResults(2, 2),
        (500, 1000): GuessResults(2, 2),
        (1000, 1500): GuessResults(4, 4),
        (1500, 2000): GuessResults(3, 9),
        (2000, 2500): GuessResults(1, 7),
        (2500, 3000): GuessResults(1, 7),
        (3000, 3500): GuessResults(0, 8),
    },
}


@pytest.fixture(scope="module", autouse=True)
def set_up_and_copy_plots():
    if os.path.exists("plots"):
        shutil.rmtree("plots")

    os.mkdir("plots")

    yield

    if os.path.exists(COPY_TO):
        shutil.rmtree(COPY_TO)

    shutil.copytree("plots", COPY_TO)


@pytest.mark.parametrize("name,answers", list(TEST_CASES.items()))
def test_tanh_estimator(name: str, answers: dict[tuple[int, int], GuessResults]) -> None:
    estimator = LeastSquaresEstimator()
    model = estimator.get_model()
    count = estimator.estimate_count(answers, len(load_character_list()))

    print(model.x)
    print(count)
    print(f"{int(np.max([count, np.float64(0)]).round(-2))}+")

    plt.plot(estimator.t_without_padding, estimator.y_without_padding, "o")
    new_t = np.linspace(1, 10_000, 10_000, dtype=np.float64)

    plt.plot(new_t, model.evaluate_range(new_t))

    plt.axvline(
        model.integral(np.float64(0), np.float64(10000)),
        ymax=model.evaluate_range(np.array([count]))[0],
        linestyle="--",
    )

    plt.title(name)
    plt.savefig(f"plots/{name}.png")
    plt.clf()
