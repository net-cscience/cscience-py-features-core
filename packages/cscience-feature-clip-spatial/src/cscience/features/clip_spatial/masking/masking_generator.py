import torch
import torch.nn.functional as F

from cscience.features.api import SpatialBatchLayout, SpatialRegion

from ..filter.filter_provider import FilterProvider
from ..geometry.geometry_provider import GeometryProvider
from ..indexer.spatial_indexer import SpatialIndexer
from .masking_mode import MaskingMode


class MaskingGenerator:
    """Creates masked or extracted image variants for spatial CLIP."""

    def __init__(
        self,
        *,
        indexer: SpatialIndexer,
        geometry: GeometryProvider,
        filter_provider: FilterProvider,
        mode: MaskingMode,
    ) -> None:
        self.indexer = indexer
        self.geometry = geometry
        self.filter_provider = filter_provider
        self.mode = mode

    @property
    def layout(self) -> SpatialBatchLayout:
        return self.indexer.layout

    @property
    def regions(self) -> tuple[SpatialRegion, ...]:
        return self.indexer.regions

    @property
    def item_keys(self) -> tuple[int, ...]:
        return self.indexer.item_keys

    def generate(self, base_tensors: torch.Tensor) -> torch.Tensor:
        """Return masked/extracted variants.

        Input:
            [N, C, H, W]

        Output:
            [N * R, C, H, W]
        """
        if base_tensors.ndim != 4:
            raise ValueError(
                f"Expected base_tensors [N, C, H, W], got {tuple(base_tensors.shape)}."
            )

        if base_tensors.shape[0] != self.layout.item_count:
            raise ValueError(
                f"Tensor item count must match layout.item_count: "
                f"{base_tensors.shape[0]} != {self.layout.item_count}."
            )

        variants: list[torch.Tensor] = []

        for spatial_index in self.indexer.iter_indices():
            base = base_tensors[spatial_index.item_index]
            variant = self._make_variant(base, spatial_index.region)
            variants.append(variant)

        result = torch.stack(variants)

        if result.shape[0] != self.layout.flat_count:
            raise RuntimeError(
                f"Expected {self.layout.flat_count} variants, got {result.shape[0]}."
            )

        return result

    def _make_variant(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        if self.mode == MaskingMode.MASK_OUT:
            return self._mask_out(base, region)

        if self.mode == MaskingMode.KEEP_ONLY:
            return self._keep_only(base, region)

        if self.mode == MaskingMode.EXTRACT:
            return self._extract(base, region)

        raise ValueError(f"Unknown masking mode: {self.mode}.")

    def _mask_out(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        variant = base.clone()
        window = self.geometry.select(variant, region)

        fill = self.filter_provider.create_fill(
            base_tensor=base,
            region=region,
            window=window,
        )

        window[:, :, :] = fill
        return variant

    def _keep_only(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        variant = torch.zeros_like(base)

        dst = self.geometry.select(variant, region)
        src = self.geometry.select(base, region)

        dst[:, :, :] = src

        return variant

    def _extract(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        crop = self.geometry.select(base, region)
        crop = crop.unsqueeze(0)

        resized = F.interpolate(
            crop,
            size=base.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )

        return resized.squeeze(0)