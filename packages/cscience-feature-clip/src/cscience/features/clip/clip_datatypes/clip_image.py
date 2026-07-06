from PIL.ImageFile import ImageFile

from ..clip_datatype import ClipDatatype


class ClipImage(ClipDatatype):

    def __init__(self, data: ImageFile) -> None:
        super().__init__(data)
