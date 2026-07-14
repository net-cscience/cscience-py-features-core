import unittest

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockFloatVector(
    PrimitiveVectorBase[float],
    CoreDatatype[list[float]],
):
    element_type = float


class MockFloatEmbedding(
    PrimitiveVectorBase[float],
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    element_type = float


class TestPrimitiveVectorBase(unittest.TestCase):
    def test_stores_primitive_vector(self) -> None:
        vector = MockFloatVector([1.0, 2.0, 3.0])

        self.assertEqual(vector.data(), [1.0, 2.0, 3.0])

    def test_reports_vector_length(self) -> None:
        vector = MockFloatVector([1.0, 2.0, 3.0])

        self.assertEqual(vector.length(), 3)

    def test_asserts_expected_length(self) -> None:
        vector = MockFloatVector(
            [1.0, 2.0, 3.0],
            assert_length=3,
        )

        self.assertEqual(vector.length(), 3)

    def test_rejects_unexpected_length(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVector(
                [1.0, 2.0],
                assert_length=3,
            )

    def test_rejects_empty_vector(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVector([])

    def test_rejects_non_list_container(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVector(
                (1.0, 2.0),  # type: ignore[arg-type]
            )

    def test_rejects_wrong_element_type(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVector(
                [1.0, 2],  # type: ignore[list-item]
            )

    def test_embedding_reports_dimension(self) -> None:
        embedding = MockFloatEmbedding([1.0, 2.0, 3.0])

        self.assertEqual(embedding.embedding_dim(), 3)

    def test_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatVector.__mro__.count(DatatypeBase),
            1,
        )

    def test_embedding_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatEmbedding.__mro__.count(DatatypeBase),
            1,
        )