from cscience.features.api.datatypes.spatial.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.spatial.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)


class SpatialScoreVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
):
    """Spatial scores for one or more queries.

    Physical structure:
        dict[flat_region_index, list[float]]

    Logical structure:
        [item_count, regions_per_item, query_count]

    query_keys maps each score-vector position back to the corresponding
    TextBatch key.
    """

    element_type = float

    def __init__(
        self,
        data: SpatialVectorBatchData[list[float]],
        query_keys: tuple[int, ...],
    ) -> None:
        self._query_keys = query_keys

        super().__init__(
            data,
            assert_length=len(query_keys),
        )

    @property
    def query_keys(self) -> tuple[int, ...]:
        return self._query_keys

    @property
    def query_count(self) -> int:
        return len(self._query_keys)