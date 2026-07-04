from ..core_datatype import CoreDatatype


class FloatVector(CoreDatatype):

    def __init__(self, data:list[float]) -> None:
        self._data: list[float] = data

    def data(self) -> list[float]:
        return self._data
