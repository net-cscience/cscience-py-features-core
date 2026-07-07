# Exported code on 2026-07-07 18:09:11.892638 with root dir packages\cscience-feature-asr-whisper
# From packages\cscience-feature-asr-whisper\tests\test_asr_whisper_feature.py
import unittest

from cscience.features.asr_whisper import AsrWhisperConnector


class AsrWhisperFeatureTest(unittest.TestCase):
    def test_connector_initializes(self):
        connector = AsrWhisperConnector()
        self.assertIsNotNone(connector)


# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_connector.py
from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal
from .asr_whisper_datatypes.whisper_transcription import WhisperTranscription
from .asr_whisper_feature import AsrWhisperFeature


class AsrWhisperConnector(ConnectorBase):
    """Public connector for Whisper ASR."""

    def __init__(self) -> None:
        self.feature = AsrWhisperFeature.get_instance()
        super().__init__("asr_whisper", AsrWhisperConversionProvider(self.feature))

    def audio_data_url(self, data: str) -> str:
        """Transcribe a base64-encoded audio data URL."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioDataUrl,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )
        return function(AudioDataUrl(data)).data()

    def audio_bytes(self, data: bytes) -> str:
        """Transcribe encoded audio bytes."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioBytes,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )
        return function(AudioBytes(data)).data()

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_conversion_provider.py
import base64
import io
from urllib.parse import unquote

import librosa
import numpy as np
import soundfile as sf

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.feature.feature_base import FeatureBase

from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import WhisperTranscription


def audio_data_url_to_bytes(data_url: AudioDataUrl) -> AudioBytes:
    """Decode a base64 audio data URL into raw bytes."""
    data = unquote(data_url.data())

    if not data or "base64," not in data:
        raise ValueError("Missing or invalid base64 audio data.")

    _, encoded = data.split("base64,", 1)
    return AudioBytes(base64.b64decode(encoded))


def audio_bytes_to_signal(audio: AudioBytes) -> AudioSignal:
    """Decode audio bytes, convert to mono float32, and resample to 16 kHz."""
    waveform, sample_rate = sf.read(io.BytesIO(audio.data()))
    waveform = np.asarray(waveform)

    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    elif waveform.ndim != 1:
        raise ValueError(f"Unexpected audio shape: {waveform.shape}")

    if waveform.dtype != np.float32:
        waveform = waveform.astype(np.float32)

    if sample_rate != 16_000:
        waveform = librosa.resample(
            waveform,
            orig_sr=sample_rate,
            target_sr=16_000,
        )
        sample_rate = 16_000

    return AudioSignal(AudioSignalData(waveform=waveform, sample_rate=sample_rate))


def transcription_to_text(result: WhisperTranscription) -> Text:
    """Extract plain text from a Whisper transcription result."""
    return Text(result.data().text)


class AsrWhisperConversionProvider(ConversionProviderBase):
    """Registers conversions required by the Whisper ASR feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter(
                name="audio_data_url_to_bytes",
                source=self._feature,
                function=audio_data_url_to_bytes,
                input_type=AudioDataUrl,
                output_type=AudioBytes,
            ),
            Converter(
                name="audio_bytes_to_signal",
                source=self._feature,
                function=audio_bytes_to_signal,
                input_type=AudioBytes,
                output_type=AudioSignal,
            ),
            Converter(
                name="whisper_transcription_to_text",
                source=self._feature,
                function=transcription_to_text,
                input_type=WhisperTranscription,
                output_type=Text,
            ),
        ]

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_feature.py
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

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\__init__.py
from cscience.features.api.registry.registry_base import RegistryBase

from .asr_whisper_connector import AsrWhisperConnector
from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_feature import AsrWhisperFeature

__all__ = [
    "AsrWhisperConnector",
    "AsrWhisperConversionProvider",
    "AsrWhisperFeature",
]


def register(registry: RegistryBase) -> None:
    registry.register("asr_whisper", AsrWhisperConversionProvider)

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\asr_whisper_datatype.py
from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class AsrWhisperDatatype(DatatypeBase, ABC):
    """Base class for Whisper ASR-specific datatypes."""

    namespace = "asr_whisper"

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_bytes.py
from cscience.features.asr_whisper.asr_whisper_datatypes.asr_whisper_datatype import AsrWhisperDatatype


class AudioBytes(AsrWhisperDatatype):
    """Raw encoded audio bytes."""

    def __init__(self, data: bytes) -> None:
        super().__init__(data)

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_data_url.py
from cscience.features.asr_whisper.asr_whisper_datatypes.asr_whisper_datatype import AsrWhisperDatatype


class AudioDataUrl(AsrWhisperDatatype):
    """Base64-encoded audio data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_signal.py
from dataclasses import dataclass

import numpy as np

from cscience.features.asr_whisper.asr_whisper_datatypes.asr_whisper_datatype import AsrWhisperDatatype


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Decoded mono audio signal."""

    waveform: np.ndarray
    sample_rate: int


class AudioSignal(AsrWhisperDatatype):
    """Mono audio waveform with an explicit sample rate."""

    def __init__(self, data: AudioSignalData) -> None:
        super().__init__(data)

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\whisper_transcription.py
from dataclasses import dataclass
from typing import Any

from cscience.features.asr_whisper.asr_whisper_datatypes.asr_whisper_datatype import AsrWhisperDatatype


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

