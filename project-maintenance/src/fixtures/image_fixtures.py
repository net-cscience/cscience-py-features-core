from __future__ import annotations

import base64
import codecs
import csv
import hashlib
import json
import random
import shutil
import socket
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

from PIL import Image, ImageOps, UnidentifiedImageError


SourceType = Literal["local", "url"]
ImageOutputFormat = Literal["jpg", "png"]
SerializedOutputFormat = Literal["base_64.txt"]
SmallImageMode = Literal["error", "skip", "upscale"]
ErrorMode = Literal["fail-fast", "collect", "ignore"]

DEFAULT_DOWNLOAD_USER_AGENT = (
    "CScienceFixtureBuilder/0.1 "
    "(https://github.com/CHANGE_ME/CHANGE_ME; mailto:CHANGE_ME)"
)

_TRUE_VALUES = {"1", "true", "yes", "y", "x"}
_FALSE_VALUES = {"", "0", "false", "no", "n", "none", "null", "-"}
_TRANSIENT_HTTP_STATUS_CODES = {429, 500, 502, 503, 504}


@dataclass(frozen=True, slots=True)
class Resolution:
    width: int
    height: int

    @classmethod
    def parse(cls, value: str) -> "Resolution":
        normalized = value.strip().lower().replace("×", "x")
        normalized = normalized.split("(", maxsplit=1)[0].strip(" _\t")
        parts = [part.strip(" _\t") for part in normalized.split("x")]

        if len(parts) != 2:
            raise ValueError(f"Invalid resolution column: {value}")

        try:
            width = int(parts[0])
            height = int(parts[1])
        except ValueError as error:
            raise ValueError(f"Invalid resolution column: {value}") from error

        if width <= 0 or height <= 0:
            raise ValueError(f"Resolution must be positive: {value}")

        return cls(width=width, height=height)

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
    goal_format: ImageOutputFormat | None
    goal_format_serialized: SerializedOutputFormat | None
    nsfw: bool = False
    anchor_x: float = 0.5
    anchor_y: float = 0.5
    license: str = ""
    author: str = ""
    landing_url: str = ""
    provider: str = ""
    classes: str = ""
    notes: str = ""

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "ImageFixtureRow":
        normalized_row = _normalize_row(row)

        identifier = _require(normalized_row, "id")
        package = _require(normalized_row, "package")
        source_type = _require(normalized_row, "source_type")
        source = _require(normalized_row, "source")

        if source_type not in {"local", "url"}:
            raise ValueError(
                f"source_type must be 'local' or 'url' for row {identifier}. "
                f"Got: {source_type}"
            )

        goal_format = _parse_goal_format(normalized_row, identifier)
        goal_format_serialized = _parse_serialized_goal_format(
            normalized_row,
            identifier,
        )
        resolutions = _selected_resolutions(normalized_row)

        if goal_format is not None and not resolutions:
            raise ValueError(
                f"No output resolutions selected for row {identifier}, but "
                f"goal_format is {goal_format!r}."
            )

        if goal_format is None and goal_format_serialized is None:
            raise ValueError(
                f"Neither goal_format nor goal_format_serialized is set for "
                f"row {identifier}."
            )

        return cls(
            identifier=identifier,
            package=package,
            source_type=source_type,  # type: ignore[arg-type]
            source=source,
            resolutions=resolutions,
            goal_format=goal_format,
            goal_format_serialized=goal_format_serialized,
            nsfw=_parse_bool(normalized_row, "nsfw", identifier),
            anchor_x=_parse_anchor(normalized_row, "anchor_x", identifier),
            anchor_y=_parse_anchor(normalized_row, "anchor_y", identifier),
            license=normalized_row.get("license", ""),
            author=normalized_row.get("author", ""),
            landing_url=normalized_row.get("landing_url", ""),
            provider=normalized_row.get("provider", ""),
            classes=normalized_row.get("classes", ""),
            notes=normalized_row.get("notes", ""),
        )


