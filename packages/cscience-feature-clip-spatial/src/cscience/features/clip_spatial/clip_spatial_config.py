
from enum import Enum

from pydantic import Field

from cscience.features.api import ConfigBase
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode


class ClipSpatialConfig(ConfigBase):
    """Configuration for CLIP Spatial."""

    @classmethod
    def _namespace(cls) -> str:
        return "clip_spatial"

    model_name: str = Field(default="xlm-roberta-base-ViT-B-32")
    pretrained: str = Field(default="laion5b_s13b_b90k")
    device: str = Field(default="auto")

    region_size: tuple[float, float] = Field(default=(1 / 3, 1 / 3))
    step_size: tuple[float, float] = Field(default=(1 / 3, 1 / 3))
    start_point: tuple[float, float] = Field(default=(1 / 6, 1 / 6))
    grid_shape: tuple[int, int] = Field(default=(3, 3))

    masking_mode: MaskingMode = Field(default=MaskingMode.KEEP_ONLY)