from abc import ABC
from typing import TypeVar, Generic

from cscience.features.api import DatatypeBase

T = TypeVar("T")

class AsrWhisperDatatype(DatatypeBase[T],  ABC, Generic[T]):
    """Base class for Whisper ASR-specific datatypes."""

    namespace = "asr_whisper"