import random
from pathlib import Path
import unittest

from PIL import Image

from cscience.features.api import measure_time
from cscience.features.api.utils.fixture_repository import FixtureRepository
from cscience.features.clip.clip_config import ClipConfig
from cscience.features.clip.clip_connector import ClipConnector

FIXTURES_ROOT = Path(__file__).parent / "fixtures"

class FeatureTest(unittest.TestCase):
    N = 10

    _images_repo: FixtureRepository[Image.Image]


    @classmethod
    def setUpClass(cls) -> None:
        ClipConfig.set_default_config_directory(FIXTURES_ROOT / "configs")
        cls.clip = ClipConnector(ClipConfig())
        cfg= ClipConfig(
            model_name="hf-hub:timm/ViT-B-16-SigLIP2-256",
            pretrained="hf-hub:timm/ViT-B-16-SigLIP2-256",
            preferred_device="cuda",
            namespace="SigLIP2",
            force_device=True
        )
        cls.clip_siglip = ClipConnector(cfg)
        cls._images_repo = FixtureRepository[Image.Image](
            (FIXTURES_ROOT / "images-gen").glob("**/*.jpg"),
            loader = Image.open,
            key_builder = lambda path: (path.parent.parent.stem.lower(), path.parent.stem.lower(), path.stem.lower())
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

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_to_vector(self):


        v = self.clip.text("Hello World")

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_to_vector(self):
        self.clip = ClipConnector(ClipConfig())
        image = self._images_repo.get_qualified("A_Golden_Retriever.16_9.1920x1080")
        v = self.clip.image(image)

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


        images = self._images_repo.query("1920x1080")[0:10]

        v = self.clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):

        images = self._images_repo

        v = self._images_repo.query("1920x1080")[0:10]

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        repo = self._images_repo.query("1920x1080")[0:10]
        length = len(repo) * 1
        # append n times the batch
        images = [random.choice(repo) for _ in range(length)]
        v = self.clip.image_batch(images)
        self.assertEqual(len(v), length)
        for key, value in v.items():
            self.assertEqual(len(value), 512)



    @measure_time(times=N, ignore_first=True)
    def test_clip_siglip_image_batch_to_vector_batch(self) -> None:


        repo = self._images_repo.query("1920x1080")[0:10]
        length = len(repo) * 1
        images = [random.choice(repo) for _ in range(length)]
        v = self.clip_siglip.image_batch(images)
        self.assertEqual(len(v), length)
        for key, value in v.items():
            self.assertEqual(len(value), 768)
