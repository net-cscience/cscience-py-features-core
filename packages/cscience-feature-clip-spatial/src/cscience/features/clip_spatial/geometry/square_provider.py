import numpy as np

from cscience.features.api import SpatialRegion

from .geometry_provider import GeometryProvider


class SquareProvider(GeometryProvider):
    """Square or rectangular region provider based on relative window size.
    geometry_size: tuple[float, float] - relative size of the region (height, width) in relation to the image dimensions.
    """

    def __init__(self, geometry_size: tuple[float, float]) -> None:
        self.geometry_size = geometry_size

    def create_region(
        self,
        *,
        index: int,
        row: int,
        column: int,
        center_x: int,
        center_y: int,
        image_width: int,
        image_height: int,
    ) -> SpatialRegion:
        region_h_rel, region_w_rel = self.geometry_size

        win_w = max(1, round(region_w_rel * image_width))
        win_h = max(1, round(region_h_rel * image_height))

        x0 = center_x - win_w // 2
        y0 = center_y - win_h // 2

        x0 = max(0, min(image_width - win_w, x0))
        y0 = max(0, min(image_height - win_h, y0))

        x1 = x0 + win_w
        y1 = y0 + win_h

        return SpatialRegion(
            index=index,
            row=row,
            column=column,
            center_x=center_x,
            center_y=center_y,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            nx0=x0 / image_width,
            ny0=y0 / image_height,
            nx1=x1 / image_width,
            ny1=y1 / image_height,
        )

    import numpy as np

    from cscience.features.api import SpatialRegion

    def create_mask(
            self,
            *,
            region: SpatialRegion,
            image_width: int,
            image_height: int,
    ) -> np.ndarray:
        mask = np.zeros(
            (image_height, image_width),
            dtype=bool,
        )

        mask[
            region.y0:region.y1,
            region.x0:region.x1,
        ] = True

        return mask