# Exported code on 2026-07-08 21:00:24.273634 with root dir packages
# From packages\cscience-feature-ocr-tesseract\tests\test_ocr_tesseract_feature.py
import unittest

import pytesseract
from PIL import Image, ImageDraw
from pytesseract import TesseractNotFoundError

from cscience.features.ocr_tesseract import OcrTesseractConnector


def make_text_image(text: str) -> Image.Image:
    image = Image.new("RGB", (500, 120), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((30, 40), text, fill="black")
    return image

def tesseract_available() -> bool:
    try:
        pytesseract.get_tesseract_version()
        return True
    except TesseractNotFoundError:
        return False


class OcrTesseractFeatureTest(unittest.TestCase):

    def test_connector_initializes(self):
        connector = OcrTesseractConnector()
        self.assertIsNotNone(connector)

    @unittest.skipUnless(
        tesseract_available(),
        "Tesseract executable is not installed or not on PATH.",
    )
    def test_extract_text_from_generated_image(self):
        image = make_text_image("Hello OCR")

        connector = OcrTesseractConnector()
        text = connector.text(image)

        self.assertIn("Hello", text)
        self.assertIn("OCR", text)

    @unittest.skipUnless(
        tesseract_available(),
        "Tesseract executable is not installed or not on PATH.",
    )
    def test_extract_text_batch_preserves_indices(self):
        images = [
            make_text_image("First OCR"),
            make_text_image("Second OCR"),
        ]

        connector = OcrTesseractConnector()
        results = connector.text_batch(images)

        self.assertEqual(set(results.keys()), {0, 1})
        self.assertIn("First", results[0])
        self.assertIn("Second", results[1])

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_connector.py
from PIL.Image import Image

from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
    Text,
    TextBatch,
)

from .ocr_tesseract_conversion_provider import OcrTesseractConversionProvider
from .ocr_tesseract_datatypes.ocr_result import OcrResult, OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import OcrResultBatch
from .ocr_tesseract_feature import OcrTesseractFeature


class OcrTesseractConnector(ConnectorBase):
    """Public connector for Tesseract OCR."""

    def __init__(self) -> None:
        self.feature = OcrTesseractFeature.get_instance()
        super().__init__("ocr_tesseract", OcrTesseractConversionProvider(self.feature))

    def extract(self, image: Image) -> OcrResultData:
        """Extract a structured OCR result from one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=OcrResult,
        )

        return function(PilImage(image)).data()

    def extract_batch(self, images: list[Image]) -> dict[int, OcrResultData]:
        """Extract structured OCR results from images."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=OcrResultBatch,
        )

        return function(image_batch).data().results

    def text(self, image: Image) -> str:
        """Extract plain text from one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=Text,
        )

        return function(PilImage(image)).data()

    def text_batch(self, images: list[Image]) -> dict[int, str]:
        """Extract plain text from images."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=TextBatch,
        )

        return function(image_batch).data()

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_conversion_provider.py
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

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_feature.py
import pytesseract

from cscience.features.api import FeatureBase, PilImageBatch

from .ocr_tesseract_datatypes.ocr_result import OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
    OcrResultBatchData,
)


class OcrTesseractFeature(FeatureBase):
    """Tesseract OCR feature service."""

    def _initialize(self) -> None:
        if self._initialized:
            return

        # Runtime configuration is intentionally deferred.
        self._initialized = True

    @classmethod
    def extract_text_batch(cls, images: PilImageBatch) -> OcrResultBatch:
        """Extract text from a batch of images using Tesseract OCR."""
        cls.get_instance()

        results: dict[int, OcrResultData] = {}

        for key, image in images.ordered_items():
            text = pytesseract.image_to_string(image).strip()
            results[key] = OcrResultData(text=text)

        return OcrResultBatch(
            OcrResultBatchData(
                results=results,
            )
        )

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\__init__.py
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

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result.py
from dataclasses import dataclass

from .ocr_result_data import OcrResultData
from .ocr_tesseract_datatype import OcrTesseractDatatype





class OcrResult(OcrTesseractDatatype):
    """Single Tesseract OCR result."""

    def __init__(self, data: OcrResultData) -> None:
        if not isinstance(data, OcrResultData):
            raise TypeError(
                f"OcrResult expects OcrResultData, got {type(data).__name__}."
            )

        if type(data.text) is not str:
            raise TypeError(
                f"OcrResultData.text expects str, got {type(data.text).__name__}."
            )

        super().__init__(data)

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result_batch.py
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

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result_batch_data.py
from dataclasses import dataclass

from .ocr_result_data import OcrResultData


@dataclass(frozen=True, slots=True)
class OcrResultBatchData:
    """OCR results indexed by source image position."""

    results: dict[int, OcrResultData]

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result_data.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OcrResultData:
    """Structured OCR result for one image."""

    text: str

# From packages\cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_tesseract_datatype.py
from abc import ABC

from cscience.features.api import DatatypeBase


class OcrTesseractDatatype(DatatypeBase, ABC):
    """Base class for Tesseract OCR-specific datatypes."""

    namespace = "ocr_tesseract"

# From packages\cscience-feature-nsfw-image\tests\nsfw_image_visual_test.py
import base64
import os
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from cscience.features.nsfw_image import NsfwImageConnector


def load_base64_image(path: Path) -> Image.Image:
    encoded = path.read_text(encoding="utf-8").strip()
    image_bytes = base64.b64decode(encoded, validate=True)
    return Image.open(BytesIO(image_bytes)).convert("RGB")


class NsfwImageVisualTest(unittest.TestCase):

    def test_mild_nudity_image_is_detected(self):
        image = load_base64_image(
            Path(__file__).parent / "fixtures" / "mild_nudity_image_base64.txt"
        )

        prediction = NsfwImageConnector().classify(image)

        self.assertGreater(
            prediction.nsfw_score,
            0.5,
            msg=f"Expected NSFW score > 0.5, got {prediction}",
        )

    def test_sfw_image_is_not_detected(self):
        image = load_base64_image(
            Path(__file__).parent / "fixtures" / "sfw_image_base64.txt"
        )

        prediction = NsfwImageConnector().classify(image)

        self.assertLess(
            prediction.nsfw_score,
            0.5,
            msg=f"Expected NSFW score < 0.5, got {prediction}",
        )

# From packages\cscience-feature-nsfw-image\tests\test_nsfw_image_feature.py
import unittest
from pathlib import Path

from PIL import Image

from cscience.features.api.utils.measure_time import measure_time
from cscience.features.nsfw_image import NsfwImageConnector


class NsfwImageFeatureTest(unittest.TestCase):

    N = 10

    def test_connector_initializes(self):
        connector = NsfwImageConnector()
        self.assertIsNotNone(connector)

    @measure_time(times=N, ignore_first=True)
    def test_classify_simple_image(self):
        image = Image.new("RGB", (224, 224), color=(255, 255, 255))

        connector = NsfwImageConnector()
        prediction = connector.classify(image)

        self.assertIn(prediction.label, {"normal", "nsfw"})
        self.assertGreaterEqual(prediction.score, 0.0)
        self.assertLessEqual(prediction.score, 1.0)
        self.assertGreaterEqual(prediction.normal_score, 0.0)
        self.assertLessEqual(prediction.normal_score, 1.0)
        self.assertGreaterEqual(prediction.nsfw_score, 0.0)
        self.assertLessEqual(prediction.nsfw_score, 1.0)

    @measure_time(times=N, ignore_first=True)
    def test_classify_batch_preserves_indices(self):
        images = {
            0: Image.new("RGB", (224, 224), color=(255, 255, 255)),
            3: Image.new("RGB", (224, 224), color=(0, 0, 0)),
        }

        connector = NsfwImageConnector()
        predictions = connector.classify_batch(list(images.values()))

        self.assertEqual(set(predictions.keys()), {0, 1})




# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_connector.py
from PIL.Image import Image

from cscience.features.api import (
    BoolValue,
    ConnectorBase,
    FeatureInfo,
    FloatValue,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
)

from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction, NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import NsfwPredictionBatch
from .nsfw_image_feature import NsfwImageFeature


class NsfwImageConnector(ConnectorBase):
    """Public connector for NSFW image classification."""

    def __init__(self) -> None:
        self.feature = NsfwImageFeature.get_instance()
        super().__init__("nsfw_image", NsfwImageConversionProvider(self.feature))

    def classify(self, image: Image) -> NsfwPredictionData:
        """Classify a single image and return the full prediction."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=NsfwPrediction,
        )

        return function(PilImage(image)).data()

    def classify_batch(self, images: list[Image]) -> dict[int, NsfwPredictionData]:
        """Classify images and return predictions indexed by input position."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=NsfwPredictionBatch,
        )

        return function(image_batch).data().predictions

    def score(self, image: Image) -> float:
        """Return the NSFW score for a single image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=FloatValue,
        )

        return function(PilImage(image)).data()

    def is_nsfw(self, image: Image, threshold: float = 0.5) -> bool:
        """Return whether a single image is classified as NSFW."""
        prediction = self.classify(image)
        return prediction.is_nsfw(threshold)

    def is_nsfw_default(self, image: Image) -> bool:
        """Return whether a single image is NSFW using the converter default threshold."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=BoolValue,
        )

        return function(PilImage(image)).data()

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")

# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_conversion_provider.py
from cscience.features.api import (
    BoolValue,
    ConversionProviderBase,
    Converter,
    FeatureBase,
    FloatValue,
)

from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction
from .nsfw_image_datatypes.nsfw_prediction_batch import NsfwPredictionBatch


def nsfw_prediction_passthrough(prediction: NsfwPrediction) -> NsfwPrediction:
    return prediction


def nsfw_prediction_batch_passthrough(batch: NsfwPredictionBatch) -> NsfwPredictionBatch:
    return batch


def nsfw_prediction_batch_to_prediction(batch: NsfwPredictionBatch) -> NsfwPrediction:
    predictions = batch.data().predictions

    if len(predictions) != 1:
        raise ValueError(
            f"Cannot convert NsfwPredictionBatch of size {len(predictions)} "
            f"to NsfwPrediction."
        )

    prediction = next(iter(predictions.values()))
    return NsfwPrediction(prediction)


def nsfw_prediction_to_float_value(prediction: NsfwPrediction) -> FloatValue:
    return FloatValue(prediction.data().nsfw_score)


def nsfw_prediction_to_bool_value(prediction: NsfwPrediction) -> BoolValue:
    return BoolValue(prediction.data().is_nsfw())


class NsfwImageConversionProvider(ConversionProviderBase):
    """Registers conversions required by the NSFW image feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[NsfwPrediction, NsfwPrediction](
                name="nsfw_prediction_passthrough",
                source=self._feature,
                function=nsfw_prediction_passthrough,
                input_type=NsfwPrediction,
                output_type=NsfwPrediction,
            ),
            Converter[NsfwPredictionBatch, NsfwPredictionBatch](
                name="nsfw_prediction_batch_passthrough",
                source=self._feature,
                function=nsfw_prediction_batch_passthrough,
                input_type=NsfwPredictionBatch,
                output_type=NsfwPredictionBatch,
            ),
            Converter[NsfwPredictionBatch, NsfwPrediction](
                name="nsfw_prediction_batch_to_prediction",
                source=self._feature,
                function=nsfw_prediction_batch_to_prediction,
                input_type=NsfwPredictionBatch,
                output_type=NsfwPrediction,
            ),
            Converter[NsfwPrediction, FloatValue](
                name="nsfw_prediction_to_float_value",
                source=self._feature,
                function=nsfw_prediction_to_float_value,
                input_type=NsfwPrediction,
                output_type=FloatValue,
            ),
            Converter[NsfwPrediction, BoolValue](
                name="nsfw_prediction_to_bool_value",
                source=self._feature,
                function=nsfw_prediction_to_bool_value,
                input_type=NsfwPrediction,
                output_type=BoolValue,
            ),
        ]

# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_feature.py
from __future__ import annotations

import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

from cscience.features.api import FeatureBase, PilImageBatch

from .nsfw_image_datatypes.nsfw_prediction import NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
    NsfwPredictionBatchData,
)


class NsfwImageFeature(FeatureBase):
    """NSFW image-classification feature backed by Falconsai/nsfw_image_detection."""

    MODEL_NAME = "Falconsai/nsfw_image_detection"

    def _initialize(self) -> None:
        if self._initialized:
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.processor = AutoImageProcessor.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForImageClassification.from_pretrained(self.MODEL_NAME)
        self.model = self.model.to(self.device).eval()

        self._initialized = True

    @classmethod
    @torch.inference_mode()
    def classify_batch(cls, images: PilImageBatch) -> NsfwPredictionBatch:
        """Classify a batch of images as normal or NSFW."""
        service = cls.get_instance()

        keys = images.ordered_keys()
        image_values = list(images.ordered_values())

        inputs = service.processor(
            images=image_values,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(service.device)
            for key, value in inputs.items()
        }

        outputs = service.model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1).detach().cpu()

        id_to_label = service.model.config.id2label
        predictions: dict[int, NsfwPredictionData] = {}

        for source_key, row in zip(keys, probabilities):
            label_scores = {
                id_to_label[class_index].lower(): float(score)
                for class_index, score in enumerate(row)
            }

            if "normal" not in label_scores or "nsfw" not in label_scores:
                raise ValueError(
                    f"Expected model labels 'normal' and 'nsfw', got {label_scores.keys()}."
                )

            predicted_index = int(row.argmax().item())
            predicted_label = id_to_label[predicted_index].lower()
            predicted_score = float(row[predicted_index].item())

            predictions[source_key] = NsfwPredictionData(
                label=predicted_label,
                score=predicted_score,
                normal_score=label_scores["normal"],
                nsfw_score=label_scores["nsfw"],
            )

        return NsfwPredictionBatch(
            NsfwPredictionBatchData(
                predictions=predictions,
            )
        )

# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\__init__.py
from cscience.features.api import RegistryBase

from .nsfw_image_connector import NsfwImageConnector
from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_datatypes.nsfw_image_datatype import NsfwImageDatatype
from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction, NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
    NsfwPredictionBatchData,
)
from .nsfw_image_feature import NsfwImageFeature

__all__ = [
    "NsfwImageConnector",
    "NsfwImageConversionProvider",
    "NsfwImageDatatype",
    "NsfwImageFeature",
    "NsfwPrediction",
    "NsfwPredictionData",
    "NsfwPredictionBatch",
    "NsfwPredictionBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("nsfw_image", NsfwImageConversionProvider)

# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_image_datatype.py
from abc import ABC

from cscience.features.api import DatatypeBase


class NsfwImageDatatype(DatatypeBase, ABC):
    """Base class for NSFW image feature-specific datatypes."""

    namespace = "nsfw_image"

# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_prediction.py
from dataclasses import dataclass

from cscience.features.api import FloatValue

from ..nsfw_image_datatypes.nsfw_image_datatype import NsfwImageDatatype


@dataclass(frozen=True, slots=True)
class NsfwPredictionData:
    """NSFW classification result for one image."""

    label: str
    score: float
    normal_score: float
    nsfw_score: float

    def is_nsfw(self, threshold: float = 0.5) -> bool:
        """Return whether the NSFW score is at or above the threshold."""
        return self.nsfw_score >= threshold


class NsfwPrediction(NsfwImageDatatype):
    """Single NSFW classification result."""

    def __init__(self, data: NsfwPredictionData) -> None:
        if type(data.label) is not str:
            raise TypeError(f"NsfwPrediction label expects str, got {type(data.label).__name__}.")

        if type(data.score) is not float:
            raise TypeError(f"NsfwPrediction score expects float, got {type(data.score).__name__}.")

        if type(data.normal_score) is not float:
            raise TypeError(
                f"NsfwPrediction normal_score expects float, got {type(data.normal_score).__name__}."
            )

        if type(data.nsfw_score) is not float:
            raise TypeError(
                f"NsfwPrediction nsfw_score expects float, got {type(data.nsfw_score).__name__}."
            )

        if not 0.0 <= data.score <= 1.0:
            raise ValueError(f"NsfwPrediction score must be in [0, 1], got {data.score}.")

        if not 0.0 <= data.normal_score <= 1.0:
            raise ValueError(
                f"NsfwPrediction normal_score must be in [0, 1], got {data.normal_score}."
            )

        if not 0.0 <= data.nsfw_score <= 1.0:
            raise ValueError(
                f"NsfwPrediction nsfw_score must be in [0, 1], got {data.nsfw_score}."
            )

        super().__init__(data)

    def nsfw_score(self) -> FloatValue:
        """Return the NSFW score as a core float value."""
        return FloatValue(self.data().nsfw_score)

# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_prediction_batch.py
from collections.abc import Mapping
from dataclasses import dataclass

from cscience.features.api import BatchBase
from .nsfw_prediction_batch_data import NsfwPredictionBatchData

from ..nsfw_image_datatypes.nsfw_image_datatype import NsfwImageDatatype
from .nsfw_prediction import NsfwPredictionData



class NsfwPredictionBatch(NsfwImageDatatype, BatchBase[NsfwPredictionData]):
    """Batch of NSFW classification results."""

    def __init__(self, data: NsfwPredictionBatchData) -> None:
        self._validate_batch_mapping(data.predictions)

        for key, prediction in data.predictions.items():
            if not isinstance(prediction, NsfwPredictionData):
                raise TypeError(
                    f"NsfwPredictionBatch expects NsfwPredictionData values, "
                    f"got {type(prediction).__name__} at key {key}."
                )

        super().__init__(
            NsfwPredictionBatchData(
                predictions=dict(data.predictions)
            )
        )

    def batch_size(self) -> int:
        """Return the number of predictions."""
        return len(self.data().predictions)

# From packages\cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_prediction_batch_data.py
from dataclasses import dataclass

from ..nsfw_image_datatypes.nsfw_prediction import NsfwPredictionData


@dataclass(frozen=True, slots=True)
class NsfwPredictionBatchData:
    """NSFW predictions indexed by source image position."""

    predictions: dict[int, NsfwPredictionData]

# From packages\cscience-feature-clip-spatial\tests\ClipMaskedInformationClusterTest.py
import argparse

import numpy as np
import torch
from PIL import Image
from matplotlib import pyplot as plt

from descriptors.clip_influence.ClipMaskedInformationInfluence import MaskingMode, ClipMaskedInformationCluster, \
    tensor_to_pil, show_overlay_any


def main(args):
    # Load and preprocess image
    kwargs = {
        "geometry_size": (1 / 3, 1 / 3),  # relative to image size
        "step_size": (1 / 3, 1 / 3),  # relative to image size
        "start_point": (1 / 6, 1 / 6),  # pixel offset relative to image size
        "steps": (3, 3),  # number of steps in h,w (1, 1) means one tile
        "mode": MaskingMode.KEEP_ONLY
    }
    cmi = ClipMaskedInformationCluster(**kwargs)

    iterations = zip(args.image_paths, args.labels)
    idx = 0
    for image_path, label in iterations:
        idx += 1
        img = Image.open(image_path).convert("RGB")
        scores, point_hard, point_soft, generator = cmi.imageTextPair(img, label)
        deltas_np = scores.cpu().numpy()
        max_index = np.argmax(deltas_np)
        # batch_img_f_masked[max_index] = 0.0  # zero-out most influential region
        # deltas = influence_calculator(img_f_base, batch_img_f_masked, txt_f,mode)
        # deltas = deltas
        image_weights = [5, 3]
        img_out = tensor_to_pil((image_weights[0]*generator.batch_img_tensor[max_index]+image_weights[1]*generator.base_img_tensor)/sum(image_weights), cmi.clip_service.preprocessor)
        show_overlay_any(img_out, scores, generator, alpha=0.5, label=label, idx=idx)
        show_overlay_any(img_out, scores, generator, alpha=0.5, label=label, title=False, idx=idx)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")

    p.add_argument("--image-paths", type=str, nargs="+",
                   default=[
                       "../../Resources/26caffb8-4062-45c2-b7c1-4b801527374a.webp",
                       "../../Resources/a38e4012-a690-49f8-aaef-b3789a39ed98.webp",
                       "../../Resources/cornflakes.webp",
                       "../../Resources/cornflakes.webp",
                       "../../Resources/kitchen2.webp",
                       "../../Resources/kitchen2.webp",
                       "../../Resources/sample1.jpg",
                       "../../Resources/sample1.jpg",
                       "../../Resources/sample1.jpg",
                       "../../Resources/astronaut.png",
                       "../../Resources/astronaut.png",
                       "../../Resources/catdog.png",
                       "../../Resources/catdog.png",
                       "../../Resources/dogbird.png",
                       "../../Resources/dogbird.png",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                   ])

    p.add_argument("--labels", type=str, nargs="+",
                   default=[
                       "a silver kettle",
                       "a golden teapot",
                       "cornflakes on a table",
                       "a tea kettle on a cooking stove",
                       "a fridge with drawings",
                       "a tea kettle on a cooking stove",
                       "photo of a dog",
                       "a golden dog",
                       "a cat on the couch",
                       "an astronaut with an orange suit",
                       "a space shuttle model in background",
                       "a cat and a dog",
                       "a dog",
                       "a bird",
                       "a dog",
                       "a wheelchair",
                       "a plant beside a golden vase",
                       "photos on a wall",
                       "ceramics on the floor",
                       "a red carped on the floor",
                   ])

    main(p.parse_args())


# From packages\cscience-feature-clip-spatial\tests\test_clip_spatial.py


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatiall_config.py
from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class ClipConfig(ConfigBase):


    @classmethod
    def _namespace(cls):
        return "clip"

    model_name:str = Field(
        default="xlm-roberta-base-ViT-B-32",
        description="The name of the CLIP model to use. Default is 'xlm-roberta-base-ViT-B-32'."
    )

    pretrained:str = Field(
        default="laion5b_s13b_b90k",
        description="The name of the pretrained model to use. Default is 'laion5b_s13b_b90k'."
    )
    device:str = Field(
        default="cpu",
        description="The device to use for inference. Default is 'cpu'."
    )


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_connector.py
from PIL.ImageFile import ImageFile


from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.conversion import conversion_provider_base
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from cscience.features.clip_spatial import ClipSpatialFeature


class ClipConnector(ConnectorBase):
    """Public connector for CLIP text and image embeddings."""
    def __init__(self,) -> None:
        self.feature = ClipSpatialFeature().get_instance()
        super().__init__("clip", ClipSpatialConversionProvider(self.feature))

    def text(self, data: str) -> list[float]:
        """Embed a single text string and return one float vector."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=ClipImage,
            input_feature_type=,
            output_feature_type=ClipTensorBatch,
            output_type= FloatVector)
        return function(Text(data)).data()

    def text_batch(self, data: list[str]) -> dict[int,list[float]]:
        """Embed text strings and return vectors indexed by input position."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=TextBatch,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensorBatch,
            output_type= FloatVectorBatch)
        return function(TextBatch(data)).data()

    def image(self, data: ImageFile) -> list[float]:
        """Embed a single image and return one float vector."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_batch,
            input_type=ClipImage,
            input_feature_type=ClipSpatialImage,
            output_feature_type=ClipSpatialTensor,
            output_type=FloatVectorBatch)
        return function(ClipImage(data)).data()

    def image_batch(self, data: list[ImageFile]) -> dict[int, list[float]]:
        """Embed images and return vectors indexed by input position."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_batch,
            input_type=ClipImageBatch,
            input_feature_type=ClipImageBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVectorBatch)
        return function(ClipImageBatch(data)).data()


    def get_service_info(self) -> ServiceInfo:
        pass


    def get_feature_info(self) -> FeatureInfo:
        pass


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_conversion_provider.py
from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_image_batch import ClipImageBatch
from cscience.features.clip.clip_datatypes.clip_tensor_batch import ClipTensorBatch


class ClipSpatialConversionProvider(ConversionProviderBase):
    """Registers datatype conversions required by the CLIP connector."""
    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        """Return CLIP-specific input and output converters."""
        converters = [
            Converter[ClipImage, ClipImageBatch]
                (
                name="image_to_image_batch",
                source=self._feature,
                function=lambda x: ClipImageBatch([x.data()]),
                input_type=ClipImage,
                output_type=ClipImageBatch
            ),
            Converter[ClipImageBatch, ClipImageBatch]
                (
                name="image_batch_passtrough",
                source=self._feature,
                function=lambda x: x,
                input_type=ClipImageBatch,
                output_type=ClipImageBatch
            ),
            Converter[ClipTensorBatch, FloatVector]
                (
                name="tensor_batch_to_float_vector",
                source=self._feature,
                function=lambda x: FloatVector(x.data()[0].tolist()),
                input_type=ClipTensorBatch,
                output_type=FloatVector
            ),
            Converter[ClipTensorBatch, FloatVectorBatch]
                (
                name="tensor_batch_to_float_vector_batch",
                source=self._feature,
                function=lambda x: FloatVectorBatch(
                    {
                        i: vector
                        for i, vector in enumerate(x.data().tolist())
                    }
                ),
                input_type=ClipTensorBatch,
                output_type=FloatVectorBatch
            ),
        ]
        return converters


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_datatype.py
from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class ClipDatatype(DatatypeBase, ABC):
    namespace = "clip_spatial"

# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature.py

from __future__ import annotations


import open_clip
import torch
import torch.nn.functional as F

from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase




class ClipSpatialFeature(FeatureBase):
    """CLIP feature service backed by OpenCLIP.

    Loads the model, tokenizer, preprocessing pipeline, and target device once.
    Public methods operate on CLIP-specific datatype wrappers.
    """

    def _initialize(self) -> None:
        if self._initialized:
            return
        self._model_name = "xlm-roberta-base-ViT-B-32"
        self._pretrained = "laion5b_s13b_b90k"

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name = self._model_name,
            pretrained= self._pretrained,
        )
        self.model = self.model.to(self._device).eval()
        self.tokenizer = open_clip.get_tokenizer(self._model_name)
        self._initialized = True


    @classmethod
    @torch.no_grad()
    def score(cls, left: ClipSpatialTensor, right: ClipSpatialTensor):
        left = F.normalize(left, dim=-1)
        right = F.normalize(right, dim=-1)
        # scalar score per image (assuming one prompt)
        return (left @ right.T).squeeze(-1)

    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_img_vectors(cls, img_tensor_batch: torch.Tensor):
        # img_batch: [B,3,224,224] in preprocessed space
        img_f = cls.model.encode_image(img_tensor_batch)
        img_f = F.normalize(img_f, dim=-1)
        return img_f

    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_img(self, img: Image):
        img_tensor = self.preprocess(img)
        img_f = self.clip_embedd_norm_img_vectors(img_tensor)  # [1,D]
        return img_f


    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_txt_vectors(self, text_tokens: torch.Tensor):
        txt_f = self._model.encode_text(text_tokens)
        txt_f = F.normalize(txt_f, dim=-1)
        return txt_f


    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_txt(self, text: str):
        text_tokens = self.tokenize(text)
        txt_f = self.clip_embedd_norm_txt_vectors(text_tokens)
        return txt_f

    @classmethod
    def influence_calculator(self, img_f_base, img_f_masked, txt_f, mode: MaskingMode, clamp_positive=True, normalize=True):
        if mode == MaskingMode.MASK_OUT:
            return self.influence_calculator_similarity_decrease(img_f_base, img_f_masked, txt_f, clamp_positive, normalize)
        elif mode == MaskingMode.KEEP_ONLY:
            return self.influence_calculator_keep_similarity(img_f_base, img_f_masked, txt_f, normalize)
        else:
            raise ValueError(f"Unknown MaskingMode: {mode}")

    @classmethod

    @torch.no_grad()
    def influence_calculator_similarity_decrease(self, img_f_base, img_f_masked, txt_f, clamp_positive=True,
                                                 normalize=True):
        base = self.clip_score(img_f_base, txt_f)  # [1]
        scores = self.clip_score(img_f_masked, txt_f)  # [B]
        deltas = base - scores  # [B] broadcast

        if clamp_positive:
            deltas = deltas.clamp(min=0.0)

        if normalize:
            d = deltas - deltas.min()
            deltas = d / (d.max() + 1e-8)

        return deltas

    @classmethod

    @torch.no_grad()
    def influence_calculator_keep_similarity(self, img_f_base, img_f_masked, txt_f, normalize=True):
        scores = self.clip_score(img_f_masked, txt_f)  # [B]
        deltas = scores  # [B] broadcast

        if normalize:
            d = deltas - deltas.min()
            deltas = d / (d.max() + 1e-8)

        return deltas

# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\__init__.py
## API

## Internal
from .clip_spatial_datatype import ClipDatatype
from .clip_spatial_connector import ClipConnector
from .clip_spatial_feature import ClipSpatialFeature



__all__ = [
    "ClipDatatype",
    "ClipConnector",
    "ClipConversionProvider",
    "ClipSpatialFeature",
]

def register(registry: RegistryBase) -> None:
        registry.register("clip", ClipConversionProvider)

# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\ClipMaskedInformationCluster.py
import numpy as np
import torch
from PIL import Image
from fractions import Fraction

from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import  MaskingGenerator
from .OpenClipScoringService import OpenClipScoringService
from cscience.features.clip_spatial.clip_spatial_feature.Geometry.SquareProvider import SquareProvider
from cscience.features.clip_spatial.clip_spatial_feature.Filter.ZeroProvider import ZeroProvider
from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingMode import  MaskingMode
from .visualization_util import taget_point_hard, taget_point_soft

class ClipMaskedInformationCluster:

    def __init__(self, **kwargs):
        self.clip_service = OpenClipScoringService()
        self.geometry_size = kwargs.get("geometry_size", (Fraction(1 / 3).limit_denominator(),Fraction(1 / 3).limit_denominator()))  # relative to image size
        self.step_size = kwargs.get("step_size", (Fraction(1 / 3).limit_denominator(), Fraction(1 / 3).limit_denominator()))  # relative to image size
        self.start_point = kwargs.get("start_point", (Fraction(1 / 6).limit_denominator(), Fraction(1 / 6).limit_denominator()))  # pixel offset relative to image size
        self.steps = kwargs.get("steps", (3, 3))  # number of steps in h,w
        self.mode = kwargs.get("mode", MaskingMode.KEEP_ONLY)
        self.geometry = SquareProvider(geometry_size=self.geometry_size)
        self.filters = ZeroProvider()
        self.settings = {
            "geometry_size": self.geometry_size,
            "step_size": self.step_size,
            "start_point": self.start_point,
            "tiling": self.steps,
            "length": self.steps[0] * self.steps[1],
            "mode": self.mode,
            "geometry": type(self.geometry).__name__,
            "filter": type(self.filters).__name__,
            "clip_service": type(self.clip_service).__name__
        }

    def embedd_text(self, text: str):
        text_tokens = self.clip_service.tokenize(text)
        txt_f = self.clip_service.clip_embedd_norm_txt_vectors(text_tokens)
        return txt_f

    def imageTextPair(self, image: Image, text: str):
        text_tokens = self.clip_service.tokenize(text)
        txt_f = self.clip_service.clip_embedd_norm_txt_vectors(text_tokens)
        img_f_base, batch_img_f_masked, generator = self.imageVectors(image)
        scores, point_hard, point_soft = self.imageTextVectorPair(img_f_base, batch_img_f_masked, txt_f,
                                                                  generator.image_w, generator.image_h)
        return scores, point_hard, point_soft, generator

    def imageTextPair_response(self, image: Image, text: str):
        scores, point_hard, point_soft, generator = self.imageTextPair(image, text)
        response = {
            "settings": self.settings,
            "processed_image_w": generator.image_w,
            "processed_image_h": generator.image_h,
            "scores": scores.detach().cpu().numpy().tolist(),
            "best_idx": int(torch.argmax(scores).item()),
            "point_hard": point_hard,
            "point_soft": point_soft,
        }
        return response

    def imageVectors(self, image: Image):
        base_img_tensor = self.clip_service.preprocess(image)  # [1,3,224,224]$

        generator = MaskingGenerator(self.step_size, self.start_point, self.steps, base_img_tensor, self.geometry,
                                     self.filters, device=self.clip_service.device, mode=self.mode)
        base_img_tensor, batch_img_tensor = generator.factory()
        img_f_base = self.clip_service.clip_embedd_norm_img_vectors(base_img_tensor)
        batch_img_f_masked = self.clip_service.clip_embedd_norm_img_vectors(batch_img_tensor)
        return img_f_base, batch_img_f_masked, generator

    def imageVectors_response(self, image: Image):
        img_f_base, batch_img_f_masked, generator = self.imageVectors(image)
        batch = batch_img_f_masked.detach().cpu().numpy().tolist()
        numberedBatch_img_f_masked =  [{"position": f"batch_img_f_masked_{generator[i].get_xy_tile_coordinates()}", "idx": i, "img_f":b}  for (b, i) in zip(batch, range(len(batch)))]
        response = {
            "settings": self.settings,
            "processed_image_w": generator.image_w,
            "processed_image_h": generator.image_h,
            "img_f_base": img_f_base.detach().cpu().numpy().tolist(),
            "batch_img_f_masked": numberedBatch_img_f_masked
        }

        return response

    def imageTextVectorPair(self,
                            img_f_base: torch.Tensor,
                            batch_img_f_masked: torch.Tensor,
                            txt_f: torch.Tensor,
                            processed_image_w,
                            processed_image_h):
        scores = self.clip_service.influence_calculator(img_f_base, batch_img_f_masked, txt_f, self.mode,
                                                        normalize=False)
        max_idx = np.argmax(scores.detach().cpu().numpy())
        dummy_image_tensor = torch.zeros((1, 3, processed_image_h, processed_image_w), device=self.clip_service.device)
        dummy_generator = MaskingGenerator(self.step_size, self.start_point, self.steps, dummy_image_tensor,
                                           self.geometry,
                                           self.filters, device=self.clip_service.device, mode=self.mode)
        point_hard = taget_point_hard(scores, dummy_generator)
        point_soft = taget_point_soft(scores, dummy_generator)
        return scores, point_hard, point_soft

    def imageTextVectorPair_response(self,
                                     img_f_base: torch.Tensor,
                                     batch_img_f_masked: torch.Tensor,
                                     txt_f: torch.Tensor,
                                     processed_image_w,
                                     processed_image_h):
        scores, point_hard, point_soft = self.imageTextVectorPair(img_f_base, batch_img_f_masked, txt_f, processed_image_w, processed_image_h)
        response = {
            "settings": self.settings,
            "processed_image_w": processed_image_w,
            "processed_image_h": processed_image_h,
            "scores": scores.detach().cpu().numpy().tolist(),
            "best_idx": int(torch.argmax(scores).item()),
            "point_hard": point_hard,
            "point_soft": point_soft,
        }
        return response


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\visualization_util.py
import numpy as np
import torch
from PIL import Image
from matplotlib import pyplot as plt
import seaborn as sns
import torch.nn.functional as F
from matplotlib.axis import Axis

from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator

font_scale = 1.0
rc = {
    "grid.linestyle": "solid",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.35,
    "axes.edgecolor": "black",
    "axes.linewidth": 0.8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "font.family": "serif",
    "font.serif": [
        "Computer Modern Roman",
        "CMU Serif",
        "Latin Modern Roman",
        "DejaVu Serif",
    ],
    "mathtext.fontset": "cm",
    "text.usetex": True,
    "font.size": 11.0 * font_scale,
    "axes.titlesize": 13.0 * font_scale,
    "axes.labelsize": 12.0 * font_scale,
    "xtick.labelsize": 11.0 * font_scale,
    "ytick.labelsize": 11.0 * font_scale,
    "legend.fontsize": 10.5 * font_scale,
    "figure.titlesize": 13.0 * font_scale,
    "axes.titlepad": 10.0,
    "axes.labelpad": 6.0,
    "legend.frameon": False,
}
sns.set_theme(style="ticks", context="paper", rc=rc)

def taget_point_hard(scores: torch.Tensor,  generator: MaskingGenerator) -> tuple[int, int]:
    _, best_idx = torch.max(scores, dim=0)
    generator.idx = int(best_idx.item())
    cx, cy = generator.get_xy_pixel_point()
    return cx, cy

def taget_point_soft(scores: torch.Tensor, generator: MaskingGenerator) -> tuple[int, int]:
    xs, ys = [], []
    w = torch.softmax(F.normalize(scores, dim=-1) / 0.05, dim=0)
    for g in generator:
        x, y = g.get_xy_pixel_point()
        xs.append(x)
        ys.append(y)

    xs = torch.tensor(xs, device=w.device, dtype=torch.float32)
    ys = torch.tensor(ys, device=w.device, dtype=torch.float32)

    cx = int(float((w * xs).sum().item()))
    cy = int(float((w * ys).sum().item()))
    return cx, cy


def show_overlay_any(image_pil_or_np, scores: torch.Tensor, generator: MaskingGenerator, alpha=0.45, label=None,  title=True, idx = None):
    if hasattr(image_pil_or_np, "convert"):
        img = np.array(image_pil_or_np.convert("RGB")).astype(np.float32) / 255.0
    else:
        img = image_pil_or_np.astype(np.float32)

    scores_cpu = scores.detach().float().cpu()  # <-- key fix

    H, W = generator.image_h, generator.image_w
    scores_tensor = torch.zeros((1, H, W), dtype=torch.float32)



    fig, ax = plt.subplots()



    for g in generator:  # resets idx internally
        val = float(scores_cpu[g.idx].item())
        g.geometry_fnc(scores_tensor)[:, :] = val

        px, py = g.get_xy_pixel_point()
        ax.text(px, py, f"${val:.2f}$\n${g.get_xy_tile_coordinates()}$", ha="center", va="center", color="w")

    ax.imshow(img)
    #ax.imshow(scores_tensor[0].numpy(), alpha=alpha, cmap="magma", interpolation="nearest")

    xh, yh = taget_point_hard(scores, generator)
    pal = sns.color_palette("Spectral", n_colors=10)
    ax.plot(xh, yh, "X", markersize=13, color=pal[9])
    xs, ys = taget_point_soft(scores, generator)
    ax.plot(xs, ys, "D", markersize=10, color=pal[7])

    ax.axis("off")
    if title and label is not None :
        ax.set_title(label)
    fig.tight_layout()
    # As pdf
    if idx is not None:
        label = f"{idx}-{str.replace(label, " ", "_")}"
    else:
        label = label if label else "overlay"

    fig.savefig(f"overlays/{label if title else f'{label}_noTitle'}.png", format="png", bbox_inches="tight", dpi=300)
    plt.show()


def tensor_to_pil(x, preprocess):
    """
    x: torch tensor [3,H,W] or [1,3,H,W] in *preprocessed* (normalized) space.
    preprocess: the transform returned by open_clip.create_model_and_transforms(...)
    Returns: PIL.Image in RGB, matching the tensor's spatial view (usually 224x224).
    """
    if x.ndim == 4:
        x = x[0]
    assert x.ndim == 3 and x.shape[0] == 3

    # Find torchvision.transforms.Normalize inside preprocess
    mean = std = None
    if hasattr(preprocess, "transforms"):
        for tr in preprocess.transforms:
            if tr.__class__.__name__ == "Normalize":
                mean = torch.tensor(tr.mean).view(3, 1, 1)
                std = torch.tensor(tr.std).view(3, 1, 1)
                break

    if mean is None or std is None:
        raise RuntimeError("Could not find Normalize(mean,std) inside preprocess.transforms")

    x = x.detach().cpu()
    x = x * std + mean  # unnormalize
    x = x.clamp(0.0, 1.0)  # valid image range
    x = (x.permute(1, 2, 0).numpy() * 255).astype(np.uint8)  # HWC uint8
    return Image.fromarray(x, mode="RGB")



# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\Filter\FilterProvider.py
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator as MaskingGenerator

class FilterProvider(ABC):

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def filter_fnc(self, generator: "MaskingGenerator"):
        pass


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\Filter\MeanFilterProvider.py
from typing import TYPE_CHECKING

import torch

from cscience.features.clip_spatial.clip_spatial_feature.Filter.FilterProvider import FilterProvider

if TYPE_CHECKING:
    from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator as MaskingGenerator

class MeanFilterProvider(FilterProvider):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.variance = kwargs.get("variance", 0.5)

    def filter_fnc(self, generator: "MaskingGenerator") -> torch.Tensor:
        window :torch.Tensor = generator.geometry_fnc(generator.base_img_tensor[0])
        return window + (self.variance**0.5) * torch.randn(window.size()).to(generator.device)


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\Filter\ZeroProvider.py
from typing import TYPE_CHECKING

from cscience.features.clip_spatial.clip_spatial_feature.Filter.FilterProvider import FilterProvider

if TYPE_CHECKING:
    from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator as MaskingGenerator

class ZeroProvider(FilterProvider):


    def __init__(self, **kwargs):
        pass


    def filter_fnc(self, generator: "MaskingGenerator") -> float:
        return 0.0



# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\Geometry\GeometryProvider.py
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

import torch

if TYPE_CHECKING:
    from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator


class GeometryProvider(ABC):

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def geometry_fnc(self, generator: "MaskingGenerator", batch_img_tensor: torch.Tensor) -> torch.Tensor:
        pass


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\Geometry\SquareProvider.py
from typing import TYPE_CHECKING

import torch

from cscience.features.clip_spatial.clip_spatial_feature.Geometry.GeometryProvider import GeometryProvider

if TYPE_CHECKING:
    from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator


class SquareProvider(GeometryProvider):
    def __init__(self, **kwargs):
        self.geometry_size = kwargs["geometry_size"]  # (h_rel, w_rel)

    def geometry_fnc(self, generator: "MaskingGenerator", batch_img_tensor: torch.Tensor) -> torch.Tensor:
        # batch_img_tensor is [C,H,W] in your usage (a single image)
        cx, cy = generator.get_xy_pixel_point()

        # fixed pixel window sizes
        win_w = max(1, round(self.geometry_size[1] * generator.image_w))
        win_h = max(1, round(self.geometry_size[0] * generator.image_h))

        # top-left from center (use half sizes)
        x0 = cx - win_w // 2
        y0 = cy - win_h // 2

        # clamp so window stays inside image while keeping size (when possible)
        x0 = max(0, min(generator.image_w - win_w, x0))
        y0 = max(0, min(generator.image_h - win_h, y0))

        x1 = x0 + win_w
        y1 = y0 + win_h

        return batch_img_tensor[:, y0:y1, x0:x1]


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\Masking\MaskingGenerator.py
import torch

from .MaskingMode import MaskingMode


class MaskingGenerator:
    def __init__(self, step_size, start_point, steps, base_img_tensor,
                 geometry, filter, device,
                 mode: MaskingMode = MaskingMode.MASK_OUT):

        self.base_img_tensor = base_img_tensor
        self.device = device

        self.geometry_fnc = lambda x: geometry.geometry_fnc(self, x)
        self.filter_fnc = lambda: filter.filter_fnc(self)

        self.step_size = step_size
        self.start_point = start_point
        self.steps = steps
        self.mode = mode

        _, _, self.image_h, self.image_w = base_img_tensor.shape


        self.batch_img_tensor = self.__initialize_batch(base_img_tensor)


    def __getitem__(self, idx):
        if idx < 0 or idx >= self.__len__():
            raise IndexError("Index out of range")
        self.idx = idx
        return self

    def __iter__(self):
        self.idx = -1
        return self

    def __next__(self):
        if self.idx + 1 >= self.__len__():
            raise StopIteration
        self.idx += 1
        return self

    def __len__(self):
        return self.steps[0] * self.steps[1]

    def __initialize_batch(self, base_img_tensor) -> torch.Tensor:
        B = self.__len__()
        if self.mode == MaskingMode.MASK_OUT:
            # start from the full image for every sample
            return base_img_tensor.repeat(B, 1, 1, 1)

        elif self.mode == MaskingMode.KEEP_ONLY:
            # start from a fully-masked canvas
            template = torch.zeros_like(base_img_tensor)

            for x in self:
                x.geometry_fnc(template[0])[:, :, :] = x.filter_fnc()

            batch =  template.repeat(B, 1, 1, 1)
            return batch

        else:
            raise ValueError(f"Unknown masking mode: {self.mode}")

    def get_xy_tile_coordinates(self) -> tuple[int, int]:
        y, x = divmod(self.idx, self.steps[1])
        return x, y

    def get_current_batch(self) -> torch.Tensor:
        return self.batch_img_tensor[self.idx]

    def get_xy_tile_length(self) -> tuple[int, int]:
        return self.steps[1], self.steps[0]

    def get_xy_pixel_point(self) -> tuple[int, int]:
        tile_x, tile_y = self.get_xy_tile_coordinates()

        point_x = round((self.start_point[1] + tile_x * self.step_size[1]) * self.image_w)
        point_y = round((self.start_point[0] + tile_y * self.step_size[0]) * self.image_h)

        # clamp just in case
        point_x = max(0, min(self.image_w - 1, point_x))
        point_y = max(0, min(self.image_h - 1, point_y))
        return point_x, point_y

    def factory(self):
        # NOTE: iterating sets idx
        for _ in self:
            if self.mode == MaskingMode.MASK_OUT:
                # mask only the region
                self.geometry_fnc(self.get_current_batch())[:, :, :] = self.filter_fnc()

            elif self.mode == MaskingMode.KEEP_ONLY:
                # copy region from base image into current masked canvas
                dst = self.geometry_fnc(self.get_current_batch())
                src = self.geometry_fnc(self.base_img_tensor[0])
                dst[:, :, :] = src

            else:
                raise ValueError(f"Unknown masking mode: {self.mode}")

        return self.base_img_tensor, self.batch_img_tensor,


# From packages\cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature\Masking\MaskingMode.py
from enum import Enum


class MaskingMode(str, Enum):
    MASK_OUT = "mask_out"     # mask the region inside an otherwise intact image
    KEEP_ONLY = "keep_only"   # keep the region; mask everything else

# From packages\cscience-feature-clip\tests\test_clip_feature.py
import random
from pathlib import Path
import unittest

from PIL import Image

from cscience.features.api import measure_time
from cscience.features.clip.clip_connector import ClipConnector


class FeatureTest(unittest.TestCase):

    N = 10
    def setUp(self):
        self.images_batch = [
            Image.open(self._resource("flickr-dog-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-dog-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-dog-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-dog-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-hummingbird.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-hummingbird.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-monkeys.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-monkeys.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-mountains.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-mountains.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-sunset.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-sunset.jpg")).convert("RGB"),
        ]

    def tearDown(self):
        self.images_batch = []

    def _resource(self, name: str) -> Path:
        return Path(__file__).resolve().parents[1] / "fixtures" / "test" / name

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_to_vector(self):
        clip = ClipConnector()
        v = clip.text("Hello World")

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_to_vector(self):
        clip = ClipConnector()
        image = Image.open(self._resource("flickr-dog-1.jpg")).convert("RGB")

        v = clip.image(image)

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_batch_to_vector_batch(self):
        clip = ClipConnector()
        v = clip.text_batch(["Hello World", "Hello World", "Hello World and Moon"])

        self.assertEqual(v[0], v[1])
        self.assertNotEqual(v[0], v[2])
        self.assertNotEqual(v[1], v[2])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector()

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])


    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector()

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])



    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector()
        length = len(self.images_batch) * 1
        # append n times the batch
        images = [random.choice(self.images_batch) for _ in range(length)]
        v = clip.image_batch(images)


# From packages\cscience-feature-clip\src\cscience\features\clip\clip_config.py
from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class ClipConfig(ConfigBase):


    @classmethod
    def _namespace(cls):
        return "clip"

    model_name:str = Field(
        default="xlm-roberta-base-ViT-B-32",
        description="The name of the CLIP model to use. Default is 'xlm-roberta-base-ViT-B-32'."
    )

    pretrained:str = Field(
        default="laion5b_s13b_b90k",
        description="The name of the pretrained model to use. Default is 'laion5b_s13b_b90k'."
    )
    device:str = Field(
        default="cpu",
        description="The device to use for inference. Default is 'cpu'."
    )


# From packages\cscience-feature-clip\src\cscience\features\clip\clip_connector.py
from PIL.Image import Image

from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.datatypes.image.pil_image import PilImage
from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from .clip_conversion_provider import ClipConversionProvider
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch
from .clip_feature import ClipFeature


class ClipConnector(ConnectorBase):
    """Public connector for CLIP text and image embeddings."""

    def __init__(self) -> None:
        self.feature = ClipFeature.get_instance()
        super().__init__("clip", ClipConversionProvider(self.feature))

    def text(self, data: str) -> list[float]:
        """Embed a single text string and return one float vector."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=Text,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVector,
        )

        return function(Text(data)).data()

    def text_batch(self, data: list[str]) -> dict[int, list[float]]:
        """Embed text strings and return vectors indexed by input position."""
        text_batch = TextBatch(
            {
                index: text
                for index, text in enumerate(data)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=TextBatch,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVectorBatch,
        )

        return function(text_batch).data()

    def image(self, data: Image) -> list[float]:
        """Embed a single image and return one float vector."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVector,
        )

        return function(PilImage(data)).data()

    def image_batch(self, data: list[Image]) -> dict[int, list[float]]:
        """Embed images and return vectors indexed by input position."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(data)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVectorBatch,
        )

        return function(image_batch).data()

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_conversion_provider.py
from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors.float_vector_batch import FloatVectorBatch
from cscience.features.api.feature.feature_base import FeatureBase

