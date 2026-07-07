import unittest

from cscience.features.nsfw_image import NsfwImageConnector


class NsfwImageFeatureTest(unittest.TestCase):
    def test_connector_initializes(self):
        connector = NsfwImageConnector()
        self.assertIsNotNone(connector)
