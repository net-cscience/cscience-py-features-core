import base64
import io

import librosa
import numpy as np
import soundfile as sf

from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    Text,
)

from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import WhisperTranscription


def audio_data_url_passthrough(data_url: AudioDataUrl) -> AudioDataUrl:
    return data_url


def audio_bytes_passthrough(audio: AudioBytes) -> AudioBytes:
    return audio


def audio_signal_passthrough(signal: AudioSignal) -> AudioSignal:
    return signal


def whisper_transcription_passthrough(
    transcription: WhisperTranscription,
) -> WhisperTranscription:
    return transcription


def audio_data_url_to_audio_bytes(data_url: AudioDataUrl) -> AudioBytes:
    """Decode a base64 audio data URL into raw encoded audio bytes."""
    encoded = data_url.payload()
    return AudioBytes(base64.b64decode(encoded, validate=True))


def audio_bytes_to_audio_signal(audio: AudioBytes) -> AudioSignal:
    """Decode audio bytes into Whisper-ready mono float32 16 kHz audio."""
    waveform, sample_rate = sf.read(io.BytesIO(audio.data()))
    waveform = np.asarray(waveform)

    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    elif waveform.ndim != 1:
        raise ValueError(f"Unexpected audio shape: {waveform.shape}")

    waveform = waveform.astype(np.float32, copy=False)

    if sample_rate != 16_000:
        waveform = librosa.resample(
            waveform,
            orig_sr=sample_rate,
            target_sr=16_000,
        )
        sample_rate = 16_000

    waveform = np.ascontiguousarray(waveform, dtype=np.float32)

    return AudioSignal(
        AudioSignalData(
            waveform=waveform,
            sample_rate=sample_rate,
        )
    )


def audio_data_url_to_audio_signal(data_url: AudioDataUrl) -> AudioSignal:
    """Decode a base64 audio data URL directly into a Whisper-ready signal."""
    return audio_bytes_to_audio_signal(
        audio_data_url_to_audio_bytes(data_url)
    )


def whisper_transcription_to_text(transcription: WhisperTranscription) -> Text:
    """Extract plain text from a Whisper transcription."""
    return Text(transcription.data().text)


class AsrWhisperConversionProvider(ConversionProviderBase):
    """Registers conversions required by the Whisper ASR feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[AudioDataUrl, AudioDataUrl](
                name="audio_data_url_passthrough",
                source=self._feature,
                function=audio_data_url_passthrough,
                input_type=AudioDataUrl,
                output_type=AudioDataUrl,
            ),
            Converter[AudioBytes, AudioBytes](
                name="audio_bytes_passthrough",
                source=self._feature,
                function=audio_bytes_passthrough,
                input_type=AudioBytes,
                output_type=AudioBytes,
            ),
            Converter[AudioSignal, AudioSignal](
                name="audio_signal_passthrough",
                source=self._feature,
                function=audio_signal_passthrough,
                input_type=AudioSignal,
                output_type=AudioSignal,
            ),
            Converter[WhisperTranscription, WhisperTranscription](
                name="whisper_transcription_passthrough",
                source=self._feature,
                function=whisper_transcription_passthrough,
                input_type=WhisperTranscription,
                output_type=WhisperTranscription,
            ),
            Converter[AudioDataUrl, AudioBytes](
                name="audio_data_url_to_audio_bytes",
                source=self._feature,
                function=audio_data_url_to_audio_bytes,
                input_type=AudioDataUrl,
                output_type=AudioBytes,
            ),
            Converter[AudioBytes, AudioSignal](
                name="audio_bytes_to_audio_signal",
                source=self._feature,
                function=audio_bytes_to_audio_signal,
                input_type=AudioBytes,
                output_type=AudioSignal,
            ),
            Converter[AudioDataUrl, AudioSignal](
                name="audio_data_url_to_audio_signal",
                source=self._feature,
                function=audio_data_url_to_audio_signal,
                input_type=AudioDataUrl,
                output_type=AudioSignal,
            ),
            Converter[WhisperTranscription, Text](
                name="whisper_transcription_to_text",
                source=self._feature,
                function=whisper_transcription_to_text,
                input_type=WhisperTranscription,
                output_type=Text,
            ),
        ]