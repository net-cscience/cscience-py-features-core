import pytesseract

from cscience.features.api import FeatureBase, PilImageBatch

from .ocr_tesseract_datatypes.ocr_result import OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
    OcrResultBatchData,
)


class OcrTesseractFeature(FeatureBase):
    """Tesseract OCR feature service."""

    def _initialize(self) -> None:
        if self._initialized:
            return

        # Runtime configuration is intentionally deferred.
        self._initialized = True

    @classmethod
    def extract_text_batch(cls, images: PilImageBatch) -> OcrResultBatch:
        """Extract text from a batch of images using Tesseract OCR."""
        cls.get_instance()

        results: dict[int, OcrResultData] = {}

        for key, image in images.ordered_items():
            text = pytesseract.image_to_string(image).strip()
            results[key] = OcrResultData(text=text)

        return OcrResultBatch(
            OcrResultBatchData(
                results=results,
            )
        )