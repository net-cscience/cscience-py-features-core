import unittest

from feature.feature_base import FeatureBase


class FeatureTest(unittest.TestCase):

    def test_feature_base(self):

        class A(FeatureBase):
            def _initialize(self) -> None:
                pass

        class B(FeatureBase):
            def _initialize(self) -> None:
                pass

        a = A()
        b = B()
        self.assertEqual(a.get_instance(), a)
        self.assertEqual(b.get_instance(), b)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a.get_instance(), b.get_instance())