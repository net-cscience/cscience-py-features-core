from abc import ABC, abstractmethod, abstractproperty
from typing import Any


class DatatypeBase(ABC):


    @abstractmethod
    def __init__(self, data: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def data(self) -> Any:
        raise NotImplementedError

    @staticmethod
    def fullname(o: object) -> str:
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__
        return module + '.' + o.__class__.__name__
