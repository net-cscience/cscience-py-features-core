import unittest
from pathlib import Path

from PIL import Image

from cscience.features.api.utils.measure_time import measure_time
from cscience.features.clip_spatial import ClipSpatialConnector
from cscience.features.clip_spatial.clip_spatial_config import ClipSpatialConfig
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode
import numpy as np



class TestSpatialFeature(unittest.TestCase):
    config_keep_only: ClipSpatialConfig
    config_mask_out: ClipSpatialConfig
    config_extract: ClipSpatialConfig

    connector_keep_only: ClipSpatialConnector
    connector_mask_out: ClipSpatialConnector
    connector_extract: ClipSpatialConnector

    image_repo: dict[str, Image.Image] = {}

    FIXTURES_ROOT = Path(__file__).parent / "fixtures"

    @classmethod
    def setUpClass(cls):
        ClipSpatialConfig.set_default_config_directory(cls.FIXTURES_ROOT / "configs")
        # runs once before any tests in this class$
        cls.config_keep_only = ClipSpatialConfig(
            step_size=(1 / 6, 1 / 8),
            start_point=(1 / 6, 1 / 8),
            grid_shape=(5, 7),
            geometry_size=(1 / 3, 1 / 4),
            masking_mode=MaskingMode.KEEP_ONLY)
        cls.config_mask_out = ClipSpatialConfig(
            step_size=(1 / 6, 1 / 8),
            start_point=(1 / 6, 1 / 8),
            grid_shape=(5, 7),
            geometry_size=(1 / 3, 1 / 4),
            masking_mode=MaskingMode.MASK_OUT)
        cls.config_extract = ClipSpatialConfig(
            step_size=(1 / 6, 1 / 8),
            start_point=(1 / 6, 1 / 8),
            grid_shape=(5, 7),
            geometry_size=(1 / 3, 1 / 4),
            masking_mode=MaskingMode.EXTRACT)

        cls.connector_keep_only = ClipSpatialConnector(config=cls.config_keep_only)
        cls.connector_mask_out = ClipSpatialConnector(config=cls.config_mask_out)
        cls.connector_extract = ClipSpatialConnector(config=cls.config_extract)

        images = Path(cls.FIXTURES_ROOT / "images-gen").glob("**/*.jpg")

        for filename in images:
            cls.image_repo[f"{filename.parent.parent.stem.lower()}-{filename.parent.stem.lower()}-{filename.stem.lower()}"] = Image.open(filename)


    def tearDownClass(cls):
        # runs once after all tests in this class
        pass


    def setUp(self):
        # runs before each test method
        pass


    def tearDown(self):
        # runs after each test method
        pass

    @measure_time(times=10, ignore_first=True)
    def test_similarities(self) -> None:
        img = self.image_repo["coco_bird_cat_1-16_9-1920x1080"]
        v = self.connector_extract.image_regions(img)
        self.assertEqual(len(v.vectors), self.config_extract.grid_shape[0] * self.config_extract.grid_shape[1])


    def test_single_vs_batch(self) -> None:
        batch = list(self.image_repo.values())[0:3]
        img = batch[0]
        v = self.connector_extract.image_regions(img)
        vb = self.connector_extract.image_region_batch(batch)
        eps = float(np.finfo(np.float32).eps)

        np.testing.assert_allclose(
            v.vectors[0],
            vb.vectors[0],
            rtol=0,
            atol=3 * eps,
        )