@dataclass(frozen=True, slots=True)
class ImageFixtureConfig:
    sources_csv: Path
    workspace_root: Path = Path.cwd()
    output_format_override: ImageOutputFormat | None = None
    jpeg_quality: int = 95
    small_image_mode: SmallImageMode = "error"
    package_filter: str | None = None
    output_dir: Path | None = None
    include_nsfw: bool = False
    update_source_info: bool = False

    error_mode: ErrorMode = "fail-fast"
    download_cache_dir: Path | None = None
    request_timeout_seconds: float = 60.0
    request_delay_seconds: float = 1.0
    download_retries: int = 5
    max_retry_after_seconds: float = 300.0
    user_agent: str = DEFAULT_DOWNLOAD_USER_AGENT


@dataclass(slots=True)
class ImageFixtureBuilder:
    config: ImageFixtureConfig
    _temporary_files: list[Path] = field(default_factory=list)
    _last_download_at: float | None = None
    _source_info_updates: dict[tuple[str, str, str], str] = field(default_factory=dict)

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

        failures: list[str] = []

        try:
            for row in rows:
                print(f"Building fixtures for {row.package}/{row.identifier}...")

                try:
                    source_resolution = self._build_row(row)

                    if self.config.update_source_info:
                        key = (row.package, row.identifier, row.source)
                        self._source_info_updates[key] = source_resolution
                except Exception as error:
                    message = f"{row.package}/{row.identifier}: {error}"
                    failures.append(message)

                    if self.config.error_mode == "fail-fast":
                        raise

                    print(f"[ERROR] {message}", file=sys.stderr)

            if self.config.update_source_info and self._source_info_updates:
                self._update_source_info()

            if failures:
                print("", file=sys.stderr)
                print("Fixture build finished with errors:", file=sys.stderr)

                for failure in failures:
                    print(f"  - {failure}", file=sys.stderr)

                if self.config.error_mode == "collect":
                    raise RuntimeError(
                        f"Fixture build failed for {len(failures)} row(s). "
                        "See the error summary above."
                    )
        finally:
            self._cleanup_temporary_files()

    def _build_row(self, row: ImageFixtureRow) -> str:
        source_path = self._resolve_source(row)
        package_dir = self._resolve_package_dir(row.package)
        output_root = self._resolve_output_root(package_dir)
        image_output_dir = output_root / row.identifier
        image_output_dir.mkdir(parents=True, exist_ok=True)

        with Image.open(source_path) as raw_image:
            image = ImageOps.exif_transpose(raw_image).convert("RGB")

        output_format = self.config.output_format_override or row.goal_format

        metadata: dict[str, object] = {
            "id": row.identifier,
            "package": row.package,
            "source_type": row.source_type,
            "source": row.source,
            "license": row.license,
            "author": row.author,
            "landing_url": row.landing_url,
            "provider": row.provider,
            "classes": row.classes,
            "notes": row.notes,
            "nsfw": row.nsfw,
            "goal_format": output_format,
            "goal_format_serialized": row.goal_format_serialized,
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

        if output_format is not None:
            if not row.resolutions:
                raise ValueError(
                    f"No output resolutions selected for row {row.identifier}."
                )

            metadata["outputs"] = self._build_image_outputs(
                row=row,
                image=image,
                image_output_dir=image_output_dir,
                output_format=output_format,
            )

        if row.goal_format_serialized is not None:
            serialized_path = image_output_dir / row.goal_format_serialized
            self._write_base64_fixture(source_path, serialized_path)
            metadata["serialized_output"] = {
                "format": "base64",
                "path": serialized_path.name,
            }

        (image_output_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return f"{image.width}x{image.height}"

    def _update_source_info(self) -> None:
        csv_path = self.config.sources_csv

        with csv_path.open("rb") as handle:
            has_utf8_bom = handle.read(3) == codecs.BOM_UTF8

        with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                raise ValueError(f"Fixture CSV has no header: {csv_path}")

            fieldnames = list(reader.fieldnames)
            raw_rows = list(reader)

        source_resolution_column = next(
            (
                column
                for column in fieldnames
                if _normalize_column_name(column) == "source_resolution"
            ),
            None,
        )

        if source_resolution_column is None:
            source_resolution_column = "source-resolution"
            fieldnames.append(source_resolution_column)

        updated_count = 0

        for raw_row in raw_rows:
            normalized_row = _normalize_row(raw_row)
            key = (
                normalized_row.get("package", ""),
                normalized_row.get("id", ""),
                normalized_row.get("source", ""),
            )
            source_resolution = self._source_info_updates.get(key)

            if source_resolution is None:
                continue

            raw_row[source_resolution_column] = source_resolution
            updated_count += 1

        temporary_path = csv_path.with_name(f".{csv_path.name}.tmp")

        try:
            encoding = "utf-8-sig" if has_utf8_bom else "utf-8"

            with temporary_path.open(
                "w",
                encoding=encoding,
                newline="",
            ) as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(raw_rows)

            temporary_path.replace(csv_path)
        finally:
            temporary_path.unlink(missing_ok=True)

        print(
            f"Updated source information for {updated_count} fixture row(s) in "
            f"{csv_path}."
        )

    def _build_image_outputs(
        self,
        *,
        row: ImageFixtureRow,
        image: Image.Image,
        image_output_dir: Path,
        output_format: ImageOutputFormat,
    ) -> dict[str, object]:
        outputs: dict[str, object] = {}
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
                                f"crop size is {crop.width}x{crop.height}."
                            )
                            continue
                        case "upscale":
                            pass

                output_file = (
                    image_output_dir
                    / aspect_name
                    / f"{resolution.filename}.{output_format}"
                )
                output_file.parent.mkdir(parents=True, exist_ok=True)

                resized = crop.resize(
                    (resolution.width, resolution.height),
                    Image.Resampling.LANCZOS,
                )
                self._save_image(resized, output_file, output_format)

                files.append(
                    {
                        "resolution": resolution.filename,
                        "path": str(output_file.relative_to(image_output_dir)),
                    }
                )

            outputs[aspect_name] = {
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

        return outputs

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

                if not source_path.is_file():
                    raise ValueError(
                        f"Source path is not a file for {row.identifier}: {source_path}"
                    )

                return source_path.resolve()
            case _:
                raise ValueError(f"Unsupported source type: {row.source_type}")

    def _download_source(self, url: str) -> Path:
        cache_path = self._download_cache_path(url)

        if self._cached_download_is_usable(cache_path):
            return cache_path

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = cache_path.with_name(f"{cache_path.name}.part")

        last_error: Exception | None = None
        sleep_before_attempt = 0.0
        max_attempts = self.config.download_retries + 1

        for attempt in range(max_attempts):
            if sleep_before_attempt > 0:
                time.sleep(sleep_before_attempt)

            self._throttle_downloads()

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": self.config.user_agent,
                    "Accept": "image/*,*/*;q=0.8",
                },
            )

            try:
                with urllib.request.urlopen(
                    request,
                    timeout=self.config.request_timeout_seconds,
                ) as response:
                    content_type = response.headers.get("Content-Type", "")
                    self._validate_content_type(content_type, url)

                    with temp_path.open("wb") as output:
                        shutil.copyfileobj(response, output)

                if temp_path.stat().st_size == 0:
                    raise ValueError(f"Downloaded image is empty: {url}")

                temp_path.replace(cache_path)
                return cache_path

            except urllib.error.HTTPError as error:
                last_error = error
                temp_path.unlink(missing_ok=True)

                if (
                    error.code not in _TRANSIENT_HTTP_STATUS_CODES
                    or attempt == max_attempts - 1
                ):
                    raise RuntimeError(
                        f"HTTP {error.code} while downloading fixture image: {url}"
                    ) from error

                retry_after = None
                if error.code == 429:
                    retry_after = _parse_retry_after(error.headers.get("Retry-After"))

                sleep_before_attempt = self._retry_delay_seconds(
                    attempt=attempt + 1,
                    retry_after=retry_after,
                )

                print(
                    f"Transient HTTP {error.code} while downloading fixture image. "
                    f"Retrying in {sleep_before_attempt:.1f}s "
                    f"({attempt + 1}/{self.config.download_retries}): {url}",
                    file=sys.stderr,
                )

            except (
                urllib.error.URLError,
                TimeoutError,
                socket.timeout,
                ValueError,
            ) as error:
                last_error = error
                temp_path.unlink(missing_ok=True)

                if attempt == max_attempts - 1:
                    break

                sleep_before_attempt = self._retry_delay_seconds(
                    attempt=attempt + 1,
                    retry_after=None,
                )

                print(
                    f"Download failed. Retrying in {sleep_before_attempt:.1f}s "
                    f"({attempt + 1}/{self.config.download_retries}): {url}. "
                    f"Reason: {error}",
                    file=sys.stderr,
                )

        raise RuntimeError(
            f"Failed to download fixture image after {max_attempts} attempt(s): {url}"
        ) from last_error

    def _download_cache_path(self, url: str) -> Path:
        cache_root = self.config.download_cache_dir

        if cache_root is None:
            cache_root = self.config.workspace_root / ".cache" / "fixture-images"

        parsed = urlparse(url)
        suffix = Path(parsed.path).suffix.lower()

        if not suffix or len(suffix) > 10:
            suffix = ".img"

        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:24]

        return cache_root.expanduser() / f"{digest}{suffix}"

    @staticmethod
    def _validate_content_type(content_type: str, url: str) -> None:
        if not content_type:
            return

        media_type = content_type.split(";", maxsplit=1)[0].strip().lower()

        if media_type.startswith("image/"):
            return

        if media_type in {"application/octet-stream", "binary/octet-stream"}:
            return

        raise ValueError(
            f"URL did not return an image. Content-Type was {content_type!r}: {url}"
        )

    @staticmethod
    def _cached_download_is_usable(path: Path) -> bool:
        if not path.exists():
            return False

        if path.stat().st_size == 0:
            path.unlink(missing_ok=True)
            return False

        try:
            with Image.open(path) as image:
                image.verify()
        except (OSError, UnidentifiedImageError):
            print(f"Ignoring invalid cached fixture download: {path}", file=sys.stderr)
            path.unlink(missing_ok=True)
            return False

        return True

    def _throttle_downloads(self) -> None:
        delay = self.config.request_delay_seconds

        if delay <= 0:
            return

        now = time.monotonic()

        if self._last_download_at is not None:
            elapsed = now - self._last_download_at
            remaining = delay - elapsed

            if remaining > 0:
                time.sleep(remaining)

        self._last_download_at = time.monotonic()

    def _retry_delay_seconds(
        self,
        *,
        attempt: int,
        retry_after: float | None,
    ) -> float:
        if retry_after is not None:
            if retry_after > self.config.max_retry_after_seconds:
                raise RuntimeError(
                    f"Server requested Retry-After={retry_after:.0f}s, "
                    f"which is above the configured maximum of "
                    f"{self.config.max_retry_after_seconds:.0f}s. "
                    "Run the command later or increase --max-retry-after."
                )

            return retry_after

        base = max(self.config.request_delay_seconds, 1.0)
        exponential = base * (2 ** max(attempt - 1, 0))
        jitter = random.uniform(0.0, min(1.0, exponential * 0.25))

        return min(exponential + jitter, self.config.max_retry_after_seconds)

    def _read_rows(self) -> list[ImageFixtureRow]:
        if not self.config.sources_csv.exists():
            raise FileNotFoundError(
                f"Fixture CSV does not exist: {self.config.sources_csv}"
            )

        rows: list[ImageFixtureRow] = []
        skipped_nsfw = 0

        with self.config.sources_csv.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)

            if reader.fieldnames is None:
                raise ValueError(f"Fixture CSV has no header: {self.config.sources_csv}")

            for row_number, raw_row in enumerate(reader, start=2):
                normalized_row = _normalize_row(raw_row)
                identifier = normalized_row.get("id", f"CSV row {row_number}")

                try:
                    is_nsfw = _parse_bool(normalized_row, "nsfw", identifier)
                except Exception as error:
                    raise ValueError(
                        f"Invalid fixture CSV row {row_number} in "
                        f"{self.config.sources_csv}: {error}"
                    ) from error

                if is_nsfw and not self.config.include_nsfw:
                    skipped_nsfw += 1
                    continue

                try:
                    rows.append(ImageFixtureRow.from_csv_row(normalized_row))
                except Exception as error:
                    raise ValueError(
                        f"Invalid fixture CSV row {row_number} in "
                        f"{self.config.sources_csv}: {error}"
                    ) from error

        if skipped_nsfw:
            print(
                f"Skipped {skipped_nsfw} NSFW fixture row(s). "
                "Use --nsfw to include them."
            )

        return rows

    def _save_image(
        self,
        image: Image.Image,
        output_file: Path,
        output_format: ImageOutputFormat,
    ) -> None:
        match output_format:
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
                raise ValueError(f"Unsupported output format: {output_format}")

    @staticmethod
    def _write_base64_fixture(source_path: Path, output_path: Path) -> None:
        encoded = base64.b64encode(source_path.read_bytes()).decode("ascii")
        output_path.write_text(encoded + "\n", encoding="ascii")

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


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None

    try:
        return max(float(value), 0.0)
    except ValueError:
        pass

    try:
        retry_time = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None

    if retry_time.tzinfo is None:
        retry_time = retry_time.replace(tzinfo=timezone.utc)

    return max((retry_time - datetime.now(timezone.utc)).total_seconds(), 0.0)


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {
        _normalize_column_name(key): (value or "").strip()
        for key, value in row.items()
        if key is not None
    }


def _normalize_column_name(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("×", "x")
    )


def _require(row: dict[str, str], key: str) -> str:
    value = row.get(key, "").strip()

    if not value:
        raise ValueError(f"Missing required CSV column value: {key}")

    return value


def _parse_bool(row: dict[str, str], key: str, identifier: str) -> bool:
    value = row.get(key, "").strip().lower()

    if value in _TRUE_VALUES:
        return True

    if value in _FALSE_VALUES:
        return False

    raise ValueError(
        f"Invalid boolean value for {key} in row {identifier}: {value!r}"
    )


def _parse_anchor(row: dict[str, str], key: str, identifier: str) -> float:
    value = row.get(key, "").strip()

    if not value:
        return 0.5

    normalized = value.replace(",", ".")

    try:
        anchor = float(normalized)
    except ValueError as error:
        raise ValueError(f"Invalid {key} for row {identifier}: {value}") from error

    if not 0.0 <= anchor <= 1.0:
        raise ValueError(f"{key} must be between 0.0 and 1.0 for row {identifier}")

    return anchor


def _parse_goal_format(
    row: dict[str, str],
    identifier: str,
) -> ImageOutputFormat | None:
    value = row.get("goal_format", "").strip().lower()

    if value in _FALSE_VALUES:
        return None

    if value == "jpeg":
        return "jpg"

    if value not in {"jpg", "png"}:
        raise ValueError(
            f"Invalid goal_format for row {identifier}: {value!r}. "
            "Supported values are jpg, png, or None."
        )

    return value  # type: ignore[return-value]


def _parse_serialized_goal_format(
    row: dict[str, str],
    identifier: str,
) -> SerializedOutputFormat | None:
    value = row.get("goal_format_serialized", "").strip().lower()

    if value in _FALSE_VALUES:
        return None

    if value in {"base64.txt", "base_64", "base64"}:
        value = "base_64.txt"

    if value != "base_64.txt":
        raise ValueError(
            f"Invalid goal_format_serialized for row {identifier}: {value!r}. "
            "Currently supported: base_64.txt or None."
        )

    return "base_64.txt"


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
        "provider",
        "classes",
        "notes",
        "nsfw",
        "goal_format",
        "goal_format_serialized",
        "source_resolution",
        "in_source_resolution",
        "swap_sides",
    }

    selected: list[Resolution] = []

    for column, value in row.items():

        if column in reserved_columns or not column:
            continue

        if value.strip().lower() not in _TRUE_VALUES:
            continue

        selected.append(Resolution.parse(column))

    return tuple(selected)
