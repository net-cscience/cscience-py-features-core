import pytesseract

from cscience.features.api import FeatureBase, PilImageBatch, FeatureInfo
from .ocr_config import OcrConfig

from .ocr_tesseract_datatypes.ocr_result import OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
    OcrResultBatchData,
)

class OcrTesseractFeature(FeatureBase):
    """Tesseract OCR feature service."""

    def _initialize(self, config:OcrConfig) -> None:
        # Runtime configuration is intentionally deferred to the first call to extract_text_batch, since Tesseract does not require any model loading or initialization.
        self._config = config
        self._initialized = True


    def extract_text_batch(self, images: PilImageBatch) -> OcrResultBatch:
        """Extract text from a batch of images using Tesseract OCR."""

        results: dict[int, OcrResultData] = {}

        for key, image in images.ordered_items():
            text = pytesseract.image_to_string(image).strip()
            results[key] = OcrResultData(text=text)

        return OcrResultBatch(
            OcrResultBatchData(
                results=results,
            )
        )

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name="pytesseract",
            device=str("cpu"),
            configuration=self._config.model_dump(mode="json"),
        )