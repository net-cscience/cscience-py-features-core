from abc import ABC
from typing import Any, Generic, TypeVar

from cscience.features.api.datatypes.datatype_base import DatatypeBase

T = TypeVar("T")



class VectorBase(DatatypeBase[T], ABC, Generic[T]):
    """Base class for vector-like datatypes.

    Provides optional length validation and exposes the length of the wrapped
    vector container.
    """
    def __init__(self, data:T, assert_length: int|None=None):
        if assert_length is None:
            super().__init__(data)
        else:
            if len(data) != assert_length:
                raise ValueError("Data length does not match the expected length")
            super().__init__(data)

    def length(self) -> int:
        """Return the length of the wrapped vector container."""
        return len(self.data())