from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar

import icontract

from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)
from cscience.features.api.datatypes.spatial.spatial_batch_layout import (
    SpatialBatchLayout,
)
from cscience.features.api.datatypes.spatial.spatial_region import (
    SpatialRegion,
)

V = TypeVar("V")


class SpatialVectorBatchBase(
    VectorBatchBase[V],
    ABC,
    Generic[V],
):
    """Mixin for spatially structured vector batches.

    Physical structure:
        dict[int, vector]

    Logical structure:
        [item_count, regions_per_item, vector_dim]
    """

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

        self._validate_spatial_structure(data)
        self._validate_vector_batch_mapping(data.vectors)

        normalized = SpatialVectorBatchData(
            vectors=dict(data.vectors),
            base_vectors=dict(data.base_vectors),
            layout=data.layout,
            item_keys=tuple(data.item_keys),
            regions=tuple(data.regions),
        )

        super().__init__(normalized)

        if assert_length is not None:
            self.assert_length(assert_length)

    @staticmethod
    @icontract.require(
        lambda data: len(data.vectors) == data.layout.flat_count,
        description=(
            "Spatial vector count must match layout.flat_count."
        ),
    )
    @icontract.require(
        lambda data: set(data.vectors) == set(
            range(data.layout.flat_count)
        ),
        description=(
            "Spatial vector keys must be contiguous flat indices "
            "0..layout.flat_count-1."
        ),
    )
    @icontract.require(
        lambda data: len(data.item_keys) == data.layout.item_count,
        description=(
            "Item key count must match layout.item_count."
        ),
    )
    @icontract.require(
        lambda data: len(set(data.item_keys)) == len(data.item_keys),
        description="Item keys must be unique.",
    )
    @icontract.require(
        lambda data: all(
            type(item_key) is int
            for item_key in data.item_keys
        ),
        description="Item keys must be integers.",
    )
    @icontract.require(
        lambda data: (
            len(data.regions)
            == data.layout.regions_per_item
        ),
        description=(
            "Region count must match layout.regions_per_item."
        ),
    )
    @icontract.require(
        lambda data: all(
            region.index == index
            for index, region in enumerate(data.regions)
        ),
        description=(
            "Region indices must match their tuple positions."
        ),
    )
    def _validate_spatial_structure(
        data: SpatialVectorBatchData[V],
    ) -> None:
        """Validate relationships between spatial data fields."""

    def _batch_mapping(self) -> Mapping[int, V]:
        """Return flat vectors indexed by flat spatial index."""
        return self.data().vectors

    @property
    def vectors(self) -> dict[int, V]:
        """Return flat vectors indexed by flat spatial index."""
        return dict(self.data().vectors)

    @property
    def layout(self) -> SpatialBatchLayout:
        """Return the spatial batch layout."""
        return self.data().layout

    @property
    def item_keys(self) -> tuple[int, ...]:
        """Return source keys in structured item order."""
        return self.data().item_keys

    @property
    def regions(self) -> tuple[SpatialRegion, ...]:
        """Return the regions used for every item."""
        return self.data().regions

    def item_count(self) -> int:
        """Return the number of structured source items."""
        return self.layout.item_count

    def regions_per_item(self) -> int:
        """Return the number of regions per source item."""
        return self.layout.regions_per_item

    def to_flat_index(
        self,
        item_index: int,
        region_index: int,
    ) -> int:
        """Return the flat index for an item-region pair."""
        return self.layout.to_flat_index(
            item_index,
            region_index,
        )

    def from_flat_index(
        self,
        flat_index: int,
    ) -> tuple[int, int]:
        """Return the item and region indices for a flat index."""
        return self.layout.from_flat_index(flat_index)

    def region_for_flat_index(
        self,
        flat_index: int,
    ) -> SpatialRegion:
        """Return the region metadata for a flat index."""
        _, region_index = self.from_flat_index(flat_index)

        return self.regions[region_index]

    def vector_at(
        self,
        item_index: int,
        region_index: int,
    ) -> V:
        """Return the vector for an item-region pair."""
        flat_index = self.to_flat_index(
            item_index,
            region_index,
        )

        return self._batch_mapping()[flat_index]

    def item_vectors(
        self,
        item_index: int,
    ) -> tuple[V, ...]:
        """Return all region vectors for one structured item."""
        return tuple(
            self.vector_at(item_index, region_index)
            for region_index in range(
                self.layout.regions_per_item
            )
        )