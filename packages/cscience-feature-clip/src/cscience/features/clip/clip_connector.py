from PIL.ImageFile import ImageFile
from multipledispatch  import dispatch

from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.conversion import conversion_provider_base
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo
from cscience.features.clip.convertion_provider import ClipConvertionProvider
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_image_batch import ClipImageBatch
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor
from cscience.features.clip.feature import ClipFeature


class ClipConnector(ConnectorBase):

    def __init__(self,) -> None:
        self.feature = ClipFeature().get_instance()
        super().__init__("clip", ClipConvertionProvider(self.feature))

    def text(self, data: str) -> list[float]:
        fnc = FunctionConnector(
            feature=self.feature,
            feature_fnc=self.feature.text,
            input_type=Text,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensor,
            output_type= FloatVector)
        return fnc(Text(data)).data()

    def text_batch(self, data: list[str]) -> dict[int,list[float]]:
        fnc = FunctionConnector(
            feature=self.feature,
            feature_fnc=self.feature.text,
            input_type=TextBatch,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensor,
            output_type= FloatVectorBatch)
        return fnc(TextBatch(data)).data()

    def image(self, data: ImageFile) -> list[float]:
        fnc = FunctionConnector(
            feature=self.feature,
            feature_fnc=self.feature.image,
            input_type=ClipImage,
            input_feature_type=ClipImage,
            output_feature_type=ClipTensor,
            output_type=FloatVector)
        return fnc(ClipImage(data)).data()



    def image_batch(self, data: list[ImageFile]) -> dict[int, list[float]]:
        fnc = FunctionConnector(
            feature=self.feature,
            feature_fnc=self.feature.image,
            input_type=ClipImageBatch,
            input_feature_type=ClipImageBatch,
            output_feature_type=ClipTensor,
            output_type=FloatVectorBatch)
        return fnc(ClipImageBatch(data)).data()


    def get_service_info(self) -> ServiceInfo:
        pass


    def get_feature_info(self) -> FeatureInfo:
        pass
