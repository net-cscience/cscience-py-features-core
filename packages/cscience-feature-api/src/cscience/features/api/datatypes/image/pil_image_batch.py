from collections.abc import Mapping

from PIL.Image import Image

from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class PilImageBatch(
    BatchBase[Image],
    CoreDatatype[dict[int, Image]],
):
    """Batch of Pillow images indexed by source position."""

    def __init__(self, data: Mapping[int, Image]) -> None:
        self._validate_batch_mapping(data)

        for key, value in data.items():
            if not isinstance(value, Image):
                raise TypeError(
                    f"PilImageBatch expects PIL images, "
                    f"got {type(value).__name__} at key {key}."
                )

        super().__init__(dict(data))