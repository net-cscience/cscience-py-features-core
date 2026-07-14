from PIL.Image import Image

from cscience.features.api import (
    BoolValue,
    ConnectorBase,
    FeatureInfo,
    FloatValue,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
)
from .nsfw_config import NsfwConfig

from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction, NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import NsfwPredictionBatch
from .nsfw_image_feature import NsfwImageFeature


class NsfwImageConnector(ConnectorBase):
    """Public connector for NSFW image classification."""

    def __init__(self, config: NsfwConfig) -> None:
        self.feature = NsfwImageFeature.get_instance(config)
        super().__init__( NsfwImageConversionProvider(self.feature))

    def classify(self, image: Image) -> NsfwPredictionData:
        """Classify a single image and return the full prediction."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=NsfwPrediction,
        )

        return function(PilImage(image)).data()

    def classify_batch(self, images: list[Image]) -> dict[int, NsfwPredictionData]:
        """Classify images and return predictions indexed by input position."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=NsfwPredictionBatch,
        )

        return function(image_batch).data().predictions

    def score(self, image: Image) -> float:
        """Return the NSFW score for a single image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=FloatValue,
        )

        return function(PilImage(image)).data()

    def is_nsfw(self, image: Image, threshold: float = 0.5) -> bool:
        """Return whether a single image is classified as NSFW."""
        prediction = self.classify(image)
        return prediction.is_nsfw(threshold)

    def is_nsfw_default(self, image: Image) -> bool:
        """Return whether a single image is NSFW using the converter default threshold."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=BoolValue,
        )

        return function(PilImage(image)).data()

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="nsfw_image",
            name="NSFW Image Classification",
            description="NSFW image classification service",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()