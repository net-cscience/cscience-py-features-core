from registry.registry_base import RegistryBase

# Internal
from .connector import ClipConnector
from .convertion_provider import ClipConvertionProvider
from .feature import ClipFeature


__all__ = [
    "ClipConnector",
    "ClipConvertionProvider",
    "ClipFeature",
]


def register(registry: RegistryBase) -> None:
        registry.register("clip", ClipConvertionProvider)