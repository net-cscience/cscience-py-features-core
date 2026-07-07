from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Decoded audio signal with an explicit sample rate."""

    waveform: np.ndarray
    sample_rate: int

