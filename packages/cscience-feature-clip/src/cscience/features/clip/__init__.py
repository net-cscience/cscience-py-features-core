from .connector import ClipConnector
from .feature import ClipFeature

__all__ = [
    "ClipConnector",
    "ClipFeature",
    "register",
]


def register(registry):
    registry.register_feature("clip", ClipFeature)
    registry.register_connector("clip", ClipConnector)