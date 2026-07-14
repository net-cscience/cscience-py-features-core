import base64
from io import BytesIO
from typing import List
from urllib.parse import unquote

from PIL import Image as PillowImage

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.image.image_bytes import ImageBytes
from cscience.features.api.datatypes.image.image_data_url import ImageDataUrl
from cscience.features.api.datatypes.image.pil_image import PilImage
from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.primitives_scalar.bool_value import BoolValue
from cscience.features.api.datatypes.primitives_scalar.float_value import FloatValue
from cscience.features.api.datatypes.primitives_scalar.int_value import IntValue
from cscience.features.api.datatypes.primitives_vectors.bool_vector import BoolVector
from cscience.features.api.datatypes.primitives_vectors_batch.bool_vector_batch import BoolVectorBatch
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.primitives_vectors.int_vector import IntVector
from cscience.features.api.datatypes.primitives_vectors_batch.int_vector_batch import IntVectorBatch
from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase


# ---------------------------------------------------------------------------
# Text conversions
# ---------------------------------------------------------------------------

def text_passthrough(text: Text) -> Text:
    return text


def text_to_text_batch(text: Text) -> TextBatch:
    return TextBatch({0: text.data()})


def text_batch_passthrough(batch: TextBatch) -> TextBatch:
    return batch


# ---------------------------------------------------------------------------
# Scalar primitive conversions
# ---------------------------------------------------------------------------

def bool_value_passthrough(value: BoolValue) -> BoolValue:
    return value


def int_value_passthrough(value: IntValue) -> IntValue:
    return value


def float_value_passthrough(value: FloatValue) -> FloatValue:
    return value


def bool_value_to_int_value(value: BoolValue) -> IntValue:
    return IntValue(1 if value.data() else 0)


def bool_value_to_float_value(value: BoolValue) -> FloatValue:
    return FloatValue(1.0 if value.data() else 0.0)


def int_value_to_float_value(value: IntValue) -> FloatValue:
    return FloatValue(float(value.data()))


# ---------------------------------------------------------------------------
# Primitive vector conversions
# ---------------------------------------------------------------------------

def bool_vector_passthrough(vector: BoolVector) -> BoolVector:
    return vector


def int_vector_passthrough(vector: IntVector) -> IntVector:
    return vector


def float_vector_passthrough(vector: FloatVector) -> FloatVector:
    return vector


def bool_vector_to_bool_vector_batch(vector: BoolVector) -> BoolVectorBatch:
    return BoolVectorBatch({0: vector.data()})


def int_vector_to_int_vector_batch(vector: IntVector) -> IntVectorBatch:
    return IntVectorBatch({0: vector.data()})


def float_vector_to_float_vector_batch(vector: FloatVector) -> FloatVectorBatch:
    return FloatVectorBatch({0: vector.data()})


def bool_vector_to_int_vector(vector: BoolVector) -> IntVector:
    return IntVector([1 if value else 0 for value in vector.data()])


def bool_vector_to_float_vector(vector: BoolVector) -> FloatVector:
    return FloatVector([1.0 if value else 0.0 for value in vector.data()])


def int_vector_to_float_vector(vector: IntVector) -> FloatVector:
    return FloatVector([float(value) for value in vector.data()])


# ---------------------------------------------------------------------------
# Primitive vector batch conversions
# ---------------------------------------------------------------------------

def bool_vector_batch_passthrough(batch: BoolVectorBatch) -> BoolVectorBatch:
    return batch


def int_vector_batch_passthrough(batch: IntVectorBatch) -> IntVectorBatch:
    return batch


def float_vector_batch_passthrough(batch: FloatVectorBatch) -> FloatVectorBatch:
    return batch


def bool_vector_batch_to_int_vector_batch(batch: BoolVectorBatch) -> IntVectorBatch:
    return IntVectorBatch(
        {
            key: [1 if value else 0 for value in vector]
            for key, vector in batch.data().items()
        }
    )


def bool_vector_batch_to_float_vector_batch(batch: BoolVectorBatch) -> FloatVectorBatch:
    return FloatVectorBatch(
        {
            key: [1.0 if value else 0.0 for value in vector]
            for key, vector in batch.data().items()
        }
    )


def int_vector_batch_to_float_vector_batch(batch: IntVectorBatch) -> FloatVectorBatch:
    return FloatVectorBatch(
        {
            key: [float(value) for value in vector]
            for key, vector in batch.data().items()
        }
    )


