from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)


class ImageBytesBase(MediaBytesBase):
    """Mixin for encoded image bytes."""

    media_type = "image"