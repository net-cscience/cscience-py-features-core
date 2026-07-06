from PIL.ImageFile import ImageFile

from ..clip_datatype import ClipDatatype


class ClipImageBatch(ClipDatatype):

    def __init__(self, data: list[ImageFile]) -> None:
        super().__init__(data)