from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class OcrTesseractDatatype(DatatypeBase, ABC):
    """Base class for Tesseract OCR-specific datatypes."""

    namespace = "ocr_tesseract"