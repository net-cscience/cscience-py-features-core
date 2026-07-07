import base64
from io import BytesIO
from urllib.parse import unquote

from PIL import Image

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.feature.feature_base import FeatureBase

from .ocr_tesseract_datatypes.image_bytes import ImageBytes
from .ocr_tesseract_datatypes.image_data_url import ImageDataUrl
from .ocr_tesseract_datatypes.ocr_image import OcrImage
from .ocr_tesseract_datatypes.ocr_result import OcrResult


def image_data_url_to_bytes(data_url: ImageDataUrl) -> ImageBytes:
    """Decode a base64 image data URL into raw bytes."""
    data = unquote(data_url.data())

    if not data or "base64," not in data:
        raise ValueError("Missing or invalid base64 image data.")

    _, encoded = data.split("base64,", 1)
    return ImageBytes(base64.b64decode(encoded))


def image_bytes_to_image(image_bytes: ImageBytes) -> OcrImage:
    """Decode image bytes into a Pillow image."""
    image = Image.open(BytesIO(image_bytes.data()))
    return OcrImage(image)


def ocr_result_to_text(result: OcrResult) -> Text:
    """Extract plain text from an OCR result."""
    return Text(result.data().text)


class OcrTesseractConversionProvider(ConversionProviderBase):
    """Registers conversions required by the Tesseract OCR feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter(
                name="image_data_url_to_bytes",
                source=self._feature,
                function=image_data_url_to_bytes,
                input_type=ImageDataUrl,
                output_type=ImageBytes,
            ),
            Converter(
                name="image_bytes_to_image",
                source=self._feature,
                function=image_bytes_to_image,
                input_type=ImageBytes,
                output_type=OcrImage,
            ),
            Converter(
                name="ocr_result_to_text",
                source=self._feature,
                function=ocr_result_to_text,
                input_type=OcrResult,
                output_type=Text,
            ),
        ]