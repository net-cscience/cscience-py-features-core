from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from cscience.features.clip_spatial.clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)


def _get_item_index(
    scores: SpatialScoreVectorBatch,
    item_key: int | None,
) -> int:
    if item_key is None:
        if len(scores.item_keys) != 1:
            raise ValueError(
                "item_key is required when scores contain multiple items."
            )

        return 0

    try:
        return scores.item_keys.index(item_key)
    except ValueError as error:
        raise KeyError(f"Unknown item key: {item_key}.") from error


def _get_query_index(
    scores: SpatialScoreVectorBatch,
    query_key: int | None,
) -> int:
    if query_key is None:
        if len(scores.query_keys) != 1:
            raise ValueError(
                "query_key is required when scores contain multiple queries."
            )

        return 0

    try:
        return scores.query_keys.index(query_key)
    except ValueError as error:
        raise KeyError(f"Unknown query key: {query_key}.") from error


def _get_region_scores(
    scores: SpatialScoreVectorBatch,
    *,
    item_key: int | None,
    query_key: int | None,
) -> torch.Tensor:
    item_index = _get_item_index(scores, item_key)
    query_index = _get_query_index(scores, query_key)

    return torch.tensor([
        scores.vectors[
            scores.layout.to_flat_index(
                item_index=item_index,
                region_index=region.index,
            )
        ][query_index]
        for region in scores.regions
    ], dtype=torch.float32)


def _get_base_score(
    scores: SpatialScoreVectorBatch,
    *,
    item_key: int | None,
    query_key: int | None,
) -> float:
    item_index = _get_item_index(scores, item_key)
    query_index = _get_query_index(scores, query_key)

    resolved_item_key = scores.item_keys[item_index]

    return float(
        scores.data().base_vectors[resolved_item_key][query_index]
    )


def target_point_hard(
    scores: SpatialScoreVectorBatch,
    *,
    item_key: int | None = None,
    query_key: int | None = None,
) -> tuple[int, int]:
    region_scores = _get_region_scores(
        scores,
        item_key=item_key,
        query_key=query_key,
    )

    best_index = int(torch.argmax(region_scores).item())

    return scores.regions[best_index].center_xy


def target_point_soft(
    scores: SpatialScoreVectorBatch,
    *,
    item_key: int | None = None,
    query_key: int | None = None,
) -> tuple[int, int]:
    region_scores = _get_region_scores(
        scores,
        item_key=item_key,
        query_key=query_key,
    )

    weights = torch.softmax(
        F.normalize(region_scores, dim=0) / 0.05,
        dim=0,
    )

    xs = torch.tensor(
        [region.center_x for region in scores.regions],
        dtype=torch.float32,
    )

    ys = torch.tensor(
        [region.center_y for region in scores.regions],
        dtype=torch.float32,
    )

    return (
        int((weights * xs).sum().item()),
        int((weights * ys).sum().item()),
    )


