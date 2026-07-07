## API
from cscience.features.api.registry.registry_base import RegistryBase

## Internal
from .clip_datatypes.clip_image import ClipImage
from .clip_datatypes.clip_image_batch import ClipImageBatch
from .clip_datatypes.clip_tensor import ClipTensor
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch
from .clip_datatype import ClipDatatype
from .clip_connector import ClipConnector
from .clip_feature import ClipFeature
from .clip_conversion_provider import ClipConversionProvider


__all__ = [
    "ClipImage",
    "ClipImageBatch",
    "ClipTensor",
    "ClipTensorBatch",
    "ClipDatatype",
    "ClipConnector",
    "ClipConversionProvider",
    "ClipFeature",
]

def register(registry: RegistryBase) -> None:
        registry.register("clip", ClipConversionProvider)