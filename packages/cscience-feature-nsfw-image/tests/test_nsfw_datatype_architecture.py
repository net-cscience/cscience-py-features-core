import unittest

from cscience.features.api import (
    BatchBase,
    DatatypeBase,
)

from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_image_datatype import (
    NsfwImageDatatype,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction import (
    NsfwPrediction,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
)


NSFW_DATATYPES = (
    NsfwPrediction,
    NsfwPredictionBatch,
)


class TestNsfwDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_nsfw_namespace(
        self,
    ) -> None:
        for datatype_class in NSFW_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "nsfw_image",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in NSFW_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        NsfwImageDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in NSFW_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_batch_structure_precedes_namespace(
        self,
    ) -> None:
        mro = NsfwPredictionBatch.__mro__

        self.assertLess(
            mro.index(BatchBase),
            mro.index(NsfwImageDatatype),
        )

import unittest

from cscience.features.api import FloatValue

from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction import (
    NsfwPrediction,
    NsfwPredictionData,
)


def make_prediction_data() -> NsfwPredictionData:
    return NsfwPredictionData(
        label="nsfw",
        score=0.8,
        normal_score=0.2,
        nsfw_score=0.8,
    )


class TestNsfwPrediction(unittest.TestCase):
    def test_stores_prediction(self) -> None:
        data = make_prediction_data()

        prediction = NsfwPrediction(data)

        self.assertIs(prediction.data(), data)
        self.assertEqual(
            prediction.namespace,
            "nsfw_image",
        )

    def test_returns_nsfw_score_as_float_value(
        self,
    ) -> None:
        prediction = NsfwPrediction(
            make_prediction_data()
        )

        score = prediction.nsfw_score()

        self.assertIsInstance(score, FloatValue)
        self.assertEqual(score.data(), 0.8)

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            NsfwPrediction(
                "invalid"  # type: ignore[arg-type]
            )

    def test_rejects_wrong_label_type(self) -> None:
        data = NsfwPredictionData(
            label=1,  # type: ignore[arg-type]
            score=0.8,
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(TypeError):
            NsfwPrediction(data)

    def test_rejects_non_float_score(self) -> None:
        data = NsfwPredictionData(
            label="nsfw",
            score=1,  # type: ignore[arg-type]
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(TypeError):
            NsfwPrediction(data)

    def test_rejects_score_below_zero(self) -> None:
        data = NsfwPredictionData(
            label="nsfw",
            score=-0.1,
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(ValueError):
            NsfwPrediction(data)

    def test_rejects_score_above_one(self) -> None:
        data = NsfwPredictionData(
            label="nsfw",
            score=1.1,
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(ValueError):
            NsfwPrediction(data)

    def test_classifies_using_threshold(self) -> None:
        data = make_prediction_data()

        self.assertTrue(data.is_nsfw(0.5))
        self.assertFalse(data.is_nsfw(0.9))

import unittest

from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction import (
    NsfwPredictionData,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction_batch_data import (
    NsfwPredictionBatchData,
)


def make_normal_prediction() -> NsfwPredictionData:
    return NsfwPredictionData(
        label="normal",
        score=0.9,
        normal_score=0.9,
        nsfw_score=0.1,
    )


def make_nsfw_prediction() -> NsfwPredictionData:
    return NsfwPredictionData(
        label="nsfw",
        score=0.8,
        normal_score=0.2,
        nsfw_score=0.8,
    )


def make_batch_data() -> NsfwPredictionBatchData:
    return NsfwPredictionBatchData(
        predictions={
            20: make_normal_prediction(),
            10: make_nsfw_prediction(),
        }
    )


class TestNsfwPredictionBatch(unittest.TestCase):
    def test_stores_prediction_batch(self) -> None:
        batch = NsfwPredictionBatch(
            make_batch_data()
        )

        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(
            batch.namespace,
            "nsfw_image",
        )

    def test_orders_predictions_by_source_key(
        self,
    ) -> None:
        batch = NsfwPredictionBatch(
            make_batch_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (10, 20),
        )
        self.assertEqual(
            tuple(
                prediction.label
                for prediction in batch.ordered_values()
            ),
            ("nsfw", "normal"),
        )

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            NsfwPredictionBatch(
                {}  # type: ignore[arg-type]
            )

    def test_rejects_empty_batch(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={}
        )

        with self.assertRaises(ValueError):
            NsfwPredictionBatch(data)

    def test_rejects_non_integer_key(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={
                "0": make_nsfw_prediction(),  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            NsfwPredictionBatch(data)

    def test_rejects_wrong_prediction_type(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={
                0: "invalid",  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            NsfwPredictionBatch(data)

    def test_rejects_invalid_prediction_data(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={
                0: NsfwPredictionData(
                    label="nsfw",
                    score=2.0,
                    normal_score=0.0,
                    nsfw_score=2.0,
                )
            }
        )

        with self.assertRaises(ValueError):
            NsfwPredictionBatch(data)