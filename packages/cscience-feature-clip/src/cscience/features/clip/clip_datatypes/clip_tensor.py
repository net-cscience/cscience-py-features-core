from torch import Tensor

from ..clip_datatype import ClipDatatype


class ClipTensor(ClipDatatype):

    def __init__(self, data:Tensor) -> None:
        self._data: Tensor = data

    def data(self) -> Tensor:
        return self._data

