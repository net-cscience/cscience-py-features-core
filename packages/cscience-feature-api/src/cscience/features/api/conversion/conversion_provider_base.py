from abc import ABC, abstractmethod
from typing import List

from .converter import Converter
from ..feature.feature_base import FeatureBase


class ConversionProviderBase(ABC):

    def __init__(self, feature: FeatureBase) -> None:
        self._feature = feature

    @abstractmethod
    def register_converters(self) -> List[Converter]:
        pass
