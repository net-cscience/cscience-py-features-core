from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    ServiceInfo,
    Text,
)

from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)
from .asr_whisper_feature import AsrWhisperFeature


class AsrWhisperConnector(ConnectorBase):
    """Public connector for Whisper ASR."""

    def __init__(self) -> None:
        self.feature = AsrWhisperFeature.get_instance()
        super().__init__("asr_whisper", AsrWhisperConversionProvider(self.feature))

    def transcribe_audio_bytes(self, data: bytes) -> WhisperTranscriptionData:
        """Transcribe encoded audio bytes and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioBytes,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioBytes(data)).data()

    def transcribe_audio_data_url(self, data: str) -> WhisperTranscriptionData:
        """Transcribe a base64-encoded audio data URL and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioDataUrl,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioDataUrl(data)).data()

    def transcribe_signal(self, data: AudioSignalData) -> WhisperTranscriptionData:
        """Transcribe a Whisper-ready audio signal and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioSignal,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioSignal(data)).data()

    def audio_bytes(self, data: bytes) -> str:
        """Transcribe encoded audio bytes and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioBytes,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioBytes(data)).data()

    def audio_data_url(self, data: str) -> str:
        """Transcribe a base64-encoded audio data URL and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioDataUrl,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioDataUrl(data)).data()

    def signal(self, data: AudioSignalData) -> str:
        """Transcribe a Whisper-ready audio signal and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioSignal,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioSignal(data)).data()

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")