from dataclasses import dataclass

from .ocr_result_data import OcrResultData
from .ocr_tesseract_datatype import OcrTesseractDatatype





class OcrResult(OcrTesseractDatatype):
    """Single Tesseract OCR result."""

    def __init__(self, data: OcrResultData) -> None:
        if not isinstance(data, OcrResultData):
            raise TypeError(
                f"OcrResult expects OcrResultData, got {type(data).__name__}."
            )

        if type(data.text) is not str:
            raise TypeError(
                f"OcrResultData.text expects str, got {type(data.text).__name__}."
            )

        super().__init__(data)