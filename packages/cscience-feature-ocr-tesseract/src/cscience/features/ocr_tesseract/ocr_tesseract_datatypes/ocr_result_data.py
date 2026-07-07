from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OcrResultData:
    """Structured OCR result for one image."""

    text: str