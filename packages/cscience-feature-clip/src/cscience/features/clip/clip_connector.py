from PIL.Image import Image

from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.datatypes.image.pil_image import PilImage
from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo
from .clip_config import ClipConfig

from .clip_conversion_provider import ClipConversionProvider
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch
from .clip_feature import ClipFeature


class ClipConnector(ConnectorBase):
    """Public connector for CLIP text and image embeddings."""

    def __init__(self,  config: ClipConfig) -> None:
        self.feature = ClipFeature.get_instance(config, init_if_missing=True)
        super().__init__(ClipConversionProvider(self.feature))

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

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="clip",
            name="CLIP",
            description="Text and image embedding service.",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()