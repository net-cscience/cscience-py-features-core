from typing import TYPE_CHECKING

from cscience.features.clip_spatial.clip_spatial_feature.Filter.FilterProvider import FilterProvider

if TYPE_CHECKING:
    from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator as MaskingGenerator

class ZeroProvider(FilterProvider):


    def __init__(self, **kwargs):
        pass


    def filter_fnc(self, generator: "MaskingGenerator") -> float:
        return 0.0

