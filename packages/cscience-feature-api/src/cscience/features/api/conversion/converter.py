from typing import Callable, Generic, TypeVar, get_type_hints
from feature.feature_base import FeatureBase

Tin = TypeVar('Tin')
Tout = TypeVar('Tout')


class Converter(Generic[Tin, Tout]):
    def __init__(self, name: str, source: FeatureBase, fnc: Callable[[Tin], Tout], input_type:type, output_type: type) -> None:
        self._name: str = name
        self._source: FeatureBase = source
        self._fnc: Callable[[Tin], Tout] = fnc
        self._input_type =input_type
        self._output_type = output_type

    def __call__(self, data: Tin) -> Tout:
        return self._fnc(data)

    def get_identifier(self) -> tuple[FeatureBase, Tin, Tout]:
        return self._source, self._input_type, self._output_type
