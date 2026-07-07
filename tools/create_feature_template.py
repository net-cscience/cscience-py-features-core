from __future__ import annotations

import argparse
from pathlib import Path


def to_pascal_case(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def write_file(path: Path, content: str) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_feature_package(root: Path, name: str) -> None:
    module = name.replace("-", "_")
    package_name = f"cscience-feature-{name.replace('_', '-')}"
    pascal = to_pascal_case(module)

    base = root / "packages" / package_name
    src = base / "src" / "cscience" / "features" / module

    write_file(
        base / "pyproject.toml",
        f"""[project]
name = "{package_name}"
version = "0.1.0"
description = "{pascal} feature implementation for the CScience feature API."
requires-python = ">=3.13,<3.14"
dependencies = [
    "cscience-feature-api",
]

[tool.uv.sources]
cscience-feature-api = {{ workspace = true }}

[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
only-include = ["src/cscience"]
sources = ["src"]

[project.entry-points."cscience.features"]
{module} = "cscience.features.{module}:register"
""",
    )

    write_file(
        src / f"{module}_datatype.py",
        f"""from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class {pascal}Datatype(DatatypeBase, ABC):
    \"\"\"Base class for {module} feature-specific datatypes.\"\"\"

    namespace = "{module}"
""",
    )

    write_file(
        src / f"{module}_feature.py",
        f"""from cscience.features.api.feature.feature_base import FeatureBase


class {pascal}Feature(FeatureBase):
    \"\"\"{pascal} feature service.\"\"\"

    def _initialize(self) -> None:
        if self._initialized:
            return

        self._initialized = True
""",
    )

    write_file(
        src / f"{module}_conversion_provider.py",
        f"""from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.feature.feature_base import FeatureBase


class {pascal}ConversionProvider(ConversionProviderBase):
    \"\"\"Registers conversions required by the {module} feature.\"\"\"

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return []
""",
    )

    write_file(
        src / f"{module}_connector.py",
        f"""from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from .{module}_conversion_provider import {pascal}ConversionProvider
from .{module}_feature import {pascal}Feature


class {pascal}Connector(ConnectorBase):
    \"\"\"Public connector for the {module} feature.\"\"\"

    def __init__(self) -> None:
        self.feature = {pascal}Feature.get_instance()
        super().__init__("{module}", {pascal}ConversionProvider(self.feature))

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")
""",
    )

    write_file(
        src / "__init__.py",
        f"""from cscience.features.api.registry.registry_base import RegistryBase

from .{module}_connector import {pascal}Connector
from .{module}_conversion_provider import {pascal}ConversionProvider
from .{module}_feature import {pascal}Feature

__all__ = [
    "{pascal}Connector",
    "{pascal}ConversionProvider",
    "{pascal}Feature",
]


def register(registry: RegistryBase) -> None:
    registry.register("{module}", {pascal}ConversionProvider)
""",
    )

    write_file(
        base / "tests" / f"test_{module}_feature.py",
        f"""import unittest

from cscience.features.{module} import {pascal}Connector


class {pascal}FeatureTest(unittest.TestCase):
    def test_connector_initializes(self):
        connector = {pascal}Connector()
        self.assertIsNotNone(connector)
""",
    )

    (src / f"{module}_datatypes").mkdir(parents=True, exist_ok=True)
    write_file(src / f"{module}_datatypes" / "__init__.py", "")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    create_feature_package(Path(args.root), args.name)


if __name__ == "__main__":
    main()