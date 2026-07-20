from abc import ABC, abstractmethod

import numpy as np
import torch

from cscience.features.api import SpatialRegion


class GeometryProvider(ABC):

    @abstractmethod
    def create_region(
        self,
        *,
        index: int,
        row: int,
        column: int,
        center_x: int,
        center_y: int,
        image_width: int,
        image_height: int,
    ) -> SpatialRegion:
        raise NotImplementedError

    @abstractmethod
    def create_mask(
        self,
        *,
        region: SpatialRegion,
        image_width: int,
        image_height: int,
    ) -> np.ndarray:
        """Return a boolean mask for one region."""
        raise NotImplementedError

    def select(
        self,
        tensor: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        return tensor[
            :,
            region.y0:region.y1,
            region.x0:region.x1,
        ]