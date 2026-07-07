from ..ocr_tesseract_datatype import OcrTesseractDatatype


class ImageDataUrl(OcrTesseractDatatype):
    """Base64-encoded image data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)