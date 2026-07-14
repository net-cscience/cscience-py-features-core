from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class ClipSpatialDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for CLIP Spatial-specific datatypes."""

    namespace = "clip_spatial"