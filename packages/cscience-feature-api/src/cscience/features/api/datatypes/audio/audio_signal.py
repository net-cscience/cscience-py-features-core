import numpy as np

from cscience.features.api.datatypes.audio.audio_signal_data import AudioSignalData
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class AudioSignal(CoreDatatype[AudioSignalData]):
    """Decoded audio signal."""

    def __init__(self, data: AudioSignalData) -> None:
        if not isinstance(data.waveform, np.ndarray):
            raise TypeError(
                f"AudioSignal waveform expects np.ndarray, "
                f"got {type(data.waveform).__name__}."
            )

        if data.waveform.ndim not in {1, 2}:
            raise ValueError(
                f"AudioSignal waveform must be 1D or 2D, got shape {data.waveform.shape}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate <= 0:
            raise ValueError("AudioSignal sample_rate must be positive.")

        super().__init__(data)