from dataclasses import dataclass

from ..ocr_tesseract_datatype import OcrTesseractDatatype


@dataclass(frozen=True, slots=True)
class OcrResultData:
    """Structured OCR result."""

    text: str


class OcrResult(OcrTesseractDatatype):
    """Tesseract OCR output."""

    def __init__(self, data: OcrResultData) -> None:
        super().__init__(data)