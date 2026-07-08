from abc import ABC
from collections.abc import Mapping, Sized
from typing import Generic, TypeVar

import icontract

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype
from cscience.features.api.datatypes.base.vector_batch_base import VectorBatchBase

from .spatial_batch_layout import SpatialBatchLayout
from .spatial_region import SpatialRegion
from .spatial_vector_batch_data import SpatialVectorBatchData

V = TypeVar("V")


class SpatialVectorBatchBase(
    CoreDatatype[SpatialVectorBatchData[V]],
    VectorBatchBase[V],
    ABC,
    Generic[V],
):
    """Base class for spatially structured vector batches.

    Physical structure:
        dict[int, vector]

    Logical structure:
        [item_count, regions_per_item, vector_dim]
    """

    @icontract.require(lambda data: len(data.vectors) == data.layout.flat_count,
                       "Spatial vector count must match layout.flat_count.",
                       )
    @icontract.require(
        lambda data: set(data.vectors.keys()) == set(range(data.layout.flat_count)),
        "Spatial vector keys must be contiguous flat indices 0..layout.flat_count-1.",
    )
    @icontract.require(
        lambda data: len(data.regions) == data.layout.regions_per_item,
        "Region count must match layout.regions_per_item.",
    )
    @icontract.require(
        lambda data: all(region.index == index for index, region in enumerate(data.regions)),
        "Region indices must match their position in the region tuple.",
    )
    def __init__(
            self,
            data: SpatialVectorBatchData[V],
            assert_length: int | None = None,
    ) -> None:
        if not isinstance(data, SpatialVectorBatchData):
            raise TypeError(
                f"{type(self).__name__} expects SpatialVectorBatchData, "
                f"got {type(data).__name__}."
            )

        self._validate_vector_batch_mapping(data.vectors)
        self._validate_uniform_vector_lengths(data.vectors)

        normalized = SpatialVectorBatchData(
            vectors=dict(data.vectors),
            layout=data.layout,
            item_keys=tuple(data.item_keys),
            regions=tuple(data.regions),
        )

        super().__init__(normalized)

        if assert_length is not None:
            self.assert_length(assert_length)

    @staticmethod
    def _validate_uniform_vector_lengths(data: Mapping[int, V]) -> None:
        lengths: dict[int, int] = {}

        for key, vector in data.items():
            if not isinstance(vector, Sized):
                raise TypeError(
                    f"Spatial vector at key {key} must be sized, "
                    f"got {type(vector).__name__}."
                )

            lengths[key] = len(vector)

        unique_lengths = set(lengths.values())

        if len(unique_lengths) != 1:
            raise ValueError(
                f"Spatial vector batch must have uniform vector lengths, got {lengths}."
            )

    @property
    def vectors(self) -> dict[int, V]:
        """Return flat vectors indexed by flat spatial index."""
        return dict(self.data().vectors)

    @property
    def layout(self) -> SpatialBatchLayout:
        """Return the spatial batch layout."""
        return self.data().layout

    @property
    def regions(self) -> tuple[SpatialRegion, ...]:
        """Return the regions used for every item."""
        return self.data().regions

    def batch_size(self) -> int:
        """Return the flat batch size."""
        return len(self.data().vectors)

    def item_count(self) -> int:
        """Return the number of structured source items."""
        return self.layout.item_count

    def regions_per_item(self) -> int:
        """Return the number of regions per source item."""
        return self.layout.regions_per_item

    def ordered_keys(self) -> tuple[int, ...]:
        """Return flat indices in canonical order."""
        return tuple(sorted(self.data().vectors.keys()))

    def ordered_values(self) -> tuple[V, ...]:
        """Return vectors in canonical flat-index order."""
        return tuple(self.data().vectors[key] for key in self.ordered_keys())

    def ordered_items(self) -> tuple[tuple[int, V], ...]:
        """Return flat-indexed vectors in canonical order."""
        return tuple((key, self.data().vectors[key]) for key in self.ordered_keys())

    def length(self) -> int:
        """Return the vector dimension."""
        first_key = self.ordered_keys()[0]
        return len(self.data().vectors[first_key])

    def assert_length(self, expected: int) -> None:
        """Raise if the vector dimension does not match the expected value."""
        actual = self.length()

        if actual != expected:
            raise ValueError(f"Expected vector length {expected}, got {actual}.")

    def to_flat_index(self, item_index: int, region_index: int) -> int:
        """Return the flat index for a structured item-region pair."""
        return self.layout.to_flat_index(item_index, region_index)

    def from_flat_index(self, flat_index: int) -> tuple[int, int]:
        """Return ``(item_index, region_index)`` for a flat index."""
        return self.layout.from_flat_index(flat_index)

    def region_for_flat_index(self, flat_index: int) -> SpatialRegion:
        """Return the region metadata for a flat index."""
        _, region_index = self.from_flat_index(flat_index)
        return self.regions[region_index]

    def vector_at(self, item_index: int, region_index: int) -> V:
        """Return the vector for a structured item-region pair."""
        return self.data().vectors[self.to_flat_index(item_index, region_index)]

    def item_vectors(self, item_index: int) -> tuple[V, ...]:
        """Return all region vectors for one structured item."""
        return tuple(
            self.vector_at(item_index, region_index)
            for region_index in range(self.layout.regions_per_item)
        )
