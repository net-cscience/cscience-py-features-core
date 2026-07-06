from abc import ABC, abstractmethod, abstractproperty
from typing import Any, TypeVar, Generic

T = TypeVar('T')

class DatatypeBase(ABC, Generic[T]):

    def __init__(self, data: T) -> None:
        self._data = data

    def data(self) -> T:
        return self._data

    @staticmethod
    def fullname(o: object) -> str:
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__
        return module + '.' + o.__class__.__name__
