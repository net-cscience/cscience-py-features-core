from collections.abc import Mapping

from torch import Tensor

from cscience.features.api import (
    EmbeddingBase,
    VectorBatchBase,
)

from .clip_spatial_datatype import ClipSpatialDatatype
from .clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)


class ClipSpatialTextTensorBatch(
    VectorBatchBase[Tensor],
    EmbeddingBase,
    ClipSpatialDatatype[
        ClipSpatialTextTensorBatchData
    ],
):
    """Packed CLIP text embedding batch with stable source keys."""

    def __init__(
        self,
        data: ClipSpatialTextTensorBatchData,
    ) -> None:
        if not isinstance(
            data,
            ClipSpatialTextTensorBatchData,
        ):
            raise TypeError(
                "ClipSpatialTextTensorBatch expects "
                f"ClipSpatialTextTensorBatchData, "
                f"got {type(data).__name__}."
            )

        vectors = data.vectors
        keys = data.keys

        if not isinstance(vectors, Tensor):
            raise TypeError(
                "ClipSpatialTextTensorBatch vectors expect Tensor, "
                f"got {type(vectors).__name__}."
            )

        if vectors.ndim != 2:
            raise ValueError(
                "ClipSpatialTextTensorBatch expects a 2D tensor, "
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
                    "ClipSpatialTextTensorBatch keys must be int, "
                    f"got {type(key).__name__}."
                )

        if len(set(keys)) != len(keys):
            raise ValueError(
                "ClipSpatialTextTensorBatch keys must be unique."
            )

        if not vectors.is_floating_point():
            raise TypeError(
                "ClipSpatialTextTensorBatch expects a "
                f"floating-point tensor, got {vectors.dtype}."
            )

        normalized = ClipSpatialTextTensorBatchData(
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
        """Return text embeddings indexed by TextBatch key."""
        return self._vectors_by_key

    @property
    def keys(self) -> tuple[int, ...]:
        """Return keys in packed tensor row order."""
        return self.data().keys

    @property
    def vectors(self) -> Tensor:
        """Return the packed tensor with shape [N, D]."""
        return self.data().vectors