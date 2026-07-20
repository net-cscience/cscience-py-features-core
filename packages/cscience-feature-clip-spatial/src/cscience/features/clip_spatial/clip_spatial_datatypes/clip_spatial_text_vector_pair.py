import icontract

from cscience.features.api import TextBatch

from .clip_spatial_datatype import ClipSpatialDatatype
from .clip_spatial_tensor_batch import ClipSpatialTensorBatch
from .clip_spatial_text_vector_pair_data import (
    ClipSpatialTextVectorPairData,
)


class ClipSpatialTextVectorPair(
    ClipSpatialDatatype[ClipSpatialTextVectorPairData],
):
    """Pair of text queries and spatial CLIP embeddings."""

    @icontract.require(
        lambda data:
            isinstance(data, ClipSpatialTextVectorPairData)
            and isinstance(data.texts, TextBatch)
            and isinstance(data.vectors, ClipSpatialTensorBatch),
        "Data must contain a TextBatch and a ClipSpatialTensorBatch.",
    )
    def __init__(
        self,
        data: ClipSpatialTextVectorPairData,
    ) -> None:
        super().__init__(data)

    @property
    def texts(self) -> TextBatch:
        return self.data().texts

    @property
    def vectors(self) -> ClipSpatialTensorBatch:
        return self.data().vectors