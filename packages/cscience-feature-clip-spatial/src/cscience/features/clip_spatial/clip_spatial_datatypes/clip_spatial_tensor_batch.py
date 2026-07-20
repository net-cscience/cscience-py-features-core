from itertools import chain

import torch
from torch import Tensor

from cscience.features.api import (
    EmbeddingBase,
    SpatialVectorBatchBase,
    SpatialVectorBatchData,
)

from .clip_spatial_datatype import ClipSpatialDatatype


class ClipSpatialTensorBatch(
    SpatialVectorBatchBase[Tensor],
    EmbeddingBase,
    ClipSpatialDatatype[SpatialVectorBatchData[Tensor]],
):
    """Spatial CLIP embeddings with one base embedding per item."""

    def __init__(
        self,
        data: SpatialVectorBatchData[Tensor],
    ) -> None:
        if not isinstance(data, SpatialVectorBatchData):
            raise TypeError(
                "ClipSpatialTensorBatch expects SpatialVectorBatchData, "
                f"got {type(data).__name__}."
            )

        vectors = chain(
            data.vectors.items(),
            data.base_vectors.items(),
        )

        for key, vector in vectors:
            if not isinstance(vector, Tensor):
                raise TypeError(
                    "ClipSpatialTensorBatch expects Tensor values, "
                    f"got {type(vector).__name__} at key {key}."
                )

            if vector.ndim != 1:
                raise ValueError(
                    "ClipSpatialTensorBatch expects 1D tensor vectors, "
                    f"got shape {tuple(vector.shape)} at key {key}."
                )

            if not vector.is_floating_point():
                raise TypeError(
                    "ClipSpatialTensorBatch expects floating-point "
                    f"tensor vectors, got {vector.dtype} at key {key}."
                )

        super().__init__(data)

    def as_flat_tensor(self) -> Tensor:
        """Return spatial embeddings with shape [N * R, D]."""
        return torch.stack(self.ordered_values())

    def as_structured_tensor(self) -> Tensor:
        """Return spatial embeddings with shape [N, R, D]."""
        flat = self.as_flat_tensor()

        return flat.reshape(
            self.layout.item_count,
            self.layout.regions_per_item,
            flat.shape[-1],
        )

    def as_base_tensor(self) -> Tensor:
        """Return base-image embeddings with shape [N, D]."""
        return torch.stack([
            self.data().base_vectors[item_key]
            for item_key in self.item_keys
        ])