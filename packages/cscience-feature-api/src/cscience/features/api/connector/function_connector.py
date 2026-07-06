from typing import TypeVar, Generic, Callable

from ..conversion.conversion_key import ConversionKey
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..conversion.search_strategy_most_specific import SearchStrategyMostSpecific
from ..datatypes.datatype_base import DatatypeBase

from ..feature.feature_base import FeatureBase
from ..registry.conversion_registry import ConversionRegistry

Tin = TypeVar('Tin', bound=DatatypeBase)
Tfi = TypeVar('Tfi', bound=DatatypeBase)
Tfo = TypeVar('Tfo', bound=DatatypeBase)
Tout = TypeVar('Tout', bound=DatatypeBase)


class FunctionConnector(Generic[Tin, Tfi, Tfo, Tout]):

    def __init__(self, feature: FeatureBase, function: Callable[[Tfi], Tfo],
                 input_type: type[DatatypeBase],
                 input_feature_type: type[DatatypeBase],
                 output_feature_type: type[DatatypeBase],
                 output_type: type[DatatypeBase],
                 ) -> None:
        strategy_in: SearchStrategyBase = SearchStrategyMostSpecific(ConversionKey(type(feature), input_type, input_feature_type))
        strategy_out: SearchStrategyBase = SearchStrategyMostSpecific(ConversionKey(type(feature), output_feature_type, output_type))
        self.inner: Converter[Tin, Tfi] = ConversionRegistry.get_best_effort_converter(strategy_in)
        self.outer: Converter[Tfo, Tout] = ConversionRegistry.get_best_effort_converter(strategy_out)
        self.function = function
        self.wrapped = lambda x: self.outer(function(self.inner(x)))

    def __call__(self, x: Tin) -> Tout:
        return self.wrapped(x)
