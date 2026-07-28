from enum import Enum
from typing import Literal

from pydantic import Field

from cscience.features.api import ConfigBase
from cscience.features.clip_spatial.config.masking_preprocessing_order import ImagePreprocessingOrder
from cscience.features.clip_spatial.config.scoring_function import ScoringFunction
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

    pretrained: str = Field(
        default="laion5b_s13b_b90k",
        description="The name of the pretrained model to use. Default is 'laion5b_s13b_b90k'."
    )

    preferred_device: Literal["cpu", "cuda", "cuda:1"] = Field(
        default="cuda",
        description="The device to use for inference. Default is 'cpu'."
    )

    force_device: bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )

    preprocessing_order: ImagePreprocessingOrder = Field(
        default=ImagePreprocessingOrder.LATE_PREPROCESSING
    )

    scoring_function: ScoringFunction = Field(
        default=ScoringFunction.RELATIVE_POSITIVE
    )

    step_size: tuple[float, float] = Field(default=((1 - 2 * 6 / 36) / 2, (1 - 2 * 6 / 48) / 3))
    start_point: tuple[float, float] = Field(default=(6 / 36, 6 / 48))
    grid_shape: tuple[int, int] = Field(default=(3, 4))

    geometry_size: tuple[float, float] = Field(default=(12 / 30, 12 / 40))

    masking_mode: MaskingMode = Field(default=MaskingMode.EXTRACT)
