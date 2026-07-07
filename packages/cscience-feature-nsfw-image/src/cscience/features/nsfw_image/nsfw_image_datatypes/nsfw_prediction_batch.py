from collections.abc import Mapping
from dataclasses import dataclass

from cscience.features.api import BatchBase
from .nsfw_prediction_batch_data import NsfwPredictionBatchData

from ..nsfw_image_datatypes.nsfw_image_datatype import NsfwImageDatatype
from .nsfw_prediction import NsfwPredictionData



class NsfwPredictionBatch(NsfwImageDatatype, BatchBase[NsfwPredictionData]):
    """Batch of NSFW classification results."""

    def __init__(self, data: NsfwPredictionBatchData) -> None:
        self._validate_batch_mapping(data.predictions)

        for key, prediction in data.predictions.items():
            if not isinstance(prediction, NsfwPredictionData):
                raise TypeError(
                    f"NsfwPredictionBatch expects NsfwPredictionData values, "
                    f"got {type(prediction).__name__} at key {key}."
                )

        super().__init__(
            NsfwPredictionBatchData(
                predictions=dict(data.predictions)
            )
        )

    def batch_size(self) -> int:
        """Return the number of predictions."""
        return len(self.data().predictions)