from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Self, TypeVar, cast

from cscience.features.api.config.config_base import ConfigBase


TConfig = TypeVar(
    "TConfig",
    bound=ConfigBase,
)


class FeatureBase(ABC, Generic[TConfig]):
    """
    Base class for model-backed feature services.

    Each configuration identity may be instantiated only once.
    Configuration identity is defined by ConfigBase.__eq__ and
    ConfigBase.__hash__, which are expected to rely on the namespace.
    """

    _instances: ClassVar[
        dict[ConfigBase, FeatureBase]
    ] = {}

    _config: TConfig

    def __new__(
        cls,
        config: TConfig,
    ) -> Self:
        if cls is FeatureBase:
            raise TypeError(
                "FeatureBase cannot be instantiated directly."
            )

        if config in FeatureBase._instances:
            raise ValueError(
                f"A feature instance for namespace "
                f"{config.namespace!r} already exists."
            )

        instance = super().__new__(cls)
        FeatureBase._instances[config] = instance

        return instance

    def __init__(
        self,
        config: TConfig,
    ) -> None:
        self._config = config
        self._initialize(config)
        self._is_initialized = True

    @property
    def config(self) -> TConfig:
        return self._config

    @classmethod
    def get_instance(
        cls,
        config: TConfig,
    ) -> Self:
        try:
            instance = FeatureBase._instances[config]
        except KeyError as error:
            raise KeyError(
                f"No feature instance exists for namespace "
                f"{config.namespace!r}."
            ) from error

        return cast(Self, instance)

    @abstractmethod
    def _initialize(
        self,
        config: TConfig,
    ) -> None:
        raise NotImplementedError