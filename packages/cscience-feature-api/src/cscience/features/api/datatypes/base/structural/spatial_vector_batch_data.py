from collections.abc import Mapping
from dataclasses import dataclass
from typing import Generic, TypeVar

from cscience.features.api.datatypes.spatial.spatial_batch_layout import SpatialBatchLayout
from cscience.features.api.datatypes.spatial.spatial_region import SpatialRegion

V = TypeVar("V")


@dataclass(frozen=True, slots=True)
class SpatialVectorBatchData(Generic[V]):
    """Spatially structured vector batch data.

    Spatial vectors are stored flat:

        vectors[flat_index] -> vector

    The layout reconstructs the logical spatial structure:

        flat_index <-> (item_index, region_index)

    ``item_keys`` maps each logical ``item_index`` back to the key of the
    corresponding source item:

        item_keys[item_index] -> item_key

    For example, with::

        item_keys = (10, 20)

    logical item index ``0`` refers to source item ``10`` and logical item
    index ``1`` refers to source item ``20``.

    ``base_vectors`` stores one non-spatial vector per source item and is
    therefore indexed directly by ``item_key``:

        base_vectors[item_key] -> vector

    ``regions`` contains the spatial region metadata shared by all items,
    where the position of each region corresponds to its ``region_index``.
    """

    vectors: Mapping[int, V]
    base_vectors: Mapping[int, V]
    layout: SpatialBatchLayout
    item_keys: tuple[int, ...]
    regions: tuple[SpatialRegion, ...]
