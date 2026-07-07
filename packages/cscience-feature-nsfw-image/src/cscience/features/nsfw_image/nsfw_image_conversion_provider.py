from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.feature.feature_base import FeatureBase


class NsfwImageConversionProvider(ConversionProviderBase):
    """Registers conversions required by the nsfw_image feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return []
