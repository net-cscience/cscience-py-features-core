from cscience.features.api.datatypes.core_datatype import CoreDatatype


class ImageDataUrl(CoreDatatype[str]):
    """Base64-encoded image data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)