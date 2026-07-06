from abc import ABC
from typing import Generic, TypeVar

from .datatype_base import DatatypeBase
T = TypeVar("T")



class CoreDatatype(DatatypeBase[T], ABC, Generic[T]):
    namespace = "core"
