from .converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase


class SearchStrategyMostSpecific(SearchStrategyBase):

    def __init__(self, feature: FeatureBase, input_type: type[DatatypeBase], output_type: type[DatatypeBase]):
        super().__init__(feature, input_type, output_type)

    def search(self,
               recordset: dict[tuple[FeatureBase, type[DatatypeBase], type[DatatypeBase]], Converter]) -> Converter:

        candidate: Converter

        for (f, i, o), converter in recordset.items():
            if type(f) == type(self.feature) and i == self.input_type and o == self.output_type:
                return converter
            if issubclass(type(f), FeatureBase) and i == self.input_type and o == self.output_type:
                return converter

        raise ValueError(
            f"No converter found for feature {self.feature} with input type {self.input_type} and output type {self.output_type}")
