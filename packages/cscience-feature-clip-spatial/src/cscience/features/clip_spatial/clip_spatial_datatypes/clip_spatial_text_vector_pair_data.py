from dataclasses import dataclass

from cscience.features.api import TextBatch

from .clip_spatial_tensor_batch import ClipSpatialTensorBatch


@dataclass(frozen=True, slots=True)
class ClipSpatialTextVectorPairData:
    texts: TextBatch
    vectors: ClipSpatialTensorBatch