import base64
import os
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from cscience.features.nsfw_image import NsfwImageConnector


def load_base64_image(path: Path) -> Image.Image:
    encoded = path.read_text(encoding="utf-8").strip()
    image_bytes = base64.b64decode(encoded, validate=True)
    return Image.open(BytesIO(image_bytes)).convert("RGB")


class NsfwImageVisualTest(unittest.TestCase):

    def test_mild_nudity_image_is_detected(self):
        image = load_base64_image(
            Path(__file__).parent / "fixtures" / "mild_nudity_image_base64.txt"
        )

        prediction = NsfwImageConnector().classify(image)

        self.assertGreater(
            prediction.nsfw_score,
            0.5,
            msg=f"Expected NSFW score > 0.5, got {prediction}",
        )

    def test_sfw_image_is_not_detected(self):
        image = load_base64_image(
            Path(__file__).parent / "fixtures" / "sfw_image_base64.txt"
        )

        prediction = NsfwImageConnector().classify(image)

        self.assertLess(
            prediction.nsfw_score,
            0.5,
            msg=f"Expected NSFW score < 0.5, got {prediction}",
        )