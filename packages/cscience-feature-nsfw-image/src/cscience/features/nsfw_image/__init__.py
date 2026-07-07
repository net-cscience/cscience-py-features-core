from cscience.features.api import RegistryBase

from .nsfw_image_connector import NsfwImageConnector
from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_datatypes.nsfw_image_datatype import NsfwImageDatatype
from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction, NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
    NsfwPredictionBatchData,
)
from .nsfw_image_feature import NsfwImageFeature

__all__ = [
    "NsfwImageConnector",
    "NsfwImageConversionProvider",
    "NsfwImageDatatype",
    "NsfwImageFeature",
    "NsfwPrediction",
    "NsfwPredictionData",
    "NsfwPredictionBatch",
    "NsfwPredictionBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("nsfw_image", NsfwImageConversionProvider)