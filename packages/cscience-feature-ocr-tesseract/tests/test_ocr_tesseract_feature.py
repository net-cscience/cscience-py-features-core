import unittest

import pytesseract
from PIL import Image, ImageDraw
from pytesseract import TesseractNotFoundError

from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.ocr_tesseract import OcrTesseractConnector
from cscience.features.ocr_tesseract.ocr_config import OcrConfig


def make_text_image(text: str) -> Image.Image:
    image = Image.new("RGB", (500, 120), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((30, 40), text, fill="black")
    return image

def tesseract_available() -> bool:
    try:
        pytesseract.get_tesseract_version()
        return True
    except TesseractNotFoundError:
        return False


class OcrTesseractFeatureTest(unittest.TestCase):

    def test_connector_initializes(self):
        connector = OcrTesseractConnector(OcrConfig())
        self.assertIsNotNone(connector)

    @unittest.skipUnless(
        tesseract_available(),
        "Tesseract executable is not installed or not on PATH.",
    )
    def test_extract_text_from_generated_image(self):
        image = make_text_image("Hello OCR")

        connector = OcrTesseractConnector(OcrConfig())
        text = connector.text(image)

        self.assertIn("Hello", text)
        self.assertIn("ocr", text)

    @unittest.skipUnless(
        tesseract_available(),
        "Tesseract executable is not installed or not on PATH.",
    )
    def test_extract_text_batch_preserves_indices(self):
        images = [
            make_text_image("first ocr"),
            make_text_image("second ocr"),
        ]

        connector = OcrTesseractConnector(OcrConfig())
        results = connector.text_batch(images)

        self.assertEqual(set(results.keys()), {0, 1})
        self.assertIn("first", results[0])
        self.assertIn("second", results[1])

