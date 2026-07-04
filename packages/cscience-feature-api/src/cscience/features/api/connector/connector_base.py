from abc import ABC, abstractmethod

from ..feature.feature_info import FeatureInfo
from ..feature.service_info import ServiceInfo


class ConnectorBase(ABC):
    @classmethod
    @abstractmethod
    def get_feature_info(cls) -> FeatureInfo:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_service_info(cls) -> ServiceInfo:
        raise NotImplementedError