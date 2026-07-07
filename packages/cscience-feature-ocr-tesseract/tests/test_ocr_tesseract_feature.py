import unittest

from cscience.features.ocr_tesseract import OcrTesseractConnector


class OcrTesseractFeatureTest(unittest.TestCase):
    def test_connector_initializes(self):
        connector = OcrTesseractConnector()
        self.assertIsNotNone(connector)
