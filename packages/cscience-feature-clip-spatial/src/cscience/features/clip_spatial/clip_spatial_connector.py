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
