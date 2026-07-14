from dataclasses import dataclass

from .nsfw_prediction import NsfwPredictionData


@dataclass(frozen=True, slots=True)
class NsfwPredictionBatchData:
    """NSFW predictions indexed by source image position."""

    predictions: dict[int, NsfwPredictionData]