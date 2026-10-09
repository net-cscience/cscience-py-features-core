from google import genai

from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.api.feature.feature_info import FeatureInfo

from .llm_gemma_config import LlmGemmaConfig


class LlmGemmaFeature(FeatureBase["LlmGemmaFeature", LlmGemmaConfig]):
    """Google Gemma language-model feature."""

    def _initialize(self, config: LlmGemmaConfig) -> None:
        self._client = genai.Client()

    def query(self, text: Text) -> Text:
        response = self._client.models.generate_content(
            model=self._config.model,
            contents=text.data(),
        )

        return Text(response.text)

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model,
            device="remote",
            configuration=self._config.model_dump(mode="json"),
        )