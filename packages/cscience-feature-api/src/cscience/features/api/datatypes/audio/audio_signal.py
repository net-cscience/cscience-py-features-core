import numpy as np

from cscience.features.api.datatypes.audio.audio_signal_data import (
    AudioSignalData,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class AudioSignal(CoreDatatype[AudioSignalData]):
    """Decoded audio signal."""

    def __init__(self, data: AudioSignalData) -> None:
        if not isinstance(data, AudioSignalData):
            raise TypeError(
                f"AudioSignal expects AudioSignalData, "
                f"got {type(data).__name__}."
            )

        waveform = data.waveform

        if not isinstance(waveform, np.ndarray):
            raise TypeError(
                f"AudioSignal waveform expects np.ndarray, "
                f"got {type(waveform).__name__}."
            )

        if waveform.ndim not in {1, 2}:
            raise ValueError(
                "AudioSignal waveform must be 1D or 2D, "
                f"got shape {waveform.shape}."
            )

        if waveform.size == 0:
            raise ValueError(
                "AudioSignal waveform cannot be empty."
            )

        if not (
            np.issubdtype(waveform.dtype, np.integer)
            or np.issubdtype(waveform.dtype, np.floating)
        ):
            raise TypeError(
                "AudioSignal waveform must have an integer or "
                f"floating-point dtype, got {waveform.dtype}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, "
                f"got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate <= 0:
            raise ValueError(
                "AudioSignal sample_rate must be positive."
            )

        super().__init__(data)