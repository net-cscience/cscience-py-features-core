from typing import TYPE_CHECKING

import torch

from cscience.features.clip_spatial.clip_spatial_feature.Filter.FilterProvider import FilterProvider

if TYPE_CHECKING:
    from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator as MaskingGenerator

class MeanFilterProvider(FilterProvider):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.variance = kwargs.get("variance", 0.5)

    def filter_fnc(self, generator: "MaskingGenerator") -> torch.Tensor:
        window :torch.Tensor = generator.geometry_fnc(generator.base_img_tensor[0])
        return window + (self.variance**0.5) * torch.randn(window.size()).to(generator.device)
