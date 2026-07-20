from collections.abc import Mapping

from PIL import Image

from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import VectorBatchBase
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class PilImageBatch(
    VectorBatchBase[Image.Image],
    CoreDatatype[dict[int, Image.Image]],
):
    def __init__(
        self,
        data: dict[int, Image.Image],
        *,
        require_same_size: bool = True,
    ) -> None:
        super().__init__(data)

        self._require_same_size = require_same_size

        if require_same_size:
            self.same_size()

    def same_size(
        self,
    ) -> tuple[int, int]:
        sizes = {
            image.size
            for image in self.ordered_values()
        }

        if len(sizes) != 1:
            raise ValueError(
                "All images in PilImageBatch must have "
                "the same dimensions."
            )

        return next(iter(sizes))

    @property
    def requires_same_size(self) -> bool:
        return self._require_same_size