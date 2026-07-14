from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class BoolVector(
    PrimitiveVectorBase[bool],
    CoreDatatype[list[bool]],
):
    """Single boolean vector."""

    element_type = bool