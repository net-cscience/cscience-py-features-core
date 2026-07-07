from abc import ABC, abstractmethod, abstractproperty
from typing import Any, TypeVar, Generic

T = TypeVar('T')

class DatatypeBase(ABC, Generic[T]):
    """Base class for all semantic feature datatypes.

    Datatypes wrap raw Python values and attach semantic meaning to them.
    Conversion and connector logic should operate on datatype classes instead
    of raw Python types whenever data crosses a feature boundary.
    """

    def __init__(self, data: T) -> None:
        """Create a datatype wrapper around raw data."""
        self._data = data

    def data(self) -> T:
        """Return the wrapped raw value."""
        return self._data

    @staticmethod
    def fullname(o: object) -> str:
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__
        return module + '.' + o.__class__.__name__
