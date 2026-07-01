from typing import TypeVar, Generic, Callable

Tin = TypeVar('Tin')
Tout = TypeVar('Tout')


class FeatureConnector(Generic[Tin, Tout]):

    def __init__(self) -> None:
        # Try load converters, first specific then generic
        self.fnc: Callable[[Tin], Tout]
        pass


    def convert(self, data: Tin) -> Tout:
        return self.fnc(data)