from typing import List
from PIL.ImageFile import ImageFile
from torch import Tensor

from clip.feature import ClipFeature
from connector.connector_base import ConnectorBase
from connector.function_connector import FunctionConnector
from feature.feature_info import FeatureInfo
from feature.service_info import ServiceInfo


class ClipConnector(ConnectorBase):

    @staticmethod
    def clip_text(data: str) -> List[float]:
        fnc = FunctionConnector(
            feature=ClipFeature().get_instance(),
            feature_fnc=ClipFeature().get_instance().clip_text,
            input_type=str,
            feature_input_type=List[str],
            feature_output_type=Tensor,
            output_type=List[float])
        return fnc(data)

    @staticmethod
    def clip_image(data: ImageFile) -> List[float]:
        fnc = FunctionConnector(
            feature=ClipFeature().get_instance(),
            feature_fnc=ClipFeature().get_instance().clip_image,
            input_type=ImageFile,
            feature_input_type=ImageFile,
            feature_output_type=Tensor,
            output_type=List[float])
        return fnc(data)


    @staticmethod
    def get_service_info() -> ServiceInfo:
        pass

    @staticmethod
    def get_feature_info() -> FeatureInfo:
        pass
