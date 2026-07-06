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