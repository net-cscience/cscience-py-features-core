from PIL.Image import Image

from cscience.features.api.datatypes.core_datatype import CoreDatatype


class PilImage(CoreDatatype[Image]):
    """Decoded Pillow image."""

    def __init__(self, data: Image) -> None:
        super().__init__(data)