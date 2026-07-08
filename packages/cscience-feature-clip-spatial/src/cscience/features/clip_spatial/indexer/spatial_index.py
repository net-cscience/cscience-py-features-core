from dataclasses import dataclass

from cscience.features.api.datatypes.spatial.spatial_region import SpatialRegion


@dataclass(frozen=True, slots=True)
class SpatialIndex:
    """Resolved spatial index entry."""

    item_index: int
    item_key: int
    region_index: int
    flat_index: int
    region: SpatialRegion
