from dataclasses import dataclass

from torch import Tensor


@dataclass(frozen=True, slots=True)
class ClipSpatialTextTensorBatchData:
    """Packed CLIP text embedding batch with stable source keys.

    vectors has shape [N, D].
    keys maps tensor rows back to TextBatch source keys.
    """

    keys: tuple[int, ...]
    vectors: Tensor