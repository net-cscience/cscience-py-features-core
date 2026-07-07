## API
from cscience.features.api.registry.registry_base import RegistryBase

## Internal
from .clip_spatial_datatype import ClipDatatype
from .clip_spatial_connector import ClipConnector
from .clip_spatial_feature import ClipSpatialFeature
from .clip_spatial_conversion_provider import ClipConversionProvider


__all__ = [
    "ClipDatatype",
    "ClipConnector",
    "ClipConversionProvider",
    "ClipSpatialFeature",
]

def register(registry: RegistryBase) -> None:
        registry.register("clip", ClipConversionProvider)