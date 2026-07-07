from PIL.Image import Image

from cscience.features.api.datatypes.core_datatype import CoreDatatype


class PilImageBatch(CoreDatatype[list[Image]]):
    """Batch of decoded Pillow images."""

    def __init__(self, data: list[Image]) -> None:
        if not data:
            raise ValueError("PilImageBatch cannot be empty.")

        super().__init__(data)