from torch import Tensor

from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)

from .clip_datatype import ClipDatatype


class ClipTensor(
    VectorBase,
    EmbeddingBase,
    ClipDatatype[Tensor],
):
    """Single CLIP embedding tensor with shape [D]."""

    def __init__(self, data: Tensor) -> None:
        if not isinstance(data, Tensor):
            raise TypeError(
                f"ClipTensor expects Tensor, "
                f"got {type(data).__name__}."
            )

        if data.ndim != 1:
            raise ValueError(
                "ClipTensor expects a 1D tensor, "
                f"got shape {tuple(data.shape)}."
            )

        if data.numel() == 0:
            raise ValueError(
                "ClipTensor cannot be empty."
            )

        if not data.is_floating_point():
            raise TypeError(
                "ClipTensor expects a floating-point tensor, "
                f"got {data.dtype}."
            )

        super().__init__(data)