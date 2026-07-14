from cscience.features.api.config.core_config import CoreConfig
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.api.feature.feature_info import FeatureInfo


class CoreFeature(FeatureBase):
    """
    This is a helper feature for register core converters.
    """

    def _initialize(self, config: CoreConfig) -> None:
        pass

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device="none",
            configuration=self._config.model_dump(mode="json"),
        )