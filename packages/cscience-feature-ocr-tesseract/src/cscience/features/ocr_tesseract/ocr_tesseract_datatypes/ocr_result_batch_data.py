from dataclasses import dataclass

from .ocr_result_data import OcrResultData


@dataclass(frozen=True, slots=True)
class OcrResultBatchData:
    """OCR results indexed by source image position."""

    results: dict[int, OcrResultData]