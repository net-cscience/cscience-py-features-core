
from enum import Enum

from pydantic import Field

from cscience.features.api import ConfigBase
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode


class ClipSpatialConfig(ConfigBase):
    """Configuration for CLIP Spatial."""

    @classmethod
    def _default_namespace(cls) -> str:
        return "clip_spatial"

    model_name: str = Field(
        default="xlm-roberta-base-ViT-B-32",
        description="The name of the CLIP model to use. Default is 'xlm-roberta-base-ViT-B-32'."
    )


    pretrained:str = Field(
        default="laion5b_s13b_b90k",
        description="The name of the pretrained model to use. Default is 'laion5b_s13b_b90k'."
    )

    preferred_device:str = Field(
        default="cuda",
        description="The device to use for inference. Default is 'cpu'."
    )

    force_device:bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )

    step_size: tuple[float, float] = Field(default=(1 / 6, 1 / 8))
    start_point: tuple[float, float] = Field(default=(1 / 6, 1 / 8))
    grid_shape: tuple[int, int] = Field(default=(5, 7))

    geometry_size: tuple[float, float] = Field(default=(1 / 3, 1 / 4))

    masking_mode: MaskingMode = Field(default=MaskingMode.KEEP_ONLY)




