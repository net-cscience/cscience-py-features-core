import torch
from PIL.ImageFile import ImageFile

from ..clip_spatial_datatype import ClipDatatype


class ClipSpatialImageBatch(ClipDatatype):

    def __init__(self, data: torch.Tensor) -> None:
        # check that data is a torch.Tensor could represent an image.
        if not (data.dim() == 4 and data.size(1) == 3):
            raise ValueError("Data must be a 4D tensor with shape (M, N, 3, H, W)")
        super().__init__(data)
