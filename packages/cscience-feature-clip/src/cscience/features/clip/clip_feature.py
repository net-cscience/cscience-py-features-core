
from __future__ import annotations

from typing import List

import open_clip
import torch
from torch import Tensor

from PIL.ImageFile import ImageFile

from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.clip.clip_datatypes.clip_image import ClipImage
from cscience.features.clip.clip_datatypes.clip_tensor import ClipTensor


class ClipFeature(FeatureBase):

    def _initialize(self) -> None:
        if self._initialized:
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
    def text(cls, text: TextBatch) -> ClipTensor:
        service = cls.get_instance()

        tokens = service._tokenizer(text.data()).to(service._device)

        with torch.no_grad():
            feats = service._model.encode_text(tokens)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vec = feats.detach().float().cpu()
        return ClipTensor(vec)

    @classmethod
    def image(cls, img: ClipImage) -> ClipTensor:
        service = cls.get_instance()
        image_tensor = service.preprocess(img.data()).unsqueeze(0).to(service._device)

        with torch.no_grad():
            feats = service._model.encode_image(image_tensor)
            feats = feats / feats.norm(dim=-1, keepdim=True)

        vec = feats[0].detach().float().cpu()
        return ClipTensor(vec)