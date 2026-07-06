from torch import Tensor

from ..clip_datatype import ClipDatatype


class ClipTensorBatch(ClipDatatype):
    """Batch of CLIP embedding tensors with shape [n, d]."""
    def __init__(self, data: Tensor) -> None:
        super().__init__(data)

