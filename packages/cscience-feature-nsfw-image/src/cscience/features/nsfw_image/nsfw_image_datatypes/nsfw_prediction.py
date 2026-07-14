from dataclasses import dataclass

from cscience.features.api import FloatValue

from .nsfw_image_datatype import NsfwImageDatatype
from .nsfw_prediction_data import NsfwPredictionData


class NsfwPrediction(
    NsfwImageDatatype[NsfwPredictionData],
):
    """Single NSFW classification result."""

    def __init__(self, data: NsfwPredictionData) -> None:
        self.validate_data(data)
        super().__init__(data)

    @staticmethod
    def validate_data(data: NsfwPredictionData) -> None:
        """Validate an NSFW prediction data object."""
        if not isinstance(data, NsfwPredictionData):
            raise TypeError(
                f"NsfwPrediction expects NsfwPredictionData, "
                f"got {type(data).__name__}."
            )

        if type(data.label) is not str:
            raise TypeError(
                f"NsfwPrediction label expects str, "
                f"got {type(data.label).__name__}."
            )

        NsfwPrediction._validate_score(
            name="score",
            value=data.score,
        )
        NsfwPrediction._validate_score(
            name="normal_score",
            value=data.normal_score,
        )
        NsfwPrediction._validate_score(
            name="nsfw_score",
            value=data.nsfw_score,
        )

    @staticmethod
    def _validate_score(
        name: str,
        value: float,
    ) -> None:
        if type(value) is not float:
            raise TypeError(
                f"NsfwPrediction {name} expects float, "
                f"got {type(value).__name__}."
            )

        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"NsfwPrediction {name} must be in [0, 1], "
                f"got {value}."
            )

    def nsfw_score(self) -> FloatValue:
        """Return the NSFW score as a core float value."""
        return FloatValue(self.data().nsfw_score)