from dataclasses import dataclass
from enum import StrEnum

import numpy as np
import numpy.typing as npt


class ModelType(StrEnum):
    NONE = "none"
    TANH = "tanh"


@dataclass
class Model:
    model_type: ModelType
    x: npt.NDArray[np.float64]

    def to_dict(self) -> dict:
        return {"model_type": str(self.model_type), "x": [float(x) for x in self.x]}

    @classmethod
    def from_dict(cls, data: dict) -> "Model":
        return Model(ModelType(data["model_type"]), np.array(data["x"], dtype=np.float64))

    @classmethod
    def default(cls, model_type: ModelType) -> "Model":
        match model_type:
            case ModelType.TANH:
                return Model(model_type, x=np.array([0.001, 3], dtype=np.float64))
            case ModelType.NONE:
                return Model(model_type, x=np.array([], dtype=np.float64))

    def residual(
        self, x: npt.NDArray[np.float64], t: npt.NDArray[np.float64], y: npt.NDArray[np.float64]
    ) -> npt.NDArray[np.float64]:
        match self.model_type:
            case ModelType.TANH:
                return tanh_model_residual(x, t, y)
            case ModelType.NONE:
                return np.array([])

    def integral(self, a: np.float64, b: np.float64) -> np.float64:
        match self.model_type:
            case ModelType.TANH:
                return tanh_model_integral(self.x, a, b)
            case ModelType.NONE:
                return np.float64(0)

    def evaluate_range(self, t: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        match self.model_type:
            case ModelType.TANH:
                return tanh_model(self.x, t)
            case ModelType.NONE:
                return np.array([], dtype=np.float64)


def tanh_model_residual(
    x: npt.NDArray[np.float64], t: npt.NDArray[np.float64], y: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """Subtract the result of the tanh model from the actual value y"""
    return tanh_model(x, t) - y


def tanh_model(x: npt.NDArray[np.float64], t: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """
    Negative tanh function running from 1 to 0, with configurable parameters x to adjust curvature
    and translation
    """
    return 0.5 - 0.5 * np.tanh((x[0] * t) - x[1])


def tanh_model_integral(x: npt.NDArray[np.float64], a: np.float64, b: np.float64) -> np.float64:
    """Calculate integral of the tanh model between a and b"""
    return _tanh_model_integral(x, b) - _tanh_model_integral(x, a)


def _tanh_model_integral(x: npt.NDArray[np.float64], t: np.float64) -> np.float64:
    """Calculate integral of the tanh model at a particular point, ignoring c"""
    return 0.5 * t - (0.5 * np.log(np.cosh(x[0] * t - x[1])) / x[0])
