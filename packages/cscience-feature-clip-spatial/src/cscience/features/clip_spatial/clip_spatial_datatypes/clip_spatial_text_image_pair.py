from cscience.features.api import (
    PilImageBatch,
    TextBatch,
)

from .clip_spatial_datatype import ClipSpatialDatatype
from .clip_spatial_text_image_pair_data import (
    ClipSpatialTextImagePairData,
)


class ClipSpatialTextImagePair(
    ClipSpatialDatatype[ClipSpatialTextImagePairData],
):
    """Pair of text queries and source images for spatial retrieval."""

    def __init__(
        self,
        data: ClipSpatialTextImagePairData,
    ) -> None:
        if not isinstance(
            data,
            ClipSpatialTextImagePairData,
        ):
            raise TypeError(
                "ClipSpatialTextImagePair expects "
                "ClipSpatialTextImagePairData, "
                f"got {type(data).__name__}."
            )

        if not isinstance(data.texts, TextBatch):
            raise TypeError(
                "ClipSpatialTextImagePair texts expects TextBatch."
            )

        if not isinstance(data.images, PilImageBatch):
            raise TypeError(
                "ClipSpatialTextImagePair images expects "
                "PilImageBatch."
            )

        super().__init__(data)

    @property
    def texts(self) -> TextBatch:
        return self.data().texts

    @property
    def images(self) -> PilImageBatch:
        return self.data().images