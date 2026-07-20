from dataclasses import dataclass

import icontract


@dataclass(frozen=True, slots=True)
class SpatialRegion:
    """Spatial region metadata.

    Pixel coordinates use half-open bounds:

        [x0, x1)
        [y0, y1)

    Normalized coordinates use the same convention in [0, 1].

    ``row == column == -1`` represents a non-grid region,
    such as the complete image.
    """

    index: int

    row: int
    column: int

    center_x: int
    center_y: int

    x0: int
    y0: int
    x1: int
    y1: int

    nx0: float
    ny0: float
    nx1: float
    ny1: float


    @property
    def center_xy(self) -> tuple[int, int]:
        """Return the center coordinates as a tuple."""
        return self.center_x, self.center_y

    @property
    def grid_xy(self) -> tuple[int, int]:
        """Return the grid coordinates as a tuple."""
        return self.row, self.column

    @property
    def grid_yx(self) -> tuple[int, int]:
        """Return the grid coordinates as a tuple."""
        return self.column, self.row

    @icontract.require(lambda self: self.index >= 0, "index must be non-negative.", )
    @icontract.require(lambda self: (self.row >= 0 and self.column >= 0)
                                    or (self.row == -1 and self.column == -1),
                       "row and column must either both be non-negative or both be -1.",
                       )
    @icontract.require(lambda self: self.x1 > self.x0, "x1 must be greater than x0.", )
    @icontract.require(lambda self: self.y1 > self.y0, "y1 must be greater than y0.", )
    @icontract.require(lambda self: self.x0 <= self.center_x < self.x1, "center_x must be inside [x0, x1).", )
    @icontract.require(lambda self: self.y0 <= self.center_y < self.y1, "center_y must be inside [y0, y1).", )
    @icontract.require(lambda self:
                       all(0.0 <= value <= 1.0 for value in (self.nx0, self.ny0, self.nx1, self.ny1,)),
                       "normalized coordinates must be in [0, 1].",
                       )
    @icontract.require(lambda self: self.nx1 > self.nx0, "nx1 must be greater than nx0.", )
    @icontract.require(lambda self: self.ny1 > self.ny0, "ny1 must be greater than ny0.", )
    def __post_init__(self) -> None:
        pass
