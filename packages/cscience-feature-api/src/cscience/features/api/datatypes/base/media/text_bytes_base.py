from cscience.features.api.datatypes.base.media.media_bytes_base import MediaBytesBase


class TextBytesBase(MediaBytesBase):
    """Mixin for encoded text bytes."""

    media_type = "text"