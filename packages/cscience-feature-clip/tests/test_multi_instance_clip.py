import unittest

from cscience.features.clip import ClipConnector
from cscience.features.clip.clip_config import ClipConfig


class FeatureTest(unittest.TestCase):

    N = 10
    @classmethod
    def setUpClass(cls) -> None:
        cls.connector_1 = ClipConnector(ClipConfig())
        cls.cfg2= ClipConfig(
            model_name="hf-hub:timm/ViT-B-16-SigLIP2-256",
            pretrained="hf-hub:timm/ViT-B-16-SigLIP2-256",
            preferred_device="cuda",
            namespace="SigLIP2",
            force_device=True
        )
        cls.connector_2 = ClipConnector(cls.cfg2)



    def test_clip_multi_embedding(self):
        t1 = self.connector_1.text("Hello World")
        t2 = self.connector_2.text("Hello World")

        self.assertEqual(len(t1),512)
        self.assertTrue(len(t2) > 0)
