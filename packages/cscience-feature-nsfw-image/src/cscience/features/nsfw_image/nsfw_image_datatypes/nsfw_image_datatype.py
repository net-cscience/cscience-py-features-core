from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class NsfwImageDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for NSFW image-specific datatypes."""

    namespace = "nsfw_image"