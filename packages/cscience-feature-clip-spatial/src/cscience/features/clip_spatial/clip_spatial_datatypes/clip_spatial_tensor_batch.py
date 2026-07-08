from torch import Tensor
import torch

from cscience.features.api import SpatialVectorBatchBase, SpatialVectorBatchData


class ClipSpatialTensorBatch(SpatialVectorBatchBase[Tensor]):
    """Spatially structured CLIP tensor batch.

    Physical structure:
        dict[flat_index, Tensor[V]]

    Logical structure:
        [item_count, regions_per_item, V]
    """

    namespace = "clip_spatial"

    def __init__(self, data: SpatialVectorBatchData[Tensor]) -> None:
        super().__init__(data)

        for key, vector in self.data().vectors.items():
            if not isinstance(vector, Tensor):
                raise TypeError(
                    f"ClipSpatialTensorBatch expects Tensor values, "
                    f"got {type(vector).__name__} at key {key}."
                )

            if vector.ndim != 1:
                raise ValueError(
                    f"ClipSpatialTensorBatch expects 1D tensor vectors, "
                    f"got shape {tuple(vector.shape)} at key {key}."
                )

    def as_flat_tensor(self) -> Tensor:
        """Return vectors as tensor with shape [N * R, V]."""
        return torch.stack(
            [
                self.data().vectors[key]
                for key in self.ordered_keys()
            ]
        )

    def as_structured_tensor(self) -> Tensor:
        """Return vectors as tensor with shape [N, R, V]."""
        flat = self.as_flat_tensor()

        return flat.reshape(
            self.layout.item_count,
            self.layout.regions_per_item,
            flat.shape[-1],
        )