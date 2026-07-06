from cscience.features.api.datatypes.vector_base import VectorBase


class FloatVectorBatch(VectorBase[dict[int,list[float]]]):

    def __init__(self, data: dict[int,list[float]],assert_length: int|None=None) -> None:
        super().__init__(data, assert_length)