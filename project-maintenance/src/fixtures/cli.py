from __future__ import annotations

import argparse
import base64
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .image_fixtures import (
    DEFAULT_DOWNLOAD_USER_AGENT,
    ErrorMode,
    ImageFixtureBuilder,
    ImageFixtureConfig,
    SmallImageMode,
)


@dataclass(frozen=True, slots=True)
class Base64FixtureCommand:
    image_path: Path
    output_path: Path | None

    def run(self) -> None:
        image_path = self.image_path.expanduser()

        if not image_path.exists():
            raise FileNotFoundError(f"Image file does not exist: {image_path}")

        if not image_path.is_file():
            raise ValueError(f"Image path is not a file: {image_path}")

        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")

        if self.output_path is None:
            sys.stdout.write(encoded)
            sys.stdout.write("\n")
            return

        output_path = self.output_path.expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(encoded + "\n", encoding="ascii")


@dataclass(frozen=True, slots=True)
class BuildImageFixturesCommand:
    sources_csv: Path
    workspace_root: Path
    output_format: str
    jpeg_quality: int
    small_image_mode: SmallImageMode
    package_filter: str | None
    output_dir: Path | None

    error_mode: ErrorMode
    download_cache_dir: Path | None
    request_timeout_seconds: float
    request_delay_seconds: float
    download_retries: int
    max_retry_after_seconds: float
    user_agent: str

    def run(self) -> None:
        ImageFixtureBuilder(
            ImageFixtureConfig(
                sources_csv=self.sources_csv.expanduser(),
                workspace_root=self.workspace_root.expanduser(),
                output_format=cast(Any, self.output_format),
                jpeg_quality=self.jpeg_quality,
                small_image_mode=self.small_image_mode,
                package_filter=self.package_filter,
                output_dir=self.output_dir.expanduser() if self.output_dir else None,
                error_mode=self.error_mode,
                download_cache_dir=(
                    self.download_cache_dir.expanduser()
                    if self.download_cache_dir is not None
                    else None
                ),
                request_timeout_seconds=self.request_timeout_seconds,
                request_delay_seconds=self.request_delay_seconds,
                download_retries=self.download_retries,
                max_retry_after_seconds=self.max_retry_after_seconds,
                user_agent=self.user_agent,
            )
        ).run()


def parse_jpeg_quality(value: str) -> int:
    try:
        quality = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("JPEG quality must be an integer.") from error

    if not 1 <= quality <= 100:
        raise argparse.ArgumentTypeError("JPEG quality must be between 1 and 100.")

    return quality


def parse_positive_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Value must be a number.") from error

    if parsed <= 0:
        raise argparse.ArgumentTypeError("Value must be greater than 0.")

    return parsed


def parse_non_negative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Value must be a number.") from error

    if parsed < 0:
        raise argparse.ArgumentTypeError("Value must be non-negative.")

    return parsed


def parse_non_negative_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Value must be an integer.") from error

    if parsed < 0:
        raise argparse.ArgumentTypeError("Value must be non-negative.")

    return parsed


def run_to_base64(args: argparse.Namespace) -> None:
    out_path:Path = args.out
    if out_path is None:
        out_path = args.image.with_suffix(".txt")

    Base64FixtureCommand(
        image_path=args.image,
        output_path=out_path,
    ).run()


def run_build_image_fixtures(args: argparse.Namespace) -> None:
    BuildImageFixturesCommand(
        sources_csv=args.sources,
        workspace_root=args.workspace_root,
        output_format=args.format,
        jpeg_quality=args.jpeg_quality,
        small_image_mode=cast(SmallImageMode, args.on_small),
        package_filter=args.package,
        output_dir=args.out_dir,
        error_mode=cast(ErrorMode, args.on_error),
        download_cache_dir=args.download_cache_dir,
        request_timeout_seconds=args.request_timeout,
        request_delay_seconds=args.request_delay,
        download_retries=args.download_retries,
        max_retry_after_seconds=args.max_retry_after,
        user_agent=args.user_agent,
    ).run()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fixtures",
        description="Fixture utility commands.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    add_to_base64_parser(subparsers)
    add_build_image_fixtures_parser(subparsers)

    return parser


def add_to_base64_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser(
        "to-base64",
        aliases=["to_base64"],
        help="Convert an image file to a base64 text fixture.",
    )

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Input image file.",
    )

    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output text file. Prints to stdout if omitted.",
    )

    parser.set_defaults(handler=run_to_base64)


def add_build_image_fixtures_parser(subparsers: Any) -> None:
    parser = subparsers.add_parser(
        "build-image-fixtures",
        aliases=["build_image_fixtures"],
        help="Build cropped image fixtures from a CSV manifest.",
    )

    parser.add_argument(
        "--sources",
        type=Path,
        required=True,
        help="CSV manifest defining source images, target packages, and resolutions.",
    )

    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path.cwd(),
        help="Workspace root. Defaults to the current working directory.",
    )

    parser.add_argument(
        "--package",
        default=None,
        help="Optional package filter. If omitted, all CSV rows are processed.",
    )

    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help=(
            "Optional output override. If omitted, files are written to "
            "<package>/tests/fixtures/images."
        ),
    )

    parser.add_argument(
        "--format",
        choices=["jpg", "png"],
        default="jpg",
        help="Output image format.",
    )

    parser.add_argument(
        "--jpeg-quality",
        type=parse_jpeg_quality,
        default=95,
        help="JPEG quality if --format jpg is used. Must be between 1 and 100.",
    )

    parser.add_argument(
        "--on-small",
        choices=["error", "skip", "upscale"],
        default="error",
        help="What to do if the source crop is smaller than a requested output.",
    )

    parser.add_argument(
        "--on-error",
        choices=["fail-fast", "collect", "ignore"],
        default="fail-fast",
        help=(
            "How row failures are handled. 'fail-fast' aborts immediately, "
            "'collect' processes all rows and fails at the end, and 'ignore' "
            "processes all rows and returns success."
        ),
    )

    parser.add_argument(
        "--download-cache-dir",
        type=Path,
        default=None,
        help=(
            "Directory for cached URL downloads. Defaults to "
            "<workspace-root>/.cache/fixture-images."
        ),
    )

    parser.add_argument(
        "--request-timeout",
        type=parse_positive_float,
        default=60.0,
        help="HTTP request timeout in seconds.",
    )

    parser.add_argument(
        "--request-delay",
        type=parse_non_negative_float,
        default=2.0,
        help="Minimum delay between uncached downloads in seconds.",
    )

    parser.add_argument(
        "--download-retries",
        type=parse_non_negative_int,
        default=6,
        help="Number of retry attempts for transient download errors.",
    )

    parser.add_argument(
        "--max-retry-after",
        type=parse_positive_float,
        default=300.0,
        help=(
            "Maximum Retry-After delay to wait automatically. If the server "
            "requests a longer delay, the command fails instead."
        ),
    )

    parser.add_argument(
        "--user-agent",
        default=DEFAULT_DOWNLOAD_USER_AGENT,
        help=(
            "HTTP User-Agent for downloads. For Wikimedia, use a descriptive "
            "value with contact information."
        ),
    )

    parser.set_defaults(handler=run_build_image_fixtures)


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    args.handler(args)


if __name__ == "__main__":
    main()