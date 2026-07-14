from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)


class AudioBytesBase(MediaBytesBase):
    """Mixin for encoded audio bytes."""

    media_type = "audio"