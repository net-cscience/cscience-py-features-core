import unittest
from collections.abc import Mapping

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockFloatVectorBatch(
    PrimitiveVectorBatchBase[float],
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class MockFloatEmbeddingBatch(
    PrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class TestPrimitiveVectorBatchBase(unittest.TestCase):
    def test_stores_vector_batch_as_dict(self) -> None:
        source: Mapping[int, list[float]] = {
            1: [3.0, 4.0],
            0: [1.0, 2.0],
        }

        batch = MockFloatVectorBatch(source)

        self.assertEqual(
            batch.data(),
            {
                1: [3.0, 4.0],
                0: [1.0, 2.0],
            },
        )
        self.assertIsInstance(batch.data(), dict)

    def test_orders_vectors_by_source_index(self) -> None:
        batch = MockFloatVectorBatch({
            5: [5.0, 6.0],
            1: [1.0, 2.0],
            3: [3.0, 4.0],
        })

        self.assertEqual(batch.ordered_keys(), (1, 3, 5))
        self.assertEqual(
            batch.ordered_values(),
            (
                [1.0, 2.0],
                [3.0, 4.0],
                [5.0, 6.0],
            ),
        )

    def test_reports_batch_size(self) -> None:
        batch = MockFloatVectorBatch({
            0: [1.0, 2.0],
            1: [3.0, 4.0],
        })

        self.assertEqual(batch.batch_size(), 2)

    def test_reports_shared_vector_length(self) -> None:
        batch = MockFloatVectorBatch({
            0: [1.0, 2.0],
            1: [3.0, 4.0],
        })

        self.assertEqual(batch.length(), 2)

    def test_asserts_expected_length(self) -> None:
        batch = MockFloatVectorBatch(
            {
                0: [1.0, 2.0],
                1: [3.0, 4.0],
            },
            assert_length=2,
        )

        self.assertEqual(batch.length(), 2)

    def test_rejects_empty_batch(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVectorBatch({})

    def test_rejects_non_integer_key(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVectorBatch(
                {
                    "0": [1.0, 2.0],  # type: ignore[dict-item]
                }
            )

    def test_rejects_non_list_vector(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVectorBatch(
                {
                    0: (1.0, 2.0),  # type: ignore[dict-item]
                }
            )

    def test_rejects_empty_vector(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVectorBatch({
                0: [],
            })

    def test_rejects_inconsistent_vector_lengths(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVectorBatch({
                0: [1.0],
                1: [2.0, 3.0],
            })

    def test_rejects_wrong_element_type(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVectorBatch({
                0: [1.0, 2],  # type: ignore[list-item]
            })

    def test_embedding_batch_reports_dimension(self) -> None:
        batch = MockFloatEmbeddingBatch({
            0: [1.0, 2.0, 3.0],
            1: [4.0, 5.0, 6.0],
        })

        self.assertEqual(batch.embedding_dim(), 3)

    def test_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatVectorBatch.__mro__.count(DatatypeBase),
            1,
        )

    def test_embedding_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatEmbeddingBatch.__mro__.count(DatatypeBase),
            1,
        )