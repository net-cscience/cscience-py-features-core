from dataclasses import dataclass

from cscience.features.api import SpatialBatchLayout, SpatialRegion
from .spatial_index import SpatialIndex

from ..geometry.geometry_provider import GeometryProvider




class SpatialIndexer:
    """Creates spatial regions and maps local indices to flat batch indices."""

    def __init__(
        self,
        *,
        item_keys: tuple[int, ...],
        image_width: int,
        image_height: int,
        grid_shape: tuple[int, int],
        start_point: tuple[float, float],
        step_size: tuple[float, float],
        geometry: GeometryProvider,
    ) -> None:
        self.item_keys = item_keys
        self.image_width = image_width
        self.image_height = image_height
        self.grid_shape = grid_shape
        self.start_point = start_point
        self.step_size = step_size
        self.geometry = geometry

        self.regions = self._build_regions()

        self.layout = SpatialBatchLayout(
            item_count=len(item_keys),
            regions_per_item=len(self.regions),
        )

    def __len__(self) -> int:
        return self.layout.flat_count

    def local_region_count(self) -> int:
        return self.layout.regions_per_item

    def _build_regions(self) -> tuple[SpatialRegion, ...]:
        rows, columns = self.grid_shape
        start_y, start_x = self.start_point
        step_y, step_x = self.step_size

        regions: list[SpatialRegion] = []

        for row in range(rows):
            for column in range(columns):
                index = row * columns + column

                center_x = round((start_x + column * step_x) * self.image_width)
                center_y = round((start_y + row * step_y) * self.image_height)

                center_x = max(0, min(self.image_width - 1, center_x))
                center_y = max(0, min(self.image_height - 1, center_y))

                region = self.geometry.create_region(
                    index=index,
                    row=row,
                    column=column,
                    center_x=center_x,
                    center_y=center_y,
                    image_width=self.image_width,
                    image_height=self.image_height,
                )

                regions.append(region)

        return tuple(regions)

    def iter_regions(self) -> tuple[SpatialRegion, ...]:
        return self.regions

    def iter_indices(self):
        """Yield all global flat indices with local item/region metadata."""
        for item_index, item_key in enumerate(self.item_keys):
            for region in self.regions:
                flat_index = self.layout.to_flat_index(
                    item_index=item_index,
                    region_index=region.index,
                )

                yield SpatialIndex(
                    item_index=item_index,
                    item_key=item_key,
                    region_index=region.index,
                    flat_index=flat_index,
                    region=region,
                )

    def from_flat_index(self, flat_index: int) -> SpatialIndex:
        item_index, region_index = self.layout.from_flat_index(flat_index)
        item_key = self.item_keys[item_index]
        region = self.regions[region_index]

        return SpatialIndex(
            item_index=item_index,
            item_key=item_key,
            region_index=region_index,
            flat_index=flat_index,
            region=region,
        )