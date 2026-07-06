from torch import Tensor

from ..clip_datatype import ClipDatatype


class ClipTensor(ClipDatatype):
    """Single CLIP embedding tensor with shape [d]."""

    def __init__(self, data:Tensor) -> None:
        super().__init__(data)
