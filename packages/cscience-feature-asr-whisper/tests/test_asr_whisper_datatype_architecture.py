import unittest

from cscience.features.api import (
    AudioBytesBase,
    DatatypeBase,
)
from cscience.features.api.datatypes.base.references.data_url_base import (
    DataUrlBase,
)

from cscience.features.asr_whisper.asr_whisper_datatypes.asr_whisper_datatype import (
    AsrWhisperDatatype,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.audio_bytes import (
    AudioBytes,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.audio_data_url import (
    AudioDataUrl,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.audio_signal import (
    AudioSignal,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
)


ASR_DATATYPES = (
    AudioBytes,
    AudioDataUrl,
    AudioSignal,
    WhisperTranscription,
)


class TestAsrWhisperDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_asr_namespace(self) -> None:
        for datatype_class in ASR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "asr_whisper",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in ASR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        AsrWhisperDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in ASR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_audio_bytes_validation_precedes_namespace(
        self,
    ) -> None:
        mro = AudioBytes.__mro__

        self.assertLess(
            mro.index(AudioBytesBase),
            mro.index(AsrWhisperDatatype),
        )

    def test_data_url_validation_precedes_namespace(
        self,
    ) -> None:
        mro = AudioDataUrl.__mro__

        self.assertLess(
            mro.index(DataUrlBase),
            mro.index(AsrWhisperDatatype),
        )


class TestAsrWhisperDatatypeConstruction(unittest.TestCase):
    def test_constructs_audio_bytes(self) -> None:
        audio = AudioBytes(b"encoded audio")

        self.assertEqual(audio.data(), b"encoded audio")

    def test_constructs_audio_data_url(self) -> None:
        data_url = AudioDataUrl(
            "data:audio/wav;base64,UklGRg=="
        )

        self.assertEqual(
            data_url.media_type(),
            "audio/wav",
        )
        self.assertTrue(data_url.is_base64())

    def test_rejects_non_audio_data_url(self) -> None:
        with self.assertRaises(ValueError):
            AudioDataUrl(
                "data:image/png;base64,aW1hZ2U="
            )

    def test_rejects_non_base64_audio_data_url(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AudioDataUrl(
                "data:audio/wav,raw-data"
            )