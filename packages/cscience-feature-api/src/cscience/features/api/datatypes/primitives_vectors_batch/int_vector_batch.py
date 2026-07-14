from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class IntVectorBatch(
    PrimitiveVectorBatchBase[int],
    CoreDatatype[dict[int, list[int]]],
):
    """Batch of integer vectors indexed by source position."""

    element_type = int