from .clip_datatypes.clip_tensor_batch import ClipTensorBatch


def clip_tensor_batch_passthrough(batch: ClipTensorBatch) -> ClipTensorBatch:
    return batch


def clip_tensor_batch_to_float_vector(batch: ClipTensorBatch) -> FloatVector:
    data = batch.data()

    if len(data.keys) != 1:
        raise ValueError(
            f"Cannot convert ClipTensorBatch of size {len(data.keys)} to FloatVector."
        )

    return FloatVector(data.vectors[0].tolist())


def clip_tensor_batch_to_float_vector_batch(batch: ClipTensorBatch) -> FloatVectorBatch:
    data = batch.data()

    return FloatVectorBatch(
        {
            key: vector.tolist()
            for key, vector in zip(data.keys, data.vectors)
        }
    )


class ClipConversionProvider(ConversionProviderBase):
    """Registers datatype conversions required by the CLIP connector."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        return [
            Converter[ClipTensorBatch, ClipTensorBatch](
                name="clip_tensor_batch_passthrough",
                source=self._feature,
                function=clip_tensor_batch_passthrough,
                input_type=ClipTensorBatch,
                output_type=ClipTensorBatch,
            ),
            Converter[ClipTensorBatch, FloatVector](
                name="clip_tensor_batch_to_float_vector",
                source=self._feature,
                function=clip_tensor_batch_to_float_vector,
                input_type=ClipTensorBatch,
                output_type=FloatVector,
            ),
            Converter[ClipTensorBatch, FloatVectorBatch](
                name="clip_tensor_batch_to_float_vector_batch",
                source=self._feature,
                function=clip_tensor_batch_to_float_vector_batch,
                input_type=ClipTensorBatch,
                output_type=FloatVectorBatch,
            ),
        ]

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_feature.py
from __future__ import annotations

import open_clip
import torch

from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase

from .clip_datatypes.clip_tensor_batch import ClipTensorBatch, ClipTensorBatchData


class ClipFeature(FeatureBase):
    """CLIP feature service backed by OpenCLIP."""

    def _initialize(self) -> None:
        if self._initialized:
            return

        self._model_name = "xlm-roberta-base-ViT-B-32"
        self._pretrained = "laion5b_s13b_b90k"

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name=self._model_name,
            pretrained=self._pretrained,
        )

        self.model = self.model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer(self._model_name)

        self._initialized = True

    @classmethod
    @torch.inference_mode()
    def text_batch(cls, texts: TextBatch) -> ClipTensorBatch:
        service = cls.get_instance()

        keys = texts.ordered_keys()
        values = list(texts.ordered_values())

        tokens = service.tokenizer(values).to(service.device)

        feats = service.model.encode_text(tokens)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=feats.detach().float().cpu(),
            )
        )

    @classmethod
    @torch.inference_mode()
    def image_batch(cls, images: PilImageBatch) -> ClipTensorBatch:
        service = cls.get_instance()

        keys = images.ordered_keys()
        values = images.ordered_values()

        image_tensors = torch.stack(
            [
                service.preprocess(image)
                for image in values
            ]
        ).to(service.device)

        feats = service.model.encode_image(image_tensors)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=feats.detach().float().cpu(),
            )
        )

# From packages\cscience-feature-clip\src\cscience\features\clip\__init__.py
from cscience.features.api.registry.registry_base import RegistryBase

from .clip_connector import ClipConnector
from .clip_conversion_provider import ClipConversionProvider
from .clip_datatypes.clip_datatype import ClipDatatype
from .clip_datatypes.clip_tensor import ClipTensor
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch, ClipTensorBatchData
from .clip_feature import ClipFeature

__all__ = [
    "ClipConnector",
    "ClipConversionProvider",
    "ClipDatatype",
    "ClipFeature",
    "ClipTensor",
    "ClipTensorBatch",
    "ClipTensorBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("clip", ClipConversionProvider)

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_datatype.py
from abc import ABC

from cscience.features.api import DatatypeBase


class ClipDatatype(DatatypeBase, ABC):
    """Base class for CLIP-specific datatypes."""

    namespace = "clip"

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor.py
from torch import Tensor

from cscience.features.clip import ClipDatatype


class ClipTensor(ClipDatatype):
    """Single CLIP embedding tensor with shape [d]."""

    def __init__(self, data: Tensor) -> None:
        if data.ndim != 1:
            raise ValueError(f"ClipTensor expects a 1D tensor, got shape {tuple(data.shape)}.")

        super().__init__(data)

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor_batch.py
from .clip_datatype import ClipDatatype
from .clip_tensor_batch_data import ClipTensorBatchData


class ClipTensorBatch(ClipDatatype):
    """Batch of CLIP embedding tensors with stable source keys."""

    def __init__(self, data: ClipTensorBatchData) -> None:
        if not data.keys:
            raise ValueError("ClipTensorBatch cannot be empty.")

        if data.vectors.ndim != 2:
            raise ValueError(
                f"ClipTensorBatch expects a 2D tensor, got shape {tuple(data.vectors.shape)}."
            )

        if len(data.keys) != data.vectors.shape[0]:
            raise ValueError(
                f"Number of keys must match tensor rows: "
                f"{len(data.keys)} keys for {data.vectors.shape[0]} rows."
            )

        for key in data.keys:
            if type(key) is not int:
                raise TypeError(
                    f"ClipTensorBatch keys must be int, got {type(key).__name__}."
                )

        if len(set(data.keys)) != len(data.keys):
            raise ValueError("ClipTensorBatch keys must be unique.")

        super().__init__(data)

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor_batch_data.py
from dataclasses import dataclass

from torch import Tensor


@dataclass(frozen=True, slots=True)
class ClipTensorBatchData:
    """CLIP tensor batch with stable source keys.

    vectors has shape [n, d].
    keys maps row positions back to source batch indices.
    """

    keys: tuple[int, ...]
    vectors: Tensor

# From packages\cscience-feature-asr-whisper\tests\test_asr_whisper_feature.py
import io
import unittest
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from cscience.features.asr_whisper import AsrWhisperConnector
from cscience.features.asr_whisper import AudioBytes
from cscience.features.asr_whisper.asr_whisper_conversion_provider import (
    audio_bytes_to_audio_signal,
)


def make_test_wav_bytes(sample_rate: int = 8_000) -> bytes:
    duration = 0.25
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.1 * np.sin(2 * np.pi * 440 * t)

    buffer = io.BytesIO()
    sf.write(buffer, waveform, sample_rate, format="WAV")
    return buffer.getvalue()

@dataclass
class Fixture:
    id: str
    audio_bytes: bytes
    contains: list[str]



class AsrWhispernTest(unittest.TestCase):

    def setUp(self):
        fixture_dir = Path(__file__).parent / "fixtures" / "ljspeech"

        self.fixtures :list[Fixture] = [
            Fixture( "LJ001-0001.wav", (fixture_dir / "LJ001-0001.wav").read_bytes(), ["printing", "arts"]),
            Fixture( "LJ001-0002.wav", (fixture_dir / "LJ001-0002.wav").read_bytes(), ["modern", "comparatively"]),
        ]



    def test_connector_initializes(self):
        connector = AsrWhisperConnector()
        self.assertIsNotNone(connector)

    def test_audio_bytes_to_audio_signal_resamples_to_16khz(self):
        audio_bytes = make_test_wav_bytes(sample_rate=8_000)

        signal = audio_bytes_to_audio_signal(AudioBytes(audio_bytes))

        self.assertEqual(signal.data().sample_rate, 16_000)
        self.assertEqual(signal.data().waveform.ndim, 1)
        self.assertEqual(signal.data().waveform.dtype, np.float32)

    def test_transcribes_local_speech_file(self):
        for fixture in self.fixtures:
            audio_bytes = fixture.audio_bytes
            expected_keywords = fixture.contains
            text = AsrWhisperConnector().audio_bytes(audio_bytes)
            for keyword in expected_keywords:
                self.assertIn(keyword, text.lower(), f"Expected keyword '{keyword}' not found in transcription '{text}' for fixture '{fixture.id}'")


# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_connector.py
from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    ServiceInfo,
    Text,
)

from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)
from .asr_whisper_feature import AsrWhisperFeature


class AsrWhisperConnector(ConnectorBase):
    """Public connector for Whisper ASR."""

    def __init__(self) -> None:
        self.feature = AsrWhisperFeature.get_instance()
        super().__init__("asr_whisper", AsrWhisperConversionProvider(self.feature))

    def transcribe_audio_bytes(self, data: bytes) -> WhisperTranscriptionData:
        """Transcribe encoded audio bytes and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioBytes,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioBytes(data)).data()

    def transcribe_audio_data_url(self, data: str) -> WhisperTranscriptionData:
        """Transcribe a base64-encoded audio data URL and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioDataUrl,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioDataUrl(data)).data()

    def transcribe_signal(self, data: AudioSignalData) -> WhisperTranscriptionData:
        """Transcribe a Whisper-ready audio signal and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioSignal,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioSignal(data)).data()

    def audio_bytes(self, data: bytes) -> str:
        """Transcribe encoded audio bytes and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioBytes,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioBytes(data)).data()

    def audio_data_url(self, data: str) -> str:
        """Transcribe a base64-encoded audio data URL and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioDataUrl,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioDataUrl(data)).data()

    def signal(self, data: AudioSignalData) -> str:
        """Transcribe a Whisper-ready audio signal and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioSignal,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioSignal(data)).data()

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_conversion_provider.py
import base64
import io

import librosa
import numpy as np
import soundfile as sf

from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    Text,
)

from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import WhisperTranscription


def audio_data_url_passthrough(data_url: AudioDataUrl) -> AudioDataUrl:
    return data_url


def audio_bytes_passthrough(audio: AudioBytes) -> AudioBytes:
    return audio


def audio_signal_passthrough(signal: AudioSignal) -> AudioSignal:
    return signal


def whisper_transcription_passthrough(
    transcription: WhisperTranscription,
) -> WhisperTranscription:
    return transcription


def audio_data_url_to_audio_bytes(data_url: AudioDataUrl) -> AudioBytes:
    """Decode a base64 audio data URL into raw encoded audio bytes."""
    encoded = data_url.payload()
    return AudioBytes(base64.b64decode(encoded, validate=True))


def audio_bytes_to_audio_signal(audio: AudioBytes) -> AudioSignal:
    """Decode audio bytes into Whisper-ready mono float32 16 kHz audio."""
    waveform, sample_rate = sf.read(io.BytesIO(audio.data()))
    waveform = np.asarray(waveform)

    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    elif waveform.ndim != 1:
        raise ValueError(f"Unexpected audio shape: {waveform.shape}")

    waveform = waveform.astype(np.float32, copy=False)

    if sample_rate != 16_000:
        waveform = librosa.resample(
            waveform,
            orig_sr=sample_rate,
            target_sr=16_000,
        )
        sample_rate = 16_000

    waveform = np.ascontiguousarray(waveform, dtype=np.float32)

    return AudioSignal(
        AudioSignalData(
            waveform=waveform,
            sample_rate=sample_rate,
        )
    )


def audio_data_url_to_audio_signal(data_url: AudioDataUrl) -> AudioSignal:
    """Decode a base64 audio data URL directly into a Whisper-ready signal."""
    return audio_bytes_to_audio_signal(
        audio_data_url_to_audio_bytes(data_url)
    )


def whisper_transcription_to_text(transcription: WhisperTranscription) -> Text:
    """Extract plain text from a Whisper transcription."""
    return Text(transcription.data().text)


class AsrWhisperConversionProvider(ConversionProviderBase):
    """Registers conversions required by the Whisper ASR feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[AudioDataUrl, AudioDataUrl](
                name="audio_data_url_passthrough",
                source=self._feature,
                function=audio_data_url_passthrough,
                input_type=AudioDataUrl,
                output_type=AudioDataUrl,
            ),
            Converter[AudioBytes, AudioBytes](
                name="audio_bytes_passthrough",
                source=self._feature,
                function=audio_bytes_passthrough,
                input_type=AudioBytes,
                output_type=AudioBytes,
            ),
            Converter[AudioSignal, AudioSignal](
                name="audio_signal_passthrough",
                source=self._feature,
                function=audio_signal_passthrough,
                input_type=AudioSignal,
                output_type=AudioSignal,
            ),
            Converter[WhisperTranscription, WhisperTranscription](
                name="whisper_transcription_passthrough",
                source=self._feature,
                function=whisper_transcription_passthrough,
                input_type=WhisperTranscription,
                output_type=WhisperTranscription,
            ),
            Converter[AudioDataUrl, AudioBytes](
                name="audio_data_url_to_audio_bytes",
                source=self._feature,
                function=audio_data_url_to_audio_bytes,
                input_type=AudioDataUrl,
                output_type=AudioBytes,
            ),
            Converter[AudioBytes, AudioSignal](
                name="audio_bytes_to_audio_signal",
                source=self._feature,
                function=audio_bytes_to_audio_signal,
                input_type=AudioBytes,
                output_type=AudioSignal,
            ),
            Converter[AudioDataUrl, AudioSignal](
                name="audio_data_url_to_audio_signal",
                source=self._feature,
                function=audio_data_url_to_audio_signal,
                input_type=AudioDataUrl,
                output_type=AudioSignal,
            ),
            Converter[WhisperTranscription, Text](
                name="whisper_transcription_to_text",
                source=self._feature,
                function=whisper_transcription_to_text,
                input_type=WhisperTranscription,
                output_type=Text,
            ),
        ]

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_feature.py
from __future__ import annotations

