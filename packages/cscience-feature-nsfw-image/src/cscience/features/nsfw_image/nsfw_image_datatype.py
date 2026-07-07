from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class NsfwImageDatatype(DatatypeBase, ABC):
    """Base class for nsfw_image feature-specific datatypes."""

    namespace = "nsfw_image"
