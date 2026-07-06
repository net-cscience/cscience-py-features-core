

from abc import ABC, abstractmethod

from .conversion_key import ConversionKey
from .converter import Converter
from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase


class SearchStrategyBase(ABC):

    def __init__(self, conversion_key: ConversionKey) -> None:
        self._conversion_key = conversion_key
        pass

    @abstractmethod
    def search(self, recordset: dict[ConversionKey, Converter]) -> Converter:
        pass


    def __str__(self) -> str:
        return str(self._conversion_key)
