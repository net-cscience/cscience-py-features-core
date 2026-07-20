import open_clip
import torch
from torchvision.transforms.functional import pil_to_tensor

from cscience.features.api import (
    FeatureBase,
    FeatureInfo,
    PilImageBatch,
    SpatialVectorBatchData,
    SpatialBatchLayout,
    SpatialRegion,
    TextBatch,
    resolve_device,
)

from .clip_spatial_config import ClipSpatialConfig
from .clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_image_pair import ClipSpatialTextImagePair
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)
from .clip_spatial_datatypes.clip_spatial_text_vector_pair import ClipSpatialTextVectorPair
from .clip_spatial_datatypes.clip_spatial_text_vector_pair_data import ClipSpatialTextVectorPairData
from .clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)
from .config.masking_preprocessing_order import ImagePreprocessingOrder
from .config.scoring_function import ScoringFunction
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
        self._device = resolve_device(config.preferred_device, config.force_device)

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

    @property
    def preprocess(self):
        return self._preprocess

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

    def prepare_masking_tensors(
            self,
            images: PilImageBatch,
    ) -> torch.Tensor:
        if (
                self._config.preprocessing_order
                == ImagePreprocessingOrder.EARLY_PREPROCESSING
        ):
            return torch.stack(
                [
                    self._preprocess(image)
                    for image in images.ordered_values()
                ]
            )

        images.same_size()

        return torch.stack(
            [
                pil_to_tensor(image)
                .float()
                .div(255.0)
                for image in images.ordered_values()
            ]
        )

    def create_generator(
            self,
            item_keys: tuple[int, ...],
            tensors: torch.Tensor,
    ) -> MaskingGenerator:
        _, channels, image_height, image_width = (
            tensors.shape
        )

        if channels != 3:
            raise ValueError(f"Expected 3 image channels, got {channels}.")

        geometry = SquareProvider(geometry_size=self._config.geometry_size)

        indexer = SpatialIndexer(
            item_keys=item_keys,
            image_width=image_width,
            image_height=image_height,
            grid_shape=self._config.grid_shape,
            start_point=self._config.start_point,
            step_size=self._config.step_size,
            geometry=geometry,
        )

        return MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=self._config.masking_mode,
        )

    def prepare_model_tensors(
            self,
            tensors: torch.Tensor,
    ) -> torch.Tensor:
        if (
                self._config.preprocessing_order
                == ImagePreprocessingOrder.EARLY_PREPROCESSING
        ):
            return tensors

        return torch.stack(
            [
                self._preprocess(tensor)
                for tensor in tensors
            ]
        )

    @torch.inference_mode()
    def image_region_batch(
            self,
            images: PilImageBatch,
    ) -> ClipSpatialTensorBatch:
        masking_tensors = self.prepare_masking_tensors(images)

        generator = self.create_generator(
            item_keys=images.ordered_keys(),
            tensors=masking_tensors,
        )

        generated_tensors = generator.generate(masking_tensors)

        region_tensors = self.prepare_model_tensors(generated_tensors)
        base_tensors = self.prepare_model_tensors(masking_tensors)

        model_tensors = torch.cat(
            (region_tensors, base_tensors),
            dim=0,
        ).to(self._device)

        vectors = self._model.encode_image(model_tensors)
        vectors = self._normalize_embeddings(vectors)
        vectors = vectors.detach().float().cpu()

        region_count = generator.layout.flat_count

        region_vectors = vectors[:region_count]
        base_vectors = vectors[region_count:]

        return ClipSpatialTensorBatch(
            SpatialVectorBatchData(
                vectors={
                    index: vector
                    for index, vector in enumerate(region_vectors)
                },
                base_vectors={
                    item_key: vector
                    for item_key, vector in zip(
                        generator.item_keys,
                        base_vectors,
                        strict=True,
                    )
                },
                layout=generator.layout,
                item_keys=generator.item_keys,
                regions=generator.regions,
            )
        )

    def score_text_vector_batch(
            self,
            pair: ClipSpatialTextVectorPair,
    ) -> SpatialScoreVectorBatch:
        """Score text queries against spatial and base image embeddings."""
        text_vectors = self.text_batch(pair.data().texts)

        return self._score_embeddings(
            text_vectors=text_vectors,
            spatial_vectors=pair.data().vectors,
        )

    def score_text_image_batch(
            self,
            pair: ClipSpatialTextImagePair,
    ) -> SpatialScoreVectorBatch:
        """Create image embeddings and score text queries."""
        spatial_vectors = self.image_region_batch(
            pair.data().images
        )

        return self.score_text_vector_batch(
            ClipSpatialTextVectorPair(
                ClipSpatialTextVectorPairData(
                    texts=pair.data().texts,
                    vectors=spatial_vectors,
                )
            )
        )

    def _score_embeddings(
            self,
            text_vectors: ClipSpatialTextTensorBatch,
            spatial_vectors: ClipSpatialTensorBatch,
    ) -> SpatialScoreVectorBatch:
        """Score spatial and base image embeddings against text embeddings."""
        scoring_function = self.config.scoring_function

        spatial_tensor = spatial_vectors.as_structured_tensor()
        base_tensor = spatial_vectors.as_base_tensor()
        text_tensor = text_vectors.vectors

        if spatial_tensor.shape[-1] != text_tensor.shape[-1]:
            raise ValueError(
                "Text and spatial embedding dimensions must match: "
                f"{text_tensor.shape[-1]} != {spatial_tensor.shape[-1]}."
            )

        if base_tensor.shape[-1] != text_tensor.shape[-1]:
            raise ValueError(
                "Text and base embedding dimensions must match: "
                f"{text_tensor.shape[-1]} != {base_tensor.shape[-1]}."
            )

        spatial_scores = spatial_tensor @ text_tensor.T
        base_scores = base_tensor @ text_tensor.T

        match scoring_function:
            case ScoringFunction.ABSOLUTE:
                pass

            case ScoringFunction.RELATIVE_POSITIVE:
                spatial_scores = spatial_scores - base_scores.unsqueeze(1)

            case ScoringFunction.RELATIVE_NEGATIVE:
                spatial_scores = base_scores.unsqueeze(1) - spatial_scores

            case ScoringFunction.ABSOLUTE_NORMALIZED:
                spatial_scores = self._normalize_scores(spatial_scores)

            case ScoringFunction.RELATIVE_POSITIVE_NORMALIZED:
                spatial_scores = spatial_scores - base_scores.unsqueeze(1)
                spatial_scores = self._normalize_scores(spatial_scores)

            case ScoringFunction.RELATIVE_NEGATIVE_NORMALIZED:
                spatial_scores = base_scores.unsqueeze(1) - spatial_scores
                spatial_scores = self._normalize_scores(spatial_scores)

        spatial_scores = spatial_scores.flatten(start_dim=0, end_dim=1)

        return SpatialScoreVectorBatch(
            data=SpatialVectorBatchData(
                vectors={
                    flat_index: [float(score) for score in score_vector.tolist()]
                    for flat_index, score_vector in enumerate(spatial_scores)
                },
                base_vectors={
                    item_key: [float(score) for score in score_vector.tolist()]
                    for item_key, score_vector in zip(
                        spatial_vectors.item_keys,
                        base_scores,
                        strict=True,
                    )
                },
                layout=spatial_vectors.layout,
                item_keys=spatial_vectors.item_keys,
                regions=spatial_vectors.regions,
            ),
            query_keys=text_vectors.keys,
        )

    @staticmethod
    def _normalize_scores(scores: torch.Tensor) -> torch.Tensor:
        minimum = scores.amin(dim=1, keepdim=True)
        maximum = scores.amax(dim=1, keepdim=True)
        denominator = maximum - minimum

        return torch.where(
            denominator > 0,
            (scores - minimum) / denominator,
            torch.zeros_like(scores),
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