def plot_spatial_scores(
    image: Image.Image | np.ndarray,
    scores: SpatialScoreVectorBatch,
    *,
    item_key: int | None = None,
    query_key: int | None = None,
    alpha: float = 0.45,
    label: str | None = None,
    show_region_scores: bool = True,
    show_base_score: bool = True,
    show: bool = True,
    output_path: Path | None = None,
) -> Path | None:
    """Plot one item/query combination from a spatial score batch."""
    image_array = _to_numpy_image(image)
    image_height, image_width = image_array.shape[:2]

    _validate_coordinate_space(
        scores,
        image_width=image_width,
        image_height=image_height,
    )

    region_scores = _get_region_scores(
        scores,
        item_key=item_key,
        query_key=query_key,
    )

    base_score = _get_base_score(
        scores,
        item_key=item_key,
        query_key=query_key,
    )

    score_map = np.zeros(
        (image_height, image_width),
        dtype=np.float32,
    )

    coverage = np.zeros(
        (image_height, image_width),
        dtype=np.float32,
    )

    figure, axis = plt.subplots(figsize=(10, 8))

    for region, score in zip(
        scores.regions,
        region_scores,
        strict=True,
    ):
        value = float(score.item())

        score_map[
            region.y0:region.y1,
            region.x0:region.x1,
        ] += value

        coverage[
            region.y0:region.y1,
            region.x0:region.x1,
        ] += 1

        if show_region_scores:
            axis.text(
                region.center_x,
                region.center_y,
                f"{value:.3f}\n{region.grid_xy}",
                ha="center",
                va="center",
                color="white",
            )

    covered = coverage > 0
    score_map[covered] /= coverage[covered]

    axis.imshow(image_array)

    axis.imshow(
        np.ma.masked_where(~covered, score_map),
        alpha=alpha,
        cmap="magma",
        interpolation="nearest",
    )

    hard_x, hard_y = target_point_hard(
        scores,
        item_key=item_key,
        query_key=query_key,
    )

    axis.plot(
        hard_x,
        hard_y,
        "X",
        markersize=13,
    )

    soft_x, soft_y = target_point_soft(
        scores,
        item_key=item_key,
        query_key=query_key,
    )

    axis.plot(
        soft_x,
        soft_y,
        "D",
        markersize=10,
    )

    axis.axis("off")

    title_parts = []

    if label is not None:
        title_parts.append(label)

    if show_base_score:
        title_parts.append(f"Base image score: {base_score:.3f}")

    if title_parts:
        axis.set_title("\n".join(title_parts))

    figure.tight_layout()

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(
            output_path,
            bbox_inches="tight",
            dpi=300,
        )

    if show:
        plt.show()
    else:
        plt.close(figure)

    return output_path


def plot_all_spatial_scores(
    images: Mapping[int, Image.Image | np.ndarray],
    scores: SpatialScoreVectorBatch,
    *,
    output_directory: Path | None = None,
    show_region_scores: bool = True,
    show_base_score: bool = True,
    show: bool = True,
) -> list[Path]:
    """Plot every item/query combination."""
    output_paths: list[Path] = []

    for item_key in scores.item_keys:
        image = images[item_key]

        for query_key in scores.query_keys:
            output_path = None

            if output_directory is not None:
                output_path = (
                    output_directory
                    / f"item-{item_key}_query-{query_key}.png"
                )

            result = plot_spatial_scores(
                image,
                scores,
                item_key=item_key,
                query_key=query_key,
                label=f"Item {item_key} — query {query_key}",
                show_region_scores=show_region_scores,
                show_base_score=show_base_score,
                show=show,
                output_path=output_path,
            )

            if result is not None:
                output_paths.append(result)

    return output_paths


def _to_numpy_image(
    image: Image.Image | np.ndarray,
) -> np.ndarray:
    if isinstance(image, Image.Image):
        return (
            np.asarray(
                image.convert("RGB"),
                dtype=np.float32,
            )
            / 255.0
        )

    array = np.asarray(image, dtype=np.float32)

    if array.max() > 1.0:
        array /= 255.0

    return array


def _validate_coordinate_space(
    scores: SpatialScoreVectorBatch,
    *,
    image_width: int,
    image_height: int,
) -> None:
    expected_width, expected_height = _infer_coordinate_size(scores)

    if (
        image_width != expected_width
        or image_height != expected_height
    ):
        raise ValueError(
            "Image dimensions do not match the spatial "
            "coordinate system of the scores: "
            f"image={image_width}x{image_height}, "
            f"scores={expected_width}x{expected_height}."
        )


def _infer_coordinate_size(
    scores: SpatialScoreVectorBatch,
) -> tuple[int, int]:
    width_candidates: list[float] = []
    height_candidates: list[float] = []

    for region in scores.regions:
        if region.nx0 > 0:
            width_candidates.append(region.x0 / region.nx0)

        if region.nx1 > 0:
            width_candidates.append(region.x1 / region.nx1)

        if region.ny0 > 0:
            height_candidates.append(region.y0 / region.ny0)

        if region.ny1 > 0:
            height_candidates.append(region.y1 / region.ny1)

    return (
        round(float(np.median(width_candidates))),
        round(float(np.median(height_candidates))),
    )