from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype
from cscience.features.api.datatypes.base.vector_batch_base import VectorBatchBase

T = TypeVar("T")


class PrimitiveVectorBatchBase(
    CoreDatatype[dict[int, list[T]]],
    VectorBatchBase[list[T]],
    ABC,
    Generic[T],
):
    """Base class for batches of list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: Mapping[int, list[T]],
        assert_length: int | None = None,
    ) -> None:
        self._validate_vector_batch_mapping(data)

        for key, vector in data.items():
            for index, value in enumerate(vector):
                if type(value) is not self.element_type:
                    raise TypeError(
                        f"{type(self).__name__} expects {self.element_type.__name__}, "
                        f"got {type(value).__name__} at key {key}, index {index}."
                    )

        super().__init__(dict(data))

        if assert_length is not None:
            self.assert_length(assert_length)