# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\tests\test_clip_feature.py
import unittest

from PIL import Image
from PIL.ImageFile import ImageFile

from cscience.features.api.registry.conversion_registry import ConversionRegistry
from cscience.features.api.utils.measure_time import measure_time
from cscience.features.clip import ClipConnector, ClipConversionProvider, ClipFeature


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


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_config.py
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


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_connector.py
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
from cscience.features.clip.clip_conversion_provider import ClipConversionProvider
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_image_batch import ClipImageBatch
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor
from cscience.features.clip.clip_datatypes.clip_tensor_batch import ClipTensorBatch
from cscience.features.clip.clip_feature import ClipFeature


class ClipConnector(ConnectorBase):

    def __init__(self,) -> None:
        self.feature = ClipFeature().get_instance()
        super().__init__("clip", ClipConversionProvider(self.feature))

    def text(self, data: str) -> list[float]:
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=Text,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensorBatch,
            output_type= FloatVector)
        return function(Text(data)).data()

    def text_batch(self, data: list[str]) -> dict[int,list[float]]:
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=TextBatch,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensorBatch,
            output_type= FloatVectorBatch)
        return function(TextBatch(data)).data()

    def image(self, data: ImageFile) -> list[float]:
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_batch,
            input_type=ClipImage,
            input_feature_type=ClipImageBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVector)
        return function(ClipImage(data)).data()

    def image_batch(self, data: list[ImageFile]) -> dict[int, list[float]]:
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


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_conversion_provider.py
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

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        converters = [
            Converter[ClipImage, ClipImageBatch]
                (
                name="image_batch_passtrough_wrapper",
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
                name="tenor_batch_to_float_vector",
                source=self._feature,
                function=lambda x: FloatVector(x.data()[0].tolist()),
                input_type=ClipTensorBatch,
                output_type=FloatVector
            ),
            Converter[ClipTensorBatch, FloatVectorBatch]
                (
                name="tensor_to_float_vector_batch",
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


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_datatype.py
from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class ClipDatatype(DatatypeBase, ABC):
    namespace = "clip"

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_feature.py

from __future__ import annotations

from typing import List

import open_clip
import torch
from torch import Tensor

from PIL.ImageFile import ImageFile

from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_image_batch import ClipImageBatch
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor
from cscience.features.clip.clip_datatypes.clip_tensor_batch import ClipTensorBatch


class ClipFeature(FeatureBase):

    def _initialize(self) -> None:
        if self._initialized:
            return
        self._model_name = "xlm-roberta-base-ViT-B-32"
        self._pretrained = "laion5b_s13b_b90k"

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name = self._model_name,
            pretrained= self._pretrained,
        )
        self._model = self._model.to(self._device).eval()
        self._tokenizer = open_clip.get_tokenizer(self._model_name)
        self._initialized = True


    @classmethod
    def text_batch(cls, texts: TextBatch) -> ClipTensorBatch:
        service = cls.get_instance()

        tokens = service._tokenizer(texts.data()).to(service._device)

        with torch.no_grad():
            feats = service._model.encode_text(tokens)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vecs = feats.detach().float().cpu()
        return ClipTensorBatch(vecs)

    @classmethod
    def image_batch(cls, images: ClipImageBatch) -> ClipTensorBatch:
        service = cls.get_instance()

        image_tensors = torch.stack([
            service.preprocess(image)
            for image in images.data()
        ]).to(service._device)

        with torch.inference_mode():
            feats = service._model.encode_image(image_tensors)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vecs = feats.detach().float().cpu()

        return ClipTensorBatch(vecs)

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\__init__.py
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

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_image.py
from PIL.ImageFile import ImageFile

from ..clip_datatype import ClipDatatype


class ClipImage(ClipDatatype):

    def __init__(self, data: ImageFile) -> None:
        super().__init__(data)


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_image_batch.py
from PIL.ImageFile import ImageFile

from ..clip_datatype import ClipDatatype


class ClipImageBatch(ClipDatatype):

    def __init__(self, data: list[ImageFile]) -> None:
        super().__init__(data)

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor.py
from torch import Tensor

from ..clip_datatype import ClipDatatype


class ClipTensor(ClipDatatype):
    """Single CLIP embedding tensor with shape [d]."""

    def __init__(self, data:Tensor) -> None:
        super().__init__(data)


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor_batch.py
from torch import Tensor

from ..clip_datatype import ClipDatatype


class ClipTensorBatch(ClipDatatype):
    """Batch of CLIP embedding tensors with shape [n, d]."""
    def __init__(self, data: Tensor) -> None:
        super().__init__(data)



# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\tests\test_config.py
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

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\tests\test_conversion.py


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\tests\test_feature.py
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

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\tests\test_service_info.py


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\__init__.py
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
# Datatypes
from .datatypes.core_datatypes.float_vector import FloatVector
from .datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from .datatypes.core_datatypes.text import Text
from .datatypes.core_datatypes.text_batch import TextBatch
from .datatypes.core_convertion_provider import CoreConvertionProvider
from .datatypes.core_datatype import CoreDatatype
from .datatypes.datatype_base import DatatypeBase
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
    # Datatypes
    "FloatVector",
    "FloatVectorBatch",
    "Text",
    "TextBatch",
    "CoreConvertionProvider",
    "CoreDatatype",
    "DatatypeBase",
    # Features
    "FeatureBase",
    "FeatureInfo",
    "ServiceInfo",
    # Registry
    "ConversionRegistry",
    "RegistryBase",
    # Utils
    "measure_time"
]



# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\config\config_base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from abc import ABC, abstractmethod

from pydantic import BaseModel


class ConfigBase(ABC, BaseModel):

    @classmethod
    @abstractmethod
    def _namespace(cls): raise NotImplementedError



# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\connector\connector_base.py
from abc import ABC, abstractmethod

from ..conversion.conversion_provider_base import ConversionProviderBase
from ..datatypes.core_convertion_provider import CoreConvertionProvider
from ..feature.core_feature import CoreFeature
from ..feature.feature_info import FeatureInfo
from ..feature.service_info import ServiceInfo
from ..registry.conversion_registry import ConversionRegistry


class ConnectorBase(ABC):

    def __init__(self, name:str, conversion_provider: ConversionProviderBase):
        core_conversion_provider = CoreConvertionProvider(CoreFeature().get_instance())
        ConversionRegistry.register("core", core_conversion_provider)
        ConversionRegistry.register(name, conversion_provider)

    @abstractmethod
    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError

    @abstractmethod
    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\connector\function_connector.py
from typing import TypeVar, Generic, Callable

from ..conversion.conversion_key import ConversionKey
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..conversion.search_strategy_most_specific import SearchStrategyMostSpecific
from ..datatypes.datatype_base import DatatypeBase

from ..feature.feature_base import FeatureBase
from ..registry.conversion_registry import ConversionRegistry

Tin = TypeVar('Tin', bound=DatatypeBase)
Tfi = TypeVar('Tfi', bound=DatatypeBase)
Tfo = TypeVar('Tfo', bound=DatatypeBase)
Tout = TypeVar('Tout', bound=DatatypeBase)


class FunctionConnector(Generic[Tin, Tfi, Tfo, Tout]):

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
        return self.wrapped(x)


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\conversion\conversion_key.py
from dataclasses import dataclass

from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase



from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ConversionKey:
    source: type[FeatureBase]
    input_type: type[DatatypeBase]
    output_type: type[DatatypeBase]

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\conversion\conversion_provider_base.py
from abc import ABC, abstractmethod
from typing import List

from .converter import Converter
from ..feature.feature_base import FeatureBase


class ConversionProviderBase(ABC):

    def __init__(self, feature: FeatureBase) -> None:
        self._feature = feature

    @abstractmethod
    def register_converters(self) -> List[Converter]:
        pass


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\conversion\converter.py
from typing import Callable, Generic, TypeVar

from .conversion_key import ConversionKey
from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase

Tin = TypeVar('Tin', bound=DatatypeBase, contravariant=True)
Tout = TypeVar('Tout', bound=DatatypeBase, covariant=True)


class Converter(Generic[Tin, Tout]):
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
        return self._function(data)

    def get_identifier(self) -> ConversionKey:
        return ConversionKey(type(self._source), self._input_type, self._output_type)


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\conversion\search_strategy_base.py


from abc import ABC, abstractmethod

from .conversion_key import ConversionKey
from .converter import Converter
from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase


class SearchStrategyBase(ABC):

    def __init__(self, conversion_key: ConversionKey) -> None:
        self._conversion_key = conversion_key
        pass

    @abstractmethod
    def search(self, recordset: dict[ConversionKey, Converter]) -> Converter:
        pass


    def __str__(self) -> str:
        return str(self._conversion_key)


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\conversion\search_strategy_most_specific.py
from .conversion_key import ConversionKey
from .converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..datatypes.datatype_base import DatatypeBase
from ..feature.core_feature import CoreFeature
from ..feature.feature_base import FeatureBase


class SearchStrategyMostSpecific(SearchStrategyBase):

    def __init__(self, conversion_key: ConversionKey):
        super().__init__(conversion_key)

    def search(self,
               recordset: dict[ConversionKey, Converter]) -> Converter:

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

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\core_convertion_provider.py
from typing import List

from ..conversion.converter import Converter
from ..feature.feature_base import FeatureBase
from ..registry.conversion_registry import ConversionRegistry


from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase



class CoreConvertionProvider(ConversionProviderBase):

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        converters = [
            Converter[Text, Text]
                (
                name="text_to_list",
                source=self._feature,
                function=lambda x: Text(x.data()),
                input_type=Text,
                output_type=Text
            ),
            Converter[Text, TextBatch]
                (
                name="text_to_list",
                source=self._feature,
                function=lambda x: TextBatch([x.data()]),
                input_type=Text,
                output_type=TextBatch
            ),
            Converter[TextBatch, TextBatch]
                (
                name="text_batch_passthrough",
                source=self._feature,
                function=lambda x: x,
                input_type=TextBatch,
                output_type=TextBatch
            ),
            Converter[FloatVector, FloatVector]
                (
                name="float_vector_paththrough",
                source=self._feature,
                function=lambda x: x,
                input_type=FloatVector,
                output_type=FloatVector
            ),
            Converter[FloatVector, FloatVectorBatch]
                (
                name="float_vector_to_float_vector_batch",
                source=self._feature,
                function=lambda x: FloatVectorBatch({0: x.data()}),
                input_type=FloatVector,
                output_type=FloatVectorBatch
            ),
            Converter[FloatVectorBatch, FloatVectorBatch]
                (
                name="float_vector_batch_paththrough",
                source=self._feature,
                function=lambda x: x,
                input_type=FloatVectorBatch,
                output_type=FloatVectorBatch
            )
        ]
        return converters


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\core_datatype.py
from abc import ABC
from typing import Generic, TypeVar

from .datatype_base import DatatypeBase
T = TypeVar("T")



class CoreDatatype(DatatypeBase[T], ABC, Generic[T]):
    namespace = "core"


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\datatype_base.py
from abc import ABC, abstractmethod, abstractproperty
from typing import Any, TypeVar, Generic

T = TypeVar('T')

class DatatypeBase(ABC, Generic[T]):

    def __init__(self, data: T) -> None:
        self._data = data

    def data(self) -> T:
        return self._data

    @staticmethod
    def fullname(o: object) -> str:
        module = o.__class__.__module__
        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__
        return module + '.' + o.__class__.__name__


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\feature\core_feature.py
from cscience.features.api.feature.feature_base import FeatureBase

class CoreFeature(FeatureBase):

    def _initialize(self) -> None:
        pass

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\feature\feature_base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class FeatureBase(ABC):
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
        return cls()

    @abstractmethod
    def _initialize(self) -> None:
        """
        Load expensive resources here, e.g. model weights.
        Called exactly once per concrete feature class.
        """
        pass

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\feature\feature_info.py
class FeatureInfo:
    pass

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\feature\service_info.py


class ServiceInfo:
    pass

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\registry\conversion_registry.py
from ..conversion.conversion_key import ConversionKey
from ..conversion.conversion_provider_base import ConversionProviderBase
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..registry.registry_base import RegistryBase, Tin


class ConversionRegistry(RegistryBase[ConversionProviderBase]):

    @classmethod
    def _initialize(cls) -> None:
        cls._converters  = {}
        pass

    _converters: dict[ConversionKey, Converter] = None

    @classmethod
    def get_converters(cls) -> dict[ConversionKey, Converter]:
        return cls._converters

    @classmethod
    def register(cls, name: str, provider: Tin) -> None:
        for converter in provider.register_converters():
            cls.get_instance().get_converters()[converter.get_identifier()] = converter

    @classmethod
    def has_best_effort_converter(cls, strategy: SearchStrategyBase) -> bool:
        try:
            strategy.search(cls.get_instance().get_converters())
            return True
        except LookupError:
            return False

    @classmethod
    def get_best_effort_converter(cls, strategy: SearchStrategyBase) -> Converter:
        try:
            return strategy.search(cls.get_instance().get_converters())
        except LookupError as ex:
            raise LookupError(f"No best effort converter found for strategy: {strategy}") from ex

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\registry\registry_base.py
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


# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\utils\measure_time.py
import timeit


def measure_time(times: int=1, ignore_first: bool=False):
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

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\core_datatypes\float_vector.py
from .vector_base import VectorBase
from ..core_datatype import CoreDatatype


class FloatVector(VectorBase[list[float]], CoreDatatype[list[float]]):

    def __init__(self, data:list[float], assert_length: int|None=None) -> None:
        super().__init__(data, assert_length)

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\core_datatypes\float_vector_batch.py
from .vector_base import VectorBase
from ..core_datatype import CoreDatatype

class FloatVectorBatch(VectorBase[dict[int,list[float]]]):

    def __init__(self, data: dict[int,list[float]],assert_length: int|None=None) -> None:
        super().__init__(data, assert_length)

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\core_datatypes\text.py
from ..core_datatype import CoreDatatype

class Text(CoreDatatype[str]):

    def __init__(self, data:str) -> None:
        super().__init__(data)

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\core_datatypes\text_batch.py
from typing import Any

from ..core_datatype import CoreDatatype

class TextBatch(CoreDatatype):


    def __init__(self, data: list[str]) -> None:
        super().__init__(data)

# From D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-api\src\cscience\features\api\datatypes\core_datatypes\vector_base.py
from abc import ABC
from typing import Any, Generic, TypeVar

from ..datatype_base import DatatypeBase

T = TypeVar("T")



class VectorBase(DatatypeBase[T], ABC, Generic[T]):

    def __init__(self, data:T, assert_length: int|None=None):
        if assert_length is None:
            super().__init__(data)
        else:
            if len(data) != assert_length:
                raise ValueError("Data length does not match the expected length")
            super().__init__(data)

    def length(self) -> int:
        return len(self.data())

