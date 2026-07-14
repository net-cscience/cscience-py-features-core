from .ocr_result_data import OcrResultData
from .ocr_tesseract_datatype import OcrTesseractDatatype


class OcrResult(
    OcrTesseractDatatype[OcrResultData],
):
    """Single Tesseract OCR result."""

    def __init__(self, data: OcrResultData) -> None:
        self.validate_data(data)
        super().__init__(data)

    @staticmethod
    def validate_data(data: OcrResultData) -> None:
        """Validate an OCR result data object."""
        if not isinstance(data, OcrResultData):
            raise TypeError(
                f"OcrResult expects OcrResultData, "
                f"got {type(data).__name__}."
            )

        if type(data.text) is not str:
            raise TypeError(
                f"OcrResultData.text expects str, "
                f"got {type(data.text).__name__}."
            )