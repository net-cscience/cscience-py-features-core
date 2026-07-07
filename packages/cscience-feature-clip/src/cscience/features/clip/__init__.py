from cscience.features.api.registry.registry_base import RegistryBase

from .clip_connector import ClipConnector
from .clip_conversion_provider import ClipConversionProvider
from .clip_datatypes.clip_datatype import ClipDatatype
from .clip_datatypes.clip_tensor import ClipTensor
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch, ClipTensorBatchData
from .clip_feature import ClipFeature

__all__ = [
    "ClipConnector",
    "ClipConversionProvider",
    "ClipDatatype",
    "ClipFeature",
    "ClipTensor",
    "ClipTensorBatch",
    "ClipTensorBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("clip", ClipConversionProvider)