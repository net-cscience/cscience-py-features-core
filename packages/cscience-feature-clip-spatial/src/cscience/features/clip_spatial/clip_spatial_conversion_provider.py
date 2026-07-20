import torch

from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    FloatVector,
    FloatVectorBatch,
    SpatialFloatVectorBatch,
    SpatialVectorBatchData,
)

from .clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_image_pair import (
    ClipSpatialTextImagePair,
)
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_vector_pair import (
    ClipSpatialTextVectorPair,
)
from .clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)


class ClipSpatialConversionProvider(ConversionProviderBase):
    """Registers conversions required by CLIP Spatial."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[
                ClipSpatialTensorBatch,
                ClipSpatialTensorBatch,
            ](
                name="clip_spatial_tensor_batch_passthrough",
                source=self._feature,
                function=self.clip_spatial_tensor_batch_passthrough,
                input_type=ClipSpatialTensorBatch,
                output_type=ClipSpatialTensorBatch,
            ),
            Converter[
                ClipSpatialTensorBatch,
                SpatialFloatVectorBatch,
            ](
                name=(
                    "clip_spatial_tensor_batch_to_"
                    "spatial_float_vector_batch"
                ),
                source=self._feature,
                function=(
                    self.clip_spatial_tensor_batch_to_spatial_float_vector_batch
                ),
                input_type=ClipSpatialTensorBatch,
                output_type=SpatialFloatVectorBatch,
            ),
            Converter[
                SpatialFloatVectorBatch,
                ClipSpatialTensorBatch,
            ](
                name=(
                    "spatial_float_vector_batch_to_"
                    "clip_spatial_tensor_batch"
                ),
                source=self._feature,
                function=(
                    self.spatial_float_vector_batch_to_clip_spatial_tensor_batch
                ),
                input_type=SpatialFloatVectorBatch,
                output_type=ClipSpatialTensorBatch,
            ),
            Converter[
                ClipSpatialTextTensorBatch,
                FloatVector,
            ](
                name="clip_spatial_text_tensor_batch_to_float_vector",
                source=self._feature,
                function=(
                    self.clip_spatial_text_tensor_batch_to_float_vector
                ),
                input_type=ClipSpatialTextTensorBatch,
                output_type=FloatVector,
            ),
            Converter[
                ClipSpatialTextTensorBatch,
                FloatVectorBatch,
            ](
                name=(
                    "clip_spatial_text_tensor_batch_to_"
                    "float_vector_batch"
                ),
                source=self._feature,
                function=(
                    self.clip_spatial_text_tensor_batch_to_float_vector_batch
                ),
                input_type=ClipSpatialTextTensorBatch,
                output_type=FloatVectorBatch,
            ),
            Converter[
                ClipSpatialTextVectorPair,
                ClipSpatialTextVectorPair,
            ](
                name="clip_spatial_text_vector_pair_passthrough",
                source=self._feature,
                function=self.clip_spatial_text_vector_pair_passthrough,
                input_type=ClipSpatialTextVectorPair,
                output_type=ClipSpatialTextVectorPair,
            ),
            Converter[
                ClipSpatialTextImagePair,
                ClipSpatialTextImagePair,
            ](
                name="clip_spatial_text_image_pair_passthrough",
                source=self._feature,
                function=self.clip_spatial_text_image_pair_passthrough,
                input_type=ClipSpatialTextImagePair,
                output_type=ClipSpatialTextImagePair,
            ),
            Converter[
                SpatialScoreVectorBatch,
                SpatialScoreVectorBatch,
            ](
                name="spatial_score_vector_batch_passthrough",
                source=self._feature,
                function=self.spatial_score_vector_batch_passthrough,
                input_type=SpatialScoreVectorBatch,
                output_type=SpatialScoreVectorBatch,
            ),
        ]

    def clip_spatial_tensor_batch_passthrough(
        self,
        batch: ClipSpatialTensorBatch,
    ) -> ClipSpatialTensorBatch:
        return batch

    def clip_spatial_text_vector_pair_passthrough(
        self,
        pair: ClipSpatialTextVectorPair,
    ) -> ClipSpatialTextVectorPair:
        return pair

    def clip_spatial_text_image_pair_passthrough(
        self,
        pair: ClipSpatialTextImagePair,
    ) -> ClipSpatialTextImagePair:
        return pair

    def spatial_score_vector_batch_passthrough(
        self,
        batch: SpatialScoreVectorBatch,
    ) -> SpatialScoreVectorBatch:
        return batch

    def clip_spatial_tensor_batch_to_spatial_float_vector_batch(
            self,
            batch: ClipSpatialTensorBatch,
    ) -> SpatialFloatVectorBatch:
        return SpatialFloatVectorBatch(
            SpatialVectorBatchData(
                vectors={
                    flat_index: [float(value) for value in vector.tolist()]
                    for flat_index, vector in batch.ordered_items()
                },
                base_vectors={
                    item_key: [float(value) for value in vector.tolist()]
                    for item_key, vector in batch.data().base_vectors.items()
                },
                layout=batch.layout,
                item_keys=batch.item_keys,
                regions=batch.regions,
            )
        )

    def spatial_float_vector_batch_to_clip_spatial_tensor_batch(
            self,
            batch: SpatialFloatVectorBatch,
    ) -> ClipSpatialTensorBatch:
        return ClipSpatialTensorBatch(
            SpatialVectorBatchData(
                vectors={
                    flat_index: torch.tensor(vector, dtype=torch.float32)
                    for flat_index, vector in batch.ordered_items()
                },
                base_vectors={
                    item_key: torch.tensor(vector, dtype=torch.float32)
                    for item_key, vector in batch.data().base_vectors.items()
                },
                layout=batch.layout,
                item_keys=batch.item_keys,
                regions=batch.regions,
            )
        )

    def clip_spatial_text_tensor_batch_to_float_vector(
        self,
        batch: ClipSpatialTextTensorBatch,
    ) -> FloatVector:
        if batch.batch_size() != 1:
            raise ValueError(
                "Cannot convert multiple text embeddings "
                "to a single FloatVector."
            )

        return FloatVector(
            [
                float(value)
                for value in batch.ordered_values()[0].tolist()
            ]
        )

    def clip_spatial_text_tensor_batch_to_float_vector_batch(
        self,
        batch: ClipSpatialTextTensorBatch,
    ) -> FloatVectorBatch:
        return FloatVectorBatch(
            {
                key: [
                    float(value)
                    for value in vector.tolist()
                ]
                for key, vector in batch.ordered_items()
            }
        )