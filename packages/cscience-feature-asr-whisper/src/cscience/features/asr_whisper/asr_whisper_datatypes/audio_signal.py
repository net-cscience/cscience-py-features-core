import numpy as np

from .asr_whisper_datatype import AsrWhisperDatatype
from .audio_signal_data import AudioSignalData


class AudioSignal(
    AsrWhisperDatatype[AudioSignalData],
):
    """Whisper-ready mono float32 audio signal at 16 kHz."""

    EXPECTED_SAMPLE_RATE = 16_000

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

        if waveform.ndim != 1:
            raise ValueError(
                "AudioSignal expects a mono 1D waveform, "
                f"got shape {waveform.shape}."
            )

        if waveform.size == 0:
            raise ValueError(
                "AudioSignal waveform cannot be empty."
            )

        if waveform.dtype != np.float32:
            raise TypeError(
                "AudioSignal expects a float32 waveform, "
                f"got {waveform.dtype}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, "
                f"got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate != self.EXPECTED_SAMPLE_RATE:
            raise ValueError(
                f"AudioSignal expects {self.EXPECTED_SAMPLE_RATE} Hz, "
                f"got {data.sample_rate} Hz."
            )

        super().__init__(data)