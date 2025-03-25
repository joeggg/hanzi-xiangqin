from typing import TYPE_CHECKING, Protocol

import numpy as np
import numpy.typing as npt
from scipy.optimize import least_squares

if TYPE_CHECKING:
    from .tester import GuessResults


class Estimator(Protocol):
    def estimate_count(self, answers: dict[int, "GuessResults"]) -> int: ...


def tanh_model(x: npt.NDArray[np.float64], t: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Subtract the result of the tanh model from the actual value y"""
    return 0.5 - 0.5 * np.tanh((x[0] * t) - x[1])


def tanh_model_inverse(
    x: npt.NDArray[np.float64], y: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """Inverse of the tanh model to get t for a given y"""
    return (np.arctanh((0.5 - y) / 0.5) + x[1]) / x[0]


def tanh_model_residual(
    x: npt.NDArray[np.float64], t: npt.NDArray[np.float64], y: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """Subtract the result of the tanh model from the actual value y"""
    return tanh_model(x, t) - y


class LeastSquaresEstimator:
    def __init__(self) -> None:
        self.name = "least_squares"

        self.t: npt.NDArray[np.float64]
        self.y: npt.NDArray[np.float64]
        self.x: npt.NDArray[np.float64]

    def estimate_count(self, answers: dict[int, "GuessResults"]) -> int:
        # Get the bin sizes and the number of correct answers for each
        ordered_answers = sorted(answers.keys())
        self.t = np.array([0, *ordered_answers, 10000], np.float64)
        self.y = np.array([1.0, *[answers[k].ratio() for k in ordered_answers], 0.0], np.float64)
        # Fit a tanh model to the data
        x0 = np.array([0.001, 3])
        results = least_squares(
            tanh_model_residual,
            x0,
            args=(self.t, self.y),
            loss="soft_l1",
        )
        self.x = results.x
        estimate = tanh_model_inverse(self.x, np.array([0.5]))[0]

        return int(estimate.round())


class SimpleEstimator:
    def estimate_count(self, answers: dict[int, "GuessResults"]) -> int:
        correct_ratios = {
            bin: results.correct / (results.correct + results.incorrect)
            for bin, results in answers.items()
        }
        max_bin = max(answers.keys())

        # Get the last bin with a ratio over 50% and the first bin with a non-zero ratio below 50%
        last_over_50, last_below_50 = 0, max_bin + 1
        for bin, ratio in correct_ratios.items():
            if ratio >= 0.5:
                last_over_50 = bin
            elif ratio > 0:
                last_below_50 = bin

        bin_size = next(iter(answers.keys()))

        # Get the number of chars up to each bin and the diff between the 2
        last_over_50_chars = (last_over_50 + 1) * bin_size
        last_below_50_chars = (last_below_50 + 1) * bin_size
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
        return round((last_over_50 + last_over_50_ratio) * bin_size) + round(extra_chars)
