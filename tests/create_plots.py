import os
import shutil

import matplotlib.pyplot as plt
import numpy as np

from hanzi_xiangqin.testers.estimators import LeastSquaresEstimator, tanh_model, tanh_model_inverse
from hanzi_xiangqin.testers.tester import GuessResults

domain = list(range(500, 9000, 500))

TEST_CASES = {
    "flat_high": {x: GuessResults(1, 0) for x in domain},
    "flat_low": {x: GuessResults(0, 1) for x in domain},
    "linear_decreasing": {x: GuessResults(len(domain), i) for i, x in enumerate(domain, 1)},
}


def run_plot_tests() -> None:
    copy_to = "/mnt/c/Users/Joe/Desktop/plots"

    if not os.path.exists("plots"):
        os.mkdir("plots")

    for name, answers in TEST_CASES.items():
        create_plot(answers, name)

    if os.path.exists(copy_to):
        shutil.rmtree(copy_to)

    shutil.copytree("plots", copy_to)


def create_plot(answers: dict[int, GuessResults], name: str) -> None:
    estimator = LeastSquaresEstimator()
    count = estimator.estimate_count(answers)

    print(estimator.x)
    print(count)
    plt.plot(estimator.t, estimator.y, "o")
    new_t = np.linspace(1, 10000, 10000, dtype=np.float64)

    plt.plot(new_t, tanh_model(estimator.x, new_t))

    plt.axvline(tanh_model_inverse(estimator.x, np.array([0.5]))[0])

    plt.title("Least Squares")
    plt.savefig(f"plots/least_squares_{name}.png")
    plt.clf()


if __name__ == "__main__":
    run_plot_tests()
