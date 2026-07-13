import random
from pathlib import Path
import unittest

from PIL import Image

from cscience.features.api import measure_time
from cscience.features.clip.clip_config import ClipConfig
from cscience.features.clip.clip_connector import ClipConnector


class FeatureTest(unittest.TestCase):

    N = 10
    def setUp(self):
        self.images_batch = [
            Image.open(self._resource("flickr-dog-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-dog-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-dog-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-dog-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-1.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-house-2.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-hummingbird.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-hummingbird.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-monkeys.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-monkeys.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-mountains.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-mountains.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-sunset.jpg")).convert("RGB"),
            Image.open(self._resource("flickr-sunset.jpg")).convert("RGB"),
        ]

    def tearDown(self):
        self.images_batch = []

    def _resource(self, name: str) -> Path:
        return Path(__file__).resolve().parents[1] / "fixtures" / "test" / name

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_to_vector(self):

        clip = ClipConnector()
        v = clip.text("Hello World")

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_to_vector(self):
        clip = ClipConnector()
        image = Image.open(self._resource("flickr-dog-1.jpg")).convert("RGB")

        v = clip.image(image)

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_batch_to_vector_batch(self):
        clip = ClipConnector()
        v = clip.text_batch(["Hello World", "Hello World", "Hello World and Moon"])

        self.assertEqual(v[0], v[1])
        self.assertNotEqual(v[0], v[2])
        self.assertNotEqual(v[1], v[2])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector()

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])


    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector()

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])



    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector()
        length = len(self.images_batch) * 1
        # append n times the batch
        images = [random.choice(self.images_batch) for _ in range(length)]
        v = clip.image_batch(images)
