import unittest
from collections.abc import Mapping
from typing import TypeVar

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)
from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
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
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
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

T = TypeVar("T")


class MockBatch(
    BatchBase[str],
    CoreDatatype[dict[int, str]],
):
    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)
        super().__init__(dict(data))


class MockPrimitiveVector(
    PrimitiveVectorBase[float],
    CoreDatatype[list[float]],
):
    element_type = float


class MockEmbeddingVector(
    PrimitiveVectorBase[float],
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    element_type = float


class MockPrimitiveVectorBatch(
    PrimitiveVectorBatchBase[float],
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class MockEmbeddingVectorBatch(
    PrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class MockSpatialEmbeddingBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    element_type = float


class MockAudioBytes(
    AudioBytesBase,
    CoreDatatype[bytes],
):
    pass


class MockImageBytes(
    ImageBytesBase,
    CoreDatatype[bytes],
):
    pass


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
            0: [0.0, 0.1],
            1: [1.0, 1.1],
            2: [2.0, 2.1],
            3: [3.0, 3.1],
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
            0: [0.0, 0.1],
            1: [1.0, 1.1],
        }
    )

class TestNamespaceNeutrality(unittest.TestCase):
    def test_structural_bases_do_not_inherit_datatype_base(
        self,
    ) -> None:
        structural_bases = (
            BatchBase,
            VectorBase,
            VectorBatchBase,
            PrimitiveVectorBase,
            PrimitiveVectorBatchBase,
            SpatialVectorBatchBase,
            SpatialPrimitiveVectorBatchBase,
        )

        for structural_base in structural_bases:
            with self.subTest(
                structural_base=structural_base,
            ):
                self.assertFalse(
                    issubclass(
                        structural_base,
                        DatatypeBase,
                    )
                )

    def test_semantic_bases_do_not_inherit_datatype_base(
        self,
    ) -> None:
        semantic_bases = (
            EmbeddingBase,
            MediaBytesBase,
            AudioBytesBase,
            ImageBytesBase,
        )

        for semantic_base in semantic_bases:
            with self.subTest(
                semantic_base=semantic_base,
            ):
                self.assertFalse(
                    issubclass(
                        semantic_base,
                        DatatypeBase,
                    )
                )

    def test_core_datatype_inherits_datatype_base(
        self,
    ) -> None:
        self.assertTrue(
            issubclass(
                CoreDatatype,
                DatatypeBase,
            )
        )

    def test_embedding_base_is_not_vector_base(
        self,
    ) -> None:
        self.assertFalse(
            issubclass(
                EmbeddingBase,
                VectorBase,
            )
        )

class TestDataOwnership(unittest.TestCase):
    def assert_has_one_data_owner_branch(
            self,
            datatype_class: type,
    ) -> None:
        data_owner_branches = tuple(
            base
            for base in datatype_class.__bases__
            if issubclass(base, DatatypeBase)
        )

        self.assertEqual(
            len(data_owner_branches),
            1,
            msg=(
                f"{datatype_class.__name__} must have exactly "
                f"one direct base leading to DatatypeBase, "
                f"got {data_owner_branches}."
            ),
        )

    def test_composed_datatypes_have_one_data_owner_branch(
            self,
    ) -> None:
        datatype_classes = (
            MockBatch,
            MockPrimitiveVector,
            MockEmbeddingVector,
            MockPrimitiveVectorBatch,
            MockEmbeddingVectorBatch,
            MockSpatialEmbeddingBatch,
            MockAudioBytes,
            MockImageBytes,
        )

        for datatype_class in datatype_classes:
            with self.subTest(
                    datatype_class=datatype_class,
            ):
                self.assert_has_one_data_owner_branch(
                    datatype_class
                )

class TestDatatypeMro(unittest.TestCase):
    def assert_mro_before(
        self,
        datatype_class: type,
        earlier_class: type,
        later_class: type,
    ) -> None:
        mro = datatype_class.__mro__

        self.assertLess(
            mro.index(earlier_class),
            mro.index(later_class),
            msg=(
                f"{earlier_class.__name__} must occur before "
                f"{later_class.__name__} in the MRO of "
                f"{datatype_class.__name__}."
            ),
        )

    def test_primitive_vector_validates_before_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockPrimitiveVector,
            PrimitiveVectorBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVector,
            VectorBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVector,
            CoreDatatype,
            DatatypeBase,
        )

    def test_embedding_vector_validates_before_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockEmbeddingVector,
            PrimitiveVectorBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockEmbeddingVector,
            EmbeddingBase,
            CoreDatatype,
        )

    def test_vector_batch_validates_before_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockPrimitiveVectorBatch,
            PrimitiveVectorBatchBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVectorBatch,
            VectorBatchBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVectorBatch,
            BatchBase,
            CoreDatatype,
        )

    def test_spatial_batch_validates_before_data_owner(
        self,
    ) -> None:
        preceding_bases = (
            SpatialPrimitiveVectorBatchBase,
            SpatialVectorBatchBase,
            VectorBatchBase,
            BatchBase,
            EmbeddingBase,
        )

        for preceding_base in preceding_bases:
            with self.subTest(
                preceding_base=preceding_base,
            ):
                self.assert_mro_before(
                    MockSpatialEmbeddingBatch,
                    preceding_base,
                    CoreDatatype,
                )

    def test_media_validation_precedes_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockAudioBytes,
            AudioBytesBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockAudioBytes,
            MediaBytesBase,
            CoreDatatype,
        )


