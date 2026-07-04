from typing import Callable, Generic, TypeVar, get_type_hints

from cscience.features.api.datatypes.datatype_base import DatatypeBase
from cscience.features.api.feature.feature_base import FeatureBase

from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase

Tin = TypeVar('Tin', bound=DatatypeBase, contravariant=True)
Tout = TypeVar('Tout', bound=DatatypeBase, covariant=True)


class Converter(Generic[Tin, Tout]):
    def __init__(self, name: str, source: FeatureBase,
                 fnc: Callable[[Tin], Tout],
                 input_type: type[DatatypeBase],
                 output_type: type[DatatypeBase]) -> None:
        self._name: str = name
        self._source: FeatureBase = source
        self._fnc: Callable[[Tin], Tout] = fnc
        self._input_type: type[DatatypeBase] = input_type
        self._output_type: type[DatatypeBase] = output_type

    def __call__(self, data: Tin) -> Tout:
        return self._fnc(data)

    def get_identifier(self) -> tuple[FeatureBase, type[DatatypeBase], type[DatatypeBase]]:
        return self._source, self._input_type, self._output_type
