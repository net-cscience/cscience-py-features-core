from enum import Enum


class MaskingMode(str, Enum):
    MASK_OUT = "mask_out"
    KEEP_ONLY = "keep_only"
    EXTRACT = "extract"