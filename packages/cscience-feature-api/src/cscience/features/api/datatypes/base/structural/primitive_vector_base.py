from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)

T = TypeVar("T")


class PrimitiveVectorBase(VectorBase, ABC, Generic[T]):
    """Mixin for non-empty list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: list[T],
        assert_length: int | None = None,
    ) -> None:
        if type(data) is not list:
            raise TypeError(
                f"{type(self).__name__} expects list, "
                f"got {type(data).__name__}."
            )

        if not data:
            raise ValueError(
                f"{type(self).__name__} cannot be empty."
            )

        for index, value in enumerate(data):
            if type(value) is not self.element_type:
                raise TypeError(
                    f"{type(self).__name__} expects "
                    f"{self.element_type.__name__}, "
                    f"got {type(value).__name__} at index {index}."
                )

        super().__init__(data)

        if assert_length is not None:
            self.assert_length(assert_length)