from typing import List

from ..conversion.converter import Converter
from ..feature.feature_base import FeatureBase
from ..registry.conversion_registry import ConversionRegistry


from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.core_datatypes.float_vector import FloatVector
from cscience.features.api.datatypes.core_datatypes.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.core_datatypes.text import Text
from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase



class CoreConvertionProvider(ConversionProviderBase):

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        converters = [
            Converter[Text, Text]
                (
                name="text_to_list",
                source=self._feature,
                function=lambda x: Text(x.data()),
                input_type=Text,
                output_type=Text
            ),
            Converter[Text, TextBatch]
                (
                name="text_to_list",
                source=self._feature,
                function=lambda x: TextBatch([x.data()]),
                input_type=Text,
                output_type=TextBatch
            ),
            Converter[TextBatch, TextBatch]
                (
                name="text_batch_passthrough",
                source=self._feature,
                function=lambda x: x,
                input_type=TextBatch,
                output_type=TextBatch
            ),
            Converter[FloatVector, FloatVector]
                (
                name="float_vector_paththrough",
                source=self._feature,
                function=lambda x: x,
                input_type=FloatVector,
                output_type=FloatVector
            ),
            Converter[FloatVector, FloatVectorBatch]
                (
                name="float_vector_to_float_vector_batch",
                source=self._feature,
                function=lambda x: FloatVectorBatch({0: x.data()}),
                input_type=FloatVector,
                output_type=FloatVectorBatch
            ),
            Converter[FloatVectorBatch, FloatVectorBatch]
                (
                name="float_vector_batch_paththrough",
                source=self._feature,
                function=lambda x: x,
                input_type=FloatVectorBatch,
                output_type=FloatVectorBatch
            )
        ]
        return converters
