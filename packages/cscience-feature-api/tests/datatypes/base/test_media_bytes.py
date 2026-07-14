import unittest

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class MockAudioBytes(
    AudioBytesBase,
    CoreDatatype[bytes],
):
    pass


class MockImageBytes(
    ImageBytesBase,
    CoreDatatype[bytes],
):
    pass


class TestMediaBytesBase(unittest.TestCase):
    def test_stores_media_bytes(self) -> None:
        media = MockAudioBytes(b"encoded audio")

        self.assertEqual(
            media.data(),
            b"encoded audio",
        )

    def test_rejects_empty_bytes(self) -> None:
        with self.assertRaises(ValueError):
            MockAudioBytes(b"")

    def test_rejects_string(self) -> None:
        with self.assertRaises(TypeError):
            MockAudioBytes(
                "encoded audio",  # type: ignore[arg-type]
            )

    def test_rejects_bytearray(self) -> None:
        with self.assertRaises(TypeError):
            MockAudioBytes(
                bytearray(b"encoded audio"),  # type: ignore[arg-type]
            )

    def test_audio_media_type(self) -> None:
        self.assertEqual(
            MockAudioBytes.media_type,
            "audio",
        )

    def test_image_media_type(self) -> None:
        self.assertEqual(
            MockImageBytes.media_type,
            "image",
        )

    def test_audio_bytes_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockAudioBytes.__mro__.count(DatatypeBase),
            1,
        )

    def test_image_bytes_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockImageBytes.__mro__.count(DatatypeBase),
            1,
        )

class TestMediaBaseArchitecture(unittest.TestCase):
    def test_media_bytes_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                MediaBytesBase,
                DatatypeBase,
            )
        )

    def test_audio_bytes_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                AudioBytesBase,
                DatatypeBase,
            )
        )

    def test_image_bytes_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                ImageBytesBase,
                DatatypeBase,
            )
        )