import threading

import torch
import whisper

from cscience.features.api import FeatureBase

from .asr_whisper_datatypes.audio_signal import AudioSignal
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)


class AsrWhisperFeature(FeatureBase):
    """Whisper ASR feature service.

    Loads the Whisper model once and transcribes decoded mono audio signals.
    """

    MODEL_NAME = "small"

    def _initialize(self) -> None:
        if self._initialized:
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = whisper.load_model(self.MODEL_NAME, device=self.device)
        self.lock = threading.Lock()

        self._initialized = True

    @classmethod
    @torch.inference_mode()
    def transcribe(cls, audio: AudioSignal) -> WhisperTranscription:
        """Transcribe a Whisper-ready audio signal."""
        service = cls.get_instance()
        fp16 = service.device.type == "cuda"

        with service.lock:
            result = service.model.transcribe(
                audio.data().waveform,
                fp16=fp16,
            )

        return WhisperTranscription(
            WhisperTranscriptionData(
                text=result.get("text", "").strip(),
                language=result.get("language"),
                segments=result.get("segments", []),
            )
        )

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\__init__.py
from cscience.features.api import RegistryBase

from .asr_whisper_connector import AsrWhisperConnector
from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_feature import AsrWhisperFeature
from .asr_whisper_datatypes.asr_whisper_datatype import AsrWhisperDatatype
from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)

