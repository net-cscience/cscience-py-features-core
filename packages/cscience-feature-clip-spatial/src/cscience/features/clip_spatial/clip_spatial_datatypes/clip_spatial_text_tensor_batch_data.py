from dataclasses import dataclass

from torch import Tensor


@dataclass(frozen=True, slots=True)
class ClipSpatialTextTensorBatchData:
    """CLIP tensor batch with stable source keys.

    vectors has shape [n, d].
    keys maps row positions back to source batch indices.
    """

    keys: tuple[int, ...]
    vectors: Tensor