import torch

from cscience.features.api import SpatialRegion

from .filter_provider import FilterProvider


class MeanNoiseProvider(FilterProvider):
    """Fill selected regions with noisy local content."""

    def __init__(self, variance: float = 0.5) -> None:
        self.variance = variance

    def create_fill(
        self,
        *,
        base_tensor: torch.Tensor,
        region: SpatialRegion,
        window: torch.Tensor,
    ) -> torch.Tensor:
        noise = (self.variance ** 0.5) * torch.randn_like(window)
        return window + noise