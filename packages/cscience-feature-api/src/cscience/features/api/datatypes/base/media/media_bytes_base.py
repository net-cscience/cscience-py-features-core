from abc import ABC


class MediaBytesBase(ABC):
    """Mixin for non-empty encoded media bytes."""

    media_type = "media"

    def __init__(self, data: bytes) -> None:
        if type(data) is not bytes:
            raise TypeError(
                f"{type(self).__name__} expects bytes, "
                f"got {type(data).__name__}."
            )

        if not data:
            raise ValueError(
                f"{type(self).__name__} cannot be empty."
            )

        super().__init__(data)