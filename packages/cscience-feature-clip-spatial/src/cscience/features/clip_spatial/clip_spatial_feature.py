import open_clip
import torch

from cscience.features.api import (
    FeatureBase,
    FeatureInfo,
    PilImageBatch,
    SpatialVectorBatchData,
    TextBatch,
)

from .clip_spatial_config import ClipSpatialConfig
from .clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)
from .clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)
from .filter.zero_provider import ZeroProvider
from .geometry.square_provider import SquareProvider
from .indexer.spatial_indexer import SpatialIndexer
from .masking.masking_generator import MaskingGenerator


class ClipSpatialFeature(
    FeatureBase["ClipSpatialFeature", ClipSpatialConfig]
):
    """CLIP Spatial feature service backed by OpenCLIP."""

    def _initialize(self, config: ClipSpatialConfig) -> None:
        self._config = config
        self._device = self._resolve_device(config)

        self._model, _, self._preprocess = (
            open_clip.create_model_and_transforms(
                model_name=config.model_name,
                pretrained=config.pretrained,
            )
        )

        self._model = self._model.to(self._device).eval()
        self._tokenizer = open_clip.get_tokenizer(
            config.model_name
        )

        self._initialized = True

    @staticmethod
    def _resolve_device(
        config: ClipSpatialConfig,
    ) -> torch.device:
        preferred = torch.device(config.preferred_device)

        if preferred.type == "cuda" and not torch.cuda.is_available():
            if config.force_device:
                raise ValueError(
                    f"Preferred device {preferred} is not available."
                )

            return torch.device("cpu")

        return preferred

    @torch.inference_mode()
    def text_batch(
        self,
        texts: TextBatch,
    ) -> ClipSpatialTextTensorBatch:
        keys = texts.ordered_keys()
        values = list(texts.ordered_values())

        tokens = self._tokenizer(values).to(self._device)

        vectors = self._model.encode_text(tokens)
        vectors = self._normalize_embeddings(vectors)

        return ClipSpatialTextTensorBatch(
            ClipSpatialTextTensorBatchData(
                keys=keys,
                vectors=vectors.detach().float().cpu(),
            )
        )

    @torch.inference_mode()
    def image_region_batch(
        self,
        images: PilImageBatch,
    ) -> ClipSpatialTensorBatch:
        item_keys = images.ordered_keys()
        image_values = images.ordered_values()

        base_tensors = torch.stack(
            [
                self._preprocess(image)
                for image in image_values
            ]
        )

        _, channels, image_height, image_width = (
            base_tensors.shape
        )

        if channels != 3:
            raise ValueError(
                f"Expected 3 image channels, got {channels}."
            )

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

        masked_tensors = generator.generate(
            base_tensors
        ).to(self._device)

        vectors = self._model.encode_image(masked_tensors)
        vectors = self._normalize_embeddings(vectors)
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

    def score_text_vector_batch(
        self,
        texts: TextBatch,
        spatial_vectors: ClipSpatialTensorBatch,
    ) -> SpatialScoreVectorBatch:
        """Score text queries against spatial image embeddings."""
        text_vectors = self.text_batch(texts)

        return self.score_embeddings(
            text_vectors=text_vectors,
            spatial_vectors=spatial_vectors,
        )

    def score_text_image_batch(
        self,
        texts: TextBatch,
        images: PilImageBatch,
    ) -> SpatialScoreVectorBatch:
        """Create spatial image embeddings and score text queries."""
        spatial_vectors = self.image_region_batch(images)

        return self.score_text_vector_batch(
            texts=texts,
            spatial_vectors=spatial_vectors,
        )

    @staticmethod
    def score_embeddings(
        text_vectors: ClipSpatialTextTensorBatch,
        spatial_vectors: ClipSpatialTensorBatch,
    ) -> SpatialScoreVectorBatch:
        """Score spatial embeddings against text embeddings.

        The resulting matrix has shape:

            [flat_region_count, query_count]
        """
        spatial_tensor = spatial_vectors.as_flat_tensor()
        text_tensor = text_vectors.vectors

        if spatial_tensor.shape[1] != text_tensor.shape[1]:
            raise ValueError(
                "Text and spatial embedding dimensions must match: "
                f"{text_tensor.shape[1]} != "
                f"{spatial_tensor.shape[1]}."
            )

        scores = spatial_tensor @ text_tensor.T

        return SpatialScoreVectorBatch(
            data=SpatialVectorBatchData(
                vectors={
                    flat_index: [
                        float(score)
                        for score in score_vector.tolist()
                    ]
                    for flat_index, score_vector
                    in enumerate(scores)
                },
                layout=spatial_vectors.layout,
                item_keys=spatial_vectors.item_keys,
                regions=spatial_vectors.regions,
            ),
            query_keys=text_vectors.keys,
        )

    @staticmethod
    def _normalize_embeddings(
        vectors: torch.Tensor,
    ) -> torch.Tensor:
        norms = vectors.norm(
            dim=-1,
            keepdim=True,
        )

        if torch.any(norms == 0):
            raise ValueError(
                "CLIP produced an embedding with zero norm."
            )

        return vectors / norms

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(
                mode="json"
            ),
        )