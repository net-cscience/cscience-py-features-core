import unittest

from cscience.features.api.config.config_base import ConfigBase
from cscience.features.api.config.core_config import CoreConfig
from cscience.features.api.feature.feature_base import FeatureBase


class FeatureTest(unittest.TestCase):

    def test_feature_base(self):

        class A(FeatureBase['A', CoreConfig]):
            def _initialize(self, config: ConfigBase) -> None:
                pass

        class B(FeatureBase['B',CoreConfig]):
            def _initialize(self, config: ConfigBase) -> None:
                pass


        a = A.get_instance(CoreConfig(namespace="A"))
        b = B.get_instance(CoreConfig(namespace="B"))
        self.assertEqual(a.get_instance(CoreConfig(namespace="A")), a)
        self.assertEqual(b.get_instance(CoreConfig(namespace="B")), b)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a.get_instance(CoreConfig(namespace="A")), b.get_instance(CoreConfig(namespace="B")))