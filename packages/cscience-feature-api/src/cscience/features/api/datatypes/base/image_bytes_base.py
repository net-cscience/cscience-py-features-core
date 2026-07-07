from .media_bytes_base import MediaBytesBase


class ImageBytesBase(MediaBytesBase):
    """Encoded image bytes."""

    media_type = "image"