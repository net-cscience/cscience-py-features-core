from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class FloatValue(CoreDatatype[float]):
    """Single floating-point value."""

    def __init__(self, data: float) -> None:
        if type(data) is not float:
            raise TypeError(f"FloatValue expects float, got {type(data).__name__}.")

        super().__init__(data)