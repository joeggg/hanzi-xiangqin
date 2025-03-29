import os
import shutil

import matplotlib.pyplot as plt
import numpy as np

from hanzi_xiangqin.data_types import load_character_list
from hanzi_xiangqin.testers import GuessResults
from hanzi_xiangqin.testers.estimators import (
    LeastSquaresEstimator,
    tanh_model,
    tanh_model_integral,
)

domain = list(range(500, 9000, 500))

TEST_CASES = {
    "flat_high": {x: GuessResults(1, 0) for x in domain},
    "flat_low": {x: GuessResults(0, 1) for x in domain},
    "single_low": {x: GuessResults(0, 1) for x in [500]},
    "linear_decreasing": {x: GuessResults(len(domain) - i, i) for i, x in enumerate(domain, 1)},
    "slow_linear_decreasing": {
        x: GuessResults(3 * len(domain) - i, i) for i, x in enumerate(domain, 1)
    },
    "fast_linear_decreasing": {
        x: GuessResults(max(0, len(domain) - 2 * i), 2 * i) for i, x in enumerate(domain, 1)
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


def run_plot_tests() -> None:
    copy_to = "/mnt/c/Users/Joe/Desktop/plots"

    if os.path.exists("plots"):
        shutil.rmtree("plots")
    os.mkdir("plots")

    for name, answers in TEST_CASES.items():
        create_plot(answers, name)

    if os.path.exists(copy_to):
        shutil.rmtree(copy_to)

    shutil.copytree("plots", copy_to)


def create_plot(answers: dict[int, GuessResults], name: str) -> None:
    estimator = LeastSquaresEstimator()
    count = estimator.estimate_count(answers, len(load_character_list()))

    print(estimator.x)
    print(count)
    print(f"{int(np.max([count, np.float64(0)]).round(-2))}+")
    print()

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


if __name__ == "__main__":
    run_plot_tests()
