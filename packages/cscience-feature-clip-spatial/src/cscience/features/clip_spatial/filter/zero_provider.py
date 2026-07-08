import torch

from cscience.features.api import SpatialRegion

from .filter_provider import FilterProvider


class ZeroProvider(FilterProvider):
    """Fill selected regions with zero."""

    def create_fill(
        self,
        *,
        base_tensor: torch.Tensor,
        region: SpatialRegion,
        window: torch.Tensor,
    ) -> float:
        return 0.0