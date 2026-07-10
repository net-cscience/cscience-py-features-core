from mypy.nodes import Enum




# config_mode.py

from enum import StrEnum


class ConfigMode(StrEnum):
    UNIFIED_CONFIG = "unified"
    CONFIG_PER_FEATURE = "per-feature"