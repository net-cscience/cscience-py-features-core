import base64
import os
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from cscience.features.api.utils.image_utils import load_base64_image
from cscience.features.nsfw_image import NsfwImageConnector

# Load model directly
import torch
from PIL import Image
from transformers import AutoModelForImageClassification, ViTImageProcessor

from cscience.features.nsfw_image.nsfw_config import NsfwConfig

TEST_FIXTURE_DIR: Path =  Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "images-gen"


class TestNsfwImageVisual(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        images_paths = list(TEST_FIXTURE_DIR.glob("**/*base_64.txt"))
        cls.nsfw_images_batch: list[Image.Image] = []
        cls.sfw_images_batch: list[Image.Image] = []
        for image_path in images_paths:
            if "nsfw_" in image_path.parent.stem:
                cls.nsfw_images_batch.append(load_base64_image(image_path))
            else:
                cls.sfw_images_batch.append(load_base64_image(image_path))


    def test_nsfw_detected(self):
        for nsfw in self.nsfw_images_batch:
            detector = NsfwImageConnector(NsfwConfig())
            prediction = detector.classify(nsfw)
            self.assertGreater(
                prediction.nsfw_score,
                0.5,
                msg=f"Expected NSFW score > 0.5, got {prediction}",
            )

    def test_sfw_not_detected(self):
        for sfw in self.sfw_images_batch:
            detector = NsfwImageConnector(NsfwConfig())
            prediction = detector.classify(sfw)
            self.assertLess(
                prediction.nsfw_score,
                0.5,
                msg=f"Expected NSFW score < 0.5, got {prediction}",
            )