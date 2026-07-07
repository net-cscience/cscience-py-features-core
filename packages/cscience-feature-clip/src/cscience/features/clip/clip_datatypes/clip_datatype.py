from abc import ABC

from cscience.features.api import DatatypeBase


class ClipDatatype(DatatypeBase, ABC):
    """Base class for CLIP-specific datatypes."""

    namespace = "clip"