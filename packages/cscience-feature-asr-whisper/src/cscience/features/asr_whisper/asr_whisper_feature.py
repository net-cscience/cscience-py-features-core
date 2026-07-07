from __future__ import annotations

import threading

import torch
import whisper

from cscience.features.api import FeatureBase

from .asr_whisper_datatypes.audio_signal import AudioSignal
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)


class AsrWhisperFeature(FeatureBase):
    """Whisper ASR feature service.

    Loads the Whisper model once and transcribes decoded mono audio signals.
    """

    MODEL_NAME = "small"

    def _initialize(self) -> None:
        if self._initialized:
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = whisper.load_model(self.MODEL_NAME, device=self.device)
        self.lock = threading.Lock()

        self._initialized = True

    @classmethod
    @torch.inference_mode()
    def transcribe(cls, audio: AudioSignal) -> WhisperTranscription:
        """Transcribe a Whisper-ready audio signal."""
        service = cls.get_instance()
        fp16 = service.device.type == "cuda"

        with service.lock:
            result = service.model.transcribe(
                audio.data().waveform,
                fp16=fp16,
            )

        return WhisperTranscription(
            WhisperTranscriptionData(
                text=result.get("text", "").strip(),
                language=result.get("language"),
                segments=result.get("segments", []),
            )
        )