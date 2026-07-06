from abc import ABC, abstractmethod
from pydantic import BaseModel
from abc import ABC, abstractmethod

from pydantic import BaseModel


class ConfigBase(ABC, BaseModel):

    @classmethod
    @abstractmethod
    def _namespace(cls): raise NotImplementedError

