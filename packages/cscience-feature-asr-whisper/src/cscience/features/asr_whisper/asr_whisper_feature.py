from __future__ import annotations

import threading

import torch
import whisper

from cscience.features.api import FeatureBase
from cscience.features.api import FeatureInfo
from .asr_config import AsrConfig

from .asr_whisper_datatypes.audio_signal import AudioSignal
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)



class AsrWhisperFeature(FeatureBase['AsrWhisperFeature',AsrConfig]):
    """Whisper ASR feature service.

    Loads the Whisper model once and transcribes decoded mono audio signals.
    """


    def _initialize(self, config: AsrConfig) -> None:

        self._config = config
        self._device = torch.device(config.preferred_device if torch.cuda.is_available() else "cpu")
        if self._config .force_device and not (self._config.preferred_device == str(self._device)):
            raise RuntimeError(
                f"Preferred device {self._config.preferred_device} is not available. "
                f"Available device is {self._device}."
            )

        self._model = whisper.load_model(self._config.model_name, device=self._device)
        self._initialized = True

    @torch.inference_mode()
    def transcribe(self, audio: AudioSignal) -> WhisperTranscription:
        """Transcribe a Whisper-ready audio signal."""

        fp16 = self._model .device.type == "cuda"

        result = self._model.transcribe(audio.data().waveform, fp16=fp16)

        return WhisperTranscription(
            WhisperTranscriptionData(
                text=result.get("text", "").strip(),
                language=result.get("language"),
                segments=result.get("segments", []),
            )
        )


    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(mode="json"),
        )