from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)

T = TypeVar("T")


class ClipDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for CLIP-specific datatypes."""

    namespace = "clip"