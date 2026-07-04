

from abc import ABC, abstractmethod

from .converter import Converter
from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase


class SearchStrategyBase(ABC):

    def __init__(self, feature: FeatureBase, input_type: type[DatatypeBase], output_type: type[DatatypeBase]) -> None:
        self.feature = feature
        self.input_type = input_type
        self.output_type = output_type
        pass

    @abstractmethod
    def search(self, recordset: dict[tuple[FeatureBase,type[DatatypeBase],type[DatatypeBase]], Converter]) -> Converter:
        pass
