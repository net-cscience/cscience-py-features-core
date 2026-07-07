from ..ocr_tesseract_datatype import OcrTesseractDatatype


class ImageBytes(OcrTesseractDatatype):
    """Raw encoded image bytes."""

    def __init__(self, data: bytes) -> None:
        super().__init__(data)