from torch import Tensor

from cscience.features.clip import ClipDatatype


class ClipTensor(ClipDatatype):
    """Single CLIP embedding tensor with shape [d]."""

    def __init__(self, data: Tensor) -> None:
        if data.ndim != 1:
            raise ValueError(f"ClipTensor expects a 1D tensor, got shape {tuple(data.shape)}.")

        super().__init__(data)