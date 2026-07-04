from abc import ABC

from .datatype_base import DatatypeBase


class CoreDatatype(DatatypeBase, ABC):
    namespace = "core"
