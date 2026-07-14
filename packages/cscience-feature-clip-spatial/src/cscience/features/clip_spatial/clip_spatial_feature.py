import open_clip
import torch

from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.api.feature.feature_base import FeatureInfo
from cscience.features.api.datatypes.spatial.spatial_vector_batch_data import SpatialVectorBatchData

from .clip_spatial_config import ClipSpatialConfig
from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch import ClipSpatialTextTensorBatch
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import ClipSpatialTextTensorBatchData
from .filter.zero_provider import ZeroProvider
from .indexer.spatial_indexer import SpatialIndexer
from .geometry.square_provider import SquareProvider
from .masking.masking_generator import MaskingGenerator
from ..api.datatypes.text.text_batch import TextBatch


class ClipSpatialFeature(FeatureBase['ClipSpatialFeature', ClipSpatialConfig]):
    """CLIP Spatial feature service backed by OpenCLIP."""

    def _initialize(self, config: ClipSpatialConfig) -> None:

        self._config = config
        self._device = torch.device(config.preferred_device) if torch.cuda.is_available() else torch.device("cpu")
        if config.force_device and not (config.preferred_device == self._device):
            raise ValueError(f"Preferred device {config.preferred_device} is not available. Using {self._device} instead.")


        self._model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name=self._config.model_name,
            pretrained=self._config.pretrained,
        )

        self._model = self._model.to(self._device).eval()
        self.tokenizer = open_clip.get_tokenizer(self._config.model_name)

        self._initialized = True

    @torch.inference_mode()
    def text_batch(self, texts: TextBatch) -> ClipSpatialTextTensorBatch:


        keys = texts.ordered_keys()
        values = list(texts.ordered_values())

        tokens = self._tokenizer(values).to(self._device)

        feats = self._model.encode_text(tokens)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        return ClipSpatialTextTensorBatch(
            ClipSpatialTextTensorBatchData(
                keys=keys,
                vectors=feats.detach().float().cpu(),
            )
        )


    @torch.inference_mode()
    def image_region_batch(self, images: PilImageBatch) -> ClipSpatialTensorBatch:


        item_keys = images.ordered_keys()
        image_values = images.ordered_values()

        base_tensors = torch.stack(
            [
                self._model.preprocess(image)
                for image in image_values
            ]
        )

        _, channels, image_height, image_width = base_tensors.shape

        if channels != 3:
            raise ValueError(f"Expected 3 image channels, got {channels}.")

        geometry = SquareProvider(
            geometry_size=self._config.geometry_size,
        )

        indexer = SpatialIndexer(
            item_keys=item_keys,
            image_width=image_width,
            image_height=image_height,
            grid_shape=self._config.grid_shape,
            start_point=self._config.start_point,
            step_size=self._config.step_size,
            geometry=geometry,
        )

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=self._config.masking_mode,
        )

        masked_tensors = generator.generate(base_tensors).to(self._device)

        vectors = self._model.encode_image(masked_tensors)
        vectors = vectors / vectors.norm(dim=-1, keepdim=True)
        vectors = vectors.detach().float().cpu()

        return ClipSpatialTensorBatch(
            SpatialVectorBatchData(
                vectors={
                    index: vector
                    for index, vector in enumerate(vectors)
                },
                layout=generator.layout,
                item_keys=generator.item_keys,
                regions=generator.regions,
            )
        )

    import icontract
    import torch

    @staticmethod
    def _score_embeddings(
            text_vectors: ClipSpatialTextTensorBatch,
            spatial_vectors: ClipSpatialTensorBatch,
    ) -> torch.Tensor:
        """Return scores with shape [flat_region_count, query_count]."""
        return spatial_vectors.data().vectors @ text_vectors.data().vectors.T



    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(mode="json"),
        )

