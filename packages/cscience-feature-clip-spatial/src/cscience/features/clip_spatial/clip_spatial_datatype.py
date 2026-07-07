from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class ClipDatatype(DatatypeBase, ABC):
    namespace = "clip_spatial"