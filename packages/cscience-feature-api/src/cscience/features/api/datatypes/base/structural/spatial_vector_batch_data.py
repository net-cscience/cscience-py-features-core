from collections.abc import Mapping
from dataclasses import dataclass
from typing import Generic, TypeVar

from cscience.features.api.datatypes.spatial.spatial_batch_layout import SpatialBatchLayout
from cscience.features.api.datatypes.spatial.spatial_region import SpatialRegion

V = TypeVar("V")


@dataclass(frozen=True, slots=True)
class SpatialVectorBatchData(Generic[V]):
    """Spatially structured vector batch data.

    The vectors are stored flat:

        vectors[flat_index] -> vector

    The layout reconstructs the logical structure:

        flat_index <-> (item_index, region_index)
    """

    vectors: Mapping[int, V]
    layout: SpatialBatchLayout
    item_keys: tuple[int, ...]
    regions: tuple[SpatialRegion, ...]