from .primitive_vector_base import PrimitiveVectorBase


class IntVector(PrimitiveVectorBase[int]):
    """Single integer vector."""

    element_type = int