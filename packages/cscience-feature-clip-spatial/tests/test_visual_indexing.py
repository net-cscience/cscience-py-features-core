import unittest
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from cscience.features.api.datatypes.image.pil_image import PilImage
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
        grid_shape=(3, 4),
        start_point=(1 / 6, 1 / 8),
        step_size=(1 / 3, 1 / 4),
        geometry=geometry,
    )

    return indexer, geometry


class TestVisualIndexing(unittest.TestCase):

    image_set: dict[str, PilImage] = {}

    def setUp(self):
        images = Path(FIXTURE_DIR).glob("**/*.jpg")

        for image in images:
            pil_image = Image.open(image).convert("RGB")
            self.image_set[image.stem] = PilImage(pil_image)


    def test_keep_only(self) -> None:

        for key, image in self.image_set.items():
            array = np.asarray(image.data(), dtype=np.float32) / 255.0
            image_tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)

            indexer, geometry = make_indexer(item_keys=(0,),image_width=image.data().width,image_height=image.data().height)

            generator = MaskingGenerator(
                indexer=indexer,
                geometry=geometry,
                filter_provider=ZeroProvider(),
                mode=MaskingMode.KEEP_ONLY,
            )


            result = generator.generate(image_tensor)
            result_np = result.permute(0,2, 3, 1).detach().cpu().numpy()

            # Temporary Store
            output_dir = Path(FIXTURE_DIR) / "images-out"
            output_dir.mkdir(parents=True, exist_ok=True)

            for i in range(result_np.shape[0]):
                Image.fromarray((result_np[i]*255).astype('uint8'), mode='RGB').save(output_dir / f"{key}_{i}.jpg", "JPEG")