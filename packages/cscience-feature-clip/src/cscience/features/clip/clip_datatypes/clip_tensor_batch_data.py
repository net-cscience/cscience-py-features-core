from dataclasses import dataclass

from torch import Tensor


@dataclass(frozen=True, slots=True)
class ClipTensorBatchData:
    """Packed CLIP embedding batch with stable source keys.

    vectors has shape [N, D].
    keys maps tensor rows back to source batch indices.
    """

    keys: tuple[int, ...]
    vectors: Tensor