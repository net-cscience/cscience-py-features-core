from cscience.features.api.datatypes.core_datatype import CoreDatatype

class Text(CoreDatatype[str]):

    def __init__(self, data:str) -> None:
        super().__init__(data)