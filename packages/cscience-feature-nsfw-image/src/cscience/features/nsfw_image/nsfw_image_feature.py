from __future__ import annotations

import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

from cscience.features.api import FeatureBase, PilImageBatch

from .nsfw_image_datatypes.nsfw_prediction import NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
    NsfwPredictionBatchData,
)


class NsfwImageFeature(FeatureBase):
    """NSFW image-classification feature backed by Falconsai/nsfw_image_detection."""

    MODEL_NAME = "Falconsai/nsfw_image_detection"

    def _initialize(self) -> None:
        if self._initialized:
            return

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.processor = AutoImageProcessor.from_pretrained(self.MODEL_NAME)
        self.model = AutoModelForImageClassification.from_pretrained(self.MODEL_NAME)
        self.model = self.model.to(self.device).eval()

        self._initialized = True




    @classmethod
    @torch.inference_mode()
    def classify_batch(cls, images: PilImageBatch) -> NsfwPredictionBatch:
        """Classify a batch of images as normal or NSFW."""
        service = cls.get_instance()

        keys = images.ordered_keys()
        image_values = list(images.ordered_values())

        inputs = service.processor(
            images=image_values,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(service.device)
            for key, value in inputs.items()
        }

        outputs = service.model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1).detach().cpu()

        id_to_label = service.model.config.id2label
        predictions: dict[int, NsfwPredictionData] = {}

        for source_key, row in zip(keys, probabilities):
            label_scores = {
                id_to_label[class_index].lower(): float(score)
                for class_index, score in enumerate(row)
            }

            if "normal" not in label_scores or "nsfw" not in label_scores:
                raise ValueError(
                    f"Expected model labels 'normal' and 'nsfw', got {label_scores.keys()}."
                )

            predicted_index = int(row.argmax().item())
            predicted_label = id_to_label[predicted_index].lower()
            predicted_score = float(row[predicted_index].item())

            predictions[source_key] = NsfwPredictionData(
                label=predicted_label,
                score=predicted_score,
                normal_score=label_scores["normal"],
                nsfw_score=label_scores["nsfw"],
            )

        return NsfwPredictionBatch(
            NsfwPredictionBatchData(
                predictions=predictions,
            )
        )