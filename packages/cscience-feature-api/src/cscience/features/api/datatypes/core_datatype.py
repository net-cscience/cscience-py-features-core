from abc import ABC
from typing import Generic, TypeVar

from .datatype_base import DatatypeBase
T = TypeVar("T")



class CoreDatatype(DatatypeBase[T], ABC, Generic[T]):
    """Base class for feature-independent core datatypes.

    Core datatypes are shared across feature implementations and are used as
    public input or output types, such as text, text batches, vectors, and
    vector batches.
    """

    namespace = "core"