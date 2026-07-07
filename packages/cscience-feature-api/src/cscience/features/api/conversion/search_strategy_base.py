

from abc import ABC, abstractmethod

from .conversion_key import ConversionKey
from .converter import Converter


class SearchStrategyBase(ABC):
    """Base class for converter lookup strategies."""
    def __init__(self, conversion_key: ConversionKey) -> None:
        self._conversion_key = conversion_key


    @abstractmethod
    def search(self, recordset: dict[ConversionKey, Converter]) -> Converter:
        """Find a converter in the given registry recordset."""
        raise NotImplementedError("Subclasses must implement search")


    def __str__(self) -> str:
        return str(self._conversion_key)
