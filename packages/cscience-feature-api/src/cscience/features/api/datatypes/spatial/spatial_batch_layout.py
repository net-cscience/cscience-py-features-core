from dataclasses import dataclass

import icontract

from cscience.features.api.datatypes.spatial.spatial_region import SpatialRegion




@dataclass(frozen=True, slots=True)
class SpatialBatchLayout:
    """Mapping between flat batch indices and structured spatial indices.

    Logical structure:
        [item_count, regions_per_item]

    Physical structure:
        [item_count * regions_per_item]
    """

    @icontract.require(
        lambda self: self.item_count > 0,
        description="item_count must be positive.",
    )
    @icontract.require(
        lambda self: self.regions_per_item > 0,
        description="regions_per_item must be positive.",
    )
    def __post_init__(self) -> None:
        pass


    item_count: int
    regions_per_item: int

    @property
    def flat_count(self) -> int:
        """Return the number of flat batch entries."""
        return self.item_count * self.regions_per_item

    @icontract.require(lambda self, item_index: 0 <= item_index < self.item_count)
    @icontract.require(lambda self, region_index: 0 <= region_index < self.regions_per_item)
    def to_flat_index(self, item_index: int, region_index: int) -> int:
        """Return the flat index for a structured item-region pair."""
        return item_index * self.regions_per_item + region_index

    @icontract.require(lambda self, flat_index: 0 <= flat_index < self.flat_count)
    def from_flat_index(self, flat_index: int) -> tuple[int, int]:
        """Return ``(item_index, region_index)`` for a flat index."""
        return divmod(flat_index, self.regions_per_item)