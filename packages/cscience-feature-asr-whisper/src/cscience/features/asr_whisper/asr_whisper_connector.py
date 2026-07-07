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