import unittest

from cscience.features.api.datatypes.image.image_data_url import (
    ImageDataUrl,
)
from cscience.features.api.datatypes.references.data_url import (
    DataUrl,
)


class TestImageDataUrl(unittest.TestCase):
    def test_accepts_base64_image_data_url(self) -> None:
        data_url = ImageDataUrl(
            "data:image/png;base64,aW1hZ2U="
        )

        self.assertEqual(
            data_url.media_type(),
            "image/png",
        )
        self.assertTrue(data_url.is_base64())

    def test_is_data_url(self) -> None:
        self.assertTrue(
            issubclass(ImageDataUrl, DataUrl)
        )

    def test_rejects_non_image_media_type(self) -> None:
        with self.assertRaises(ValueError):
            ImageDataUrl(
                "data:text/plain;base64,aGVsbG8="
            )

    def test_rejects_non_base64_image_data_url(self) -> None:
        with self.assertRaises(ValueError):
            ImageDataUrl(
                "data:image/png,raw-data"
            )