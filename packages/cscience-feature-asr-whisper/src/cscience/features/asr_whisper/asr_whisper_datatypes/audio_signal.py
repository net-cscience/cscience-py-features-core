from dataclasses import dataclass

import numpy as np

from ..asr_whisper_datatype import AsrWhisperDatatype


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Decoded mono audio signal."""

    waveform: np.ndarray
    sample_rate: int


class AudioSignal(AsrWhisperDatatype):
    """Mono audio waveform with an explicit sample rate."""

    def __init__(self, data: AudioSignalData) -> None:
        super().__init__(data)