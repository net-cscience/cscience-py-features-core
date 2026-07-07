from PIL.Image import Image

from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
    Text,
    TextBatch,
)

from .ocr_tesseract_conversion_provider import OcrTesseractConversionProvider
from .ocr_tesseract_datatypes.ocr_result import OcrResult, OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import OcrResultBatch
from .ocr_tesseract_feature import OcrTesseractFeature


class OcrTesseractConnector(ConnectorBase):
    """Public connector for Tesseract OCR."""

    def __init__(self) -> None:
        self.feature = OcrTesseractFeature.get_instance()
        super().__init__("ocr_tesseract", OcrTesseractConversionProvider(self.feature))

    def extract(self, image: Image) -> OcrResultData:
        """Extract a structured OCR result from one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=OcrResult,
        )

        return function(PilImage(image)).data()

    def extract_batch(self, images: list[Image]) -> dict[int, OcrResultData]:
        """Extract structured OCR results from images."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=OcrResultBatch,
        )

        return function(image_batch).data().results

    def text(self, image: Image) -> str:
        """Extract plain text from one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=Text,
        )

        return function(PilImage(image)).data()

    def text_batch(self, images: list[Image]) -> dict[int, str]:
        """Extract plain text from images."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=TextBatch,
        )

        return function(image_batch).data()

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")