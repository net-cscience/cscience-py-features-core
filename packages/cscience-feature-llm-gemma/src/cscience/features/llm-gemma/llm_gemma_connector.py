from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from .llm_gemma_config import LlmGemmaConfig
from .llm_gemma_conversion_provider import LlmGemmaConversionProvider
from .llm_gemma_feature import LlmGemmaFeature


class LlmGemmaConnector(ConnectorBase):
    """Public connector for Google Gemma language-model inference."""

    def __init__(self, config: LlmGemmaConfig) -> None:
        self.feature = LlmGemmaFeature.get_instance(config, init_if_missing=True)
        super().__init__(LlmGemmaConversionProvider(self.feature))

    def query(self, data: str) -> str:
        """Generate a response for a text query."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.query,
            input_type=Text,
            input_feature_type=Text,
            output_feature_type=Text,
            output_type=Text,
        )

        return function(Text(data)).data()

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="llm_gemma",
            name="Gemma",
            description="Google Gemma language-model service.",
            operations=ServiceInfo.generate_operations(cls),
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()