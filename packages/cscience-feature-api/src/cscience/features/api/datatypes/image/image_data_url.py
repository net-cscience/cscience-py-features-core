from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class ImageDataUrl(CoreDatatype[str]):
    """Base64-encoded image data URL."""

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(f"ImageDataUrl expects str, got {type(data).__name__}.")

        if not data:
            raise ValueError("ImageDataUrl cannot be empty.")

        super().__init__(data)