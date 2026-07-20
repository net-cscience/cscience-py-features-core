from __future__ import annotations

import unittest
from pathlib import Path


REQUIRED_HEADINGS = (
    "## Overview",
    "## Architecture",
    "## Public API",
    "## Datatypes",
    "## Configuration",
    "## Usage",
    "## Development",
    "## Design Notes",
)


class TestPackageReadmes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repository_root = Path(__file__).resolve().parents[3]
        cls.packages_root = cls.repository_root / "packages"

    def test_root_readme_exists(self) -> None:
        self.assertTrue(
            (self.repository_root / "README.md").is_file(),
            "The repository root must contain README.md.",
        )

    def test_every_package_has_structured_readme(self) -> None:
        package_roots = sorted(
            pyproject.parent
            for pyproject in self.packages_root.glob("*/pyproject.toml")
        )

        self.assertTrue(
            package_roots,
            "No package pyproject.toml files were found.",
        )

        for package_root in package_roots:
            with self.subTest(package=package_root.name):
                readme = package_root / "README.md"

                self.assertTrue(
                    readme.is_file(),
                    f"{package_root.name} must contain README.md.",
                )

                content = readme.read_text(encoding="utf-8")

                missing = [
                    heading
                    for heading in REQUIRED_HEADINGS
                    if heading not in content
                ]

                self.assertEqual(
                    missing,
                    [],
                    f"{package_root.name}/README.md is missing sections: "
                    f"{', '.join(missing)}",
                )


if __name__ == "__main__":
    unittest.main()
