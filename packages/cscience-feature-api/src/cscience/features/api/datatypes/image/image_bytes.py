from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class ImageBytes(
    ImageBytesBase,
    CoreDatatype[bytes],
):
    """Encoded image bytes."""