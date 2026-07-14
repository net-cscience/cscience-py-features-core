from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.structural.spatial_vector_batch_base import (
    SpatialVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)

T = TypeVar("T")


class SpatialPrimitiveVectorBatchBase(
    SpatialVectorBatchBase[list[T]],
    ABC,
    Generic[T],
):
    """Mixin for spatial batches of list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: SpatialVectorBatchData[list[T]],
        assert_length: int | None = None,
    ) -> None:
        super().__init__(
            data,
            assert_length=assert_length,
        )

        for key, vector in self._batch_mapping().items():
            if type(vector) is not list:
                raise TypeError(
                    f"{type(self).__name__} expects list vectors, "
                    f"got {type(vector).__name__} at key {key}."
                )

            for index, value in enumerate(vector):
                if type(value) is not self.element_type:
                    raise TypeError(
                        f"{type(self).__name__} expects "
                        f"{self.element_type.__name__}, "
                        f"got {type(value).__name__} "
                        f"at key {key}, index {index}."
                    )