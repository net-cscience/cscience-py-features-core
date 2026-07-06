from abc import ABC, abstractmethod

from ..conversion.conversion_provider_base import ConversionProviderBase
from ..datatypes.core_conversion_provider import CoreConversionProvider
from ..feature.core_feature import CoreFeature
from ..feature.feature_info import FeatureInfo
from ..feature.service_info import ServiceInfo
from ..registry.conversion_registry import ConversionRegistry


class ConnectorBase(ABC):
    """Base class for public feature connectors.

    A connector registers core conversions and feature-specific conversions,
    then exposes convenient methods using normal Python input and output types.
    """

    def __init__(self, name:str, conversion_provider: ConversionProviderBase):
        """Register core conversions and the connector's feature conversions."""
        core_conversion_provider = CoreConversionProvider(CoreFeature().get_instance())
        ConversionRegistry.register("core", core_conversion_provider)
        ConversionRegistry.register(name, conversion_provider)

    @abstractmethod
    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError

    @abstractmethod
    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError