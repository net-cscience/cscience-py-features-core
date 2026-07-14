import unittest

from cscience.features.api import (
    DatatypeBase,
    EmbeddingBase,
    SpatialPrimitiveVectorBatchBase,
    SpatialVectorBatchBase,
    VectorBatchBase,
)

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_datatype import (
    ClipSpatialDatatype,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)


CLIP_SPATIAL_DATATYPES = (
    ClipSpatialTensorBatch,
    ClipSpatialTextTensorBatch,
    SpatialScoreVectorBatch,
)


class TestClipSpatialDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_clip_spatial_namespace(
        self,
    ) -> None:
        for datatype_class in CLIP_SPATIAL_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "clip_spatial",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in CLIP_SPATIAL_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        ClipSpatialDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in CLIP_SPATIAL_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_spatial_tensor_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipSpatialTensorBatch.__mro__

        self.assertLess(
            mro.index(SpatialVectorBatchBase),
            mro.index(ClipSpatialDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipSpatialDatatype),
        )

    def test_text_tensor_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipSpatialTextTensorBatch.__mro__

        self.assertLess(
            mro.index(VectorBatchBase),
            mro.index(ClipSpatialDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipSpatialDatatype),
        )

    def test_score_structure_precedes_namespace(
        self,
    ) -> None:
        mro = SpatialScoreVectorBatch.__mro__

        self.assertLess(
            mro.index(SpatialPrimitiveVectorBatchBase),
            mro.index(ClipSpatialDatatype),
        )

    def test_scores_are_not_embeddings(self) -> None:
        self.assertFalse(
            issubclass(
                SpatialScoreVectorBatch,
                EmbeddingBase,
            )
        )

import torch

from cscience.features.api import (
    SpatialBatchLayout,
    SpatialRegion,
    SpatialVectorBatchData,
)


def make_regions() -> tuple[SpatialRegion, ...]:
    return (
        SpatialRegion(
            index=0,
            row=0,
            column=0,
            center_x=5,
            center_y=5,
            x0=0,
            y0=0,
            x1=10,
            y1=10,
            nx0=0.0,
            ny0=0.0,
            nx1=0.5,
            ny1=1.0,
        ),
        SpatialRegion(
            index=1,
            row=0,
            column=1,
            center_x=15,
            center_y=5,
            x0=10,
            y0=0,
            x1=20,
            y1=10,
            nx0=0.5,
            ny0=0.0,
            nx1=1.0,
            ny1=1.0,
        ),
    )


def make_spatial_tensor_data(
) -> SpatialVectorBatchData[torch.Tensor]:
    return SpatialVectorBatchData(
        vectors={
            0: torch.tensor([0.0, 0.1, 0.2]),
            1: torch.tensor([1.0, 1.1, 1.2]),
            2: torch.tensor([2.0, 2.1, 2.2]),
            3: torch.tensor([3.0, 3.1, 3.2]),
        },
        layout=SpatialBatchLayout(
            item_count=2,
            regions_per_item=2,
        ),
        item_keys=(10, 20),
        regions=make_regions(),
    )

import unittest

import torch

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)