__all__ = [
    "AsrWhisperConnector",
    "AsrWhisperConversionProvider",
    "AsrWhisperDatatype",
    "AsrWhisperFeature",
    "AudioBytes",
    "AudioDataUrl",
    "AudioSignal",
    "AudioSignalData",
    "WhisperTranscription",
    "WhisperTranscriptionData",
]


def register(registry: RegistryBase) -> None:
    registry.register("asr_whisper", AsrWhisperConversionProvider)

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\asr_whisper_datatype.py
from abc import ABC

from cscience.features.api import DatatypeBase


class AsrWhisperDatatype(DatatypeBase, ABC):
    """Base class for Whisper ASR-specific datatypes."""

    namespace = "asr_whisper"

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_bytes.py
from cscience.features.api import AudioBytesBase


class AudioBytes(AudioBytesBase):
    """Raw encoded audio bytes."""

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_data_url.py
from cscience.features.api import DataUrl


class AudioDataUrl(DataUrl):
    """Base64-encoded audio data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)

        media_type = self.media_type()
        if media_type is None or not media_type.startswith("audio/"):
            raise ValueError(f"AudioDataUrl expects audio media type, got {media_type}.")

        if not self.is_base64():
            raise ValueError("AudioDataUrl expects base64-encoded audio data.")

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_signal.py
from dataclasses import dataclass

import numpy as np

from .asr_whisper_datatype import AsrWhisperDatatype


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Whisper-ready mono audio signal."""

    waveform: np.ndarray
    sample_rate: int


class AudioSignal(AsrWhisperDatatype):
    """Whisper-ready mono float32 audio signal at 16 kHz."""

    EXPECTED_SAMPLE_RATE = 16_000

    def __init__(self, data: AudioSignalData) -> None:
        if not isinstance(data, AudioSignalData):
            raise TypeError(
                f"AudioSignal expects AudioSignalData, got {type(data).__name__}."
            )

        if not isinstance(data.waveform, np.ndarray):
            raise TypeError(
                f"AudioSignal waveform expects np.ndarray, "
                f"got {type(data.waveform).__name__}."
            )

        if data.waveform.ndim != 1:
            raise ValueError(
                f"AudioSignal expects mono 1D waveform, got shape {data.waveform.shape}."
            )

        if data.waveform.dtype != np.float32:
            raise TypeError(
                f"AudioSignal expects float32 waveform, got {data.waveform.dtype}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate != self.EXPECTED_SAMPLE_RATE:
            raise ValueError(
                f"AudioSignal expects {self.EXPECTED_SAMPLE_RATE} Hz, "
                f"got {data.sample_rate} Hz."
            )

        super().__init__(data)

# From packages\cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\whisper_transcription.py
from dataclasses import dataclass
from typing import Any

from .asr_whisper_datatype import AsrWhisperDatatype


@dataclass(frozen=True, slots=True)
class WhisperTranscriptionData:
    """Structured Whisper transcription result."""

    text: str
    language: str | None
    segments: list[dict[str, Any]]


class WhisperTranscription(AsrWhisperDatatype):
    """Whisper transcription output."""

    def __init__(self, data: WhisperTranscriptionData) -> None:
        if not isinstance(data, WhisperTranscriptionData):
            raise TypeError(
                f"WhisperTranscription expects WhisperTranscriptionData, "
                f"got {type(data).__name__}."
            )

        if type(data.text) is not str:
            raise TypeError(
                f"WhisperTranscriptionData.text expects str, got {type(data.text).__name__}."
            )

        if data.language is not None and type(data.language) is not str:
            raise TypeError(
                f"WhisperTranscriptionData.language expects str | None, "
                f"got {type(data.language).__name__}."
            )

        if type(data.segments) is not list:
            raise TypeError(
                f"WhisperTranscriptionData.segments expects list, "
                f"got {type(data.segments).__name__}."
            )

        super().__init__(data)

# From packages\cscience-feature-api\tests\test_config.py
import unittest
from typing import Literal

from numpy import random
from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class MockConfig(ConfigBase):
        string_value: str = Field(
            default="Hello World!",
            title='A string value',
            description='This is a string value for testing purposes.',
            min_length=3,
            max_length=50,
        )
        int_value:int = Field(
            default=42,
            title='An integer value',
            description='This is an integer value for testing purposes.',
            ge=0,
            le=100
        )
        bool_value:bool = Field(
            default=False,
            title='A boolean value',
            description='This is a boolean value for testing purposes.'
        )
        float_value:float = Field(
            default=3.14,
            title='A float value',
            description='This is a float value for testing purposes.',
            ge=0,
            le=10
        )
        list_value:list[int] = Field(
            default=[1, 2, 3],
            title='A list value',
            description='This is a list value for testing purposes.'
        )
        dict_value:dict[str,str] = Field(
            default={"key": "value"},
            title='A dict value',
            description='This is a dict value for testing purposes.'
        )
        literal_value: Literal["test1", "test2"] = Field(
            default="test1",
            title='A literal value',
            description='This is a literal value for testing purposes.'
        )

        @classmethod
        def _namespace(cls):
            return "mock"

class ConfigTest(unittest.TestCase):

    def test_read(self):
        cfg=MockConfig()
        print(cfg.model_dump())
        self.assertEqual(cfg.string_value, "Hello World!")
        self.assertEqual(cfg.int_value, 42)
        self.assertEqual(cfg.bool_value, False)
        self.assertEqual(cfg.float_value, 3.14)
        self.assertEqual(cfg.list_value, [1, 2, 3])
        self.assertEqual(cfg.dict_value, {"key": "value"})
        self.assertEqual(cfg.literal_value, "test1")
        pass

    def test_multiple(self):
        cfg1 = MockConfig()
        cfg2 = MockConfig()
        self.assertEqual(cfg1.model_dump(), cfg2.model_dump())
        cfg2.string_value = "Hello World and Moon!"
        print(f"\n-Dump cfg 1 contains: {cfg1.model_dump()}")
        print(f"\n-Dump cfg 2 contains: {cfg2.model_dump()}")
        print(cfg2.model_dump())
        self.assertNotEqual(cfg1.model_dump(), cfg2.model_dump())
        pass

    def test_literal(self):
        cfg = MockConfig()
        cfg.literal_value = "test2"
        self.assertEqual(cfg.literal_value, "test2")
        cfg.literal_value = "test3"
        MockConfig.model_validate(cfg)
        pass

# From packages\cscience-feature-api\tests\test_conversion.py


# From packages\cscience-feature-api\tests\test_feature.py
import unittest

from feature.feature_base import FeatureBase


class FeatureTest(unittest.TestCase):

    def test_feature_base(self):

        class A(FeatureBase):
            def _initialize(self) -> None:
                pass

        class B(FeatureBase):
            def _initialize(self) -> None:
                pass

        a = A()
        b = B()
        self.assertEqual(a.get_instance(), a)
        self.assertEqual(b.get_instance(), b)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a.get_instance(), b.get_instance())

