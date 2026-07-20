import unittest
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image

from cscience.features.api.utils.fixture_repository import FixtureRepository
from cscience.features.clip_spatial import ClipSpatialConnector
from cscience.features.clip_spatial.clip_spatial_config import ClipSpatialConfig
from cscience.features.clip_spatial.config.masking_preprocessing_order import ImagePreprocessingOrder
from cscience.features.clip_spatial.config.scoring_function import ScoringFunction
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode
from utils.visualization_util import plot_spatial_scores


class ExpSpatialFeature(unittest.TestCase):
    image_repo: dict[str, Image.Image] = {}
    connector_repository: dict[str, ClipSpatialConnector] = {}
    FIXTURES_ROOT = Path(__file__).parent / "fixtures"


    @classmethod
    def setUpClass(cls):
        ClipSpatialConfig.set_default_config_directory(cls.FIXTURES_ROOT / "configs")
        # runs once before any tests in this class$

        tilings: List[str] = ["4_3_20percent", "5_7_50percent"]
        masking_modes: List[str] = [MaskingMode.EXTRACT, MaskingMode.MASK_OUT, MaskingMode.KEEP_ONLY]
        preprocessing_modes: List[str] = [ImagePreprocessingOrder.LATE_PREPROCESSING,
                                          ImagePreprocessingOrder.EARLY_PREPROCESSING]
        scoring_functions: List[str] = [ScoringFunction.ABSOLUTE_NORMALIZED, ScoringFunction.RELATIVE_POSITIVE_NORMALIZED]

        for masking_mode in masking_modes:
            for preprocessing_mode in preprocessing_modes:
                for scoring_function in scoring_functions:
                    for tiling in tilings:

                        namespace = f"exp_{tiling}_{masking_mode}_{preprocessing_mode}_{scoring_function}"

                        if tiling == "5_7_50percent":
                            config = ClipSpatialConfig(
                                namespace=namespace,
                                step_size=(1 / 6, 1 / 8),
                                start_point=(1 / 6, 1 / 8),
                                grid_shape=(5, 7),
                                geometry_size=(1 / 3, 1 / 4),
                                masking_mode=masking_mode,
                                preprocessing_order=preprocessing_mode,
                                scoring_function=scoring_function
                            )
                        elif tiling == "4_3_20percent":
                            config = cls.config_extract_late_preprocessing_low_res = ClipSpatialConfig(
                                namespace=namespace,
                                step_size=((1 - 2 * 6 / 36) / 2, (1 - 2 * 6 / 48) / 3),
                                start_point=(6 / 36, 6 / 48),
                                grid_shape=(3, 4),
                                geometry_size=(12 / 30, 12 / 40),
                                masking_mode=masking_mode,
                                preprocessing_order=preprocessing_mode,
                                scoring_function=scoring_function
                            )
                        else:
                            raise NotImplementedError

                        cls.connector_repository[namespace] = ClipSpatialConnector(config=config)
        cls._images_repo = FixtureRepository[Image.Image](
            (cls.FIXTURES_ROOT / "images-gen").glob("**/*.jpg"),
            loader=Image.open,
            key_builder=lambda path: (path.parent.parent.stem.lower(), path.parent.stem.lower(), path.stem.lower())
        )

    @classmethod
    def tearDownClass(cls):
        # runs once after all tests in this class
        pass

    def setUp(self):
        # runs before each test method
        pass

    def tearDown(self):
        # runs after each test method
        pass



    @unittest.skip("skipping")
    def test_scoring_cat_dog_1920x1440(
            self,
    ) -> None:
        images = self._images_repo.query_regex(r"(?=.*cat)(?=.*dog).*\.1920x1440$")

        texts = ["a cat", "a dog"]

        for key, connector in self.connector_repository.items():
            v = connector.score_images(texts, images)

            for iid in range(len(images)):
                for qid in range(len(texts)):
                    label = texts[qid]
                    image = images[iid]
                    plot_spatial_scores(
                        image,
                        v,
                        item_key=iid,
                        query_key=qid,
                        label=f"config:{key} - prompt {label}"
                    )

    @unittest.skip("skipping")
    def test_scoring_cat_dog_640x480(
            self,
    ) -> None:
        images = self._images_repo.query_regex(r"(?=.*cat)(?=.*dog).*\.640x480$")

        texts = ["a cat", "a dog"]

        for key, connector in self.connector_repository.items():
            v = connector.score_images(texts, images)

            for iid in range(len(images)):
                for qid in range(len(texts)):
                    label = texts[qid]
                    image = images[iid]
                    plot_spatial_scores(
                        image,
                        v,
                        item_key=iid,
                        query_key=qid,
                        label=f"config:{key} - prompt {label}"
                    )

