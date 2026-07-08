
from abc import ABC

from cscience.features.api import DatatypeBase


class ClipSpatialDatatype(DatatypeBase, ABC):
    """Base class for CLIP Spatial-specific datatypes."""

    namespace = "clip_spatial"