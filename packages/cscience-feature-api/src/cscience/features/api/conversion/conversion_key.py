from dataclasses import dataclass

from ..datatypes.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase



from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ConversionKey:
    """Dictionary key identifying a registered datatype conversion.

    A conversion is scoped by feature class and by source/target datatype.
    Core conversions use `CoreFeature` as their source and may be used as
    fallback conversions by search strategies.
    """

    source: type[FeatureBase]
    input_type: type[DatatypeBase]
    output_type: type[DatatypeBase]