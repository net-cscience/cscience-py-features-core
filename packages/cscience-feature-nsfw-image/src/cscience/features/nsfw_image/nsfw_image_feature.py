from __future__ import annotations

import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

from cscience.features.api import FeatureBase, PilImageBatch, FeatureInfo
from .nsfw_config import NsfwConfig

from .nsfw_image_datatypes.nsfw_prediction import NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
    NsfwPredictionBatchData,
)


class NsfwImageFeature(FeatureBase):
    """NSFW image-classification feature backed by Falconsai/nsfw_image_detection."""

    def _initialize(self, config: NsfwConfig) -> None:

        self._config = config
        self._device = torch.device(self._config.preferred_device if torch.cuda.is_available() else "cpu")
        if self._config.force_device and not (self._config.preferred_device == str(self._device)):
            raise RuntimeError(
                f"Preferred device {self._config.preferred_device} is not available. "
                f"Available device is {self._device}."
            )

        self._processor = AutoImageProcessor.from_pretrained(self._config.model_name)
        self._model = AutoModelForImageClassification.from_pretrained(self._config.model_name).to(self._device).eval()

        self._initialized = True


    @torch.inference_mode()
    def classify_batch(self, images: PilImageBatch) -> NsfwPredictionBatch:
        """Classify a batch of images as normal or NSFW."""

        keys = images.ordered_keys()
        image_values = list(images.ordered_values())

        inputs = self._processor(
            images=image_values,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self._device)
            for key, value in inputs.items()
        }

        outputs = self._model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1).detach().cpu()

        id_to_label = self._model.config.id2label
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

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(mode="json"),
        )