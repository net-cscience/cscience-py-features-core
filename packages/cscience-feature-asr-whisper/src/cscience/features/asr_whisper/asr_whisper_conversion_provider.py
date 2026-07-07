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