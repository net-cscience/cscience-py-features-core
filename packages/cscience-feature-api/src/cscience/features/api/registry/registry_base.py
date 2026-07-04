from abc import ABC, abstractmethod
from typing import TypeVar, Union, Generic, ClassVar, Any

Tin = TypeVar("Tin", contravariant=True)


class RegistryBase(ABC, Generic[Tin]):

    _instances: ClassVar[dict[type["RegistryBase"], "RegistryBase"]] = {}
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls is RegistryBase:
            raise TypeError("FeatureBase cannot be instantiated directly.")

        if cls not in RegistryBase._instances:
            RegistryBase._instances[cls] = super().__new__(cls)

        return RegistryBase._instances[cls]

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialize()
        self._initialized = True


    @classmethod
    def get_instance(cls):
        return cls()

    @classmethod
    @abstractmethod
    def _initialize(cls) -> None:
        """
        Load expensive resources here, e.g. model weights.
        Called exactly once per concrete feature class.
        """
        pass

    @abstractmethod
    def register(self, name: str, domain: Tin) -> None:
        """Register a feature in the registry."""
        pass
