from abc import ABC, abstractmethod

import torch

from cscience.features.api import SpatialRegion


class GeometryProvider(ABC):
    """Maps spatial regions to tensor windows."""

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
        """Create region metadata for one grid position."""
        raise NotImplementedError

    def select(
        self,
        tensor: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        """Return the tensor view covered by the region.

        Expects:
            tensor shape [C, H, W]
        """
        return tensor[:, region.y0:region.y1, region.x0:region.x1]