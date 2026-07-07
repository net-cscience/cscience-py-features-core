from cscience.features.api.registry.registry_base import RegistryBase

from .ocr_tesseract_connector import OcrTesseractConnector
from .ocr_tesseract_conversion_provider import OcrTesseractConversionProvider
from .ocr_tesseract_feature import OcrTesseractFeature

__all__ = [
    "OcrTesseractConnector",
    "OcrTesseractConversionProvider",
    "OcrTesseractFeature",
]


def register(registry: RegistryBase) -> None:
    registry.register("ocr_tesseract", OcrTesseractConversionProvider)
