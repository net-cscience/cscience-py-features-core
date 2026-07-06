from ..conversion.conversion_key import ConversionKey
from ..conversion.conversion_provider_base import ConversionProviderBase
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..registry.registry_base import RegistryBase, Tin


class ConversionRegistry(RegistryBase[ConversionProviderBase]):

    @classmethod
    def _initialize(cls) -> None:
        cls._converters  = {}
        pass

    _converters: dict[ConversionKey, Converter] = None

    @classmethod
    def get_converters(cls) -> dict[ConversionKey, Converter]:
        return cls._converters

    @classmethod
    def register(cls, name: str, provider: Tin) -> None:
        for converter in provider.register_converters():
            cls.get_instance().get_converters()[converter.get_identifier()] = converter

    @classmethod
    def has_best_effort_converter(cls, strategy: SearchStrategyBase) -> bool:
        try:
            strategy.search(cls.get_instance().get_converters())
            return True
        except LookupError:
            return False

    @classmethod
    def get_best_effort_converter(cls, strategy: SearchStrategyBase) -> Converter:
        try:
            return strategy.search(cls.get_instance().get_converters())
        except LookupError as ex:
            raise LookupError(f"No best effort converter found for strategy: {strategy}") from ex