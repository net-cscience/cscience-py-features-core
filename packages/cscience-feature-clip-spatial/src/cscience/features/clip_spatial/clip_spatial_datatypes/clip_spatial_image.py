import torch

from ..clip_spatial_datatype import ClipDatatype


class ClipSpatialImage(ClipDatatype):

    def __init__(self, data: torch.Tensor) -> None:
        # check that data is a torch.Tensor could represent an image.
        if not (data.dim() == 4 and data.size(1) == 3):
            raise ValueError("Data must be a 4D tensor with shape (N, 3, H, W)")
        super().__init__(data)
