from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class IntVector(
    PrimitiveVectorBase[int],
    CoreDatatype[list[int]],
):
    """Single integer vector."""

    element_type = int