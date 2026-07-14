from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


_FEATURE_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$")


@dataclass(frozen=True, slots=True)
class FeatureName:
    raw: str

    def __post_init__(self) -> None:
        if not _FEATURE_NAME_PATTERN.fullmatch(self.raw):
            raise ValueError(
                "Feature name must use lowercase words separated by '-' or '_'. "
                f"Got: {self.raw}"
            )

    @property
    def module(self) -> str:
        return self.raw.replace("-", "_")

    @property
    def distribution(self) -> str:
        return f"cscience-feature-{self.raw.replace('_', '-')}"

    @property
    def pascal(self) -> str:
        return "".join(part.capitalize() for part in self.module.split("_"))

    @property
    def namespace(self) -> str:
        return self.module


@dataclass(frozen=True, slots=True)
class FileSpec:
    path: Path
    content: str


@dataclass(frozen=True, slots=True)
class FeaturePackageTemplate:
    root: Path
    feature_name: FeatureName

    @property
    def base_dir(self) -> Path:
        return self.root / "packages" / self.feature_name.distribution

    @property
    def source_dir(self) -> Path:
        return (
            self.base_dir
            / "src"
            / "cscience"
            / "features"
            / self.feature_name.module
        )

    def files(self) -> list[FileSpec]:
        name = self.feature_name

        return [
            FileSpec(
                self.base_dir / "pyproject.toml",
                self._render_pyproject(),
            ),
            FileSpec(
                self.source_dir / f"{name.module}_datatype.py",
                self._render_datatype(),
            ),
            FileSpec(
                self.source_dir / f"{name.module}_feature.py",
                self._render_feature(),
            ),
            FileSpec(
                self.source_dir / f"{name.module}_conversion_provider.py",
                self._render_conversion_provider(),
            ),
            FileSpec(
                self.source_dir / f"{name.module}_connector.py",
                self._render_connector(),
            ),
            FileSpec(
                self.source_dir / "__init__.py",
                self._render_package_init(),
            ),
            FileSpec(
                self.source_dir / f"{name.module}_datatypes" / "__init__.py",
                "",
            ),
            FileSpec(
                self.base_dir / "tests" / f"test_{name.module}_feature.py",
                self._render_test(),
            ),
        ]

    def _render_pyproject(self) -> str:
        name = self.feature_name

        return f"""[project]
name = "{name.distribution}"
version = "0.1.0"
description = "{name.pascal} feature implementation for the CScience feature API."
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
{name.module} = "cscience.features.{name.module}:register"
"""

    def _render_datatype(self) -> str:
        name = self.feature_name

        return f"""from abc import ABC

from cscience.features.api.datatypes.datatype_base import DatatypeBase


class {name.pascal}Datatype(DatatypeBase, ABC):
    \"\"\"Base class for {name.namespace} feature-specific datatypes.\"\"\"

    namespace = "{name.namespace}"
"""

    def _render_feature(self) -> str:
        name = self.feature_name

        return f"""from cscience.features.api.feature.feature_base import FeatureBase


class {name.pascal}Feature(FeatureBase):
    \"\"\"{name.pascal} feature service.\"\"\"

    def _initialize(self) -> None:
        if self._initialized:
            return

        self._initialized = True
"""

    def _render_conversion_provider(self) -> str:
        name = self.feature_name

        return f"""from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.feature.feature_base import FeatureBase


class {name.pascal}ConversionProvider(ConversionProviderBase):
    \"\"\"Registers conversions required by the {name.namespace} feature.\"\"\"

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return []
"""

    def _render_connector(self) -> str:
        name = self.feature_name

        return f"""from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo

from .{name.module}_conversion_provider import {name.pascal}ConversionProvider
from .{name.module}_feature import {name.pascal}Feature


class {name.pascal}Connector(ConnectorBase):
    \"\"\"Public connector for the {name.namespace} feature.\"\"\"

    def __init__(self) -> None:
        self.feature = {name.pascal}Feature.get_instance()
        super().__init__("{name.namespace}", {name.pascal}ConversionProvider(self.feature))

    def get_service_info(self) -> ServiceInfo:
        raise NotImplementedError("ServiceInfo is intentionally deferred.")

    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError("FeatureInfo is intentionally deferred.")
"""

    def _render_package_init(self) -> str:
        name = self.feature_name

        return f"""from cscience.features.api.registry.registry_base import RegistryBase

from .{name.module}_connector import {name.pascal}Connector
from .{name.module}_conversion_provider import {name.pascal}ConversionProvider
from .{name.module}_feature import {name.pascal}Feature

__all__ = [
    "{name.pascal}Connector",
    "{name.pascal}ConversionProvider",
    "{name.pascal}Feature",
]


def register(registry: RegistryBase) -> None:
    registry.register("{name.namespace}", {name.pascal}ConversionProvider)
"""

    def _render_test(self) -> str:
        name = self.feature_name

        return f"""import unittest

from cscience.features.{name.module} import {name.pascal}Connector


class {name.pascal}FeatureTest(unittest.TestCase):
    def test_connector_initializes(self) -> None:
        connector = {name.pascal}Connector()
        self.assertIsNotNone(connector)
"""


@dataclass(frozen=True, slots=True)
class CreateFeatureTemplateCommand:
    root: Path
    name: str
    dry_run: bool = False

    def run(self) -> None:
        template = FeaturePackageTemplate(
            root=self.root,
            feature_name=FeatureName(self.name),
        )

        files = template.files()

        if self.dry_run:
            for file in files:
                print(file.path)
            return

        for file in files:
            self._write_file(file)

    @staticmethod
    def _write_file(file: FileSpec) -> None:
        if file.path.exists():
            raise FileExistsError(f"Refusing to overwrite existing file: {file.path}")

        file.path.parent.mkdir(parents=True, exist_ok=True)
        file.path.write_text(file.content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="templating",
        description="Create a new CScience feature package skeleton.",
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Feature name, for example 'clip-spatial' or 'nsfw-image'.",
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Workspace root. Defaults to the current working directory.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be created without writing them.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    CreateFeatureTemplateCommand(
        root=args.root,
        name=args.name,
        dry_run=args.dry_run,
    ).run()


if __name__ == "__main__":
    main()