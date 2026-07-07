from __future__ import annotations

import threading

import torch
import whisper

from cscience.features.api.feature.feature_base import FeatureBase

from .asr_whisper_datatypes.audio_signal import AudioSignal
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)


class AsrWhisperFeature(FeatureBase):
    """Whisper ASR feature service.

    Loads the Whisper model once and transcribes decoded mono audio signals.
    """

    def _initialize(self) -> None:
        if self._initialized:
            return

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model = whisper.load_model("small", device=self._device)
        self._lock = threading.Lock()
        self._initialized = True

    @classmethod
    @torch.inference_mode()
    def transcribe(cls, audio: AudioSignal) -> WhisperTranscription:
        """Transcribe a mono 16 kHz audio signal with Whisper."""
        service = cls.get_instance()
        fp16 = service._device.type == "cuda"

        with service._lock:
            result = service._model.transcribe(audio.data().waveform, fp16=fp16)

        return WhisperTranscription(
            WhisperTranscriptionData(
                text=result.get("text", "").strip(),
                language=result.get("language"),
                segments=result.get("segments", []),
            )
        )