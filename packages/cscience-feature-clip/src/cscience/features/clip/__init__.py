## API
from cscience.features.api.registry.registry_base import RegistryBase

## Internal
from .clip_datatypes.clip_image import ClipImage
from .clip_datatypes.clip_tensor import ClipTensor
from .clip_datatype import ClipDatatype
from .connector import ClipConnector
from .feature import ClipFeature
from .convertion_provider import ClipConvertionProvider


__all__ = [
    "ClipImage",
    "ClipTensor",
    "ClipDatatype",
    "ClipConnector",
    "ClipConvertionProvider",
    "ClipFeature",
]

def register(registry: RegistryBase) -> None:
        registry.register("clip", ClipConvertionProvider)