class TestClipSpatialTensorBatch(unittest.TestCase):
    def test_constructs_spatial_embedding_batch(self) -> None:
        batch = ClipSpatialTensorBatch(
            make_spatial_tensor_data()
        )

        self.assertEqual(batch.batch_size(), 4)
        self.assertEqual(batch.item_count(), 2)
        self.assertEqual(batch.regions_per_item(), 2)
        self.assertEqual(batch.length(), 3)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_returns_flat_tensor(self) -> None:
        batch = ClipSpatialTensorBatch(
            make_spatial_tensor_data()
        )

        flat = batch.as_flat_tensor()

        self.assertEqual(tuple(flat.shape), (4, 3))
        self.assertTrue(
            torch.equal(
                flat[2],
                torch.tensor([2.0, 2.1, 2.2]),
            )
        )

    def test_returns_structured_tensor(self) -> None:
        batch = ClipSpatialTensorBatch(
            make_spatial_tensor_data()
        )

        structured = batch.as_structured_tensor()

        self.assertEqual(
            tuple(structured.shape),
            (2, 2, 3),
        )

    def test_rejects_non_tensor_vector(self) -> None:
        data = make_spatial_tensor_data()
        invalid = SpatialVectorBatchData(
            vectors={
                **data.vectors,
                3: [3.0, 3.1, 3.2],
            },
            layout=data.layout,
            item_keys=data.item_keys,
            regions=data.regions,
        )

        with self.assertRaises(TypeError):
            ClipSpatialTensorBatch(invalid)

    def test_rejects_non_vector_tensor(self) -> None:
        data = make_spatial_tensor_data()
        invalid = SpatialVectorBatchData(
            vectors={
                **data.vectors,
                3: torch.zeros((1, 3)),
            },
            layout=data.layout,
            item_keys=data.item_keys,
            regions=data.regions,
        )

        with self.assertRaises(ValueError):
            ClipSpatialTensorBatch(invalid)

    def test_rejects_integer_tensor(self) -> None:
        data = make_spatial_tensor_data()
        invalid = SpatialVectorBatchData(
            vectors={
                **data.vectors,
                3: torch.tensor([1, 2, 3]),
            },
            layout=data.layout,
            item_keys=data.item_keys,
            regions=data.regions,
        )

        with self.assertRaises(TypeError):
            ClipSpatialTensorBatch(invalid)


import unittest

import torch

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)


class TestClipSpatialTextTensorBatch(unittest.TestCase):
    def test_constructs_text_embedding_batch(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(20, 10),
            vectors=torch.tensor(
                [
                    [2.0, 2.1, 2.2],
                    [1.0, 1.1, 1.2],
                ]
            ),
        )

        batch = ClipSpatialTextTensorBatch(data)

        self.assertEqual(batch.keys, (20, 10))
        self.assertEqual(batch.ordered_keys(), (10, 20))
        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_orders_vectors_by_text_key(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(20, 10),
            vectors=torch.tensor(
                [
                    [2.0, 2.1],
                    [1.0, 1.1],
                ]
            ),
        )

        batch = ClipSpatialTextTensorBatch(data)
        ordered = batch.ordered_values()

        self.assertTrue(
            torch.equal(
                ordered[0],
                torch.tensor([1.0, 1.1]),
            )
        )

    def test_rejects_duplicate_keys(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(10, 10),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipSpatialTextTensorBatch(data)

    def test_rejects_key_row_mismatch(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(10,),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipSpatialTextTensorBatch(data)


import unittest

from cscience.features.api import SpatialVectorBatchData

from cscience.features.clip_spatial.clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)


def make_score_data(
) -> SpatialVectorBatchData[list[float]]:
    tensor_data = make_spatial_tensor_data()

    return SpatialVectorBatchData(
        vectors={
            0: [0.1, 0.2],
            1: [0.3, 0.4],
            2: [0.5, 0.6],
            3: [0.7, 0.8],
        },
        layout=tensor_data.layout,
        item_keys=tensor_data.item_keys,
        regions=tensor_data.regions,
    )


class TestSpatialScoreVectorBatch(unittest.TestCase):
    def test_constructs_score_batch(self) -> None:
        batch = SpatialScoreVectorBatch(
            make_score_data(),
            query_keys=(100, 200),
        )

        self.assertEqual(batch.query_keys, (100, 200))
        self.assertEqual(batch.query_count, 2)
        self.assertEqual(batch.length(), 2)
        self.assertEqual(batch.namespace, "clip_spatial")

    def test_rejects_query_count_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(100,),
            )

    def test_rejects_empty_query_keys(self) -> None:
        with self.assertRaises(ValueError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(),
            )

    def test_rejects_duplicate_query_keys(self) -> None:
        with self.assertRaises(ValueError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(100, 100),
            )

    def test_rejects_non_integer_query_key(self) -> None:
        with self.assertRaises(TypeError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(
                    100,
                    "200",  # type: ignore[arg-type]
                ),
            )