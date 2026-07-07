from .primitive_vector_base import PrimitiveVectorBase


class BoolVector(PrimitiveVectorBase[bool]):
    """Single boolean vector."""

    element_type = bool