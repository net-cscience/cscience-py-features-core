from dataclasses import dataclass

from cscience.features.api import FloatValue

from ..nsfw_image_datatypes.nsfw_image_datatype import NsfwImageDatatype


@dataclass(frozen=True, slots=True)
class NsfwPredictionData:
    """NSFW classification result for one image."""

    label: str
    score: float
    normal_score: float
    nsfw_score: float

    def is_nsfw(self, threshold: float = 0.5) -> bool:
        """Return whether the NSFW score is at or above the threshold."""
        return self.nsfw_score >= threshold


class NsfwPrediction(NsfwImageDatatype):
    """Single NSFW classification result."""

    def __init__(self, data: NsfwPredictionData) -> None:
        if type(data.label) is not str:
            raise TypeError(f"NsfwPrediction label expects str, got {type(data.label).__name__}.")

        if type(data.score) is not float:
            raise TypeError(f"NsfwPrediction score expects float, got {type(data.score).__name__}.")

        if type(data.normal_score) is not float:
            raise TypeError(
                f"NsfwPrediction normal_score expects float, got {type(data.normal_score).__name__}."
            )

        if type(data.nsfw_score) is not float:
            raise TypeError(
                f"NsfwPrediction nsfw_score expects float, got {type(data.nsfw_score).__name__}."
            )

        if not 0.0 <= data.score <= 1.0:
            raise ValueError(f"NsfwPrediction score must be in [0, 1], got {data.score}.")

        if not 0.0 <= data.normal_score <= 1.0:
            raise ValueError(
                f"NsfwPrediction normal_score must be in [0, 1], got {data.normal_score}."
            )

        if not 0.0 <= data.nsfw_score <= 1.0:
            raise ValueError(
                f"NsfwPrediction nsfw_score must be in [0, 1], got {data.nsfw_score}."
            )

        super().__init__(data)

    def nsfw_score(self) -> FloatValue:
        """Return the NSFW score as a core float value."""
        return FloatValue(self.data().nsfw_score)