from .primitive_vector_batch_base import PrimitiveVectorBatchBase


class BoolVectorBatch(PrimitiveVectorBatchBase[bool]):
    """Batch of boolean vectors indexed by source position."""

    element_type = bool