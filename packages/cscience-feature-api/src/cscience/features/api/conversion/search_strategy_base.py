from conversion.converter import Converter
from feature.feature_base import FeatureBase

from abc import ABC, abstractmethod
class SearchStrategyBase(ABC):

    def __init__(self, feature: FeatureBase, input_type: type, output_type: type) -> None:
        self.feature = feature
        self.input_type = input_type
        self.output_type = output_type
        pass

    @abstractmethod
    def search(self, recordset: dict[tuple[FeatureBase,type,type], Converter]) -> Converter:
        pass
