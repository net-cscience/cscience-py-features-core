from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Whisper-ready mono audio signal."""

    waveform: np.ndarray
    sample_rate: int
