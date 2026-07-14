from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class NsfwConfig(ConfigBase):


    @classmethod
    def _default_namespace(cls) -> str:
        return "nsfw"

    model_name:str = Field(
        default="Falconsai/nsfw_image_detection",
        description="The name of the NSFW model to use."
    )

    preferred_device:str = Field(
        default="cuda",
        description="The device to use for inference. Default is 'cpu'."
    )

    force_device:bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )
