from cscience.features.api import DataUrl


class AudioDataUrl(DataUrl):
    """Base64-encoded audio data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)

        media_type = self.media_type()
        if media_type is None or not media_type.startswith("audio/"):
            raise ValueError(f"AudioDataUrl expects audio media type, got {media_type}.")

        if not self.is_base64():
            raise ValueError("AudioDataUrl expects base64-encoded audio data.")