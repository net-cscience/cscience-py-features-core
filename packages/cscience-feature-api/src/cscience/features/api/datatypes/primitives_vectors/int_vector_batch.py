from .primitive_vector_batch_base import PrimitiveVectorBatchBase


class IntVectorBatch(PrimitiveVectorBatchBase[int]):
    """Batch of integer vectors indexed by source position."""

    element_type = int