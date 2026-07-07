from torch import Tensor

from ..clip_spatial_datatype import ClipDatatype


class ClipSpatialTensorBatch(ClipDatatype):
    """Batch of CLIP embedding tensors with shape [n, d]."""
    def __init__(self, data: Tensor) -> None:
        super().__init__(data)

