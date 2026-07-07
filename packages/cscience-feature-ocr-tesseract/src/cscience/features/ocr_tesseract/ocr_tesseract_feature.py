from cscience.features.api.feature.feature_base import FeatureBase


class OcrTesseractFeature(FeatureBase):
    """OcrTesseract feature service."""

    def _initialize(self) -> None:
        if self._initialized:
            return

        self._initialized = True
