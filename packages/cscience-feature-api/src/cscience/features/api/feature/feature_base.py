
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class FeatureBase(ABC):
    _instances: ClassVar[dict[type["FeatureBase"], "FeatureBase"]] = {}
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls is FeatureBase:
            raise TypeError("FeatureBase cannot be instantiated directly.")

        if cls not in FeatureBase._instances:
            FeatureBase._instances[cls] = super().__new__(cls)

        return FeatureBase._instances[cls]

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialize()
        self._initialized = True

    @classmethod
    def get_instance(cls):
        return cls()

    @abstractmethod
    def _initialize(self) -> None:
        """
        Load expensive resources here, e.g. model weights.
        Called exactly once per concrete feature class.
        """
        pass