class TestCooperativeConstruction(unittest.TestCase):
    def test_batch_reaches_datatype_base(self) -> None:
        batch = MockBatch({
            1: "one",
            0: "zero",
        })

        self.assertIsInstance(
            batch,
            DatatypeBase,
        )
        self.assertEqual(
            batch.data(),
            {
                1: "one",
                0: "zero",
            },
        )

    def test_primitive_vector_reaches_datatype_base(
        self,
    ) -> None:
        vector = MockPrimitiveVector([
            1.0,
            2.0,
        ])

        self.assertIsInstance(
            vector,
            DatatypeBase,
        )
        self.assertEqual(
            vector.data(),
            [1.0, 2.0],
        )

    def test_embedding_vector_reaches_datatype_base(
        self,
    ) -> None:
        vector = MockEmbeddingVector([
            1.0,
            2.0,
            3.0,
        ])

        self.assertEqual(
            vector.embedding_dim(),
            3,
        )
        self.assertEqual(
            vector.data(),
            [1.0, 2.0, 3.0],
        )

    def test_vector_batch_reaches_datatype_base(
        self,
    ) -> None:
        batch = MockPrimitiveVectorBatch({
            0: [1.0, 2.0],
            1: [3.0, 4.0],
        })

        self.assertEqual(
            batch.data(),
            {
                0: [1.0, 2.0],
                1: [3.0, 4.0],
            },
        )
        self.assertEqual(batch.length(), 2)

    def test_spatial_batch_reaches_datatype_base(
        self,
    ) -> None:
        data = make_spatial_data()

        batch = MockSpatialEmbeddingBatch(data)

        self.assertIsInstance(
            batch,
            DatatypeBase,
        )
        self.assertIsInstance(
            batch.data(),
            SpatialVectorBatchData,
        )
        self.assertEqual(
            batch.data().vectors,
            data.vectors,
        )
        self.assertEqual(
            batch.embedding_dim(),
            2,
        )

    def test_audio_bytes_reaches_datatype_base(
        self,
    ) -> None:
        audio = MockAudioBytes(b"audio")

        self.assertEqual(
            audio.data(),
            b"audio",
        )

    def test_image_bytes_reaches_datatype_base(
        self,
    ) -> None:
        image = MockImageBytes(b"image")

        self.assertEqual(
            image.data(),
            b"image",
        )