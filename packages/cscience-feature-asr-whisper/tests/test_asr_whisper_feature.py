import io
import unittest
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from cscience.features.asr_whisper import AsrWhisperConnector
from cscience.features.asr_whisper import AudioBytes
from cscience.features.asr_whisper.asr_config import AsrConfig
from cscience.features.asr_whisper.asr_whisper_conversion_provider import (
    audio_bytes_to_audio_signal,
)


def make_test_wav_bytes(sample_rate: int = 8_000) -> bytes:
    duration = 0.25
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.1 * np.sin(2 * np.pi * 440 * t)

    buffer = io.BytesIO()
    sf.write(buffer, waveform, sample_rate, format="WAV")
    return buffer.getvalue()

@dataclass
class Fixture:
    id: str
    audio_bytes: bytes
    contains: list[str]


FICTURE_DIR = Path(__file__).parent / "fixtures"
class AsrWhispernTest(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        AsrConfig.set_default_config_directory(FICTURE_DIR / "config")

    def setUp(self):

        AsrConfig.set_default_config_directory(FICTURE_DIR / "config")
        fixture_dir = FICTURE_DIR / "ljspeech"

        self.fixtures :list[Fixture] = [
            Fixture( "LJ001-0001.wav", (fixture_dir / "LJ001-0001.wav").read_bytes(), ["printing", "arts"]),
            Fixture( "LJ001-0002.wav", (fixture_dir / "LJ001-0002.wav").read_bytes(), ["modern", "comparatively"]),
        ]



    def test_connector_initializes(self):

        connector = AsrWhisperConnector(AsrConfig())
        self.assertIsNotNone(connector)

    def test_audio_bytes_to_audio_signal_resamples_to_16khz(self):
        audio_bytes = make_test_wav_bytes(sample_rate=8_000)

        signal = audio_bytes_to_audio_signal(AudioBytes(audio_bytes))

        self.assertEqual(signal.data().sample_rate, 16_000)
        self.assertEqual(signal.data().waveform.ndim, 1)
        self.assertEqual(signal.data().waveform.dtype, np.float32)

    def test_transcribes_local_speech_file(self):
        for fixture in self.fixtures:
            audio_bytes = fixture.audio_bytes
            expected_keywords = fixture.contains
            text = AsrWhisperConnector(AsrConfig()).audio_bytes(audio_bytes)
            for keyword in expected_keywords:
                self.assertIn(keyword, text.lower(), f"Expected keyword '{keyword}' not found in transcription '{text}' for fixture '{fixture.id}'")
