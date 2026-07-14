# packages/cscience-feature-clip-spatial/src/cscience/features/clip_spatial/clip_spatial_connector.py

from PIL.Image import Image

from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
    SpatialFloatVectorBatch,
)
from .clip_spatial_config import ClipSpatialConfig

from .clip_spatial_conversion_provider import ClipSpatialConversionProvider
from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch
from .clip_spatial_feature import ClipSpatialFeature


class ClipSpatialConnector(ConnectorBase):
    """Public connector for CLIP Spatial region embeddings."""

    def __init__(self, config: ClipSpatialConfig) -> None:
        self.feature = ClipSpatialFeature.get_instance(config, init_if_missing=True)
        super().__init__( ClipSpatialConversionProvider(self.feature))

    def image_regions(self, image: Image) -> SpatialFloatVectorBatch:
        """Embed spatial regions of one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_region_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipSpatialTensorBatch,
            output_type=SpatialFloatVectorBatch,
        )

        return function(PilImage(image)).data()

    def image_region_batch(
        self,
        images: list[Image],
    ) -> SpatialFloatVectorBatch:
        """Embed spatial regions of an image batch."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
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

        return function(image_batch).data()






    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="clip_spatial",
            name="Clip spatial regions",
            description="Clip spatial region embedding",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()