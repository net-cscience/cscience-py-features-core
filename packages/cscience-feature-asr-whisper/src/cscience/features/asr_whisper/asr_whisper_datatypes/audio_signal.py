from dataclasses import dataclass

import numpy as np

from .asr_whisper_datatype import AsrWhisperDatatype
from .audio_signal_data import AudioSignalData


class AudioSignal(AsrWhisperDatatype[AudioSignalData]):
    """Whisper-ready mono float32 audio signal at 16 kHz."""

    EXPECTED_SAMPLE_RATE = 16_000

    def __init__(self, data: AudioSignalData) -> None:
        if not isinstance(data, AudioSignalData):
            raise TypeError(
                f"AudioSignal expects AudioSignalData, got {type(data).__name__}."
            )

        if not isinstance(data.waveform, np.ndarray):
            raise TypeError(
                f"AudioSignal waveform expects np.ndarray, "
                f"got {type(data.waveform).__name__}."
            )

        if data.waveform.ndim != 1:
            raise ValueError(
                f"AudioSignal expects mono 1D waveform, got shape {data.waveform.shape}."
            )

        if data.waveform.dtype != np.float32:
            raise TypeError(
                f"AudioSignal expects float32 waveform, got {data.waveform.dtype}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate != self.EXPECTED_SAMPLE_RATE:
            raise ValueError(
                f"AudioSignal expects {self.EXPECTED_SAMPLE_RATE} Hz, "
                f"got {data.sample_rate} Hz."
            )

        super().__init__(data)