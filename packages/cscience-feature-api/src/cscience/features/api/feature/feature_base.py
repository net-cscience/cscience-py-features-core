
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class FeatureBase(ABC):
    """Base class for model-backed feature services.

    Each concrete feature class is instantiated as a singleton. Expensive
    resources such as neural network weights should be loaded in `_initialize`.
    """

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
        """Return the singleton instance of the concrete feature class."""
        return cls()

    @abstractmethod
    def _initialize(self) -> None:
        """Initialize expensive feature resources exactly once."""
        pass