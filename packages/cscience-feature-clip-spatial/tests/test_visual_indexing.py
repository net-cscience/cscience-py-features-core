import unittest
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from cscience.features.clip_spatial.filter.zero_provider import ZeroProvider
from cscience.features.clip_spatial.geometry.square_provider import SquareProvider
from cscience.features.clip_spatial.indexer.spatial_indexer import SpatialIndexer
from cscience.features.clip_spatial.masking.masking_generator import MaskingGenerator
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture_tensor(name: str, size: tuple[int, int] = (224, 224)) -> torch.Tensor:
    image = Image.open(FIXTURE_DIR / name).convert("RGB").resize(size)
    array = np.asarray(image, dtype=np.float32) / 255.0

    return torch.from_numpy(array).permute(2, 0, 1)


def make_indexer(
    item_keys: tuple[int, ...],
    image_width: int = 224,
    image_height: int = 224,
) -> tuple[SpatialIndexer, SquareProvider]:
    geometry = SquareProvider(
        geometry_size=(1 / 3, 1 / 3),
    )

    indexer = SpatialIndexer(
        item_keys=item_keys,
        image_width=image_width,
        image_height=image_height,
        grid_shape=(3, 3),
        start_point=(1 / 6, 1 / 6),
        step_size=(1 / 3, 1 / 3),
        geometry=geometry,
    )

    return indexer, geometry


class TestVisualIndexing(unittest.TestCase):

    def test_keep_only_creates_flat_spatial_batch_for_one_image(self) -> None:
        base = load_fixture_tensor("dogbird.png").unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.KEEP_ONLY,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (9, 3, 224, 224))
        self.assertEqual(generator.layout.flat_count, 9)
        self.assertEqual(generator.item_keys, (0,))
        self.assertEqual(len(generator.regions), 9)

        region = generator.regions[0]

        selected = result[0, :, region.y0:region.y1, region.x0:region.x1]
        expected = base[0, :, region.y0:region.y1, region.x0:region.x1]

        self.assertTrue(torch.allclose(selected, expected))

        outside_mask = torch.ones_like(result[0], dtype=torch.bool)
        outside_mask[:, region.y0:region.y1, region.x0:region.x1] = False

        self.assertTrue(torch.all(result[0][outside_mask] == 0.0))

    def test_mask_out_zeroes_only_selected_region(self) -> None:
        base = load_fixture_tensor("catdog.png").unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.MASK_OUT,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (9, 3, 224, 224))

        region = generator.regions[4]

        selected = result[4, :, region.y0:region.y1, region.x0:region.x1]
        self.assertTrue(torch.all(selected == 0.0))

        outside_mask = torch.ones_like(result[4], dtype=torch.bool)
        outside_mask[:, region.y0:region.y1, region.x0:region.x1] = False

        self.assertTrue(torch.allclose(result[4][outside_mask], base[0][outside_mask]))

    def test_extract_keeps_stackable_shape(self) -> None:
        base = load_fixture_tensor("astronaut.png").unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.EXTRACT,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (9, 3, 224, 224))

    def test_batch_two_images_creates_n_times_r_variants(self) -> None:
        dogbird = load_fixture_tensor("dogbird.png")
        catdog = load_fixture_tensor("catdog.png")
        base = torch.stack([dogbird, catdog])

        indexer, geometry = make_indexer(item_keys=(10, 20))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.KEEP_ONLY,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (18, 3, 224, 224))
        self.assertEqual(generator.layout.item_count, 2)
        self.assertEqual(generator.layout.regions_per_item, 9)
        self.assertEqual(generator.layout.flat_count, 18)
        self.assertEqual(generator.item_keys, (10, 20))