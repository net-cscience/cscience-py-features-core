from .connector import YoloConnector
from .feature import YoloFeature

__all__ = [
    "YoloConnector",
    "YoloFeature",
    "register",
]


def register(registry):
    registry.register_feature("yolo", YoloFeature)
    registry.register_connector("yolo", YoloConnector)