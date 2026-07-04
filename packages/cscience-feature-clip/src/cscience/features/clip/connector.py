from typing import List
from PIL.ImageFile import ImageFile
from torch import Tensor
from torch._C import TensorType

from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo
from cscience.features.clip.feature import ClipFeature

from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor


class ClipConnector(ConnectorBase):

    @staticmethod
    def clip_text(data: str) -> List[float]:
        fnc = FunctionConnector(
            feature=ClipFeature().get_instance(),
            feature_fnc=ClipFeature().get_instance().clip_text,
            input_type=Text,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensor,
            output_type= FloatVector)
        return fnc(Text(data)).data()

    @staticmethod
    def clip_image(data: ImageFile) -> List[float]:
        fnc = FunctionConnector(
            feature=ClipFeature().get_instance(),
            feature_fnc=ClipFeature().get_instance().clip_image,
            input_type=ClipImage,
            input_feature_type=ClipImage,
            output_feature_type=ClipTensor,
            output_type=FloatVector)
        return fnc(ClipImage(data)).data()


    @staticmethod
    def get_service_info() -> ServiceInfo:
        pass

    @staticmethod
    def get_feature_info() -> FeatureInfo:
        pass
