from dataclasses import dataclass

from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase



from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ConversionKey:
    source: type[FeatureBase]
    input_type: type[DatatypeBase]
    output_type: type[DatatypeBase]