import unittest
from dataclasses import replace

from icontract import ViolationError

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_base import (
    SpatialVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)
from cscience.features.api.datatypes.spatial.spatial_batch_layout import (
    SpatialBatchLayout,
)
from cscience.features.api.datatypes.spatial.spatial_region import (
    SpatialRegion,
)


class MockSpatialFloatVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    element_type = float


def make_region(index: int) -> SpatialRegion:
    return SpatialRegion(
        index=index,
        row=0,
        column=index,
        center_x=5,
        center_y=5,
        x0=0,
        y0=0,
        x1=10,
        y1=10,
        nx0=0.0,
        ny0=0.0,
        nx1=1.0,
        ny1=1.0,
    )


def make_spatial_data() -> SpatialVectorBatchData[list[float]]:
    return SpatialVectorBatchData(
        vectors={
            0: [0.0, 0.1, 0.2],
            1: [1.0, 1.1, 1.2],
            2: [2.0, 2.1, 2.2],
            3: [3.0, 3.1, 3.2],
        },
        layout=SpatialBatchLayout(
            item_count=2,
            regions_per_item=2,
        ),
        item_keys=(10, 20),
        regions=(
            make_region(0),
            make_region(1),
        ),
        base_vectors={
            0: [0.0, 0.1, 0.2],
            1: [1.0, 1.1, 1.2],
        }
    )


class TestSpatialVectorBatchBase(unittest.TestCase):
    def test_stores_spatial_data(self) -> None:
        data = make_spatial_data()

        batch = MockSpatialFloatVectorBatch(data)

        self.assertEqual(batch.layout, data.layout)
        self.assertEqual(batch.item_keys, (10, 20))
        self.assertEqual(batch.regions, data.regions)

    def test_reports_flat_batch_size(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(batch.batch_size(), 4)

    def test_reports_structured_dimensions(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(batch.item_count(), 2)
        self.assertEqual(batch.regions_per_item(), 2)
        self.assertEqual(batch.length(), 3)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_uses_inherited_ordering(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (0, 1, 2, 3),
        )

        self.assertEqual(
            batch.ordered_values(),
            (
                [0.0, 0.1, 0.2],
                [1.0, 1.1, 1.2],
                [2.0, 2.1, 2.2],
                [3.0, 3.1, 3.2],
            ),
        )

    def test_returns_vector_at_structured_index(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(
            batch.vector_at(
                item_index=1,
                region_index=0,
            ),
            [2.0, 2.1, 2.2],
        )

    def test_returns_vectors_for_item(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(
            batch.item_vectors(1),
            (
                [2.0, 2.1, 2.2],
                [3.0, 3.1, 3.2],
            ),
        )

    def test_rejects_wrong_item_key_count(self) -> None:
        data = replace(
            make_spatial_data(),
            item_keys=(10,),
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_duplicate_item_keys(self) -> None:
        data = replace(
            make_spatial_data(),
            item_keys=(10, 10),
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_non_contiguous_vector_keys(self) -> None:
        data = replace(
            make_spatial_data(),
            vectors={
                0: [0.0, 0.1, 0.2],
                1: [1.0, 1.1, 1.2],
                2: [2.0, 2.1, 2.2],
                4: [3.0, 3.1, 3.2],
            },
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_wrong_region_count(self) -> None:
        data = replace(
            make_spatial_data(),
            regions=(make_region(0),),
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_inconsistent_vector_lengths(self) -> None:
        data = replace(
            make_spatial_data(),
            vectors={
                0: [0.0, 0.1],
                1: [1.0, 1.1, 1.2],
                2: [2.0, 2.1, 2.2],
                3: [3.0, 3.1, 3.2],
            },
        )

        with self.assertRaises(ValueError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_wrong_primitive_type(self) -> None:
        data = replace(
            make_spatial_data(),
            vectors={
                0: [0.0, 0.1, 0.2],
                1: [1.0, 1.1, 1.2],
                2: [2.0, 2.1, 2.2],
                3: [3.0, 3.1, 3],
            },
        )

        with self.assertRaises(TypeError):
            MockSpatialFloatVectorBatch(data)

    def test_asserts_expected_length(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data(),
            assert_length=3,
        )

        self.assertEqual(batch.length(), 3)

    def test_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockSpatialFloatVectorBatch.__mro__.count(
                DatatypeBase
            ),
            1,
        )

    def test_spatial_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                SpatialVectorBatchBase,
                DatatypeBase,
            )
        )