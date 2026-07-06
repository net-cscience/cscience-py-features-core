import unittest

from PIL import Image
from PIL.ImageFile import ImageFile

from cscience.features.api.registry.conversion_registry import ConversionRegistry
from cscience.features.api.utils.measure_time import measure_time
from cscience.features.clip import ClipConnector, ClipConversionProvider, ClipFeature


class FeatureTest(unittest.TestCase):

    N = 10
    @measure_time(times=N, ignore_first=True)
    def test_clip_text_to_vector(self):
        clip = ClipConnector()
        v = clip.text("Hello World")
        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_to_vector(self):
        clip = ClipConnector()
        i: ImageFile = Image.open("../resources/test/flickr-dog-1.jpg")
        v = clip.image(i)
        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_batch_to_vector_batch(self):
        ConversionRegistry.register("clip", ClipConversionProvider(ClipFeature().get_instance()))
        clip = ClipConnector()
        v = clip.text_batch(["Hello World", "Hello World", "Hello World and Moon"])

        self.assertEqual(v[0], v[1])
        self.assertNotEqual(v[0], v[2])
        self.assertNotEqual(v[1], v[2])


    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        ConversionRegistry.register("clip", ClipConversionProvider(ClipFeature().get_instance()))
        clip = ClipConnector()
        images: list[ImageFile] = [
            Image.open("../resources/test/flickr-dog-1.jpg"),
            Image.open("../resources/test/flickr-dog-1.jpg"),
            Image.open("../resources/test/flickr-dog-2.jpg"),
            Image.open("../resources/test/flickr-dog-2.jpg"),
            Image.open("../resources/test/flickr-house-1.jpg"),
            Image.open("../resources/test/flickr-house-1.jpg"),
            Image.open("../resources/test/flickr-house-2.jpg"),
            Image.open("../resources/test/flickr-house-2.jpg"),
            Image.open("../resources/test/flickr-hummingbird.jpg"),
            Image.open("../resources/test/flickr-hummingbird.jpg"),
            Image.open("../resources/test/flickr-monkeys.jpg"),
            Image.open("../resources/test/flickr-monkeys.jpg"),
            Image.open("../resources/test/flickr-mountains.jpg"),
            Image.open("../resources/test/flickr-mountains.jpg"),
            Image.open("../resources/test/flickr-sunset.jpg"),
            Image.open("../resources/test/flickr-sunset.jpg")
        ]
        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])
