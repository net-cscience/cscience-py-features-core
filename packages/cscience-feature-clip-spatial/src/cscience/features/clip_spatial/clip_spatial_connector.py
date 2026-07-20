from PIL.Image import Image

from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FloatVector,
    FloatVectorBatch,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
    SpatialFloatVectorBatch,
    SpatialVectorBatchData,
    Text,
    TextBatch,
)

from .clip_spatial_config import ClipSpatialConfig
from .clip_spatial_conversion_provider import (
    ClipSpatialConversionProvider,
)
from .clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_image_pair import (
    ClipSpatialTextImagePair,
)
from .clip_spatial_datatypes.clip_spatial_text_image_pair_data import (
    ClipSpatialTextImagePairData,
)
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_vector_pair import (
    ClipSpatialTextVectorPair,
)
from .clip_spatial_datatypes.clip_spatial_text_vector_pair_data import (
    ClipSpatialTextVectorPairData,
)
from .clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)
from .clip_spatial_feature import ClipSpatialFeature


class ClipSpatialConnector(ConnectorBase):
    """Public connector for CLIP Spatial."""

    def __init__(self, config: ClipSpatialConfig) -> None:
        self.feature = ClipSpatialFeature.get_instance(
            config,
            init_if_missing=True,
        )

        self._conversion_provider = ClipSpatialConversionProvider(
            self.feature
        )

        super().__init__(self._conversion_provider)

    def text(
            self,
            data: str,
    ) -> list[float]:
        """Embed a single text string."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=Text,
            input_feature_type=TextBatch,
            output_feature_type=ClipSpatialTextTensorBatch,
            output_type=FloatVector,
        )

        return function(
            Text(data)
        ).data()

    def text_batch(
            self,
            data: list[str],
    ) -> dict[int, list[float]]:
        """Embed text strings indexed by input position."""
        text_batch = TextBatch(
            {
                index: text
                for index, text in enumerate(data)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=TextBatch,
            input_feature_type=TextBatch,
            output_feature_type=ClipSpatialTextTensorBatch,
            output_type=FloatVectorBatch,
        )

        return function(
            text_batch
        ).data()

    def image_regions(
            self,
            data: Image,
    ) -> SpatialVectorBatchData[list[float]]:
        """Embed spatial regions of one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_region_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipSpatialTensorBatch,
            output_type=SpatialFloatVectorBatch,
        )

        return function(
            PilImage(data)
        ).data()

    def image_region_batch(
            self,
            data: list[Image],
    ) -> SpatialVectorBatchData[list[float]]:
        """Embed spatial regions of an image batch."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(data)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_region_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipSpatialTensorBatch,
            output_type=SpatialFloatVectorBatch,
        )

        return function(
            image_batch
        ).data()

    def score_regions(
            self,
            texts: list[str],
            spatial_vectors: SpatialVectorBatchData[list[float]],
    ) -> SpatialScoreVectorBatch:
        """Score text queries against existing spatial embeddings."""
        text_batch = TextBatch(
            {
                index: text
                for index, text in enumerate(texts)
            }
        )

        public_vectors = SpatialFloatVectorBatch(
            spatial_vectors
        )

        feature_vectors = (
            self._conversion_provider
            .spatial_float_vector_batch_to_clip_spatial_tensor_batch(
                public_vectors
            )
        )

        pair: ClipSpatialTextVectorPair = ClipSpatialTextVectorPair(
            ClipSpatialTextVectorPairData(
                texts=text_batch,
                vectors=feature_vectors,
            )
        )

        function = FunctionConnector[
            ClipSpatialTextVectorPair,
            ClipSpatialTextVectorPair, SpatialScoreVectorBatch, SpatialScoreVectorBatch](
            feature=self.feature,
            function=self.feature.score_text_vector_batch,
            input_type=ClipSpatialTextVectorPair,
            input_feature_type=ClipSpatialTextVectorPair,
            output_feature_type=SpatialScoreVectorBatch,
            output_type=SpatialScoreVectorBatch,
        )

        return function(pair)

    def score_images(
            self,
            texts: list[str],
            images: list[Image],
    ) -> SpatialScoreVectorBatch:
        """Create spatial embeddings and score text queries."""
        pair = ClipSpatialTextImagePair(
            ClipSpatialTextImagePairData(
                texts=TextBatch(
                    {
                        index: text
                        for index, text in enumerate(texts)
                    }
                ),
                images=PilImageBatch(
                    {
                        index: image
                        for index, image in enumerate(images)
                    }
                ),
            )
        )

        function = (FunctionConnector(
            feature=self.feature,
            function=self.feature.score_text_image_batch,
            input_type=ClipSpatialTextImagePair,
            input_feature_type=ClipSpatialTextImagePair,
            output_feature_type=SpatialScoreVectorBatch,
            output_type=SpatialScoreVectorBatch,
        ))

        return function(pair)

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="clip_spatial",
            name="CLIP Spatial",
            description=(
                "Spatial CLIP embedding and "
                "text-to-region similarity scoring"
            ),
            operations=ServiceInfo.generate_operations(cls),
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()
