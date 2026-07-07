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