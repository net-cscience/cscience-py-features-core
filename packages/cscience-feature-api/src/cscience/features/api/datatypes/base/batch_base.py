from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar

T = TypeVar("T")


class BatchBase(ABC, Generic[T]):
    """Mixin for indexed batch datatypes.

    Guarantee:
    - batch data is a non-empty mapping
    - keys are integer source indices
    - values are batch elements

    Ordering is not part of the guarantee. Converters that need ordered output
    must explicitly sort by key.
    """

    def _validate_batch_mapping(self, data: Mapping[int, T]) -> None:
        if not data:
            raise ValueError(f"{type(self).__name__} cannot be empty.")

        for key in data.keys():
            if type(key) is not int:
                raise TypeError(
                    f"{type(self).__name__} keys must be int, "
                    f"got {type(key).__name__}."
                )

    def batch_size(self) -> int:
        """Return the number of batch elements."""
        return len(self.data())