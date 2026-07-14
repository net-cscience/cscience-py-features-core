from dataclasses import dataclass
from typing import Any

from .asr_whisper_datatype import AsrWhisperDatatype


@dataclass(frozen=True, slots=True)
class WhisperTranscriptionData:
    """Structured Whisper transcription result."""

    text: str
    language: str | None
    segments: list[dict[str, Any]]


class WhisperTranscription(
    AsrWhisperDatatype[WhisperTranscriptionData],
):
    """Whisper transcription output."""

    def __init__(
        self,
        data: WhisperTranscriptionData,
    ) -> None:
        if not isinstance(data, WhisperTranscriptionData):
            raise TypeError(
                "WhisperTranscription expects "
                f"WhisperTranscriptionData, "
                f"got {type(data).__name__}."
            )

        if type(data.text) is not str:
            raise TypeError(
                "WhisperTranscriptionData.text expects str, "
                f"got {type(data.text).__name__}."
            )

        if (
            data.language is not None
            and type(data.language) is not str
        ):
            raise TypeError(
                "WhisperTranscriptionData.language expects "
                f"str | None, got {type(data.language).__name__}."
            )

        if type(data.segments) is not list:
            raise TypeError(
                "WhisperTranscriptionData.segments expects list, "
                f"got {type(data.segments).__name__}."
            )

        super().__init__(data)