from dataclasses import dataclass
from typing import Any

from ..asr_whisper_datatype import AsrWhisperDatatype


@dataclass(frozen=True, slots=True)
class WhisperTranscriptionData:
    """Structured Whisper transcription result."""

    text: str
    language: str | None
    segments: list[dict[str, Any]]


class WhisperTranscription(AsrWhisperDatatype):
    """Whisper transcription output."""

    def __init__(self, data: WhisperTranscriptionData) -> None:
        super().__init__(data)