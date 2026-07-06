from abc import ABC, abstractmethod
from typing import List

from .converter import Converter
from ..feature.feature_base import FeatureBase


class ConversionProviderBase(ABC):
    """Base class for groups of converters belonging to one feature."""

    def __init__(self, feature: FeatureBase) -> None:
        self._feature = feature

    @abstractmethod
    def register_converters(self) -> List[Converter]:
        """Return all converters provided by this feature or provider."""
        raise NotImplementedError("Subclasses must implement register_converters()")
