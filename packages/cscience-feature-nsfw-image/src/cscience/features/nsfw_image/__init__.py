from cscience.features.api.registry.registry_base import RegistryBase

from .nsfw_image_connector import NsfwImageConnector
from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_feature import NsfwImageFeature

__all__ = [
    "NsfwImageConnector",
    "NsfwImageConversionProvider",
    "NsfwImageFeature",
]


def register(registry: RegistryBase) -> None:
    registry.register("nsfw_image", NsfwImageConversionProvider)
