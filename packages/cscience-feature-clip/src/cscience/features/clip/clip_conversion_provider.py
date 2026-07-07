from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors.float_vector_batch import FloatVectorBatch
from cscience.features.api.feature.feature_base import FeatureBase

from .clip_datatypes.clip_tensor_batch import ClipTensorBatch


def clip_tensor_batch_passthrough(batch: ClipTensorBatch) -> ClipTensorBatch:
    return batch


def clip_tensor_batch_to_float_vector(batch: ClipTensorBatch) -> FloatVector:
    data = batch.data()

    if len(data.keys) != 1:
        raise ValueError(
            f"Cannot convert ClipTensorBatch of size {len(data.keys)} to FloatVector."
        )

    return FloatVector(data.vectors[0].tolist())


def clip_tensor_batch_to_float_vector_batch(batch: ClipTensorBatch) -> FloatVectorBatch:
    data = batch.data()

    return FloatVectorBatch(
        {
            key: vector.tolist()
            for key, vector in zip(data.keys, data.vectors)
        }
    )


class ClipConversionProvider(ConversionProviderBase):
    """Registers datatype conversions required by the CLIP connector."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        return [
            Converter[ClipTensorBatch, ClipTensorBatch](
                name="clip_tensor_batch_passthrough",
                source=self._feature,
                function=clip_tensor_batch_passthrough,
                input_type=ClipTensorBatch,
                output_type=ClipTensorBatch,
            ),
            Converter[ClipTensorBatch, FloatVector](
                name="clip_tensor_batch_to_float_vector",
                source=self._feature,
                function=clip_tensor_batch_to_float_vector,
                input_type=ClipTensorBatch,
                output_type=FloatVector,
            ),
            Converter[ClipTensorBatch, FloatVectorBatch](
                name="clip_tensor_batch_to_float_vector_batch",
                source=self._feature,
                function=clip_tensor_batch_to_float_vector_batch,
                input_type=ClipTensorBatch,
                output_type=FloatVectorBatch,
            ),
        ]