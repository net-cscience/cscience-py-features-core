import unittest

import numpy as np

from cscience.features.api.datatypes.audio.audio_signal import (
    AudioSignal,
)
from cscience.features.api.datatypes.audio.audio_signal_data import (
    AudioSignalData,
)


class TestAudioSignal(unittest.TestCase):
    def test_accepts_mono_signal(self) -> None:
        data = AudioSignalData(
            waveform=np.array(
                [0.0, 0.5, -0.5],
                dtype=np.float32,
            ),
            sample_rate=16_000,
        )

        signal = AudioSignal(data)

        self.assertIs(signal.data(), data)

    def test_accepts_two_dimensional_signal(self) -> None:
        data = AudioSignalData(
            waveform=np.zeros(
                (2, 100),
                dtype=np.float32,
            ),
            sample_rate=16_000,
        )

        signal = AudioSignal(data)

        self.assertIs(signal.data(), data)

    def test_rejects_empty_waveform(self) -> None:
        data = AudioSignalData(
            waveform=np.array([], dtype=np.float32),
            sample_rate=16_000,
        )

        with self.assertRaises(ValueError):
            AudioSignal(data)

    def test_rejects_non_numeric_waveform(self) -> None:
        data = AudioSignalData(
            waveform=np.array(["a", "b"]),
            sample_rate=16_000,
        )

        with self.assertRaises(TypeError):
            AudioSignal(data)

    def test_rejects_invalid_dimensions(self) -> None:
        data = AudioSignalData(
            waveform=np.zeros(
                (1, 2, 3),
                dtype=np.float32,
            ),
            sample_rate=16_000,
        )

        with self.assertRaises(ValueError):
            AudioSignal(data)

    def test_rejects_non_positive_sample_rate(self) -> None:
        data = AudioSignalData(
            waveform=np.array(
                [0.0],
                dtype=np.float32,
            ),
            sample_rate=0,
        )

        with self.assertRaises(ValueError):
            AudioSignal(data)