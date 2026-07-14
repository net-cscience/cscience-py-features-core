from torch import Tensor

from cscience.features.api.datatypes.base.vector_batch_base import VectorBatchBase
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_datatype import ClipSpatialDatatype
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import \
    ClipSpatialTextTensorBatchData


class ClipSpatialTextTensorBatch(ClipSpatialDatatype,VectorBatchBase[Tensor]):
    """Batch of CLIP embedding tensors with stable source keys."""

    def __init__(self, data: ClipSpatialTextTensorBatchData) -> None:
        if not data.keys:
            raise ValueError("ClipTensorBatch cannot be empty.")

        if data.vectors.ndim != 2:
            raise ValueError(
                f"ClipTensorBatch expects a 2D tensor, got shape {tuple(data.vectors.shape)}."
            )

        if len(data.keys) != data.vectors.shape[0]:
            raise ValueError(
                f"Number of keys must match tensor rows: "
                f"{len(data.keys)} keys for {data.vectors.shape[0]} rows."
            )

        for key in data.keys:
            if type(key) is not int:
                raise TypeError(
                    f"ClipTensorBatch keys must be int, got {type(key).__name__}."
                )

        if len(set(data.keys)) != len(data.keys):
            raise ValueError("ClipTensorBatch keys must be unique.")

        super().__init__(data)