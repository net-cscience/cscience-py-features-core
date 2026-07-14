from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class SpatialFloatVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    """Spatially structured batch of float embedding vectors.

    Physical structure:
        dict[int, list[float]]

    Logical structure:
        [item_count, regions_per_item, embedding_dim]
    """

    element_type = float