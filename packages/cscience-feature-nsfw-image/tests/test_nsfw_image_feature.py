import unittest
from pathlib import Path

from PIL import Image

from cscience.features.api.utils.measure_time import measure_time
from cscience.features.nsfw_image import NsfwImageConnector
from cscience.features.nsfw_image.nsfw_config import NsfwConfig

FIXTURES_DIR = Path(__file__).parent

class NsfwImageFeatureTest(unittest.TestCase):

    N = 10

    @classmethod
    def setUpClass(cls):
        NsfwConfig.set_default_config_directory(FIXTURES_DIR / "nsfw_config")

    def test_connector_initializes(self):
        connector = NsfwImageConnector(NsfwConfig())
        self.assertIsNotNone(connector)

    @measure_time(times=N, ignore_first=True)
    def test_classify_simple_image(self):
        image = Image.new("RGB", (224, 224), color=(255, 255, 255))

        connector = NsfwImageConnector(NsfwConfig())
        prediction = connector.classify(image)

        self.assertIn(prediction.label, {"normal", "nsfw"})
        self.assertGreaterEqual(prediction.score, 0.0)
        self.assertLessEqual(prediction.score, 1.0)
        self.assertGreaterEqual(prediction.normal_score, 0.0)
        self.assertLessEqual(prediction.normal_score, 1.0)
        self.assertGreaterEqual(prediction.nsfw_score, 0.0)
        self.assertLessEqual(prediction.nsfw_score, 1.0)

    @measure_time(times=N, ignore_first=True)
    def test_classify_batch_preserves_indices(self):
        images = {
            0: Image.new("RGB", (224, 224), color=(255, 255, 255)),
            3: Image.new("RGB", (224, 224), color=(0, 0, 0)),
        }

        connector = NsfwImageConnector(NsfwConfig())
        predictions = connector.classify_batch(list(images.values()))

        self.assertEqual(set(predictions.keys()), {0, 1})


