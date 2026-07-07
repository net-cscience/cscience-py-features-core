from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class Text(CoreDatatype[str]):
    """Single text string."""

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(f"Text expects str, got {type(data).__name__}.")

        super().__init__(data)