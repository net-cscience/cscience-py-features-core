from __future__ import annotations

import open_clip
import torch

from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase

from .clip_datatypes.clip_tensor_batch import ClipTensorBatch, ClipTensorBatchData


class ClipFeature(FeatureBase):
    """CLIP feature service backed by OpenCLIP."""

    def _initialize(self) -> None:
        if self._initialized:
            return

        self._model_name = "xlm-roberta-base-ViT-B-32"
        self._pretrained = "laion5b_s13b_b90k"

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name=self._model_name,
            pretrained=self._pretrained,
        )

        self.model = self.model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer(self._model_name)

        self._initialized = True

    @classmethod
    @torch.inference_mode()
    def text_batch(cls, texts: TextBatch) -> ClipTensorBatch:
        """Embed a batch of text strings into normalized CLIP vectors."""
        service = cls.get_instance()

        ordered_items = sorted(texts.data().items(), key=lambda item: item[0])
        keys = tuple(key for key, _ in ordered_items)
        values = [text for _, text in ordered_items]

        tokens = service.tokenizer(values).to(service.device)

        feats = service.model.encode_text(tokens)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        vectors = feats.detach().float().cpu()

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=vectors,
            )
        )

    @classmethod
    @torch.inference_mode()
    def image_batch(cls, images: PilImageBatch) -> ClipTensorBatch:
        """Embed a batch of PIL images into normalized CLIP vectors."""
        service = cls.get_instance()

        ordered_items = sorted(images.data().items(), key=lambda item: item[0])
        keys = tuple(key for key, _ in ordered_items)

        image_tensors = torch.stack(
            [
                service.preprocess(image)
                for _, image in ordered_items
            ]
        ).to(service.device)

        feats = service.model.encode_image(image_tensors)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        vectors = feats.detach().float().cpu()

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=vectors,
            )
        )