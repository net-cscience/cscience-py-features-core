from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class BoolValue(CoreDatatype[bool]):
    """Single boolean value."""

    def __init__(self, data: bool) -> None:
        if type(data) is not bool:
            raise TypeError(f"BoolValue expects bool, got {type(data).__name__}.")
        super().__init__(data)