
from __future__ import annotations

from typing import List

import numpy as np
import open_clip
import torch
from PIL import Image
from PIL.ImageFile import ImageFile

from api.feature import FeatureRegistry


class ClipFeature(FeatureRegistry):
    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._model_name = "xlm-roberta-base-ViT-B-32"
        self._pretrained = "laion5b_s13b_b90k"

        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self._model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name = self._model_name,
            pretrained= self._pretrained,
        )
        self._model = self._model.to(self._device).eval()
        self._tokenizer = open_clip.get_tokenizer(self._model_name)
        self._initialized = True


    @classmethod
    def _clip_text(cls, text: List[str]) -> torch.tensor:
        service = cls._get_instance()

        tokens = service._tokenizer(text).to(service._device)

        with torch.no_grad():
            feats = service._model.encode_text(tokens)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vec = feats[0].detach().float().cpu()
        return vec

    @classmethod
    def _clip_image(cls, img: ImageFile) -> torch.tensor:
        service = cls._get_instance()
        image_tensor = service.preprocess(img).unsqueeze(0).to(service._device)

        with torch.no_grad():
            feats = service._model.encode_image(image_tensor)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vec = feats[0].detach().float().cpu()
        return vec