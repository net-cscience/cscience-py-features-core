import unittest
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from cscience.features.api.datatypes.image.pil_image import PilImage
from cscience.features.clip_spatial.filter.filter_provider import FilterProvider
from cscience.features.clip_spatial.filter.zero_provider import ZeroProvider
from cscience.features.clip_spatial.geometry.square_provider import SquareProvider
from cscience.features.clip_spatial.indexer.spatial_indexer import SpatialIndexer
from cscience.features.clip_spatial.masking.masking_generator import MaskingGenerator
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def make_indexer(
    item_keys: tuple[int, ...],
    image_width: int = 224,
    image_height: int = 224,
) -> tuple[SpatialIndexer, SquareProvider]:
    geometry = SquareProvider(
        geometry_size=(1 / 3, 1 / 4),
    )

    indexer = SpatialIndexer(
        item_keys=item_keys,
        image_width=image_width,
        image_height=image_height,
        grid_shape=(5, 7),
        start_point=(1 / 6, 1 / 8),
        step_size=(1 / 6, 1 / 8),
        geometry=geometry,
    )

    return indexer, geometry


class TestVisualIndexing(unittest.TestCase):

    image_set: dict[tuple[str,str,str], PilImage] = {}


    @classmethod
    def setUpClass(cls) -> None:
        images = Path(FIXTURE_DIR/ "images-gen").glob("**/*.jpg")

        for image in images:
            pil_image = Image.open(image).convert("RGB")
            cls.image_set[(image.parent.parent.name, image.parent.name, image.stem)] = PilImage(pil_image)
            break

    def _directory_from_key(self, key: tuple[str,str,str], mode: MaskingMode) -> Path:
        return Path(FIXTURE_DIR) / "images-out" / mode / key[0] / key[1] / key[2]

    def test_keep_only(self) -> None:

        for key, image in self.image_set.items():
            self._run(key, image, MaskingMode.KEEP_ONLY, ZeroProvider())


    def test_mask_out(self) -> None:

        for key, image in self.image_set.items():
            self._run(key, image, MaskingMode.MASK_OUT, ZeroProvider())


    def test_extract(self) -> None:
        for key, image in self.image_set.items():
            self._run(key, image, MaskingMode.EXTRACT, ZeroProvider())

    def _run(self, key:tuple[str,str,str], image:PilImage, mode: MaskingMode, filter: FilterProvider) -> None:


        array = np.asarray(image.data(), dtype=np.float32) / 255.0
        image_tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,), image_width=image.data().width,
                                         image_height=image.data().height)

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=filter,
            mode=mode,
        )

        result = generator.generate(image_tensor)
        result_np = result.permute(0, 2, 3, 1).detach().cpu().numpy()

        # Temporary Store
        output_dir = self._directory_from_key(key, mode)
        output_dir.mkdir(parents=True, exist_ok=True)

        for i in range(result_np.shape[0]):
            Image.fromarray((result_np[i] * 255).astype('uint8'), mode='RGB').save(
                output_dir / f"{key[2]}_{i}.jpg", "JPEG")