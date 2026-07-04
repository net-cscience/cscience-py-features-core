from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor


class ClipConvertionProvider(ConversionProviderBase):

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        converters = [
            Converter[Text,TextBatch]
                (
                name="text_to_list_wrapper",
                source=self._feature,
                fnc =lambda x: TextBatch([x.data()]),
                input_type= Text,
                output_type= TextBatch
            ),
            Converter[ClipImage,ClipImage]
                (
                name="image_passtrough_wrapper",
                source=self._feature,
                fnc=lambda x: x,
                input_type=ClipImage,
                output_type=ClipImage
            ),
            Converter[ClipTensor,FloatVector]
                (
                name="tensor_to_floatlist_wrapper",
                source=self._feature,
                fnc=lambda x: FloatVector(x.data().tolist()),
                input_type=ClipTensor,
                output_type=FloatVector
            ),
        ]
        return converters
