from abc import ABC
from typing import Generic, TypeVar

from .spatial_vector_batch_base import SpatialVectorBatchBase
from .spatial_vector_batch_data import SpatialVectorBatchData

T = TypeVar("T")


class SpatialPrimitiveVectorBatchBase(
    SpatialVectorBatchBase[list[T]],
    ABC,
    Generic[T],
):
    """Base class for spatial batches of list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: SpatialVectorBatchData[list[T]],
        assert_length: int | None = None,
    ) -> None:
        super().__init__(data, assert_length=assert_length)

        for key, vector in self.data().vectors.items():
            for index, value in enumerate(vector):
                if type(value) is not self.element_type:
                    raise TypeError(
                        f"{type(self).__name__} expects {self.element_type.__name__}, "
                        f"got {type(value).__name__} at key {key}, index {index}."
                    )