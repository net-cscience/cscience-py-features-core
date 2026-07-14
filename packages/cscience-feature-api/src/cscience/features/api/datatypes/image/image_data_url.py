from cscience.features.api.datatypes.references.data_url import DataUrl


class ImageDataUrl(DataUrl):
    """Base64-encoded image data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)

        media_type = self.media_type()

        if media_type is None or not media_type.startswith("image/"):
            raise ValueError(
                "ImageDataUrl must declare an image media type."
            )

        if not self.is_base64():
            raise ValueError(
                "ImageDataUrl must declare base64 encoding."
            )