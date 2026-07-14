

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class FeatureInfo:
    namespace: str
    feature_type: str
    model_name: str | None
    device: str | None
    configuration: dict[str, Any]