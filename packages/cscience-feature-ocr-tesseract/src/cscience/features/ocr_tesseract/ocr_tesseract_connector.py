from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from .ocr_tesseract_conversion_provider import OcrTesseractConversionProvider
from .ocr_tesseract_feature import OcrTesseractFeature


class OcrTesseractConnector(ConnectorBase):
    """Public connector for the ocr_tesseract feature."""

    def __init__(self) -> None:
        self.feature = OcrTesseractFeature.get_instance()
        super().__init__("ocr_tesseract", OcrTesseractConversionProvider(self.feature))

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")
