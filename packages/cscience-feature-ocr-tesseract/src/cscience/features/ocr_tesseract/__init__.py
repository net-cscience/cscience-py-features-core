from cscience.features.api import RegistryBase

from .ocr_tesseract_connector import OcrTesseractConnector
from .ocr_tesseract_conversion_provider import OcrTesseractConversionProvider
from .ocr_tesseract_datatypes.ocr_tesseract_datatype import OcrTesseractDatatype
from .ocr_tesseract_feature import OcrTesseractFeature
from .ocr_tesseract_datatypes.ocr_result import OcrResult
from .ocr_tesseract_datatypes.ocr_result_data import OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import OcrResultBatch
from .ocr_tesseract_datatypes.ocr_result_batch_data import OcrResultBatchData


__all__ = [
    "OcrTesseractConnector",
    "OcrTesseractConversionProvider",
    "OcrTesseractDatatype",
    "OcrTesseractFeature",
    "OcrResult",
    "OcrResultData",
    "OcrResultBatch",
    "OcrResultBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("ocr_tesseract", OcrTesseractConversionProvider)