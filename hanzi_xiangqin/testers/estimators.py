import itertools
from typing import TYPE_CHECKING, Protocol

import numpy as np
import numpy.typing as npt
from scipy.optimize import least_squares

if TYPE_CHECKING:
    from .tester import GuessResults


class Estimator(Protocol):
    def estimate_count(
        self, answers: dict[int, "GuessResults"], maximum_characters: int
    ) -> np.float64: ...


def tanh_model(x: npt.NDArray[np.float64], t: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Subtract the result of the tanh model from the actual value y"""
    return 0.5 - 0.5 * np.tanh((x[0] * t) - x[1])


def tanh_model_integral(x: npt.NDArray[np.float64], a: np.float64, b: np.float64) -> np.float64:
    """Calculate integral of the tanh model between a and b"""
    return _tanh_model_integral(x, b) - _tanh_model_integral(x, a)


def _tanh_model_integral(x: npt.NDArray[np.float64], t: np.float64) -> np.float64:
    """Calculate integral of the tanh model at a particular point, ignoring c"""
    return 0.5 * t - (0.5 * np.log(np.cosh(x[0] * t - x[1])) / x[0])


def tanh_model_residual(
    x: npt.NDArray[np.float64], t: npt.NDArray[np.float64], y: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """Subtract the result of the tanh model from the actual value y"""
    return tanh_model(x, t) - y


class LeastSquaresEstimator:
    """
    Fits a tanh curve to the given test data using scipy's least_squares function, then will
    integrate across the total number of characters to estimate the number of characters known
    """

    def __init__(self) -> None:
        self.name = "least_squares"
        self.maximum_characters = 10_000

        self.t: npt.NDArray[np.float64]
        self.y: npt.NDArray[np.float64]
        self.x: npt.NDArray[np.float64]

    def _get_t_padding(self) -> list[int]:
        return list(range(self.maximum_characters, self.maximum_characters + 20_000, 1000))

    @property
    def t_without_padding(self) -> npt.NDArray[np.float64]:
        padding = self._get_t_padding()
        return self.t[: -len(padding)]

    @property
    def y_without_padding(self) -> npt.NDArray[np.float64]:
        padding = self._get_t_padding()
        return self.y[: -len(padding)]

    def estimate_count(
        self, answers: dict[int, "GuessResults"], maximum_characters: int
    ) -> np.float64:
        self.maximum_characters = maximum_characters
        # Ensure bins are sorted from lowest to highest
        ordered_bins = sorted(answers.keys())
        # Padding helps ensure the curve drops to 0 soon after the max number of characters
        top_padding = self._get_t_padding()

        self.t = np.array([*ordered_bins, *top_padding], np.float64)
        self.y = np.array(
            [
                *[answers[k].ratio() for k in ordered_bins],
                *itertools.repeat(0.0, len(top_padding)),
            ],
            np.float64,
        )
        # Initialise with experimentally determined parameters that form a believable curve
        x0 = np.array([0.001, 3])
        # Fit a tanh model to the data
        results = least_squares(
            tanh_model_residual,
            x0,
            args=(self.t, self.y),
            loss="soft_l1",
        )
        self.x = results.x
        # Get the area under the curve from 0 to the max number of characters
        return tanh_model_integral(self.x, np.float64(0), np.float64(self.maximum_characters))


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
