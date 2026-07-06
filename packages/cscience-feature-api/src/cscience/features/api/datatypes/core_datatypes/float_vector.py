from .vector_base import VectorBase
from ..core_datatype import CoreDatatype


class FloatVector(VectorBase[list[float]], CoreDatatype[list[float]]):

    def __init__(self, data:list[float], assert_length: int|None=None) -> None:
        super().__init__(data, assert_length)