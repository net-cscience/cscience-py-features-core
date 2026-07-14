from __future__ import annotations

from abc import ABC, abstractmethod
import threading
from typing import ClassVar, Generic, Self, TypeVar, cast

from cscience.features.api.config.config_base import ConfigBase
from cscience.features.api.feature.feature_info import FeatureInfo

TConfig = TypeVar(
    "TConfig",
    bound=ConfigBase,
)

TFeature = TypeVar(
    "TFeature",
    bound="FeatureBase",
)


class FeatureBase(ABC, Generic[TFeature, TConfig]):
    """
    Base class for model-backed feature services.

    Each configuration identity may be instantiated only once.
    Instances must be obtained through get_instance().

    Configuration identity is defined by ConfigBase.__eq__ and
    ConfigBase.__hash__, which are expected to rely on the namespace.
    """

    _instances: ClassVar[
        dict[ConfigBase, FeatureBase]
    ] = {}

    _lock: ClassVar[threading.Lock] = threading.Lock()
    _creation_state: ClassVar[threading.local] = threading.local()

    _config: TConfig

    def __new__(
        cls,
        config: TConfig,
    ) -> Self:
        if cls is FeatureBase:
            raise TypeError(
                "FeatureBase cannot be instantiated directly."
            )

        if not getattr(
            FeatureBase._creation_state,
            "allowed",
            False,
        ):
            raise RuntimeError(
                f"{cls.__name__} instances must be created using "
                f"{cls.__name__}.get_instance(config)."
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

    @property
    def config(self) -> TConfig:
        return self._config

    @classmethod
    def get_instance(
        cls: type[TFeature],
        config: TConfig,
        init_if_missing: bool = True,
    ) -> TFeature:
        with FeatureBase._lock:
            existing = FeatureBase._instances.get(config)

            if existing is not None:
                return existing

            if not init_if_missing:
                raise LookupError(
                    f"No feature instance exists for namespace "
                    f"{config.namespace!r}."
                )

            FeatureBase._creation_state.allowed = True
            cls(config)

            try:
                existing = FeatureBase._instances.get(config)
                if existing is not None:
                    return existing
                raise  RuntimeError(
                    f"Failed to create feature instance for namespace "
                    f"{config.namespace!r}."
                )
            except Exception:
                FeatureBase._instances.pop(config, None)
                raise
            finally:
                FeatureBase._creation_state.allowed = False

    @abstractmethod
    def _initialize(
        self,
        config: TConfig,
    ) -> None:
        raise NotImplementedError



    @abstractmethod
    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError