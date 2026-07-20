from enum import StrEnum


class ScoringFunction(StrEnum):
    """
    ABSOLUTE: The regional score is the absolute value of the COSINE CLIP similarity between the masked image and the text.
    ABSOLUTE_NORMALIZED: The regional score is the absolute value of the COSINE CLIP similarity between the masked image and the text, normalized to [0, 1]
    """
    ABSOLUTE = "absolute"
    ABSOLUTE_NORMALIZED = "absolute_normalized"
    RELATIVE_POSITIVE = "relative_positive"
    RELATIVE_POSITIVE_NORMALIZED = "relative_positive_normalized"
    RELATIVE_NEGATIVE = "relative_negative"
    RELATIVE_NEGATIVE_NORMALIZED = "relative_negative_normalized"
