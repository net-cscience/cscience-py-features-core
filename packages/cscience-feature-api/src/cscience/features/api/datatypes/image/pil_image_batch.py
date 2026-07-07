from collections.abc import Mapping

from PIL.Image import Image

from cscience.features.api.datatypes.base.batch_base import BatchBase
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class PilImageBatch(CoreDatatype[dict[int, Image]], BatchBase[Image]):
    """Batch of Pillow images indexed by source position."""

    def __init__(self, data: Mapping[int, Image]) -> None:
        self._validate_batch_mapping(data)

        for key, value in data.items():
            if not isinstance(value, Image):
                raise TypeError(
                    f"PilImageBatch expects PIL images, got {type(value).__name__} "
                    f"at key {key}."
                )

        super().__init__(dict(data))