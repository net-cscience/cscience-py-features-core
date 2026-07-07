from collections.abc import Mapping

from cscience.features.api.datatypes.base.batch_base import BatchBase
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class TextBatch(CoreDatatype[dict[int, str]], BatchBase[str]):
    """Batch of text strings indexed by source position."""

    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)

        for key, value in data.items():
            if type(value) is not str:
                raise TypeError(
                    f"TextBatch expects str values, got {type(value).__name__} "
                    f"at key {key}."
                )

        super().__init__(dict(data))