import unittest

from cscience.features.clip_spatial.geometry.square_provider import SquareProvider
from cscience.features.clip_spatial.indexer.spatial_indexer import SpatialIndexer


class SpatialIndexerTest(unittest.TestCase):

    def test_builds_expected_3x3_regions(self) -> None:
        geometry = SquareProvider(
            geometry_size=(1 / 3, 1 / 3),
        )

        indexer = SpatialIndexer(
            item_keys=(10, 20),
            image_width=224,
            image_height=224,
            grid_shape=(3, 3),
            start_point=(1 / 6, 1 / 6),
            step_size=(1 / 3, 1 / 3),
            geometry=geometry,
        )

        self.assertEqual(indexer.layout.item_count, 2)
        self.assertEqual(indexer.layout.regions_per_item, 9)
        self.assertEqual(indexer.layout.flat_count, 18)
        self.assertEqual(len(indexer.regions), 9)

        first = indexer.regions[0]
        self.assertEqual(first.index, 0)
        self.assertEqual(first.grid_yx, (0, 0))
        self.assertEqual(first.grid_xy, (0, 0))

        center = indexer.regions[4]
        self.assertEqual(center.index, 4)
        self.assertEqual(center.grid_yx, (1, 1))
        self.assertEqual(center.grid_xy, (1, 1))

    def test_flat_index_mapping_preserves_item_and_region(self) -> None:
        geometry = SquareProvider(
            geometry_size=(1 / 3, 1 / 3),
        )

        indexer = SpatialIndexer(
            item_keys=(100, 200),
            image_width=224,
            image_height=224,
            grid_shape=(3, 3),
            start_point=(1 / 6, 1 / 6),
            step_size=(1 / 3, 1 / 3),
            geometry=geometry,
        )

        flat = indexer.layout.to_flat_index(
            item_index=1,
            region_index=5,
        )

        spatial_index = indexer.from_flat_index(flat)

        self.assertEqual(flat, 14)
        self.assertEqual(spatial_index.item_index, 1)
        self.assertEqual(spatial_index.item_key, 200)
        self.assertEqual(spatial_index.region_index, 5)
        self.assertEqual(spatial_index.region.index, 5)