# ---------------------------------------------------------------------------
# Image conversions
# ---------------------------------------------------------------------------

def image_data_url_passthrough(data_url: ImageDataUrl) -> ImageDataUrl:
    return data_url


def image_bytes_passthrough(image_bytes: ImageBytes) -> ImageBytes:
    return image_bytes


def pil_image_passthrough(image: PilImage) -> PilImage:
    return image


def pil_image_batch_passthrough(batch: PilImageBatch) -> PilImageBatch:
    return batch


def image_data_url_to_image_bytes(data_url: ImageDataUrl) -> ImageBytes:
    data = unquote(data_url.data())

    if "base64," not in data:
        raise ValueError("Missing or invalid base64 image data URL.")

    header, encoded = data.split("base64,", 1)

    if header and not header.startswith("data:image/"):
        raise ValueError(f"Expected image data URL, got header: {header}")

    return ImageBytes(base64.b64decode(encoded, validate=True))


def image_bytes_to_pil_image(image_bytes: ImageBytes) -> PilImage:
    image = PillowImage.open(BytesIO(image_bytes.data()))
    image.load()
    return PilImage(image)


def pil_image_to_pil_image_batch(image: PilImage) -> PilImageBatch:
    return PilImageBatch({0: image.data()})


class CoreConversionProvider(ConversionProviderBase):
    """Registers feature-independent core conversions."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        return [
            # -----------------------------------------------------------------
            # Text
            # -----------------------------------------------------------------
            Converter[Text, Text](
                name="text_passthrough",
                source=self._feature,
                function=text_passthrough,
                input_type=Text,
                output_type=Text,
            ),
            Converter[Text, TextBatch](
                name="text_to_text_batch",
                source=self._feature,
                function=text_to_text_batch,
                input_type=Text,
                output_type=TextBatch,
            ),
            Converter[TextBatch, TextBatch](
                name="text_batch_passthrough",
                source=self._feature,
                function=text_batch_passthrough,
                input_type=TextBatch,
                output_type=TextBatch,
            ),

            # -----------------------------------------------------------------
            # Scalar primitives
            # -----------------------------------------------------------------
            Converter[BoolValue, BoolValue](
                name="bool_value_passthrough",
                source=self._feature,
                function=bool_value_passthrough,
                input_type=BoolValue,
                output_type=BoolValue,
            ),
            Converter[IntValue, IntValue](
                name="int_value_passthrough",
                source=self._feature,
                function=int_value_passthrough,
                input_type=IntValue,
                output_type=IntValue,
            ),
            Converter[FloatValue, FloatValue](
                name="float_value_passthrough",
                source=self._feature,
                function=float_value_passthrough,
                input_type=FloatValue,
                output_type=FloatValue,
            ),
            Converter[BoolValue, IntValue](
                name="bool_value_to_int_value",
                source=self._feature,
                function=bool_value_to_int_value,
                input_type=BoolValue,
                output_type=IntValue,
            ),
            Converter[BoolValue, FloatValue](
                name="bool_value_to_float_value",
                source=self._feature,
                function=bool_value_to_float_value,
                input_type=BoolValue,
                output_type=FloatValue,
            ),
            Converter[IntValue, FloatValue](
                name="int_value_to_float_value",
                source=self._feature,
                function=int_value_to_float_value,
                input_type=IntValue,
                output_type=FloatValue,
            ),

            # -----------------------------------------------------------------
            # Primitive vectors
            # -----------------------------------------------------------------
            Converter[BoolVector, BoolVector](
                name="bool_vector_passthrough",
                source=self._feature,
                function=bool_vector_passthrough,
                input_type=BoolVector,
                output_type=BoolVector,
            ),
            Converter[IntVector, IntVector](
                name="int_vector_passthrough",
                source=self._feature,
                function=int_vector_passthrough,
                input_type=IntVector,
                output_type=IntVector,
            ),
            Converter[FloatVector, FloatVector](
                name="float_vector_passthrough",
                source=self._feature,
                function=float_vector_passthrough,
                input_type=FloatVector,
                output_type=FloatVector,
            ),
            Converter[BoolVector, BoolVectorBatch](
                name="bool_vector_to_bool_vector_batch",
                source=self._feature,
                function=bool_vector_to_bool_vector_batch,
                input_type=BoolVector,
                output_type=BoolVectorBatch,
            ),
            Converter[IntVector, IntVectorBatch](
                name="int_vector_to_int_vector_batch",
                source=self._feature,
                function=int_vector_to_int_vector_batch,
                input_type=IntVector,
                output_type=IntVectorBatch,
            ),
            Converter[FloatVector, FloatVectorBatch](
                name="float_vector_to_float_vector_batch",
                source=self._feature,
                function=float_vector_to_float_vector_batch,
                input_type=FloatVector,
                output_type=FloatVectorBatch,
            ),
            Converter[BoolVector, IntVector](
                name="bool_vector_to_int_vector",
                source=self._feature,
                function=bool_vector_to_int_vector,
                input_type=BoolVector,
                output_type=IntVector,
            ),
            Converter[BoolVector, FloatVector](
                name="bool_vector_to_float_vector",
                source=self._feature,
                function=bool_vector_to_float_vector,
                input_type=BoolVector,
                output_type=FloatVector,
            ),
            Converter[IntVector, FloatVector](
                name="int_vector_to_float_vector",
                source=self._feature,
                function=int_vector_to_float_vector,
                input_type=IntVector,
                output_type=FloatVector,
            ),

            # -----------------------------------------------------------------
            # Primitive vector batches
            # -----------------------------------------------------------------
            Converter[BoolVectorBatch, BoolVectorBatch](
                name="bool_vector_batch_passthrough",
                source=self._feature,
                function=bool_vector_batch_passthrough,
                input_type=BoolVectorBatch,
                output_type=BoolVectorBatch,
            ),
            Converter[IntVectorBatch, IntVectorBatch](
                name="int_vector_batch_passthrough",
                source=self._feature,
                function=int_vector_batch_passthrough,
                input_type=IntVectorBatch,
                output_type=IntVectorBatch,
            ),
            Converter[FloatVectorBatch, FloatVectorBatch](
                name="float_vector_batch_passthrough",
                source=self._feature,
                function=float_vector_batch_passthrough,
                input_type=FloatVectorBatch,
                output_type=FloatVectorBatch,
            ),
            Converter[BoolVectorBatch, IntVectorBatch](
                name="bool_vector_batch_to_int_vector_batch",
                source=self._feature,
                function=bool_vector_batch_to_int_vector_batch,
                input_type=BoolVectorBatch,
                output_type=IntVectorBatch,
            ),
            Converter[BoolVectorBatch, FloatVectorBatch](
                name="bool_vector_batch_to_float_vector_batch",
                source=self._feature,
                function=bool_vector_batch_to_float_vector_batch,
                input_type=BoolVectorBatch,
                output_type=FloatVectorBatch,
            ),
            Converter[IntVectorBatch, FloatVectorBatch](
                name="int_vector_batch_to_float_vector_batch",
                source=self._feature,
                function=int_vector_batch_to_float_vector_batch,
                input_type=IntVectorBatch,
                output_type=FloatVectorBatch,
            ),

            # -----------------------------------------------------------------
            # Images
            # -----------------------------------------------------------------
            Converter[ImageDataUrl, ImageDataUrl](
                name="image_data_url_passthrough",
                source=self._feature,
                function=image_data_url_passthrough,
                input_type=ImageDataUrl,
                output_type=ImageDataUrl,
            ),
            Converter[ImageBytes, ImageBytes](
                name="image_bytes_passthrough",
                source=self._feature,
                function=image_bytes_passthrough,
                input_type=ImageBytes,
                output_type=ImageBytes,
            ),
            Converter[PilImage, PilImage](
                name="pil_image_passthrough",
                source=self._feature,
                function=pil_image_passthrough,
                input_type=PilImage,
                output_type=PilImage,
            ),
            Converter[PilImageBatch, PilImageBatch](
                name="pil_image_batch_passthrough",
                source=self._feature,
                function=pil_image_batch_passthrough,
                input_type=PilImageBatch,
                output_type=PilImageBatch,
            ),
            Converter[ImageDataUrl, ImageBytes](
                name="image_data_url_to_image_bytes",
                source=self._feature,
                function=image_data_url_to_image_bytes,
                input_type=ImageDataUrl,
                output_type=ImageBytes,
            ),
            Converter[ImageBytes, PilImage](
                name="image_bytes_to_pil_image",
                source=self._feature,
                function=image_bytes_to_pil_image,
                input_type=ImageBytes,
                output_type=PilImage,
            ),
            Converter[PilImage, PilImageBatch](
                name="pil_image_to_pil_image_batch",
                source=self._feature,
                function=pil_image_to_pil_image_batch,
                input_type=PilImage,
                output_type=PilImageBatch,
            ),
        ]