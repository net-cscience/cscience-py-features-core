from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class CoreConfig(ConfigBase):


    @classmethod
    def _default_namespace(cls) -> str:
        return "core"

    model_name:str = Field(
        default="Config for empty core model",
        description="The core model is used for registering core converters."
    )

