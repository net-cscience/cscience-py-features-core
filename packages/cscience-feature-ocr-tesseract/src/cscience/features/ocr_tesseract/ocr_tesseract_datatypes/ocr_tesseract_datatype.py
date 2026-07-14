from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class OcrTesseractDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for Tesseract OCR-specific datatypes."""

    namespace = "ocr_tesseract"