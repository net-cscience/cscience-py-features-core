from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class FloatVector(
    PrimitiveVectorBase[float],
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    """Single float embedding vector."""

    element_type = float