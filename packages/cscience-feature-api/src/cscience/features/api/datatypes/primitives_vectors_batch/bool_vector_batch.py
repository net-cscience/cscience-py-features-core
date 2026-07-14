from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class BoolVectorBatch(
    PrimitiveVectorBatchBase[bool],
    CoreDatatype[dict[int, list[bool]]],
):
    """Batch of boolean vectors indexed by source position."""

    element_type = bool