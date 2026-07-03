from typing import  List

from PIL.ImageFile import ImageFile
from torch import Tensor

from conversion.converter import Converter
from conversion.conversion_provider_base import ConversionProviderBase
from feature.feature_base import FeatureBase


class ClipConvertionProvider(ConversionProviderBase):

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        converters = [
            Converter
                (
                name="text_to_list_wrapper",
                source=self._feature,
                fnc=lambda x: [x],
                input_type= str,
                output_type= List[str]
            ),
            Converter
                (
                name="image_passtrough_wrapper",
                source=self._feature,
                fnc=lambda x: x,
                input_type=ImageFile,
                output_type=ImageFile
            ),
            Converter
                (
                name="tensor_to_floatlist_wrapper",
                source=self._feature,
                fnc=lambda x: x.tolist(),
                input_type=Tensor,
                output_type=List[float]
            ),
        ]
        return converters
