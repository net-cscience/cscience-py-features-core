from ..asr_whisper_datatype import AsrWhisperDatatype


class AudioBytes(AsrWhisperDatatype):
    """Raw encoded audio bytes."""

    def __init__(self, data: bytes) -> None:
        super().__init__(data)