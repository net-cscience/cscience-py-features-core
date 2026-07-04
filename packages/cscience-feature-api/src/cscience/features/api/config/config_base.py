from abc import ABC, abstractmethod
from pathlib import Path

class ConfigBase(ABC):

    def __init__(self):
        self._config_path: Path
        self._schema_path: Path

    def load(self):
        self._load_config()
        self._load_schema()
        self._validate()
    
    @abstractmethod
    def _load_config(self):
        pass
    
    @abstractmethod
    def _load_schema(self):
        pass

    @abstractmethod
    def _validate(self):
        pass
    
    @abstractmethod
    def _save(self):
        pass
    
    