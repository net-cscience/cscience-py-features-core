from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class AudioBytes(
    AudioBytesBase,
    CoreDatatype[bytes],
):
    """Encoded audio bytes."""