# packages/cscience-feature-clip-spatial/src/cscience/features/clip_spatial/clip_spatial_conversion_provider.py

from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    SpatialFloatVectorBatch,
    SpatialVectorBatchData,
)

from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch





class ClipSpatialConversionProvider(ConversionProviderBase):
    """Registers conversions required by CLIP Spatial."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[ClipSpatialTensorBatch, ClipSpatialTensorBatch](
                name="clip_spatial_tensor_batch_passthrough",
                source=self._feature,
                function=self.clip_spatial_tensor_batch_passthrough,
                input_type=ClipSpatialTensorBatch,
                output_type=ClipSpatialTensorBatch,
            ),
            Converter[ClipSpatialTensorBatch, SpatialFloatVectorBatch](
                name="clip_spatial_tensor_batch_to_spatial_float_vector_batch",
                source=self._feature,
                function=self.clip_spatial_tensor_batch_to_spatial_float_vector_batch,
                input_type=ClipSpatialTensorBatch,
                output_type=SpatialFloatVectorBatch,
            ),
        ]


    def clip_spatial_tensor_batch_passthrough(
            self,
            batch: ClipSpatialTensorBatch,
    ) -> ClipSpatialTensorBatch:
        return batch


    def clip_spatial_tensor_batch_to_spatial_float_vector_batch(
            self,
            batch: ClipSpatialTensorBatch,
    ) -> SpatialFloatVectorBatch:
        return SpatialFloatVectorBatch(
            SpatialVectorBatchData(
                vectors={
                    flat_index: [
                        float(value)
                        for value in vector.detach().cpu().tolist()
                    ]
                    for flat_index, vector in batch.ordered_items()
                },
                layout=batch.layout,
                item_keys=batch.item_keys,
                regions=batch.regions,
            )
        )