from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_feature import NsfwImageFeature


class NsfwImageConnector(ConnectorBase):
    """Public connector for the nsfw_image feature."""

    def __init__(self) -> None:
        self.feature = NsfwImageFeature.get_instance()
        super().__init__("nsfw_image", NsfwImageConversionProvider(self.feature))

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")
