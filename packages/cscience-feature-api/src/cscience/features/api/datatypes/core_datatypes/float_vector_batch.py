from .vector_base import VectorBase
from ..core_datatype import CoreDatatype

class FloatVectorBatch(VectorBase[dict[int,list[float]]]):

    def __init__(self, data: dict[int,list[float]],assert_length: int|None=None) -> None:
        super().__init__(data, assert_length)