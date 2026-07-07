from cscience.features.api.feature.feature_base import FeatureBase


class NsfwImageFeature(FeatureBase):
    """NsfwImage feature service."""

    def _initialize(self) -> None:
        if self._initialized:
            return

        self._initialized = True
