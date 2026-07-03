from functools import cached_property
from typing import TypeVar, Generic, Callable

from conversion.converter import Converter
from registry.conversion_registry import ConversionRegistry
from conversion.search_strategy_base import SearchStrategyBase
from conversion.search_strategy_most_specific import SearchStrategyMostSpecific
from feature.feature_base import FeatureBase

Tin = TypeVar('Tin')
Tfi = TypeVar('Tfi')
Tfo = TypeVar('Tfo')
Tout = TypeVar('Tout')


class FunctionConnector(Generic[Tin, Tfi, Tfo, Tout]):

    def __init__(self, feature: FeatureBase, feature_fnc: Callable[[Tfi], Tfo], input_type: type,
                 feature_input_type: type, feature_output_type: type,
                 output_type: type) -> None:
        # Try load converters, first specific then generic

        strategy_in: SearchStrategyBase = SearchStrategyMostSpecific(feature, input_type, feature_input_type)
        strategy_out: SearchStrategyBase = SearchStrategyMostSpecific(feature, feature_output_type, output_type)
        self.inner: Converter[Tin, Tfi] = ConversionRegistry.get_best_effort_converter(strategy_in)
        self.outer: Converter[Tfo, Tout] = ConversionRegistry.get_best_effort_converter(strategy_out)
        self.feature_fnc = feature_fnc
        self.wrapped = lambda x: self.outer(feature_fnc(self.inner(x)))


    def __call__(self, x: Tin) -> Tfo:
        return self.wrapped(x)


