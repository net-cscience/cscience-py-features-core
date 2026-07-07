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
    - ordered_* methods return the canonical order by ascending source index
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

    def ordered_keys(self) -> tuple[int, ...]:
        """Return source indices in canonical batch order."""
        return tuple(sorted(self.data().keys()))

    def ordered_values(self) -> tuple[T, ...]:
        """Return values in canonical batch order."""
        return tuple(self.data()[key] for key in self.ordered_keys())

    def ordered_items(self) -> tuple[tuple[int, T], ...]:
        """Return items in canonical batch order."""
        return tuple((key, self.data()[key]) for key in self.ordered_keys())