from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ExportConfig:
    root: Path
    output_dir: Path
    include_python: bool = True
    include_toml: bool = True
    include_structure: bool = True
    excluded_dirs: tuple[str, ...] = (
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "export",
        ".egg-info",
    )


@dataclass(slots=True)
class ProjectExporter:
    config: ExportConfig
    timestamp: datetime = field(default_factory=datetime.now)

    def run(self) -> None:
        root = self.config.root.resolve()
        output_dir = self.config.output_dir.resolve()

        if not root.exists():
            raise FileNotFoundError(f"Root directory does not exist: {root}")

        if not root.is_dir():
            raise ValueError(f"Root path is not a directory: {root}")

        output_dir.mkdir(parents=True, exist_ok=True)

        if self.config.include_structure:
            self.export_file_structure(root, output_dir / "exported_file_structure.txt")

        if self.config.include_python:
            self.export_sources(
                root=root,
                output_file=output_dir / "exported_code.py",
                pattern="*.py",
                header="Exported code",
            )

        if self.config.include_toml:
            self.export_sources(
                root=root,
                output_file=output_dir / "exported_toml.toml",
                pattern="*.toml",
                header="Exported TOML",
            )

    def export_file_structure(self, root: Path, output_file: Path) -> None:
        files = self._collect_files(root, "*.py")

        with output_file.open("w", encoding="utf-8") as handle:
            handle.write(
                f"# Exported file structure on {self.timestamp} "
                f"with root dir {root}\n"
            )

            for file in files:
                handle.write(f"{file.relative_to(root)}\n")

    def export_sources(
        self,
        root: Path,
        output_file: Path,
        pattern: str,
        header: str,
    ) -> None:
        files = self._collect_files(root, pattern)

        with output_file.open("w", encoding="utf-8") as handle:
            handle.write(f"# {header} on {self.timestamp} with root dir {root}\n")

            for file in files:
                try:
                    content = file.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    print(f"Skipping {file} due to encoding issues.")
                    continue

                handle.write(f"# From {file.relative_to(root)}\n")
                handle.write(content)
                handle.write("\n\n")

    def _collect_files(self, root: Path, pattern: str) -> list[Path]:
        return sorted(
            file
            for file in root.rglob(pattern)
            if file.is_file() and not self._is_excluded(file)
        )

    def _is_excluded(self, file: Path) -> bool:
        parts = set(file.parts)

        if any(excluded in parts for excluded in self.config.excluded_dirs):
            return True

        output_dir = self.config.output_dir.resolve()
        resolved_file = file.resolve()

        return resolved_file == output_dir or output_dir in resolved_file.parents


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="exporting",
        description="Export project source files for review or sharing.",
    )

    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to export. Defaults to the current working directory.",
    )

    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path.cwd() / "export",
        help="Directory where exported files are written. Defaults to ./export.",
    )

    parser.add_argument(
        "--no-python",
        action="store_true",
        help="Do not export Python source files.",
    )

    parser.add_argument(
        "--no-toml",
        action="store_true",
        help="Do not export TOML files.",
    )

    parser.add_argument(
        "--no-structure",
        action="store_true",
        help="Do not export the Python file structure.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    ProjectExporter(
        ExportConfig(
            root=args.root,
            output_dir=args.out_dir,
            include_python=not args.no_python,
            include_toml=not args.no_toml,
            include_structure=not args.no_structure,
        )
    ).run()


if __name__ == "__main__":
    main()