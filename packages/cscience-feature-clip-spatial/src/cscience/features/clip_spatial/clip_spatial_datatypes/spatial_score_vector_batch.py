from cscience.features.api import (
    SpatialPrimitiveVectorBatchBase,
    SpatialVectorBatchData,
)

from .clip_spatial_datatype import ClipSpatialDatatype


class SpatialScoreVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    ClipSpatialDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    """Spatial scores for one or more text queries.

    Physical structure:
        dict[flat_region_index, list[float]]

    Logical structure:
        [item_count, regions_per_item, query_count]

    Each score-vector position corresponds to the TextBatch key at the same
    position in query_keys.
    """

    element_type = float

    def __init__(
        self,
        data: SpatialVectorBatchData[list[float]],
        query_keys: tuple[int, ...],
    ) -> None:
        if type(query_keys) is not tuple:
            raise TypeError(
                "SpatialScoreVectorBatch query_keys expects tuple, "
                f"got {type(query_keys).__name__}."
            )

        if not query_keys:
            raise ValueError(
                "SpatialScoreVectorBatch query_keys cannot be empty."
            )

        for key in query_keys:
            if type(key) is not int:
                raise TypeError(
                    "SpatialScoreVectorBatch query keys must be int, "
                    f"got {type(key).__name__}."
                )

        if len(set(query_keys)) != len(query_keys):
            raise ValueError(
                "SpatialScoreVectorBatch query keys must be unique."
            )

        self._query_keys = query_keys

        super().__init__(
            data,
            assert_length=len(query_keys),
        )

    @property
    def query_keys(self) -> tuple[int, ...]:
        """Return query keys in score-vector position order."""
        return self._query_keys

    @property
    def query_count(self) -> int:
        """Return the number of represented queries."""
        return len(self._query_keys)