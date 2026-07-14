from abc import ABC
from typing import Generic, TypeVar
import icontract

T = TypeVar("T")



@icontract.invariant(lambda self: self._data is not None, "Data cannot be None.")
class DatatypeBase(ABC, Generic[T]):
    """Base class for all semantic feature datatypes.

    A datatype wraps a raw Python value and attaches semantic meaning to it.
    Conversion and connector logic should use datatype classes rather than raw
    Python types at feature boundaries.
    """

    def __init__(self, data: T) -> None:
        self._data = data

    def data(self) -> T:
        """Return the wrapped raw value."""
        return self._data

    @staticmethod
    def fullname(o: object) -> str:
        """Return the fully qualified class name of an object."""
        module = o.__class__.__module__

        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__

        return module + "." + o.__class__.__name__