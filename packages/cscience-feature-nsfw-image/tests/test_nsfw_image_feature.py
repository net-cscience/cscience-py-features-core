import unittest
from pathlib import Path

from PIL import Image

from cscience.features.api.utils.measure_time import measure_time
from cscience.features.nsfw_image import NsfwImageConnector


class NsfwImageFeatureTest(unittest.TestCase):

    N = 10

    def test_connector_initializes(self):
        connector = NsfwImageConnector()
        self.assertIsNotNone(connector)

    @measure_time(times=N, ignore_first=True)
    def test_classify_simple_image(self):
        image = Image.new("RGB", (224, 224), color=(255, 255, 255))

        connector = NsfwImageConnector()
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

        connector = NsfwImageConnector()
        predictions = connector.classify_batch(list(images.values()))

        self.assertEqual(set(predictions.keys()), {0, 1})


