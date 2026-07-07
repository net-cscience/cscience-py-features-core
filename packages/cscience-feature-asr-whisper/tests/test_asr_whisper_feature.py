import unittest

from cscience.features.asr_whisper import AsrWhisperConnector


class AsrWhisperFeatureTest(unittest.TestCase):
    def test_connector_initializes(self):
        connector = AsrWhisperConnector()
        self.assertIsNotNone(connector)
