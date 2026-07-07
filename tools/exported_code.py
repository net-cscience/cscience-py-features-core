# From packages\cscience-feature-clip\tests\test_clip_feature.py
import unittest

from PIL import Image
from PIL.ImageFile import ImageFile

from cscience.features.api.registry.conversion_registry import ConversionRegistry
from cscience.features.api.utils.measure_time import measure_time
from cscience.features.clip.clip_connector import ClipConnector
from cscience.features.clip.clip_conversion_provider import ClipConversionProvider
from cscience.features.clip.clip_feature import ClipFeature


class FeatureTest(unittest.TestCase):

    N = 10
    @measure_time(times=N, ignore_first=True)
    def test_clip_text_to_vector(self):
        clip = ClipConnector()
        v = clip.text("Hello World")
        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_to_vector(self):
        clip = ClipConnector()
        i: ImageFile = Image.open("../resources/test/flickr-dog-1.jpg")
        v = clip.image(i)
        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_batch_to_vector_batch(self):
        ConversionRegistry.register("clip", ClipConversionProvider(ClipFeature().get_instance()))
        clip = ClipConnector()
        v = clip.text_batch(["Hello World", "Hello World", "Hello World and Moon"])

        self.assertEqual(v[0], v[1])
        self.assertNotEqual(v[0], v[2])
        self.assertNotEqual(v[1], v[2])


    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        ConversionRegistry.register("clip", ClipConversionProvider(ClipFeature().get_instance()))
        clip = ClipConnector()
        images: list[ImageFile] = [
            Image.open("../resources/test/flickr-dog-1.jpg"),
            Image.open("../resources/test/flickr-dog-1.jpg"),
            Image.open("../resources/test/flickr-dog-2.jpg"),
            Image.open("../resources/test/flickr-dog-2.jpg"),
            Image.open("../resources/test/flickr-house-1.jpg"),
            Image.open("../resources/test/flickr-house-1.jpg"),
            Image.open("../resources/test/flickr-house-2.jpg"),
            Image.open("../resources/test/flickr-house-2.jpg"),
            Image.open("../resources/test/flickr-hummingbird.jpg"),
            Image.open("../resources/test/flickr-hummingbird.jpg"),
            Image.open("../resources/test/flickr-monkeys.jpg"),
            Image.open("../resources/test/flickr-monkeys.jpg"),
            Image.open("../resources/test/flickr-mountains.jpg"),
            Image.open("../resources/test/flickr-mountains.jpg"),
            Image.open("../resources/test/flickr-sunset.jpg"),
            Image.open("../resources/test/flickr-sunset.jpg")
        ]
        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])

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
from PIL.ImageFile import ImageFile


from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo
from cscience.features.clip.clip_conversion_provider import ClipConversionProvider
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_image_batch import ClipImageBatch
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor
from cscience.features.clip.clip_datatypes.clip_tensor_batch import ClipTensorBatch
from cscience.features.clip.clip_feature import ClipFeature


class ClipConnector(ConnectorBase):
    """Public connector for CLIP text and image embeddings."""
    def __init__(self,) -> None:
        self.feature = ClipFeature().get_instance()
        super().__init__("clip", ClipConversionProvider(self.feature))

    def text(self, data: str) -> list[float]:
        """Embed a single text string and return one float vector."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=Text,
            input_feature_type=TextBatch,
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
            input_feature_type=ClipImageBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVector)
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


# From packages\cscience-feature-clip\src\cscience\features\clip\clip_conversion_provider.py
from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_image_batch import ClipImageBatch
from cscience.features.clip.clip_datatypes.clip_tensor_batch import ClipTensorBatch


class ClipConversionProvider(ConversionProviderBase):
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


# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatype.py
from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class ClipDatatype(DatatypeBase, ABC):
    namespace = "clip"

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_feature.py

from __future__ import annotations

import open_clip
import torch

from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase
from .clip_datatypes.clip_image_batch import ClipImageBatch
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch


class ClipFeature(FeatureBase):
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
        self.model = self.model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer(self._model_name)
        self._initialized = True


    @classmethod
    def text_batch(cls, texts: TextBatch) -> ClipTensorBatch:
        """Embed a batch of text strings into normalized CLIP vectors."""
        service = cls.get_instance()

        tokens = service.tokenizer(texts.data()).to(service.device)

        with torch.no_grad():
            feats = service.model.encode_text(tokens)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vecs = feats.detach().float().cpu()
        return ClipTensorBatch(vecs)

    @classmethod
    def image_batch(cls, images: ClipImageBatch) -> ClipTensorBatch:
        """Embed a batch of PIL images into normalized CLIP vectors."""
        service = cls.get_instance()

        image_tensors = torch.stack([
            service.preprocess(image)
            for image in images.data()
        ]).to(service._device)

        with torch.inference_mode():
            feats = service.model.encode_image(image_tensors)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vecs = feats.detach().float().cpu()

        return ClipTensorBatch(vecs)

# From packages\cscience-feature-clip\src\cscience\features\clip\__init__.py
## API
from cscience.features.api.registry.registry_base import RegistryBase

## Internal
from .clip_datatypes.clip_image import ClipImage
from .clip_datatypes.clip_image_batch import ClipImageBatch
from .clip_datatypes.clip_tensor import ClipTensor
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch
from .clip_datatype import ClipDatatype
from .clip_connector import ClipConnector
from .clip_feature import ClipFeature
from .clip_conversion_provider import ClipConversionProvider


__all__ = [
    "ClipImage",
    "ClipImageBatch",
    "ClipTensor",
    "ClipTensorBatch",
    "ClipDatatype",
    "ClipConnector",
    "ClipConversionProvider",
    "ClipFeature",
]

def register(registry: RegistryBase) -> None:
        registry.register("clip", ClipConversionProvider)

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_image.py
from PIL.ImageFile import ImageFile

from ..clip_datatype import ClipDatatype


class ClipImage(ClipDatatype):

    def __init__(self, data: ImageFile) -> None:
        super().__init__(data)


# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_image_batch.py
from PIL.ImageFile import ImageFile

from ..clip_datatype import ClipDatatype


class ClipImageBatch(ClipDatatype):

    def __init__(self, data: list[ImageFile]) -> None:
        super().__init__(data)

# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor.py
from torch import Tensor

from ..clip_datatype import ClipDatatype


class ClipTensor(ClipDatatype):
    """Single CLIP embedding tensor with shape [d]."""

    def __init__(self, data:Tensor) -> None:
        super().__init__(data)


# From packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor_batch.py
from torch import Tensor

from ..clip_datatype import ClipDatatype


class ClipTensorBatch(ClipDatatype):
    """Batch of CLIP embedding tensors with shape [n, d]."""
    def __init__(self, data: Tensor) -> None:
        super().__init__(data)



