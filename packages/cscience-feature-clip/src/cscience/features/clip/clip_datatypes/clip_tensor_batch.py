from collections.abc import Mapping

from torch import Tensor

from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)

from .clip_datatype import ClipDatatype
from .clip_tensor_batch_data import ClipTensorBatchData


class ClipTensorBatch(
    VectorBatchBase[Tensor],
    EmbeddingBase,
    ClipDatatype[ClipTensorBatchData],
):
    """Packed batch of CLIP embedding tensors with stable source keys."""

    def __init__(
        self,
        data: ClipTensorBatchData,
    ) -> None:
        if not isinstance(data, ClipTensorBatchData):
            raise TypeError(
                f"ClipTensorBatch expects ClipTensorBatchData, "
                f"got {type(data).__name__}."
            )

        vectors = data.vectors
        keys = data.keys

        if not isinstance(vectors, Tensor):
            raise TypeError(
                f"ClipTensorBatch vectors expect Tensor, "
                f"got {type(vectors).__name__}."
            )

        if vectors.ndim != 2:
            raise ValueError(
                "ClipTensorBatch expects a 2D tensor, "
                f"got shape {tuple(vectors.shape)}."
            )

        if len(keys) != vectors.shape[0]:
            raise ValueError(
                "Number of keys must match tensor rows: "
                f"{len(keys)} keys for {vectors.shape[0]} rows."
            )

        for key in keys:
            if type(key) is not int:
                raise TypeError(
                    "ClipTensorBatch keys must be int, "
                    f"got {type(key).__name__}."
                )

        if len(set(keys)) != len(keys):
            raise ValueError(
                "ClipTensorBatch keys must be unique."
            )

        if not vectors.is_floating_point():
            raise TypeError(
                "ClipTensorBatch expects a floating-point tensor, "
                f"got {vectors.dtype}."
            )

        normalized = ClipTensorBatchData(
            keys=tuple(keys),
            vectors=vectors,
        )

        self._vectors_by_key = dict(
            zip(
                normalized.keys,
                normalized.vectors.unbind(dim=0),
                strict=True,
            )
        )

        self._validate_vector_batch_mapping(
            self._vectors_by_key
        )

        super().__init__(normalized)

    def _batch_mapping(self) -> Mapping[int, Tensor]:
        """Return embedding rows indexed by source key."""
        return self._vectors_by_key

    @property
    def keys(self) -> tuple[int, ...]:
        """Return source keys in packed tensor row order."""
        return self.data().keys

    @property
    def vectors(self) -> Tensor:
        """Return the packed embedding tensor with shape [N, D]."""
        return self.data().vectors