from abc import ABC
from typing import Generic, TypeVar

from .datatype_base import DatatypeBase

T = TypeVar("T")


class CoreDatatype(DatatypeBase[T], ABC, Generic[T]):
    """Base class for feature-independent core datatypes.

    Core datatypes describe generic media, primitive, text, vector, or
    embedding containers. They must not encode feature-specific model results.
    """

    namespace = "core"