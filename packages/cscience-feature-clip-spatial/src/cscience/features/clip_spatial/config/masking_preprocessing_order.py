from enum import StrEnum


class ImagePreprocessingOrder(StrEnum):
    """
    EARLY_PREPROCESSING: Preprocessing is applied before masking and before embedding
    LATE_PREPROCESSING: Preprocessing is applied after masking on each masked image, and before embedding.
    """
    EARLY_PREPROCESSING = "early_preprocessing"
    LATE_PREPROCESSING = "late_preprocessing"
