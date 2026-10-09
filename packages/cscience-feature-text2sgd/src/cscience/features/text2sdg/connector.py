from typing import Any

from rpy2.robjects import StrVector
from rpy2.robjects.packages import importr


class Text2SdgConnector:
    def __init__(self) -> None:
        self._text2sdg = importr("text2sdg")

    def detect(self, texts: list[str]) -> Any:
        return self._text2sdg.detect_sdg(StrVector(texts), verbose=False)