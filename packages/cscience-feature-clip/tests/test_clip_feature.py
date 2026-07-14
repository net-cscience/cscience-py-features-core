import random
from pathlib import Path
import unittest

from PIL import Image

from cscience.features.api import measure_time
from cscience.features.clip.clip_config import ClipConfig
from cscience.features.clip.clip_connector import ClipConnector


TEST_FIXTURE_DIR: Path =  Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "test"

class FeatureTest(unittest.TestCase):
    N = 10


    @classmethod
    def setUpClass(cls) -> None:
        images_paths = list(TEST_FIXTURE_DIR.glob("*.jpg"))
        cls.images_batch: list[Image.Image] = []
        for image_path in images_paths:
            cls.images_batch.append(Image.open(image_path))

    def _resource(self, name: str) -> Image.Image:
        return Image.open(TEST_FIXTURE_DIR / name).convert("RGB")

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_to_vector(self):

        clip = ClipConnector(ClipConfig())
        v = clip.text("Hello World")

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_to_vector(self):
        clip = ClipConnector(ClipConfig())
        image = self._resource("flickr-dog-1.jpg")

        v = clip.image(image)

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())
        v = clip.text_batch(["Hello World", "Hello World", "Hello World and Moon"])

        self.assertEqual(v[0], v[1])
        self.assertNotEqual(v[0], v[2])
        self.assertNotEqual(v[1], v[2])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())
        length = len(self.images_batch) * 1
        # append n times the batch
        images = [random.choice(self.images_batch) for _ in range(length)]
        v = clip.image_batch(images)
        self.assertEqual(len(v), length)
        for key, value in v.items():
            self.assertEqual(len(value), 512)



    @measure_time(times=N, ignore_first=True)
    def test_clip_siglip_image_batch_to_vector_batch(self) -> None:

        cfg= ClipConfig(
            model_name="hf-hub:timm/ViT-B-16-SigLIP2-256",
            pretrained="hf-hub:timm/ViT-B-16-SigLIP2-256",
            preferred_device="cuda",
            namespace="SigLIP2",
            force_device=True
        )
        clip = ClipConnector(cfg)
        length = len(self.images_batch) * 1
        images = [random.choice(self.images_batch) for _ in range(length)]
        v = clip.image_batch(images)
        self.assertEqual(len(v), length)
        for key, value in v.items():
            self.assertEqual(len(value), 768)
