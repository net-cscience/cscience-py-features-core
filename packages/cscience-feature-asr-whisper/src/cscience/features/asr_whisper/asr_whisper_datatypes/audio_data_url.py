from cscience.features.api.datatypes.base.references.data_url_base import (
    DataUrlBase,
)

from .asr_whisper_datatype import AsrWhisperDatatype


class AudioDataUrl(
    DataUrlBase,
    AsrWhisperDatatype[str],
):
    """Base64-encoded audio data URL for Whisper input."""

    def __init__(self, data: str) -> None:
        super().__init__(data)

        media_type = self.media_type()

        if media_type is None or not media_type.startswith("audio/"):
            raise ValueError(
                "AudioDataUrl must declare an audio media type."
            )

        if not self.is_base64():
            raise ValueError(
                "AudioDataUrl must declare base64 encoding."
            )