# From packages\cscience-feature-api\tests\test_service_info.py


# From packages\cscience-feature-api\src\cscience\features\api\__init__.py
# Config
from .config.config_base import ConfigBase

# Connectors
from .connector.connector_base import ConnectorBase
from .connector.function_connector import FunctionConnector

# Conversions
from .conversion.conversion_provider_base import ConversionProviderBase
from .conversion.converter import Converter
from .conversion.search_strategy_base import SearchStrategyBase
from .conversion.search_strategy_most_specific import SearchStrategyMostSpecific

# Datatype conversion provider
from .datatypes.core_conversion_provider import CoreConversionProvider

# Datatype base classes
from .datatypes.base.audio_bytes_base import AudioBytesBase
from .datatypes.base.batch_base import BatchBase
from .datatypes.base.core_datatype import CoreDatatype
from .datatypes.base.datatype_base import DatatypeBase
from .datatypes.base.embedding_base import EmbeddingBase
from .datatypes.base.image_bytes_base import ImageBytesBase
from .datatypes.base.media_bytes_base import MediaBytesBase
from .datatypes.base.vector_base import VectorBase
from .datatypes.base.vector_batch_base import VectorBatchBase

# Datatype references
from .datatypes.references.data_url import DataUrl
from .datatypes.references.file_path import FilePath

# Spa
from .datatypes.spatial.spatial_batch_layout import SpatialBatchLayout
from .datatypes.spatial.spatial_region import SpatialRegion
from .datatypes.spatial.spatial_vector_batch_data import SpatialVectorBatchData
from .datatypes.spatial.spatial_vector_batch_base import SpatialVectorBatchBase
from .datatypes.spatial.spatial_primitive_vector_batch_base import SpatialPrimitiveVectorBatchBase
from .datatypes.spatial.spatial_float_vector_batch import SpatialFloatVectorBatch

# Text datatypes
from .datatypes.text.text import Text
from .datatypes.text.text_batch import TextBatch

# Image datatypes
from .datatypes.image.image_bytes import ImageBytes
from .datatypes.image.image_data_url import ImageDataUrl
from .datatypes.image.pil_image import PilImage
from .datatypes.image.pil_image_batch import PilImageBatch

# Audio datatypes
from .datatypes.audio.audio_bytes import AudioBytes
from .datatypes.audio.audio_signal import AudioSignal, AudioSignalData

# Scalar primitive datatypes
from .datatypes.primitives_scalar.bool_value import BoolValue
from .datatypes.primitives_scalar.float_value import FloatValue
from .datatypes.primitives_scalar.int_value import IntValue

# Primitive vector datatypes
from .datatypes.primitives_vectors.bool_vector import BoolVector
from .datatypes.primitives_vectors.bool_vector_batch import BoolVectorBatch
from .datatypes.primitives_vectors.float_vector import FloatVector
from .datatypes.primitives_vectors.float_vector_batch import FloatVectorBatch
from .datatypes.primitives_vectors.int_vector import IntVector
from .datatypes.primitives_vectors.int_vector_batch import IntVectorBatch
from .datatypes.primitives_vectors.primitive_vector_base import PrimitiveVectorBase
from .datatypes.primitives_vectors.primitive_vector_batch_base import PrimitiveVectorBatchBase

# Features
from .feature.feature_base import FeatureBase
from .feature.feature_info import FeatureInfo
from .feature.service_info import ServiceInfo

# Registry
from .registry.conversion_registry import ConversionRegistry
from .registry.registry_base import RegistryBase

# Utils
from .utils.measure_time import measure_time


__all__ = [
    # Config
    "ConfigBase",

    # Connectors
    "ConnectorBase",
    "FunctionConnector",

    # Conversions
    "ConversionProviderBase",
    "Converter",
    "SearchStrategyBase",
    "SearchStrategyMostSpecific",

    # Datatype conversion provider
    "CoreConversionProvider",

    # Datatype base classes
    "AudioBytesBase",
    "BatchBase",
    "CoreDatatype",
    "DatatypeBase",
    "EmbeddingBase",
    "ImageBytesBase",
    "MediaBytesBase",
    "VectorBase",
    "VectorBatchBase",

    # Datatype references
    "DataUrl",
    "FilePath",

    # Spatial datatypes
    "SpatialBatchLayout",
    "SpatialRegion",
    "SpatialVectorBatchData",
    "SpatialVectorBatchBase",
    "SpatialPrimitiveVectorBatchBase",
    "SpatialFloatVectorBatch",

    # Text datatypes
    "Text",
    "TextBatch",

    # Image datatypes
    "ImageBytes",
    "ImageDataUrl",
    "PilImage",
    "PilImageBatch",

    # Audio datatypes
    # "AudioBytes",
    # "AudioSignal",
    # "AudioSignalData",

    # Scalar primitive datatypes
    "BoolValue",
    "FloatValue",
    "IntValue",

    # Primitive vector datatypes
    "BoolVector",
    "BoolVectorBatch",
    "FloatVector",
    "FloatVectorBatch",
    "IntVector",
    "IntVectorBatch",
    "PrimitiveVectorBase",
    #"PrimitiveVectorBatchBase",

    # Features
    "FeatureBase",
    "FeatureInfo",
    "ServiceInfo",

    # Registry
    "ConversionRegistry",
    "RegistryBase",

    # Utils
    "measure_time",
]

# From packages\cscience-feature-api\src\cscience\features\api\config\config_base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from abc import ABC, abstractmethod

from pydantic import BaseModel


class ConfigBase(ABC, BaseModel):

    @classmethod
    @abstractmethod
    def _namespace(cls): raise NotImplementedError



# From packages\cscience-feature-api\src\cscience\features\api\connector\connector_base.py
from abc import ABC, abstractmethod

from ..conversion.conversion_provider_base import ConversionProviderBase
from ..datatypes.core_conversion_provider import CoreConversionProvider
from ..feature.core_feature import CoreFeature
from ..feature.feature_info import FeatureInfo
from ..feature.service_info import ServiceInfo
from ..registry.conversion_registry import ConversionRegistry


class ConnectorBase(ABC):
    """Base class for public feature connectors.

    A connector registers core conversions and feature-specific conversions,
    then exposes convenient methods using normal Python input and output types.
    """

    def __init__(self, name:str, conversion_provider: ConversionProviderBase):
        """Register core conversions and the connector's feature conversions."""
        core_conversion_provider = CoreConversionProvider(CoreFeature().get_instance())
        ConversionRegistry.register("core", core_conversion_provider)
        ConversionRegistry.register(name, conversion_provider)

    @abstractmethod
    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError

    @abstractmethod
    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError

# From packages\cscience-feature-api\src\cscience\features\api\connector\function_connector.py
from typing import TypeVar, Generic, Callable

from ..conversion.conversion_key import ConversionKey
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..conversion.search_strategy_most_specific import SearchStrategyMostSpecific
from ..datatypes.base.datatype_base import DatatypeBase

from ..feature.feature_base import FeatureBase
from ..registry.conversion_registry import ConversionRegistry

Tin = TypeVar('Tin', bound=DatatypeBase)
Tfi = TypeVar('Tfi', bound=DatatypeBase)
Tfo = TypeVar('Tfo', bound=DatatypeBase)
Tout = TypeVar('Tout', bound=DatatypeBase)


class FunctionConnector(Generic[Tin, Tfi, Tfo, Tout]):
    """Wrap a feature function with input and output conversions.

    The connector resolves one converter from public input type to feature input
    type and one converter from feature output type to public output type.
    """
    def __init__(self, feature: FeatureBase, function: Callable[[Tfi], Tfo],
                 input_type: type[DatatypeBase],
                 input_feature_type: type[DatatypeBase],
                 output_feature_type: type[DatatypeBase],
                 output_type: type[DatatypeBase],
                 ) -> None:
        strategy_in: SearchStrategyBase = SearchStrategyMostSpecific(ConversionKey(type(feature), input_type, input_feature_type))
        strategy_out: SearchStrategyBase = SearchStrategyMostSpecific(ConversionKey(type(feature), output_feature_type, output_type))
        self.inner: Converter[Tin, Tfi] = ConversionRegistry.get_best_effort_converter(strategy_in)
        self.outer: Converter[Tfo, Tout] = ConversionRegistry.get_best_effort_converter(strategy_out)
        self.function = function
        self.wrapped = lambda x: self.outer(function(self.inner(x)))

    def __call__(self, x: Tin) -> Tout:
        """Run input conversion, feature function, and output conversion."""
        return self.wrapped(x)


# From packages\cscience-feature-api\src\cscience\features\api\conversion\conversion_key.py
from ..datatypes.base.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase



from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ConversionKey:
    """Dictionary key identifying a registered datatype conversion.

    A conversion is scoped by feature class and by source/target datatype.
    Core conversions use `CoreFeature` as their source and may be used as
    fallback conversions by search strategies.
    """

    source: type[FeatureBase]
    input_type: type[DatatypeBase]
    output_type: type[DatatypeBase]

# From packages\cscience-feature-api\src\cscience\features\api\conversion\conversion_provider_base.py
from abc import ABC, abstractmethod
from typing import List

from .converter import Converter
from ..feature.feature_base import FeatureBase


class ConversionProviderBase(ABC):
    """Base class for groups of converters belonging to one feature."""

    def __init__(self, feature: FeatureBase) -> None:
        self._feature = feature

    @abstractmethod
    def register_converters(self) -> List[Converter]:
        """Return all converters provided by this feature or provider."""
        raise NotImplementedError("Subclasses must implement register_converters()")


# From packages\cscience-feature-api\src\cscience\features\api\conversion\converter.py
from typing import Callable, Generic, TypeVar

from .conversion_key import ConversionKey
from ..datatypes.base.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase

Tin = TypeVar('Tin', bound=DatatypeBase, contravariant=True)
Tout = TypeVar('Tout', bound=DatatypeBase, covariant=True)


class Converter(Generic[Tin, Tout]):
    """Callable conversion from one datatype into another datatype."""
    def __init__(self, name: str, source: FeatureBase,
                 function: Callable[[Tin], Tout],
                 input_type: type[DatatypeBase],
                 output_type: type[DatatypeBase]) -> None:
        self._name: str = name
        self._source: FeatureBase = source
        self._function: Callable[[Tin], Tout] = function
        self._input_type: type[DatatypeBase] = input_type
        self._output_type: type[DatatypeBase] = output_type

    def __call__(self, data: Tin) -> Tout:
        """Convert one datatype instance into another datatype instance."""
        return self._function(data)

    def get_identifier(self) -> ConversionKey:
        """Return the registry key under which this converter is stored."""
        return ConversionKey(type(self._source), self._input_type, self._output_type)


# From packages\cscience-feature-api\src\cscience\features\api\conversion\search_strategy_base.py


from abc import ABC, abstractmethod

from .conversion_key import ConversionKey
from .converter import Converter


class SearchStrategyBase(ABC):
    """Base class for converter lookup strategies."""
    def __init__(self, conversion_key: ConversionKey) -> None:
        self._conversion_key = conversion_key


    @abstractmethod
    def search(self, recordset: dict[ConversionKey, Converter]) -> Converter:
        """Find a converter in the given registry recordset."""
        raise NotImplementedError("Subclasses must implement search")


    def __str__(self) -> str:
        return str(self._conversion_key)


# From packages\cscience-feature-api\src\cscience\features\api\conversion\search_strategy_most_specific.py
from .conversion_key import ConversionKey
from .converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..feature.core_feature import CoreFeature


class SearchStrategyMostSpecific(SearchStrategyBase):
    """Resolve a converter by exact feature key, then by core fallback key."""
    def __init__(self, conversion_key: ConversionKey):
        super().__init__(conversion_key)

    def search(self,
               recordset: dict[ConversionKey, Converter]) -> Converter:
        """Return the best matching converter or raise `LookupError`."""

        key: ConversionKey = self._conversion_key
        key_core: ConversionKey = ConversionKey(CoreFeature, key.input_type, key.output_type)


        try:
            return recordset[key]
        except KeyError:
            try:
                return recordset[key_core]
            except KeyError:
                raise LookupError(
                    f"No converter found for {self._conversion_key}"
                )

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\core_conversion_provider.py
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
from cscience.features.api.datatypes.primitives_vectors.bool_vector_batch import BoolVectorBatch
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.primitives_vectors.int_vector import IntVector
from cscience.features.api.datatypes.primitives_vectors.int_vector_batch import IntVectorBatch
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

# From packages\cscience-feature-api\src\cscience\features\api\feature\core_feature.py
from cscience.features.api.feature.feature_base import FeatureBase

class CoreFeature(FeatureBase):
    """
    This is a helper feature for register core converters.
    """
    def _initialize(self) -> None:
        pass

