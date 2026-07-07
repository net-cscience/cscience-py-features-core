from abc import ABC

from cscience.features.api import DatatypeBase


class NsfwImageDatatype(DatatypeBase, ABC):
    """Base class for NSFW image feature-specific datatypes."""

    namespace = "nsfw_image"