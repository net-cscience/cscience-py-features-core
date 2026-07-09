from __future__ import annotations

import csv
import json
import shutil
import tempfile
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from PIL import Image, ImageOps


SourceType = Literal["local", "url"]
SmallImageMode = Literal["error", "skip", "upscale"]


_TRUE_VALUES = {"1", "true", "yes", "y", "x"}


@dataclass(frozen=True, slots=True)
class Resolution:
    width: int
    height: int

    @classmethod
    def parse(cls, value: str) -> "Resolution":
        normalized = value.strip().lower().replace("×", "x")
        parts = normalized.split("x")

        if len(parts) != 2:
            raise ValueError(f"Invalid resolution column: {value}")

        return cls(width=int(parts[0]), height=int(parts[1]))

    @property
    def filename(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

    @property
    def aspect_name(self) -> str:
        if self.width == self.height:
            return "1_1"

        ratio = self.aspect_ratio

        if abs(ratio - 16 / 9) < 0.01:
            return "16_9"

        if abs(ratio - 4 / 3) < 0.01:
            return "4_3"

        raise ValueError(
            f"Unsupported aspect ratio for {self.filename}. "
            "Supported aspects are 16:9, 4:3, and 1:1."
        )


@dataclass(frozen=True, slots=True)
class ImageFixtureRow:
    identifier: str
    package: str
    source_type: SourceType
    source: str
    resolutions: tuple[Resolution, ...]
    anchor_x: float = 0.5
    anchor_y: float = 0.5
    license: str = ""
    author: str = ""
    landing_url: str = ""
    classes: str = ""
    notes: str = ""

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "ImageFixtureRow":
        identifier = _require(row, "id")
        package = _require(row, "package")
        source_type = _require(row, "source_type")
        source = _require(row, "source")

        if source_type not in {"local", "url"}:
            raise ValueError(
                f"source_type must be 'local' or 'url' for row {identifier}. "
                f"Got: {source_type}"
            )

        resolutions = _selected_resolutions(row)

        if not resolutions:
            raise ValueError(f"No output resolutions selected for row {identifier}")

        return cls(
            identifier=identifier,
            package=package,
            source_type=source_type,  # type: ignore[arg-type]
            source=source,
            resolutions=resolutions,
            anchor_x=float(row.get("anchor_x") or 0.5),
            anchor_y=float(row.get("anchor_y") or 0.5),
            license=row.get("license", ""),
            author=row.get("author", ""),
            landing_url=row.get("landing_url", ""),
            classes=row.get("classes", ""),
            notes=row.get("notes", ""),
        )


@dataclass(frozen=True, slots=True)
class ImageFixtureConfig:
    sources_csv: Path
    workspace_root: Path = Path.cwd()
    output_format: Literal["jpg", "png"] = "jpg"
    jpeg_quality: int = 95
    small_image_mode: SmallImageMode = "error"
    package_filter: str | None = None
    output_dir: Path | None = None


@dataclass(slots=True)
class ImageFixtureBuilder:
    config: ImageFixtureConfig
    _temporary_files: list[Path] = field(default_factory=list)

    def run(self) -> None:
        rows = self._read_rows()

        if self.config.package_filter is not None:
            rows = [
                row
                for row in rows
                if row.package == self.config.package_filter
            ]

        if not rows:
            print("No fixture rows selected.")
            return

        try:
            for row in rows:
                print(f"Building fixtures for {row.package}/{row.identifier}...")
                self._build_row(row)
        finally:
            self._cleanup_temporary_files()

    def _build_row(self, row: ImageFixtureRow) -> None:
        source_path = self._resolve_source(row)
        package_dir = self._resolve_package_dir(row.package)
        output_root = self._resolve_output_root(package_dir)

        with Image.open(source_path) as raw_image:
            image = ImageOps.exif_transpose(raw_image).convert("RGB")

        image_output_dir = output_root / row.identifier
        image_output_dir.mkdir(parents=True, exist_ok=True)

        metadata: dict[str, object] = {
            "id": row.identifier,
            "package": row.package,
            "source_type": row.source_type,
            "source": row.source,
            "license": row.license,
            "author": row.author,
            "landing_url": row.landing_url,
            "classes": row.classes,
            "notes": row.notes,
            "source_size": {
                "width": image.width,
                "height": image.height,
            },
            "anchor": {
                "x": row.anchor_x,
                "y": row.anchor_y,
            },
            "outputs": {},
        }

        grouped = self._group_by_aspect(row.resolutions)

        for aspect_name, resolutions in grouped.items():
            aspect_ratio = resolutions[0].aspect_ratio

            crop_box = self._compute_crop_box(
                image_size=image.size,
                aspect_ratio=aspect_ratio,
                anchor_x=row.anchor_x,
                anchor_y=row.anchor_y,
            )

            crop = image.crop(crop_box)
            files: list[dict[str, str]] = []

            for resolution in sorted(
                resolutions,
                key=lambda item: item.width * item.height,
                reverse=True,
            ):
                if self._would_upscale(crop, resolution):
                    match self.config.small_image_mode:
                        case "error":
                            raise ValueError(
                                f"Source {row.identifier} is too small for "
                                f"{resolution.filename}. "
                                f"Crop size is {crop.width}x{crop.height}. "
                                "Use --on-small skip or --on-small upscale."
                            )
                        case "skip":
                            print(
                                f"Skipping {row.identifier}/{resolution.filename}: "
                                "source crop too small."
                            )
                            continue
                        case "upscale":
                            pass

                output_file = (
                    image_output_dir
                    / aspect_name
                    / f"{resolution.filename}.{self.config.output_format}"
                )

                output_file.parent.mkdir(parents=True, exist_ok=True)

                resized = crop.resize(
                    (resolution.width, resolution.height),
                    Image.Resampling.LANCZOS,
                )

                self._save_image(resized, output_file)

                files.append(
                    {
                        "resolution": resolution.filename,
                        "path": str(output_file.relative_to(image_output_dir)),
                    }
                )

            metadata["outputs"][aspect_name] = {
                "crop_box": {
                    "left": crop_box[0],
                    "top": crop_box[1],
                    "right": crop_box[2],
                    "bottom": crop_box[3],
                },
                "crop_size": {
                    "width": crop_box[2] - crop_box[0],
                    "height": crop_box[3] - crop_box[1],
                },
                "files": files,
            }

        (image_output_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _resolve_output_root(self, package_dir: Path) -> Path:
        if self.config.output_dir is not None:
            return self.config.output_dir.resolve()

        return package_dir / "tests" / "fixtures" / "images-gen"

    def _resolve_package_dir(self, package: str) -> Path:
        package_path = Path(package)

        if package_path.exists():
            return package_path.resolve()

        candidate = self.config.workspace_root / "packages" / package

        if candidate.exists():
            return candidate.resolve()

        raise FileNotFoundError(
            f"Could not resolve package '{package}'. Expected either an existing "
            f"path or {candidate}."
        )

    def _resolve_source(self, row: ImageFixtureRow) -> Path:
        match row.source_type:
            case "url":
                return self._download_source(row.source)
            case "local":
                source_path = Path(row.source)

                if not source_path.is_absolute():
                    source_path = self.config.sources_csv.parent / source_path

                if not source_path.exists():
                    raise FileNotFoundError(
                        f"Source image does not exist for {row.identifier}: {source_path}"
                    )

                return source_path.resolve()
            case _:
                raise ValueError(f"Unsupported source type: {row.source_type}")

    def _download_source(self, url: str) -> Path:
        parsed = urlparse(url)
        suffix = Path(parsed.path).suffix or ".jpg"

        handle = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_path = Path(handle.name)
        handle.close()

        request = urllib.request.Request(
            url,
            headers={"User-Agent": "cscience-project-maintenance/0.1"},
        )

        with urllib.request.urlopen(request, timeout=60) as response:
            with temp_path.open("wb") as output:
                shutil.copyfileobj(response, output)

        self._temporary_files.append(temp_path)
        return temp_path

    def _read_rows(self) -> list[ImageFixtureRow]:
        if not self.config.sources_csv.exists():
            raise FileNotFoundError(
                f"Fixture CSV does not exist: {self.config.sources_csv}"
            )

        with self.config.sources_csv.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            return [ImageFixtureRow.from_csv_row(row) for row in reader]

    def _save_image(self, image: Image.Image, output_file: Path) -> None:
        match self.config.output_format:
            case "jpg":
                image.save(
                    output_file,
                    format="JPEG",
                    quality=self.config.jpeg_quality,
                    optimize=True,
                )
            case "png":
                image.save(output_file, format="PNG", optimize=True)
            case _:
                raise ValueError(f"Unsupported output format: {self.config.output_format}")

    @staticmethod
    def _group_by_aspect(
        resolutions: tuple[Resolution, ...],
    ) -> dict[str, list[Resolution]]:
        grouped: dict[str, list[Resolution]] = {}

        for resolution in resolutions:
            grouped.setdefault(resolution.aspect_name, []).append(resolution)

        return grouped

    @staticmethod
    def _compute_crop_box(
        image_size: tuple[int, int],
        aspect_ratio: float,
        anchor_x: float,
        anchor_y: float,
    ) -> tuple[int, int, int, int]:
        image_width, image_height = image_size

        anchor_x = min(max(anchor_x, 0.0), 1.0)
        anchor_y = min(max(anchor_y, 0.0), 1.0)

        image_ratio = image_width / image_height

        if image_ratio >= aspect_ratio:
            crop_height = image_height
            crop_width = round(crop_height * aspect_ratio)
        else:
            crop_width = image_width
            crop_height = round(crop_width / aspect_ratio)

        center_x = round(anchor_x * image_width)
        center_y = round(anchor_y * image_height)

        left = center_x - crop_width // 2
        top = center_y - crop_height // 2

        left = min(max(left, 0), image_width - crop_width)
        top = min(max(top, 0), image_height - crop_height)

        return left, top, left + crop_width, top + crop_height

    @staticmethod
    def _would_upscale(image: Image.Image, resolution: Resolution) -> bool:
        return resolution.width > image.width or resolution.height > image.height

    def _cleanup_temporary_files(self) -> None:
        for file in self._temporary_files:
            file.unlink(missing_ok=True)


def _require(row: dict[str, str], key: str) -> str:
    value = row.get(key, "").strip()

    if not value:
        raise ValueError(f"Missing required CSV column value: {key}")

    return value


def _selected_resolutions(row: dict[str, str]) -> tuple[Resolution, ...]:
    reserved_columns = {
        "id",
        "package",
        "source_type",
        "source",
        "anchor_x",
        "anchor_y",
        "license",
        "author",
        "landing_url",
        "classes",
        "notes",
    }

    selected: list[Resolution] = []

    for column, value in row.items():
        if column in reserved_columns:
            continue

        if not column:
            continue

        if value.strip().lower() not in _TRUE_VALUES:
            continue

        selected.append(Resolution.parse(column))

    return tuple(selected)