import unittest
import timeit

from PIL import Image
from PIL.ImageFile import ImageFile

from cscience.features.api.registry.conversion_registry import ConversionRegistry
from cscience.features.clip import ClipConnector, ClipConvertionProvider, ClipFeature


def measure_time(times: int=1, ignore_first: bool=False):
    def inner(func):
        def wrapper(*args, **kwargs):

            t_total = 0
            result = None
            if ignore_first:
                result = func(*args, **kwargs)

            n = max(1, times)
            for i in range(n):
                start = timeit.default_timer()
                result = func(*args, **kwargs)
                end = timeit.default_timer()
                t_total += end - start

            print(f"\t{func.__name__} \t\t [mean] ⌛ {t_total/n:.5f} s for 🧮 {n} iterations")
            return result
        return wrapper
    return inner


class FeatureTest(unittest.TestCase):

    @measure_time(times=10, ignore_first=True)
    def test_feature_text_to_list(self):
        ConversionRegistry.register("clip", ClipConvertionProvider(ClipFeature().get_instance()))
        c = ClipConnector()
        v = c.clip_text("Hello World")
        self.assertIsInstance(v, list)

    @measure_time(times=10, ignore_first=True)
    def test_feature_image_to_list(self):
        ConversionRegistry.register("clip", ClipConvertionProvider(ClipFeature().get_instance()))
        c = ClipConnector()
        i: ImageFile = Image.open("../resources/test/dog.jpg")
        v = c.clip_image(i)
        self.assertIsInstance(v, list)
