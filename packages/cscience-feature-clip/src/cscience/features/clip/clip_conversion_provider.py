from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_image_batch import ClipImageBatch
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor
from cscience.features.clip.clip_datatypes.clip_tensor_batch import ClipTensorBatch


class ClipConvertionProvider(ConversionProviderBase):

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        converters = [
            Converter[ClipImage, ClipImageBatch]
                (
                name="image_batch_passtrough_wrapper",
                source=self._feature,
                fnc=lambda x: ClipImageBatch([x.data()]),
                input_type=ClipImage,
                output_type=ClipImageBatch
            ),
            Converter[ClipImageBatch, ClipImageBatch]
                (
                name="image_batch_passtrough",
                source=self._feature,
                fnc=lambda x: x,
                input_type=ClipImageBatch,
                output_type=ClipImageBatch
            ),
            Converter[ClipTensorBatch, FloatVector]
                (
                name="tenor_batch_to_float_vector",
                source=self._feature,
                fnc=lambda x: FloatVector(x.data().tolist()),
                input_type=ClipTensorBatch,
                output_type=FloatVector
            ),
            Converter[ClipTensorBatch, FloatVectorBatch]
                (
                name="tensor_to_float_vector_batch",
                source=self._feature,
                fnc=lambda x: FloatVectorBatch(
                    {
                        i: vector
                        for i, vector in enumerate(x.data().tolist())
                    }
                ),
                input_type=ClipTensorBatch,
                output_type=FloatVectorBatch
            ),
        ]
        return converters
