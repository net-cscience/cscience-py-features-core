from cscience.features.api import RegistryBase

from .clip_spatial_connector import ClipSpatialConnector
from .clip_spatial_conversion_provider import ClipSpatialConversionProvider
from .clip_spatial_datatypes.clip_spatial_datatype import ClipSpatialDatatype
from .clip_spatial_feature import ClipSpatialFeature
from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch
from .filter.filter_provider import FilterProvider
from .filter.mean_noise_provider import MeanNoiseProvider
from .filter.zero_provider import ZeroProvider
from .geometry.geometry_provider import GeometryProvider
from .geometry.square_provider import SquareProvider
from .indexer.spatial_index import SpatialIndex
from .indexer.spatial_indexer import SpatialIndexer
from .masking.masking_generator import MaskingGenerator
from .masking.masking_mode import MaskingMode

__all__ = [
    "ClipSpatialConnector",
    "ClipSpatialConversionProvider",
    "ClipSpatialDatatype",
    "ClipSpatialFeature",
    "ClipSpatialTensorBatch",

    "FilterProvider",
    "MeanNoiseProvider",
    "ZeroProvider",
    "GeometryProvider",
    "SquareProvider",
    "SpatialIndex",
    "SpatialIndexer",
    "MaskingGenerator",
    "MaskingMode",
]


def register(registry: RegistryBase) -> None:
    registry.register("clip_spatial", ClipSpatialConversionProvider)