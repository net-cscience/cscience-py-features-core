from ..core_datatype import CoreDatatype

class Text(CoreDatatype):

    def __init__(self, data:str) -> None:
        self._data: str  = data
        pass

    def data(self) -> str :
        return self._data