from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class IntValue(CoreDatatype[int]):
    """Single integer value."""

    def __init__(self, data: int) -> None:
        if type(data) is not int:
            raise TypeError(f"IntValue expects int, got {type(data).__name__}.")
        super().__init__(data)