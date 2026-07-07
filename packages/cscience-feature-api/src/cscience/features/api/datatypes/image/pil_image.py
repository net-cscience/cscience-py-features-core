from PIL.Image import Image

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class PilImage(CoreDatatype[Image]):
    """Decoded Pillow image."""

    def __init__(self, data: Image) -> None:
        if not isinstance(data, Image):
            raise TypeError(f"PilImage expects PIL image, got {type(data).__name__}.")

        super().__init__(data)