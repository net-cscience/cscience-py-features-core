from typing import Callable, Generic, TypeVar

from .conversion_key import ConversionKey
from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase

Tin = TypeVar('Tin', bound=DatatypeBase, contravariant=True)
Tout = TypeVar('Tout', bound=DatatypeBase, covariant=True)


class Converter(Generic[Tin, Tout]):
    def __init__(self, name: str, source: FeatureBase,
                 function: Callable[[Tin], Tout],
                 input_type: type[DatatypeBase],
                 output_type: type[DatatypeBase]) -> None:
        self._name: str = name
        self._source: FeatureBase = source
        self._function: Callable[[Tin], Tout] = function
        self._input_type: type[DatatypeBase] = input_type
        self._output_type: type[DatatypeBase] = output_type

    def __call__(self, data: Tin) -> Tout:
        return self._function(data)

    def get_identifier(self) -> ConversionKey:
        return ConversionKey(type(self._source), self._input_type, self._output_type)
