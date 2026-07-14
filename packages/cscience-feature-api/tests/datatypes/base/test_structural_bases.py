import unittest
from collections.abc import Mapping
from dataclasses import dataclass

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.batch_base import BatchBase
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockBatch(
    BatchBase[str],
    CoreDatatype[dict[int, str]],
):
    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)
        super().__init__(dict(data))


class MockVector(
    VectorBase,
    CoreDatatype[list[float]],
):
    pass


class MockVectorBatch(
    VectorBatchBase[list[float]],
    CoreDatatype[dict[int, list[float]]],
):
    def __init__(
        self,
        data: Mapping[int, list[float]],
    ) -> None:
        self._validate_vector_batch_mapping(data)
        super().__init__(dict(data))


class MockEmbedding(
    VectorBase,
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    pass


@dataclass(frozen=True, slots=True)
class WrappedBatchData:
    values: Mapping[int, str]


class MockWrappedBatch(
    BatchBase[str],
    CoreDatatype[WrappedBatchData],
):
    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)
        super().__init__(
            WrappedBatchData(values=dict(data))
        )

    def _batch_mapping(self) -> Mapping[int, str]:
        return self.data().values


class TestBatchBase(unittest.TestCase):
    def test_orders_batch_by_source_index(self) -> None:
        batch = MockBatch({
            5: "five",
            1: "one",
            3: "three",
        })

        self.assertEqual(batch.ordered_keys(), (1, 3, 5))
        self.assertEqual(
            batch.ordered_values(),
            ("one", "three", "five"),
        )
        self.assertEqual(
            batch.ordered_items(),
            (
                (1, "one"),
                (3, "three"),
                (5, "five"),
            ),
        )

    def test_reports_batch_size(self) -> None:
        batch = MockBatch({
            10: "a",
            20: "b",
        })

        self.assertEqual(batch.batch_size(), 2)

    def test_supports_overridden_batch_mapping(self) -> None:
        batch = MockWrappedBatch({
            2: "two",
            1: "one",
        })

        self.assertEqual(batch.ordered_values(), ("one", "two"))


class TestVectorBase(unittest.TestCase):
    def test_reports_vector_length(self) -> None:
        vector = MockVector([1.0, 2.0, 3.0])

        self.assertEqual(vector.length(), 3)

    def test_asserts_expected_vector_length(self) -> None:
        vector = MockVector([1.0, 2.0])

        with self.assertRaises(ValueError):
            vector.assert_length(3)


class TestVectorBatchBase(unittest.TestCase):
    def test_reports_shared_vector_length(self) -> None:
        batch = MockVectorBatch({
            1: [1.0, 2.0],
            0: [3.0, 4.0],
        })

        self.assertEqual(batch.length(), 2)

    def test_rejects_inconsistent_vector_lengths(self) -> None:
        with self.assertRaises(ValueError):
            MockVectorBatch({
                0: [1.0],
                1: [2.0, 3.0],
            })


class TestEmbeddingBase(unittest.TestCase):
    def test_reports_embedding_dimension(self) -> None:
        embedding = MockEmbedding([1.0, 2.0, 3.0])

        self.assertEqual(embedding.embedding_dim(), 3)

    def test_does_not_inherit_vector_base(self) -> None:
        self.assertFalse(issubclass(EmbeddingBase, VectorBase))


class TestDatatypeInheritance(unittest.TestCase):
    def test_mock_types_reach_datatype_base_once(self) -> None:
        datatype_classes = (
            MockBatch,
            MockVector,
            MockVectorBatch,
            MockEmbedding,
            MockWrappedBatch,
        )

        for datatype_class in datatype_classes:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(DatatypeBase),
                    1,
                )