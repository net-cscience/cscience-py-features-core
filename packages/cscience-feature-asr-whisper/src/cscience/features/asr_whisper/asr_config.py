from typing import Literal

from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class AsrConfig(ConfigBase):
    """
    Available Whisper model variants:

    +--------+------------+--------------------+--------------------+---------------+----------------+
    | Size   | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
    +========+============+====================+====================+===============+================+
    | tiny   | 39 M       | tiny.en            | tiny               | ~1 GB         | ~10x           |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | base   | 74 M       | base.en            | base               | ~1 GB         | ~7x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | small  | 244 M      | small.en           | small              | ~2 GB         | ~4x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | medium | 769 M      | medium.en          | medium             | ~5 GB         | ~2x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | large  | 1550 M     | N/A                | large              | ~10 GB        | 1x             |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | turbo  | 809 M      | N/A                | turbo              | ~6 GB         | ~8x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    """

    @classmethod
    def _default_namespace(cls) -> str:
        return "asr_whisper"

    model_name:Literal["small", "medium", "large"] = Field(
        default="small",
        description="The name of the ASR model to use."
    )

    preferred_device:str = Field(
        default="cuda",
        description="The device to use for inference."
    )

    force_device:bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )
