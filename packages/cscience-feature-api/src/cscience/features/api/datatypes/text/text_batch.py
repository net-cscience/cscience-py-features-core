from cscience.features.api.datatypes.core_datatype import CoreDatatype

class TextBatch(CoreDatatype):


    def __init__(self, data: list[str]) -> None:
        super().__init__(data)