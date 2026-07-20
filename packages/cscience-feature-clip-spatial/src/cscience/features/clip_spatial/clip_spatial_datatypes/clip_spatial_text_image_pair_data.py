from dataclasses import dataclass

from cscience.features.api import (
    PilImageBatch,
    TextBatch,
)


@dataclass(frozen=True, slots=True)
class ClipSpatialTextImagePairData:
    texts: TextBatch
    images: PilImageBatch