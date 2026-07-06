from typing import Any

from ..core_datatype import CoreDatatype

class TextBatch(CoreDatatype):


    def __init__(self, data: list[str]) -> None:
        super().__init__(data)