from typing import List

from ..conversion.converter import Converter
from ..feature.feature_base import FeatureBase
from ..registry.conversion_registry import ConversionRegistry


class CoreConversions(ConversionRegistry):

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        pass