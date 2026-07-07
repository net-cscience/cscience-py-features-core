from abc import ABC

from .core_datatype import CoreDatatype


class MediaBytesBase(CoreDatatype[bytes], ABC):
    """Base class for encoded media byte containers."""

    media_type: str = "media"

    def __init__(self, data: bytes) -> None:
        if not data:
            raise ValueError(f"{type(self).__name__} cannot be empty.")

        super().__init__(data)