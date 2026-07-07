from cscience.features.api import (
    BoolValue,
    ConversionProviderBase,
    Converter,
    FeatureBase,
    FloatValue,
)

from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction
from .nsfw_image_datatypes.nsfw_prediction_batch import NsfwPredictionBatch


def nsfw_prediction_passthrough(prediction: NsfwPrediction) -> NsfwPrediction:
    return prediction


def nsfw_prediction_batch_passthrough(batch: NsfwPredictionBatch) -> NsfwPredictionBatch:
    return batch


def nsfw_prediction_batch_to_prediction(batch: NsfwPredictionBatch) -> NsfwPrediction:
    predictions = batch.data().predictions

    if len(predictions) != 1:
        raise ValueError(
            f"Cannot convert NsfwPredictionBatch of size {len(predictions)} "
            f"to NsfwPrediction."
        )

    prediction = next(iter(predictions.values()))
    return NsfwPrediction(prediction)


def nsfw_prediction_to_float_value(prediction: NsfwPrediction) -> FloatValue:
    return FloatValue(prediction.data().nsfw_score)


def nsfw_prediction_to_bool_value(prediction: NsfwPrediction) -> BoolValue:
    return BoolValue(prediction.data().is_nsfw())


class NsfwImageConversionProvider(ConversionProviderBase):
    """Registers conversions required by the NSFW image feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[NsfwPrediction, NsfwPrediction](
                name="nsfw_prediction_passthrough",
                source=self._feature,
                function=nsfw_prediction_passthrough,
                input_type=NsfwPrediction,
                output_type=NsfwPrediction,
            ),
            Converter[NsfwPredictionBatch, NsfwPredictionBatch](
                name="nsfw_prediction_batch_passthrough",
                source=self._feature,
                function=nsfw_prediction_batch_passthrough,
                input_type=NsfwPredictionBatch,
                output_type=NsfwPredictionBatch,
            ),
            Converter[NsfwPredictionBatch, NsfwPrediction](
                name="nsfw_prediction_batch_to_prediction",
                source=self._feature,
                function=nsfw_prediction_batch_to_prediction,
                input_type=NsfwPredictionBatch,
                output_type=NsfwPrediction,
            ),
            Converter[NsfwPrediction, FloatValue](
                name="nsfw_prediction_to_float_value",
                source=self._feature,
                function=nsfw_prediction_to_float_value,
                input_type=NsfwPrediction,
                output_type=FloatValue,
            ),
            Converter[NsfwPrediction, BoolValue](
                name="nsfw_prediction_to_bool_value",
                source=self._feature,
                function=nsfw_prediction_to_bool_value,
                input_type=NsfwPrediction,
                output_type=BoolValue,
            ),
        ]