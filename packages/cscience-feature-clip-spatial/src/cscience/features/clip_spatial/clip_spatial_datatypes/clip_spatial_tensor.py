from torch import Tensor

from ..clip_spatial_datatype import ClipDatatype


class ClipSpatialTensor(ClipDatatype):
    """Single CLIP embedding tensor with shape [d]."""

    def __init__(self, data:Tensor) -> None:
        super().__init__(data)
