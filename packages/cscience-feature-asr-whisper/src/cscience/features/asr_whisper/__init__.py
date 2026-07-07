from cscience.features.api import RegistryBase

from .asr_whisper_connector import AsrWhisperConnector
from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_feature import AsrWhisperFeature
from .asr_whisper_datatypes.asr_whisper_datatype import AsrWhisperDatatype
from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)

__all__ = [
    "AsrWhisperConnector",
    "AsrWhisperConversionProvider",
    "AsrWhisperDatatype",
    "AsrWhisperFeature",
    "AudioBytes",
    "AudioDataUrl",
    "AudioSignal",
    "AudioSignalData",
    "WhisperTranscription",
    "WhisperTranscriptionData",
]


def register(registry: RegistryBase) -> None:
    registry.register("asr_whisper", AsrWhisperConversionProvider)