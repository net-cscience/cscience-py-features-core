from cscience.features.api.datatypes.base.embedding_base import EmbeddingBase

from .spatial_primitive_vector_batch_base import SpatialPrimitiveVectorBatchBase


class SpatialFloatVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
):
    """Spatially structured batch of float embedding vectors.

    Physical structure:
        dict[int, list[float]]

    Logical structure:
        [item_count, regions_per_item, embedding_dim]
    """

    element_type = float