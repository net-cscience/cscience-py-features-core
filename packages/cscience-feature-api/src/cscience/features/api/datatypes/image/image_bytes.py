from cscience.features.api.datatypes.core_datatype import CoreDatatype


class ImageBytes(CoreDatatype[bytes]):
    """Encoded image bytes."""

    def __init__(self, data: bytes) -> None:
        super().__init__(data)