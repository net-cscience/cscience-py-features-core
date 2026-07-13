from __future__ import annotations

import open_clip
import torch

from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase
from .clip_config import ClipConfig

from .clip_datatypes.clip_tensor_batch import ClipTensorBatch, ClipTensorBatchData


class ClipFeature(FeatureBase[ClipConfig]):
    """CLIP feature service backed by OpenCLIP."""

    def _initialize(self, config: ClipConfig) -> None:
        if self._is_initialized:
            return

        self._model_name = config.model_name
        self._pretrained = config.pretrained


        self.device = torch.device(config.preferred_device if torch.cuda.is_available() else "cpu")
        if config.force_device and (config.preferred_device == str(self.device)):
            raise RuntimeError(
                f"Preferred device {config.preferred_device} is not available. "
                f"Available device is {self.device}."
            )

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name=self._model_name,
            pretrained=self._pretrained,
        )

        self.model = self.model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer(self._model_name)

        self._initialized = True


    @torch.inference_mode()
    def text_batch(self, texts: TextBatch) -> ClipTensorBatch:


        keys = texts.ordered_keys()
        values = list(texts.ordered_values())

        tokens = self.tokenizer(values).to(self.device)

        feats = self.model.encode_text(tokens)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=feats.detach().float().cpu(),
            )
        )


    @torch.inference_mode()
    def image_batch(self, images: PilImageBatch) -> ClipTensorBatch:

        keys = images.ordered_keys()
        values = images.ordered_values()

        image_tensors = torch.stack(
            [
                self.preprocess(image)
                for image in values
            ]
        ).to(self.device)

        feats = self.model.encode_image(image_tensors)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=feats.detach().float().cpu(),
            )
        )