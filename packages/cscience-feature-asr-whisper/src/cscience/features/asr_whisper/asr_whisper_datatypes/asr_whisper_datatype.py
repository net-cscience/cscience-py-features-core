from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class AsrWhisperDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for Whisper ASR-specific datatypes."""

    namespace = "asr_whisper"