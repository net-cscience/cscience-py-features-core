from abc import ABC

from cscience.features.api import DatatypeBase


class OcrTesseractDatatype(DatatypeBase, ABC):
    """Base class for Tesseract OCR-specific datatypes."""

    namespace = "ocr_tesseract"