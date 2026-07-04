from ..conversion.conversion_provider_base import ConversionProviderBase
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..feature.feature_base import FeatureBase
from ..registry.registry_base import RegistryBase, Tin


class ConversionRegistry(RegistryBase[ConversionProviderBase]):

    @classmethod
    def _initialize(cls) -> None:
        cls._converters  = {}
        pass

    _converters: dict[tuple[FeatureBase, type, type], Converter] = None


    @classmethod
    def register(cls, name: str, domain: Tin) -> None:
        for converter in domain.register_converters():
            cls.get_instance()._converters[converter.get_identifier()] = converter

    @classmethod
    def has_best_effort_converter(cls, strategy: SearchStrategyBase) -> bool:
        return strategy.search(cls.get_instance()._converters) is not None

    @classmethod
    def get_best_effort_converter(cls, strategy: SearchStrategyBase) -> Converter:
        if cls.has_best_effort_converter(strategy):
            return strategy.search(cls.get_instance()._converters)
        raise Exception("No best effort converter found")
