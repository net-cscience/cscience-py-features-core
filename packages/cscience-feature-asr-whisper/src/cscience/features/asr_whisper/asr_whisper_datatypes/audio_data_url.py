from ..asr_whisper_datatype import AsrWhisperDatatype


class AudioDataUrl(AsrWhisperDatatype):
    """Base64-encoded audio data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)