from abc import ABC

from cscience.features.api import DatatypeBase


class AsrWhisperDatatype(DatatypeBase, ABC):
    """Base class for Whisper ASR-specific datatypes."""

    namespace = "asr_whisper"