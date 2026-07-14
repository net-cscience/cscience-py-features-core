from collections.abc import Mapping

from cscience.features.api import BatchBase

from .ocr_result import OcrResult
from .ocr_result_batch_data import OcrResultBatchData
from .ocr_result_data import OcrResultData
from .ocr_tesseract_datatype import OcrTesseractDatatype


class OcrResultBatch(
    BatchBase[OcrResultData],
    OcrTesseractDatatype[OcrResultBatchData],
):
    """Batch of Tesseract OCR results."""

    def __init__(
        self,
        data: OcrResultBatchData,
    ) -> None:
        if not isinstance(data, OcrResultBatchData):
            raise TypeError(
                f"OcrResultBatch expects OcrResultBatchData, "
                f"got {type(data).__name__}."
            )

        self._validate_batch_mapping(data.results)

        for result in data.results.values():
            OcrResult.validate_data(result)

        normalized = OcrResultBatchData(
            results=dict(data.results),
        )

        super().__init__(normalized)

    def _batch_mapping(
        self,
    ) -> Mapping[int, OcrResultData]:
        """Return OCR results indexed by source image position."""
        return self.data().results