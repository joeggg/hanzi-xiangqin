import os
import shutil

import matplotlib.pyplot as plt
import numpy as np
import pytest

from hanzi_xiangqin.data_types import load_character_list
from hanzi_xiangqin.testers import GuessResults
from hanzi_xiangqin.testers.estimators import (
    LeastSquaresEstimator,
    tanh_model,
    tanh_model_integral,
)

DOMAIN = list(range(500, 9000, 500))
COPY_TO = "plots"

TEST_CASES = {
    "flat_high": {x: GuessResults(1, 0) for x in DOMAIN},
    "flat_low": {x: GuessResults(0, 1) for x in DOMAIN},
    "single_low": {x: GuessResults(0, 1) for x in [500]},
    "linear_decreasing": {x: GuessResults(len(DOMAIN) - i, i) for i, x in enumerate(DOMAIN, 1)},
    "slow_linear_decreasing": {
        x: GuessResults(3 * len(DOMAIN) - i, i) for i, x in enumerate(DOMAIN, 1)
    },
    "fast_linear_decreasing": {
        x: GuessResults(max(0, len(DOMAIN) - 2 * i), 2 * i) for i, x in enumerate(DOMAIN, 1)
    },
    "realistic_medium": {
        500: GuessResults(4, 0),
        1000: GuessResults(4, 0),
        1500: GuessResults(3, 1),
        2000: GuessResults(1, 3),
        2500: GuessResults(5, 3),
        3000: GuessResults(3, 8),
        3500: GuessResults(0, 4),
    },
    "realistic_low": {
        500: GuessResults(4, 0),
        1000: GuessResults(5, 3),
        1500: GuessResults(2, 10),
        2000: GuessResults(1, 7),
    },
    "realistic_very_low": {
        500: GuessResults(3, 1),
        1000: GuessResults(3, 5),
        1500: GuessResults(1, 3),
    },
    "realistic_high": {
        500: GuessResults(4, 0),
        1000: GuessResults(4, 0),
        1500: GuessResults(4, 0),
        2000: GuessResults(3, 1),
        2500: GuessResults(3, 1),
        3000: GuessResults(2, 2),
        3500: GuessResults(5, 3),
        4000: GuessResults(3, 9),
        4500: GuessResults(1, 7),
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
def test_tanh_estimator(name: str, answers: dict[int, GuessResults]) -> None:
    estimator = LeastSquaresEstimator()
    count = estimator.estimate_count(answers, len(load_character_list()))

    print(estimator.x)
    print(count)
    print(f"{int(np.max([count, np.float64(0)]).round(-2))}+")

    plt.plot(estimator.t_without_padding, estimator.y_without_padding, "o")
    new_t = np.linspace(1, 10_000, 10_000, dtype=np.float64)

    plt.plot(new_t, tanh_model(estimator.x, new_t))

    plt.axvline(
        tanh_model_integral(estimator.x, np.float64(0), np.float64(10000)),
        ymax=tanh_model(estimator.x, np.array([count]))[0],
        linestyle="--",
    )

    plt.title(name)
    plt.savefig(f"plots/{name}.png")
    plt.clf()
