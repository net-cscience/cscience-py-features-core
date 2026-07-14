from typing import Literal

from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class OcrConfig(ConfigBase):

    @classmethod
    def _default_namespace(cls) -> str:
        return "ocr_tesseract"