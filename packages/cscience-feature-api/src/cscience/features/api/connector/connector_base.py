from abc import ABC

from mypy.checker_shared import abstractmethod

from feature.feature_info import FeatureInfo
from feature.service_info import ServiceInfo


class ConnectorBase(ABC):


    @staticmethod
    @abstractmethod
    def get_feature_info() -> FeatureInfo:
        return FeatureInfo()

    @staticmethod
    @abstractmethod
    def get_service_info() -> ServiceInfo:
        return ServiceInfo()