from cscience.features.api.config.config_base import ConfigBase


class ClipConfig(ConfigBase):

    def _initialize(self):
        self._model_name = "xlm-roberta-base-ViT-B-32"
        self._pretrained = "laion5b_s13b_b90k"
        self._device = "cpu"
