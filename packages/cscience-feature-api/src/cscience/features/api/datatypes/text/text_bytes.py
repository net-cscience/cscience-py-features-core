from cscience.features.api.datatypes.base.media.text_bytes_base import TextBytesBase
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class TextBytes(
    TextBytesBase,
    CoreDatatype[bytes],
):
    """Encoded image bytes."""
