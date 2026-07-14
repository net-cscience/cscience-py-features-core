from collections.abc import Mapping

from cscience.features.api import BatchBase

from .nsfw_image_datatype import NsfwImageDatatype
from .nsfw_prediction import (
    NsfwPrediction,
    NsfwPredictionData,
)
from .nsfw_prediction_batch_data import (
    NsfwPredictionBatchData,
)


class NsfwPredictionBatch(
    BatchBase[NsfwPredictionData],
    NsfwImageDatatype[NsfwPredictionBatchData],
):
    """Batch of NSFW classification results."""

    def __init__(
        self,
        data: NsfwPredictionBatchData,
    ) -> None:
        if not isinstance(data, NsfwPredictionBatchData):
            raise TypeError(
                "NsfwPredictionBatch expects "
                f"NsfwPredictionBatchData, "
                f"got {type(data).__name__}."
            )

        self._validate_batch_mapping(data.predictions)

        for prediction in data.predictions.values():
            NsfwPrediction.validate_data(prediction)

        normalized = NsfwPredictionBatchData(
            predictions=dict(data.predictions),
        )

        super().__init__(normalized)

    def _batch_mapping(
        self,
    ) -> Mapping[int, NsfwPredictionData]:
        """Return predictions indexed by source image position."""
        return self.data().predictions