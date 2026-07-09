import base64
import os
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from cscience.features.nsfw_image import NsfwImageConnector

# Load model directly
import torch
from PIL import Image
from transformers import AutoModelForImageClassification, ViTImageProcessor


def load_base64_image(path: Path) -> Image.Image:
    encoded = path.read_text(encoding="utf-8").strip()
    image_bytes = base64.b64decode(encoded, validate=True)
    return Image.open(BytesIO(image_bytes)).convert("RGB")


class TestNsfwImageVisual(unittest.TestCase):

    def testexample_feature(self):



        img = Image.open(r"D:\myRepo\net.cscience\cscience-py-features-core\packages\cscience-feature-nsfw-image\tests\fixtures\img.jpg")
        model = AutoModelForImageClassification.from_pretrained("Falconsai/nsfw_image_detection")
        processor = ViTImageProcessor.from_pretrained('Falconsai/nsfw_image_detection')
        with torch.no_grad():
            inputs = processor(images=img, return_tensors="pt")
            outputs = model(**inputs)
            logits = outputs.logits

        probabilities = torch.softmax(outputs.logits, dim=-1).detach().cpu()

        predicted_label = logits.argmax(-1).item()
        l = model.config.id2label[predicted_label]
        pass


    def test_mild_nudity_image_is_detected(self):
        image = load_base64_image(
            Path(__file__).parent / "fixtures" / "nsfw_archives_deros_marconi_base64.txt"
        )

        prediction = NsfwImageConnector().classify(image)

        self.assertGreater(
            prediction.nsfw_score,
            0.5,
            msg=f"Expected NSFW score > 0.5, got {prediction}",
        )

    def test_sfw_image_is_not_detected(self):
        image = load_base64_image(
            Path(__file__).parent / "fixtures" / "sfw_astronaut_base64.txt"
        )

        prediction = NsfwImageConnector().classify(image)

        self.assertLess(
            prediction.nsfw_score,
            0.5,
            msg=f"Expected NSFW score < 0.5, got {prediction}",
        )