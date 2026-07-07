from cscience.features.api.datatypes.base.embedding_base import EmbeddingBase

from .primitive_vector_batch_base import PrimitiveVectorBatchBase


class FloatVectorBatch(PrimitiveVectorBatchBase[float], EmbeddingBase):
    """Batch of float vectors indexed by source position."""

    element_type = float