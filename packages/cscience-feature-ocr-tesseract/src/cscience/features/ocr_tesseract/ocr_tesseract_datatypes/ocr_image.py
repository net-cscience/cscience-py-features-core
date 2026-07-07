from PIL.ImageFile import ImageFile

from ..ocr_tesseract_datatype import OcrTesseractDatatype


class OcrImage(OcrTesseractDatatype):
    """Pillow-backed image for OCR."""

    def __init__(self, data: ImageFile) -> None:
        super().__init__(data)