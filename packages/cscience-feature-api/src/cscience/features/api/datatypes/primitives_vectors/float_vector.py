from cscience.features.api.datatypes.base.embedding_base import EmbeddingBase

from .primitive_vector_base import PrimitiveVectorBase


class FloatVector(PrimitiveVectorBase[float], EmbeddingBase):
    """Single float vector."""

    element_type = float