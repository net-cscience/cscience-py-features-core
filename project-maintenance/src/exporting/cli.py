from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ExportConfig:
    root: Path
    output_dir: Path
    directory_filter: str | None = None
    include_python: bool = True
    include_toml: bool = True
    include_md: bool = True
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

        export_roots = self._collect_export_roots(root)

        if self.config.include_structure:
            self.export_file_structure(
                root=root,
                export_roots=export_roots,
                output_file=output_dir / "exported_file_structure.txt",
            )

        if self.config.include_python:
            self.export_sources(
                root=root,
                export_roots=export_roots,
                output_file=output_dir / "exported_code.py",
                pattern="*.py",
                header="Exported code",
            )

        if self.config.include_toml:
            self.export_sources(
                root=root,
                export_roots=export_roots,
                output_file=output_dir / "exported_toml.toml",
                pattern="*.toml",
                header="Exported TOML",
            )

        if self.config.include_md:
            self.export_sources(
                root=root,
                export_roots=export_roots,
                output_file=output_dir / "exported_md.md",
                pattern="*.md",
                header="Exported Markdown",
            )

    def export_file_structure(
        self,
        root: Path,
        export_roots: tuple[Path, ...],
        output_file: Path,
    ) -> None:
        files = self._collect_files(
            root=root,
            export_roots=export_roots,
            pattern="*.py",
        )

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
        export_roots: tuple[Path, ...],
        output_file: Path,
        pattern: str,
        header: str,
    ) -> None:
        files = self._collect_files(
            root=root,
            export_roots=export_roots,
            pattern=pattern,
        )

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

    def _collect_export_roots(self, root: Path) -> tuple[Path, ...]:
        directory_filter = self.config.directory_filter

        if directory_filter is None:
            return (root,)

        normalized_filter = directory_filter.replace("\\", "/")

        directories = tuple(
            sorted(
                directory
                for directory in root.glob(normalized_filter)
                if directory.is_dir() and not self._is_excluded(directory)
            )
        )

        print(
            f"Matched {len(directories)} directories "
            f"for filter {normalized_filter!r}."
        )

        return directories

    def _collect_files(
        self,
        root: Path,
        export_roots: tuple[Path, ...],
        pattern: str,
    ) -> list[Path]:
        files = {
            file
            for export_root in export_roots
            for file in export_root.rglob(pattern)
            if file.is_file() and not self._is_excluded(file)
        }

        return sorted(
            files,
            key=lambda file: file.relative_to(root).as_posix(),
        )

    def _is_excluded(self, path: Path) -> bool:
        parts = set(path.parts)

        if any(excluded in parts for excluded in self.config.excluded_dirs):
            return True

        output_dir = self.config.output_dir.resolve()
        resolved_path = path.resolve()

        return resolved_path == output_dir or output_dir in resolved_path.parents


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
        "--filter",
        dest="directory_filter",
        help=(
            "Directory glob relative to the root. Only files below matching "
            'directories are exported, for example "**/packages/**/datatype".'
        ),
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
        "--no-md",
        action="store_true",
        help="Do not export Markdown files.",
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
            directory_filter=args.directory_filter,
            include_python=not args.no_python,
            include_toml=not args.no_toml,
            include_md=not args.no_md,
            include_structure=not args.no_structure,
        )
    ).run()


if __name__ == "__main__":
    main()