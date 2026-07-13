from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class ClipConfig(ConfigBase):


    @classmethod
    def _default_namespace(cls) -> str:
        return "clip"

    model_name:str = Field(
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