# From packages\cscience-feature-api\src\cscience\features\api\feature\feature_base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class FeatureBase(ABC):
    """Base class for model-backed feature services.

    Each concrete feature class is instantiated as a singleton. Expensive
    resources such as neural network weights should be loaded in `_initialize`.
    """

    _instances: ClassVar[dict[type["FeatureBase"], "FeatureBase"]] = {}
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls is FeatureBase:
            raise TypeError("FeatureBase cannot be instantiated directly.")

        if cls not in FeatureBase._instances:
            FeatureBase._instances[cls] = super().__new__(cls)

        return FeatureBase._instances[cls]

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialize()
        self._initialized = True

    @classmethod
    def get_instance(cls):
        """Return the singleton instance of the concrete feature class."""
        return cls()

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize expensive feature resources exactly once."""
        pass

# From packages\cscience-feature-api\src\cscience\features\api\feature\feature_info.py
class FeatureInfo:
    pass

# From packages\cscience-feature-api\src\cscience\features\api\feature\service_info.py


class ServiceInfo:
    pass

# From packages\cscience-feature-api\src\cscience\features\api\registry\conversion_registry.py
from ..conversion.conversion_key import ConversionKey
from ..conversion.conversion_provider_base import ConversionProviderBase
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..registry.registry_base import RegistryBase, Tin


class ConversionRegistry(RegistryBase[ConversionProviderBase]):
    """Singleton registry for datatype converters."""
    @classmethod
    def _initialize(cls) -> None:
        cls._converters  = {}
        pass

    _converters: dict[ConversionKey, Converter] = None

    @classmethod
    def get_converters(cls) -> dict[ConversionKey, Converter]:
        """Return the dictionary of all registered converters."""
        return cls._converters

    @classmethod
    def register(cls, name: str, provider: Tin) -> None:
        """Register all converters exposed by a conversion provider."""
        for converter in provider.register_converters():
            cls.get_instance().get_converters()[converter.get_identifier()] = converter

    @classmethod
    def has_best_effort_converter(cls, strategy: SearchStrategyBase) -> bool:
        """Check if the given strategy has a best effort converter."""
        try:
            strategy.search(cls.get_instance().get_converters())
            return True
        except LookupError:
            return False

    @classmethod
    def get_best_effort_converter(cls, strategy: SearchStrategyBase) -> Converter:
        """Resolve a converter with the given search strategy."""
        try:
            return strategy.search(cls.get_instance().get_converters())
        except LookupError as ex:
            raise LookupError(f"No best effort converter found for strategy: {strategy}") from ex

# From packages\cscience-feature-api\src\cscience\features\api\registry\registry_base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Union, Generic, ClassVar, Any

Tin = TypeVar("Tin", contravariant=True)


class RegistryBase(ABC, Generic[Tin]):

    _instances: ClassVar[dict[type["RegistryBase"], "RegistryBase"]] = {}
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls is RegistryBase:
            raise TypeError("FeatureBase cannot be instantiated directly.")

        if cls not in RegistryBase._instances:
            RegistryBase._instances[cls] = super().__new__(cls)

        return RegistryBase._instances[cls]

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialize()
        self._initialized = True


    @classmethod
    def get_instance(cls):
        return cls()

    @classmethod
    @abstractmethod
    def _initialize(cls) -> None:
        """
        Load expensive resources here, e.g. model weights.
        Called exactly once per concrete feature class.
        """
        pass

    @abstractmethod
    def register(self, name: str, provider: Tin) -> None:
        """Register a feature in the registry."""
        pass


# From packages\cscience-feature-api\src\cscience\features\api\utils\measure_time.py
import timeit


def measure_time(times: int=1, ignore_first: bool=False):
    """Measure the mean runtime of a function over repeated executions.

    Intended for lightweight development benchmarks, not for production
    profiling.
    """
    def inner(func):
        def wrapper(*args, **kwargs):

            t_total = 0
            result = None
            if ignore_first:
                result = func(*args, **kwargs)

            n = max(1, times)
            for i in range(n):
                start = timeit.default_timer()
                result = func(*args, **kwargs)
                end = timeit.default_timer()
                t_total += end - start

            max_width = 39

            print(
                f"\t{func.__name__:<{max_width}} "
                f"[mean] ⌛ {t_total / n:.5f} s for 🧮 {n} iterations"
            )
            return result
        return wrapper
    return inner

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\audio\audio_bytes.py
from cscience.features.api.datatypes.base.audio_bytes_base import AudioBytesBase


class AudioBytes(AudioBytesBase):
    """Encoded audio bytes."""

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\audio\audio_signal.py
import numpy as np

from cscience.features.api.datatypes.audio.audio_signal_data import AudioSignalData
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class AudioSignal(CoreDatatype[AudioSignalData]):
    """Decoded audio signal."""

    def __init__(self, data: AudioSignalData) -> None:
        if not isinstance(data.waveform, np.ndarray):
            raise TypeError(
                f"AudioSignal waveform expects np.ndarray, "
                f"got {type(data.waveform).__name__}."
            )

        if data.waveform.ndim not in {1, 2}:
            raise ValueError(
                f"AudioSignal waveform must be 1D or 2D, got shape {data.waveform.shape}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate <= 0:
            raise ValueError("AudioSignal sample_rate must be positive.")

        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\audio\audio_signal_data.py
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Decoded audio signal with an explicit sample rate."""

    waveform: np.ndarray
    sample_rate: int



# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\audio_bytes_base.py
from cscience.features.api.datatypes.base.media_bytes_base import MediaBytesBase


class AudioBytesBase(MediaBytesBase):
    """Encoded audio bytes."""

    media_type = "audio"

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\batch_base.py
from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar

T = TypeVar("T")


class BatchBase(ABC, Generic[T]):
    """Mixin for indexed batch datatypes.

    Guarantee:
    - batch data is a non-empty mapping
    - keys are integer source indices
    - values are batch elements
    - ordered_* methods return the canonical order by ascending source index
    """

    def _validate_batch_mapping(self, data: Mapping[int, T]) -> None:
        if not data:
            raise ValueError(f"{type(self).__name__} cannot be empty.")

        for key in data.keys():
            if type(key) is not int:
                raise TypeError(
                    f"{type(self).__name__} keys must be int, "
                    f"got {type(key).__name__}."
                )

    def batch_size(self) -> int:
        """Return the number of batch elements."""
        return len(self.data())

    def ordered_keys(self) -> tuple[int, ...]:
        """Return source indices in canonical batch order."""
        return tuple(sorted(self.data().keys()))

    def ordered_values(self) -> tuple[T, ...]:
        """Return values in canonical batch order."""
        return tuple(self.data()[key] for key in self.ordered_keys())

    def ordered_items(self) -> tuple[tuple[int, T], ...]:
        """Return items in canonical batch order."""
        return tuple((key, self.data()[key]) for key in self.ordered_keys())

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\core_datatype.py
from abc import ABC
from typing import Generic, TypeVar

from .datatype_base import DatatypeBase

T = TypeVar("T")


class CoreDatatype(DatatypeBase[T], ABC, Generic[T]):
    """Base class for feature-independent core datatypes.

    Core datatypes describe generic media, primitive, text, vector, or
    embedding containers. They must not encode feature-specific model results.
    """

    namespace = "core"

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\datatype_base.py
from abc import ABC
from typing import Generic, TypeVar

T = TypeVar("T")


class DatatypeBase(ABC, Generic[T]):
    """Base class for all semantic feature datatypes.

    A datatype wraps a raw Python value and attaches semantic meaning to it.
    Conversion and connector logic should use datatype classes rather than raw
    Python types at feature boundaries.
    """

    def __init__(self, data: T) -> None:
        self._data = data

    def data(self) -> T:
        """Return the wrapped raw value."""
        return self._data

    @staticmethod
    def fullname(o: object) -> str:
        """Return the fully qualified class name of an object."""
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__
        return module + "." + o.__class__.__name__

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\embedding_base.py
from abc import ABC

from .vector_base import VectorBase


class EmbeddingBase(VectorBase, ABC):
    """Mixin for semantic embedding vectors."""

    def embedding_dim(self) -> int:
        """Return the embedding dimension."""
        return self.length()

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\image_bytes_base.py
from .media_bytes_base import MediaBytesBase


class ImageBytesBase(MediaBytesBase):
    """Encoded image bytes."""

    media_type = "image"

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\media_bytes_base.py
from abc import ABC

from .core_datatype import CoreDatatype


class MediaBytesBase(CoreDatatype[bytes], ABC):
    """Base class for encoded media byte containers."""

    media_type: str = "media"

    def __init__(self, data: bytes) -> None:
        if not data:
            raise ValueError(f"{type(self).__name__} cannot be empty.")

        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\vector_base.py
from abc import ABC
from collections.abc import Sized


class VectorBase(ABC):
    """Mixin for single vector datatypes."""

    def length(self) -> int:
        """Return the vector dimension."""
        data = self.data()

        if not isinstance(data, Sized):
            raise ValueError(f"Cannot infer vector length from {type(data).__name__}.")

        return len(data)

    def assert_length(self, expected: int) -> None:
        """Raise if the vector dimension does not match the expected value."""
        actual = self.length()

        if actual != expected:
            raise ValueError(f"Expected vector length {expected}, got {actual}.")

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\base\vector_batch_base.py
from abc import ABC
from collections.abc import Mapping, Sized
from typing import Generic, TypeVar

from .batch_base import BatchBase

V = TypeVar("V")


class VectorBatchBase(BatchBase[V], ABC, Generic[V]):
    """Mixin for indexed batches of vectors."""

    def _validate_vector_batch_mapping(self, data: Mapping[int, V]) -> None:
        self._validate_batch_mapping(data)

        lengths: set[int] = set()

        for key, vector in data.items():
            if not isinstance(vector, Sized):
                raise TypeError(
                    f"Vector at key {key} must be sized, "
                    f"got {type(vector).__name__}."
                )

            vector_length = len(vector)

            if vector_length == 0:
                raise ValueError(f"Vector at key {key} cannot be empty.")

            lengths.add(vector_length)

        if len(lengths) != 1:
            raise ValueError(f"Inconsistent vector lengths: {sorted(lengths)}.")

    def length(self) -> int:
        """Return the shared vector dimension."""
        return len(self.ordered_values()[0])

    def assert_length(self, expected: int) -> None:
        """Raise if the shared vector dimension does not match the expected value."""
        actual = self.length()

        if actual != expected:
            raise ValueError(f"Expected vector length {expected}, got {actual}.")

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\image\image_bytes.py
from cscience.features.api.datatypes.base.image_bytes_base import ImageBytesBase


class ImageBytes(ImageBytesBase):
    """Encoded image bytes."""

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\image\image_data_url.py
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class ImageDataUrl(CoreDatatype[str]):
    """Base64-encoded image data URL."""

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(f"ImageDataUrl expects str, got {type(data).__name__}.")

        if not data:
            raise ValueError("ImageDataUrl cannot be empty.")

        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\image\pil_image.py
from PIL.Image import Image

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class PilImage(CoreDatatype[Image]):
    """Decoded Pillow image."""

    def __init__(self, data: Image) -> None:
        if not isinstance(data, Image):
            raise TypeError(f"PilImage expects PIL image, got {type(data).__name__}.")

        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\image\pil_image_batch.py
from collections.abc import Mapping

from PIL.Image import Image

from cscience.features.api.datatypes.base.batch_base import BatchBase
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class PilImageBatch(CoreDatatype[dict[int, Image]], BatchBase[Image]):
    """Batch of Pillow images indexed by source position."""

    def __init__(self, data: Mapping[int, Image]) -> None:
        self._validate_batch_mapping(data)

        for key, value in data.items():
            if not isinstance(value, Image):
                raise TypeError(
                    f"PilImageBatch expects PIL images, got {type(value).__name__} "
                    f"at key {key}."
                )

        super().__init__(dict(data))

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_scalar\bool_value.py
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class BoolValue(CoreDatatype[bool]):
    """Single boolean value."""

    def __init__(self, data: bool) -> None:
        if type(data) is not bool:
            raise TypeError(f"BoolValue expects bool, got {type(data).__name__}.")
        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_scalar\float_value.py
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class FloatValue(CoreDatatype[float]):
    """Single floating-point value."""

    def __init__(self, data: float) -> None:
        if type(data) is not float:
            raise TypeError(f"FloatValue expects float, got {type(data).__name__}.")

        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_scalar\int_value.py
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class IntValue(CoreDatatype[int]):
    """Single integer value."""

    def __init__(self, data: int) -> None:
        if type(data) is not int:
            raise TypeError(f"IntValue expects int, got {type(data).__name__}.")
        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\bool_vector.py
from .primitive_vector_base import PrimitiveVectorBase


class BoolVector(PrimitiveVectorBase[bool]):
    """Single boolean vector."""

    element_type = bool

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\bool_vector_batch.py
from .primitive_vector_batch_base import PrimitiveVectorBatchBase


class BoolVectorBatch(PrimitiveVectorBatchBase[bool]):
    """Batch of boolean vectors indexed by source position."""

    element_type = bool

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\float_vector.py
from cscience.features.api.datatypes.base.embedding_base import EmbeddingBase

from .primitive_vector_base import PrimitiveVectorBase


class FloatVector(PrimitiveVectorBase[float], EmbeddingBase):
    """Single float vector."""

    element_type = float

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\float_vector_batch.py
from cscience.features.api.datatypes.base.embedding_base import EmbeddingBase

from .primitive_vector_batch_base import PrimitiveVectorBatchBase


class FloatVectorBatch(PrimitiveVectorBatchBase[float], EmbeddingBase):
    """Batch of float vectors indexed by source position."""

    element_type = float

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\int_vector.py
from .primitive_vector_base import PrimitiveVectorBase


class IntVector(PrimitiveVectorBase[int]):
    """Single integer vector."""

    element_type = int

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\int_vector_batch.py
from .primitive_vector_batch_base import PrimitiveVectorBatchBase


class IntVectorBatch(PrimitiveVectorBatchBase[int]):
    """Batch of integer vectors indexed by source position."""

    element_type = int

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\primitive_vector_base.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype
from cscience.features.api.datatypes.base.vector_base import VectorBase

T = TypeVar("T")


class PrimitiveVectorBase(CoreDatatype[list[T]], VectorBase, ABC, Generic[T]):
    """Base class for list-backed primitive vectors."""

    element_type: type

    def __init__(self, data: list[T], assert_length: int | None = None) -> None:
        if not data:
            raise ValueError(f"{type(self).__name__} cannot be empty.")

        for index, value in enumerate(data):
            if type(value) is not self.element_type:
                raise TypeError(
                    f"{type(self).__name__} expects {self.element_type.__name__}, "
                    f"got {type(value).__name__} at index {index}."
                )

        super().__init__(data)

        if assert_length is not None:
            self.assert_length(assert_length)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\primitive_vector_batch_base.py
from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype
from cscience.features.api.datatypes.base.vector_batch_base import VectorBatchBase

T = TypeVar("T")


class PrimitiveVectorBatchBase(
    CoreDatatype[dict[int, list[T]]],
    VectorBatchBase[list[T]],
    ABC,
    Generic[T],
):
    """Base class for batches of list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: Mapping[int, list[T]],
        assert_length: int | None = None,
    ) -> None:
        self._validate_vector_batch_mapping(data)

        for key, vector in data.items():
            for index, value in enumerate(vector):
                if type(value) is not self.element_type:
                    raise TypeError(
                        f"{type(self).__name__} expects {self.element_type.__name__}, "
                        f"got {type(value).__name__} at key {key}, index {index}."
                    )

        super().__init__(dict(data))

        if assert_length is not None:
            self.assert_length(assert_length)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\references\data_url.py
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class DataUrl(CoreDatatype[str]):
    """Generic data URL reference.

    A DataUrl stores a string such as:

        data:image/png;base64,...

    It does not decode the payload. Decoding belongs to converters.
    """

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(f"DataUrl expects str, got {type(data).__name__}.")

        if not data:
            raise ValueError("DataUrl cannot be empty.")

        if not data.startswith("data:"):
            raise ValueError("DataUrl must start with 'data:'.")

        if "," not in data:
            raise ValueError("DataUrl must contain a header and payload separated by ','.")

        super().__init__(data)

    def header(self) -> str:
        """Return the data URL header without the payload."""
        return self.data().split(",", 1)[0]

    def payload(self) -> str:
        """Return the encoded payload part without decoding it."""
        return self.data().split(",", 1)[1]

    def media_type(self) -> str | None:
        """Return the declared media type, if present."""
        header = self.header()

        # Examples:
        # data:image/png;base64
        # data:text/plain;charset=utf-8
        prefix = "data:"
        if not header.startswith(prefix):
            return None

        rest = header[len(prefix):]
        if not rest:
            return None

        return rest.split(";", 1)[0] or None

    def is_base64(self) -> bool:
        """Return whether the data URL declares base64 encoding."""
        return ";base64" in self.header()

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\references\file_path.py
from pathlib import Path

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class FilePath(CoreDatatype[Path]):
    """Filesystem path reference.

    FilePath stores a path-like reference. It does not open, read, or validate
    the file contents.
    """

    def __init__(self, data: str | Path) -> None:
        if not isinstance(data, str | Path):
            raise TypeError(f"FilePath expects str or Path, got {type(data).__name__}.")

        path = Path(data)

        if not str(path):
            raise ValueError("FilePath cannot be empty.")

        super().__init__(path)

    def exists(self) -> bool:
        """Return whether the referenced path currently exists."""
        return self.data().exists()

    def is_file(self) -> bool:
        """Return whether the referenced path currently points to a file."""
        return self.data().is_file()

    def suffix(self) -> str:
        """Return the file suffix."""
        return self.data().suffix

    def name(self) -> str:
        """Return the final path component."""
        return self.data().name

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_batch_layout.py
from dataclasses import dataclass

import icontract


@icontract.invariant(lambda self: self.item_count > 0, "item_count must be positive.")
@icontract.invariant(lambda self: self.regions_per_item > 0, "regions_per_item must be positive.")
@dataclass(frozen=True, slots=True)
class SpatialBatchLayout:
    """Mapping between flat batch indices and structured spatial indices.

    Logical structure:
        [item_count, regions_per_item]

    Physical structure:
        [item_count * regions_per_item]
    """

    item_count: int
    regions_per_item: int

    @property
    def flat_count(self) -> int:
        """Return the number of flat batch entries."""
        return self.item_count * self.regions_per_item

    @icontract.require(lambda self, item_index: 0 <= item_index < self.item_count)
    @icontract.require(lambda self, region_index: 0 <= region_index < self.regions_per_item)
    def to_flat_index(self, item_index: int, region_index: int) -> int:
        """Return the flat index for a structured item-region pair."""
        return item_index * self.regions_per_item + region_index

    @icontract.require(lambda self, flat_index: 0 <= flat_index < self.flat_count)
    def from_flat_index(self, flat_index: int) -> tuple[int, int]:
        """Return ``(item_index, region_index)`` for a flat index."""
        return divmod(flat_index, self.regions_per_item)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_float_vector_batch.py
from cscience.features.api.datatypes.base.embedding_base import EmbeddingBase

from .spatial_primitive_vector_batch_base import SpatialPrimitiveVectorBatchBase


class SpatialFloatVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
):
    """Spatially structured batch of float embedding vectors.

    Physical structure:
        dict[int, list[float]]

    Logical structure:
        [item_count, regions_per_item, embedding_dim]
    """

    element_type = float

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_primitive_vector_batch_base.py
from abc import ABC
from typing import Generic, TypeVar

from .spatial_vector_batch_base import SpatialVectorBatchBase
from .spatial_vector_batch_data import SpatialVectorBatchData

T = TypeVar("T")


class SpatialPrimitiveVectorBatchBase(
    SpatialVectorBatchBase[list[T]],
    ABC,
    Generic[T],
):
    """Base class for spatial batches of list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: SpatialVectorBatchData[list[T]],
        assert_length: int | None = None,
    ) -> None:
        super().__init__(data, assert_length=assert_length)

        for key, vector in self.data().vectors.items():
            for index, value in enumerate(vector):
                if type(value) is not self.element_type:
                    raise TypeError(
                        f"{type(self).__name__} expects {self.element_type.__name__}, "
                        f"got {type(value).__name__} at key {key}, index {index}."
                    )

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_region.py
from dataclasses import dataclass

import icontract


@icontract.invariant(lambda self: self.index >= 0, "index must be non-negative.")
@icontract.invariant(lambda self: self.row >= 0, "row must be non-negative.")
@icontract.invariant(lambda self: self.column >= 0, "column must be non-negative.")
@icontract.invariant(lambda self: self.x1 > self.x0, "x1 must be greater than x0.")
@icontract.invariant(lambda self: self.y1 > self.y0, "y1 must be greater than y0.")
@icontract.invariant(lambda self: self.x0 <= self.center_x < self.x1, "center_x must be inside [x0, x1).")
@icontract.invariant(lambda self: self.y0 <= self.center_y < self.y1, "center_y must be inside [y0, y1).")
@icontract.invariant(
    lambda self: all(0.0 <= value <= 1.0 for value in (self.nx0, self.ny0, self.nx1, self.ny1)),
    "normalized coordinates must be in [0, 1].",
)
@icontract.invariant(lambda self: self.nx1 > self.nx0, "nx1 must be greater than nx0.")
@icontract.invariant(lambda self: self.ny1 > self.ny0, "ny1 must be greater than ny0.")
@dataclass(frozen=True, slots=True)
class SpatialRegion:
    """Spatial region metadata.

    Pixel coordinates use half-open bounds:

        [x0, x1)
        [y0, y1)

    Normalized coordinates use the same convention in [0, 1].
    """

    index: int

    row: int
    column: int

    center_x: int
    center_y: int

    x0: int
    y0: int
    x1: int
    y1: int

    nx0: float
    ny0: float
    nx1: float
    ny1: float

    @property
    def width(self) -> int:
        """Return the region width in pixels."""
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        """Return the region height in pixels."""
        return self.y1 - self.y0

    @property
    def center_xy(self) -> tuple[int, int]:
        """Return the pixel center as ``(x, y)``."""
        return self.center_x, self.center_y

    @property
    def grid_xy(self) -> tuple[int, int]:
        """Return grid coordinates as ``(x, y)`` / ``(column, row)``."""
        return self.column, self.row

    @property
    def grid_yx(self) -> tuple[int, int]:
        """Return grid coordinates as ``(y, x)`` / ``(row, column)``."""
        return self.row, self.column

    @property
    def box_xyxy(self) -> tuple[int, int, int, int]:
        """Return the pixel box as ``(x0, y0, x1, y1)``."""
        return self.x0, self.y0, self.x1, self.y1

    @property
    def normalized_box_xyxy(self) -> tuple[float, float, float, float]:
        """Return the normalized box as ``(nx0, ny0, nx1, ny1)``."""
        return self.nx0, self.ny0, self.nx1, self.ny1

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_vector_batch_base.py
from abc import ABC
from collections.abc import Mapping, Sized
from typing import Generic, TypeVar

import icontract

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype
from cscience.features.api.datatypes.base.vector_batch_base import VectorBatchBase

from .spatial_batch_layout import SpatialBatchLayout
from .spatial_region import SpatialRegion
from .spatial_vector_batch_data import SpatialVectorBatchData

V = TypeVar("V")


class SpatialVectorBatchBase(
    CoreDatatype[SpatialVectorBatchData[V]],
    VectorBatchBase[V],
    ABC,
    Generic[V],
):
    """Base class for spatially structured vector batches.

    Physical structure:
        dict[int, vector]

    Logical structure:
        [item_count, regions_per_item, vector_dim]
    """

    @icontract.require(lambda data: len(data.vectors) == data.layout.flat_count,
                       "Spatial vector count must match layout.flat_count.",
                       )
    @icontract.require(
        lambda data: set(data.vectors.keys()) == set(range(data.layout.flat_count)),
        "Spatial vector keys must be contiguous flat indices 0..layout.flat_count-1.",
    )
    @icontract.require(
        lambda data: len(data.regions) == data.layout.regions_per_item,
        "Region count must match layout.regions_per_item.",
    )
    @icontract.require(
        lambda data: all(region.index == index for index, region in enumerate(data.regions)),
        "Region indices must match their position in the region tuple.",
    )
    def __init__(
            self,
            data: SpatialVectorBatchData[V],
            assert_length: int | None = None,
    ) -> None:
        if not isinstance(data, SpatialVectorBatchData):
            raise TypeError(
                f"{type(self).__name__} expects SpatialVectorBatchData, "
                f"got {type(data).__name__}."
            )

        self._validate_vector_batch_mapping(data.vectors)
        self._validate_uniform_vector_lengths(data.vectors)

        normalized = SpatialVectorBatchData(
            vectors=dict(data.vectors),
            layout=data.layout,
            regions=tuple(data.regions),
        )

        super().__init__(normalized)

        if assert_length is not None:
            self.assert_length(assert_length)

    @staticmethod
    def _validate_uniform_vector_lengths(data: Mapping[int, V]) -> None:
        lengths: dict[int, int] = {}

        for key, vector in data.items():
            if not isinstance(vector, Sized):
                raise TypeError(
                    f"Spatial vector at key {key} must be sized, "
                    f"got {type(vector).__name__}."
                )

            lengths[key] = len(vector)

        unique_lengths = set(lengths.values())

        if len(unique_lengths) != 1:
            raise ValueError(
                f"Spatial vector batch must have uniform vector lengths, got {lengths}."
            )

    @property
    def vectors(self) -> dict[int, V]:
        """Return flat vectors indexed by flat spatial index."""
        return dict(self.data().vectors)

    @property
    def layout(self) -> SpatialBatchLayout:
        """Return the spatial batch layout."""
        return self.data().layout

    @property
    def regions(self) -> tuple[SpatialRegion, ...]:
        """Return the regions used for every item."""
        return self.data().regions

    def batch_size(self) -> int:
        """Return the flat batch size."""
        return len(self.data().vectors)

    def item_count(self) -> int:
        """Return the number of structured source items."""
        return self.layout.item_count

    def regions_per_item(self) -> int:
        """Return the number of regions per source item."""
        return self.layout.regions_per_item

    def ordered_keys(self) -> tuple[int, ...]:
        """Return flat indices in canonical order."""
        return tuple(sorted(self.data().vectors.keys()))

    def ordered_values(self) -> tuple[V, ...]:
        """Return vectors in canonical flat-index order."""
        return tuple(self.data().vectors[key] for key in self.ordered_keys())

    def ordered_items(self) -> tuple[tuple[int, V], ...]:
        """Return flat-indexed vectors in canonical order."""
        return tuple((key, self.data().vectors[key]) for key in self.ordered_keys())

    def length(self) -> int:
        """Return the vector dimension."""
        first_key = self.ordered_keys()[0]
        return len(self.data().vectors[first_key])

    def assert_length(self, expected: int) -> None:
        """Raise if the vector dimension does not match the expected value."""
        actual = self.length()

        if actual != expected:
            raise ValueError(f"Expected vector length {expected}, got {actual}.")

    def to_flat_index(self, item_index: int, region_index: int) -> int:
        """Return the flat index for a structured item-region pair."""
        return self.layout.to_flat_index(item_index, region_index)

    def from_flat_index(self, flat_index: int) -> tuple[int, int]:
        """Return ``(item_index, region_index)`` for a flat index."""
        return self.layout.from_flat_index(flat_index)

    def region_for_flat_index(self, flat_index: int) -> SpatialRegion:
        """Return the region metadata for a flat index."""
        _, region_index = self.from_flat_index(flat_index)
        return self.regions[region_index]

    def vector_at(self, item_index: int, region_index: int) -> V:
        """Return the vector for a structured item-region pair."""
        return self.data().vectors[self.to_flat_index(item_index, region_index)]

    def item_vectors(self, item_index: int) -> tuple[V, ...]:
        """Return all region vectors for one structured item."""
        return tuple(
            self.vector_at(item_index, region_index)
            for region_index in range(self.layout.regions_per_item)
        )


# From packages\cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_vector_batch_data.py
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Generic, TypeVar

from .spatial_batch_layout import SpatialBatchLayout
from .spatial_region import SpatialRegion

V = TypeVar("V")


@dataclass(frozen=True, slots=True)
class SpatialVectorBatchData(Generic[V]):
    """Spatially structured vector batch data.

    The vectors are stored flat:

        vectors[flat_index] -> vector

    The layout reconstructs the logical structure:

        flat_index <-> (item_index, region_index)
    """

    vectors: Mapping[int, V]
    layout: SpatialBatchLayout
    item_keys: tuple[int, ...]
    regions: tuple[SpatialRegion, ...]

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\text\text.py
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class Text(CoreDatatype[str]):
    """Single text string."""

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(f"Text expects str, got {type(data).__name__}.")

        super().__init__(data)

# From packages\cscience-feature-api\src\cscience\features\api\datatypes\text\text_batch.py
from collections.abc import Mapping

from cscience.features.api.datatypes.base.batch_base import BatchBase
from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class TextBatch(CoreDatatype[dict[int, str]], BatchBase[str]):
    """Batch of text strings indexed by source position."""

    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)

        for key, value in data.items():
            if type(value) is not str:
                raise TypeError(
                    f"TextBatch expects str values, got {type(value).__name__} "
                    f"at key {key}."
                )

        super().__init__(dict(data))

