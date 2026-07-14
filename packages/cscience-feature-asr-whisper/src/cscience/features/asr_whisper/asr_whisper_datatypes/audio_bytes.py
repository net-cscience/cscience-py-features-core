from cscience.features.api import AudioBytesBase

from .asr_whisper_datatype import AsrWhisperDatatype


class AudioBytes(
    AudioBytesBase,
    AsrWhisperDatatype[bytes],
):
    """Whisper input containing encoded audio bytes."""