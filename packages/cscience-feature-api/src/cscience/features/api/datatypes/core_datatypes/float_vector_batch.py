from ..core_datatype import CoreDatatype

class FloatVectorBatch(CoreDatatype):

    def __init__(self, data:list[list[float]]) -> None:
        self._data: list[list[float]] | None = data
        pass
