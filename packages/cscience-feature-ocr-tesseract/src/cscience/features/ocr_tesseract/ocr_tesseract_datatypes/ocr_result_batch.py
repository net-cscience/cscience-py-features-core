from collections.abc import Mapping
from dataclasses import dataclass

from cscience.features.api import BatchBase
from .ocr_result_batch_data import OcrResultBatchData

from .ocr_tesseract_datatype import OcrTesseractDatatype
from .ocr_result import OcrResultData





class OcrResultBatch(OcrTesseractDatatype, BatchBase[OcrResultData]):
    """Batch of Tesseract OCR results."""

    def __init__(self, data: OcrResultBatchData) -> None:
        if not isinstance(data, OcrResultBatchData):
            raise TypeError(
                f"OcrResultBatch expects OcrResultBatchData, got {type(data).__name__}."
            )

        self._validate_batch_mapping(data.results)

        for key, result in data.results.items():
            if not isinstance(result, OcrResultData):
                raise TypeError(
                    f"OcrResultBatch expects OcrResultData values, "
                    f"got {type(result).__name__} at key {key}."
                )

        super().__init__(
            OcrResultBatchData(
                results=dict(data.results)
            )
        )

    def batch_size(self) -> int:
        """Return the number of OCR results."""
        return len(self.data().results)

    def ordered_keys(self) -> tuple[int, ...]:
        """Return source indices in canonical order."""
        return tuple(sorted(self.data().results.keys()))

    def ordered_values(self) -> tuple[OcrResultData, ...]:
        """Return OCR results in canonical source-index order."""
        return tuple(self.data().results[key] for key in self.ordered_keys())

    def ordered_items(self) -> tuple[tuple[int, OcrResultData], ...]:
        """Return indexed OCR results in canonical source-index order."""
        return tuple((key, self.data().results[key]) for key in self.ordered_keys())