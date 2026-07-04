from typing import Any

from ..core_datatype import CoreDatatype

class TextBatch(CoreDatatype):


    def __init__(self, data: list[str]) -> None:
        self._data: list[str]  = data
        pass

    def data(self) -> list[str]:
        return self._data
