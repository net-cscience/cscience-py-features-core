from .conversion_key import ConversionKey
from .converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..datatypes.datatype_base import DatatypeBase
from ..feature.core_feature import CoreFeature
from ..feature.feature_base import FeatureBase


class SearchStrategyMostSpecific(SearchStrategyBase):
    """Resolve a converter by exact feature key, then by core fallback key."""
    def __init__(self, conversion_key: ConversionKey):
        super().__init__(conversion_key)

    def search(self,
               recordset: dict[ConversionKey, Converter]) -> Converter:
        """Return the best matching converter or raise `LookupError`."""

        key: ConversionKey = self._conversion_key
        key_core: ConversionKey = ConversionKey(CoreFeature, key.input_type, key.output_type)


        try:
            return recordset[key]
        except KeyError:
            try:
                return recordset[key_core]
            except KeyError:
                raise LookupError(
                    f"No converter found for {self._conversion_key}"
                )