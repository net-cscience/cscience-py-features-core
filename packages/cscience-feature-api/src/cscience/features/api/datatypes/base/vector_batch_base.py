from abc import ABC
from collections.abc import Mapping, Sized
from typing import Generic, TypeVar

from .batch_base import BatchBase

V = TypeVar("V")


class VectorBatchBase(BatchBase[V], ABC, Generic[V]):
    """Mixin for indexed batches of vectors.

    Guarantee:
    - data is a non-empty mapping from int source indices to vectors
    - each vector is non-empty
    - all vectors have the same length
    - batch_size() returns the number of vectors
    - length() returns the shared vector dimension
    """

    def _validate_vector_batch_mapping(self, data: Mapping[int, V]) -> None:
        self._validate_batch_mapping(data)

        lengths: set[int] = set()

        for key, vector in data.items():
            if not isinstance(vector, Sized):
                raise TypeError(
                    f"Vector at key {key} must be sized, "
                    f"got {type(vector).__name__}."
                )

            vector_length = len(vector)

            if vector_length == 0:
                raise ValueError(f"Vector at key {key} cannot be empty.")

            lengths.add(vector_length)

        if len(lengths) != 1:
            raise ValueError(f"Inconsistent vector lengths: {sorted(lengths)}.")

    def length(self) -> int:
        """Return the shared vector dimension."""
        first_vector = next(iter(self.data().values()))
        return len(first_vector)

    def assert_length(self, expected: int) -> None:
        """Raise if the shared vector dimension does not match the expected value."""
        actual = self.length()

        if actual != expected:
            raise ValueError(f"Expected vector length {expected}, got {actual}.")