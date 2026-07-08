from abc import ABC, abstractmethod

import torch

from cscience.features.api import SpatialRegion


class FilterProvider(ABC):
    """Produces replacement values for masked regions."""

    @abstractmethod
    def create_fill(
        self,
        *,
        base_tensor: torch.Tensor,
        region: SpatialRegion,
        window: torch.Tensor,
    ) -> torch.Tensor | float:
        """Create replacement content for a region.

        base_tensor:
            Full source tensor [C, H, W]

        window:
            Selected region view [C, h, w]
        """
        raise NotImplementedError