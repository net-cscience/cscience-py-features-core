import torch

from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.api.datatypes.spatial.spatial_vector_batch_data import SpatialVectorBatchData

from .clip_spatial_config import ClipSpatialConfig
from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch
from .filter.zero_provider import ZeroProvider
from .indexer.spatial_indexer import SpatialIndexer
from .geometry.square_provider import SquareProvider
from .masking.masking_generator import MaskingGenerator



class ClipSpatialFeature(FeatureBase):
    """CLIP Spatial feature service backed by OpenCLIP."""

    def _initialize(self, open_clip=None) -> None:
        if self._initialized:
            return

        self.config = ClipSpatialConfig()

        if self.config.device == "auto":
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(self.config.device)

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name=self.config.model_name,
            pretrained=self.config.pretrained,
        )

        self.model = self.model.to(self.device).eval()
        self.tokenizer = open_clip.get_tokenizer(self.config.model_name)

        self._initialized = True

    @classmethod
    @torch.inference_mode()
    def image_region_batch(cls, images: PilImageBatch) -> ClipSpatialTensorBatch:
        service = cls.get_instance()

        item_keys = images.ordered_keys()
        image_values = images.ordered_values()

        base_tensors = torch.stack(
            [
                service.preprocess(image)
                for image in image_values
            ]
        )

        _, channels, image_height, image_width = base_tensors.shape

        if channels != 3:
            raise ValueError(f"Expected 3 image channels, got {channels}.")

        geometry = SquareProvider(
            geometry_size=service.config.region_size,
        )

        indexer = SpatialIndexer(
            item_keys=item_keys,
            image_width=image_width,
            image_height=image_height,
            grid_shape=service.config.grid_shape,
            start_point=service.config.start_point,
            step_size=service.config.step_size,
            geometry=geometry,
        )

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=service.config.masking_mode,
        )

        masked_tensors = generator.generate(base_tensors).to(service.device)

        vectors = service.model.encode_image(masked_tensors)
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
