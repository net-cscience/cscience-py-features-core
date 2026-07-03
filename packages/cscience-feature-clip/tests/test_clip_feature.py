import unittest

from PIL import Image
from PIL.ImageFile import ImageFile

from clip import ClipConnector, ClipConvertionProvider, ClipFeature
from registry.conversion_registry import ConversionRegistry


class FeatureTest(unittest.TestCase):

    def test_feature_text_to_list(self):
        ConversionRegistry.register("clip", ClipConvertionProvider(ClipFeature().get_instance()))
        c = ClipConnector()
        v = c.clip_text("Hello World")
        self.assertIsInstance(v, list)


    def test_feature_image_to_list(self):
        ConversionRegistry.register("clip", ClipConvertionProvider(ClipFeature().get_instance()))
        c = ClipConnector()
        i: ImageFile = Image.open("resources/dog.jpg")
        v = c.clip_image(i)
        self.assertIsInstance(v, list)
