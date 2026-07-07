
from __future__ import annotations


import open_clip
import torch
import torch.nn.functional as F

from cscience.features.api.datatypes.core_datatypes.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase




class ClipSpatialFeature(FeatureBase):
    """CLIP feature service backed by OpenCLIP.

    Loads the model, tokenizer, preprocessing pipeline, and target device once.
    Public methods operate on CLIP-specific datatype wrappers.
    """

    def _initialize(self) -> None:
        if self._initialized:
            return
        self._model_name = "xlm-roberta-base-ViT-B-32"
        self._pretrained = "laion5b_s13b_b90k"

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name = self._model_name,
            pretrained= self._pretrained,
        )
        self.model = self.model.to(self._device).eval()
        self.tokenizer = open_clip.get_tokenizer(self._model_name)
        self._initialized = True


    @classmethod
    @torch.no_grad()
    def score(cls, left: ClipSpatialTensor, right: ClipSpatialTensor):
        left = F.normalize(left, dim=-1)
        right = F.normalize(right, dim=-1)
        # scalar score per image (assuming one prompt)
        return (left @ right.T).squeeze(-1)

    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_img_vectors(cls, img_tensor_batch: torch.Tensor):
        # img_batch: [B,3,224,224] in preprocessed space
        img_f = cls.model.encode_image(img_tensor_batch)
        img_f = F.normalize(img_f, dim=-1)
        return img_f

    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_img(self, img: Image):
        img_tensor = self.preprocess(img)
        img_f = self.clip_embedd_norm_img_vectors(img_tensor)  # [1,D]
        return img_f


    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_txt_vectors(self, text_tokens: torch.Tensor):
        txt_f = self._model.encode_text(text_tokens)
        txt_f = F.normalize(txt_f, dim=-1)
        return txt_f


    @classmethod
    @torch.no_grad()
    def clip_embedd_norm_txt(self, text: str):
        text_tokens = self.tokenize(text)
        txt_f = self.clip_embedd_norm_txt_vectors(text_tokens)
        return txt_f

    @classmethod
    def influence_calculator(self, img_f_base, img_f_masked, txt_f, mode: MaskingMode, clamp_positive=True, normalize=True):
        if mode == MaskingMode.MASK_OUT:
            return self.influence_calculator_similarity_decrease(img_f_base, img_f_masked, txt_f, clamp_positive, normalize)
        elif mode == MaskingMode.KEEP_ONLY:
            return self.influence_calculator_keep_similarity(img_f_base, img_f_masked, txt_f, normalize)
        else:
            raise ValueError(f"Unknown MaskingMode: {mode}")

    @classmethod

    @torch.no_grad()
    def influence_calculator_similarity_decrease(self, img_f_base, img_f_masked, txt_f, clamp_positive=True,
                                                 normalize=True):
        base = self.clip_score(img_f_base, txt_f)  # [1]
        scores = self.clip_score(img_f_masked, txt_f)  # [B]
        deltas = base - scores  # [B] broadcast

        if clamp_positive:
            deltas = deltas.clamp(min=0.0)

        if normalize:
            d = deltas - deltas.min()
            deltas = d / (d.max() + 1e-8)

        return deltas

    @classmethod

    @torch.no_grad()
    def influence_calculator_keep_similarity(self, img_f_base, img_f_masked, txt_f, normalize=True):
        scores = self.clip_score(img_f_masked, txt_f)  # [B]
        deltas = scores  # [B] broadcast

        if normalize:
            d = deltas - deltas.min()
            deltas = d / (d.max() + 1e-8)

        return deltas