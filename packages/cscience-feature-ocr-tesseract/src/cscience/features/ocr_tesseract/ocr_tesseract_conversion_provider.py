from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    Text,
    TextBatch,
)

from .ocr_tesseract_datatypes.ocr_result import OcrResult
from .ocr_tesseract_datatypes.ocr_result_batch import OcrResultBatch


def ocr_result_passthrough(result: OcrResult) -> OcrResult:
    return result


def ocr_result_batch_passthrough(batch: OcrResultBatch) -> OcrResultBatch:
    return batch


def ocr_result_to_text(result: OcrResult) -> Text:
    return Text(result.data().text)


def ocr_result_batch_to_result(batch: OcrResultBatch) -> OcrResult:
    results = batch.data().results

    if len(results) != 1:
        raise ValueError(
            f"Cannot convert OcrResultBatch of size {len(results)} to OcrResult."
        )

    return OcrResult(next(iter(results.values())))


def ocr_result_batch_to_text(batch: OcrResultBatch) -> Text:
    results = batch.data().results

    if len(results) != 1:
        raise ValueError(
            f"Cannot convert OcrResultBatch of size {len(results)} to Text."
        )

    return Text(next(iter(results.values())).text)


def ocr_result_batch_to_text_batch(batch: OcrResultBatch) -> TextBatch:
    return TextBatch(
        {
            key: result.text
            for key, result in batch.data().results.items()
        }
    )


class OcrTesseractConversionProvider(ConversionProviderBase):
    """Registers conversions required by the Tesseract OCR feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[OcrResult, OcrResult](
                name="ocr_result_passthrough",
                source=self._feature,
                function=ocr_result_passthrough,
                input_type=OcrResult,
                output_type=OcrResult,
            ),
            Converter[OcrResultBatch, OcrResultBatch](
                name="ocr_result_batch_passthrough",
                source=self._feature,
                function=ocr_result_batch_passthrough,
                input_type=OcrResultBatch,
                output_type=OcrResultBatch,
            ),
            Converter[OcrResult, Text](
                name="ocr_result_to_text",
                source=self._feature,
                function=ocr_result_to_text,
                input_type=OcrResult,
                output_type=Text,
            ),
            Converter[OcrResultBatch, OcrResult](
                name="ocr_result_batch_to_result",
                source=self._feature,
                function=ocr_result_batch_to_result,
                input_type=OcrResultBatch,
                output_type=OcrResult,
            ),
            Converter[OcrResultBatch, Text](
                name="ocr_result_batch_to_text",
                source=self._feature,
                function=ocr_result_batch_to_text,
                input_type=OcrResultBatch,
                output_type=Text,
            ),
            Converter[OcrResultBatch, TextBatch](
                name="ocr_result_batch_to_text_batch",
                source=self._feature,
                function=ocr_result_batch_to_text_batch,
                input_type=OcrResultBatch,
                output_type=TextBatch,
            ),
        ]