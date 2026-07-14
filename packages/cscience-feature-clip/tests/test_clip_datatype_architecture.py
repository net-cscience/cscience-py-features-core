import unittest

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)
from cscience.features.clip.clip_datatypes.clip_datatype import (
    ClipDatatype,
)
from cscience.features.clip.clip_datatypes.clip_tensor import (
    ClipTensor,
)
from cscience.features.clip.clip_datatypes.clip_tensor_batch import (
    ClipTensorBatch,
)


CLIP_DATATYPES = (
    ClipTensor,
    ClipTensorBatch,
)


class TestClipDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_clip_namespace(self) -> None:
        for datatype_class in CLIP_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "clip",
                )

    def test_package_datatypes_inherit_clip_datatype(
        self,
    ) -> None:
        for datatype_class in CLIP_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        ClipDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in CLIP_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_clip_tensor_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipTensor.__mro__

        self.assertLess(
            mro.index(VectorBase),
            mro.index(ClipDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipDatatype),
        )

    def test_clip_tensor_batch_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipTensorBatch.__mro__

        self.assertLess(
            mro.index(VectorBatchBase),
            mro.index(ClipDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipDatatype),
        )

import unittest

import torch

from cscience.features.clip.clip_datatypes.clip_tensor import (
    ClipTensor,
)


class TestClipTensor(unittest.TestCase):
    def test_stores_embedding_tensor(self) -> None:
        tensor = torch.tensor(
            [1.0, 2.0, 3.0],
            dtype=torch.float32,
        )

        embedding = ClipTensor(tensor)

        self.assertIs(embedding.data(), tensor)
        self.assertEqual(embedding.length(), 3)
        self.assertEqual(embedding.embedding_dim(), 3)

    def test_accepts_float16_tensor(self) -> None:
        embedding = ClipTensor(
            torch.tensor(
                [1.0, 2.0],
                dtype=torch.float16,
            )
        )

        self.assertEqual(
            embedding.data().dtype,
            torch.float16,
        )

    def test_rejects_non_tensor(self) -> None:
        with self.assertRaises(TypeError):
            ClipTensor(
                [1.0, 2.0]  # type: ignore[arg-type]
            )

    def test_rejects_non_vector_tensor(self) -> None:
        with self.assertRaises(ValueError):
            ClipTensor(
                torch.zeros((2, 3))
            )

    def test_rejects_empty_tensor(self) -> None:
        with self.assertRaises(ValueError):
            ClipTensor(
                torch.empty((0,))
            )

    def test_rejects_integer_tensor(self) -> None:
        with self.assertRaises(TypeError):
            ClipTensor(
                torch.tensor([1, 2, 3])
            )

import unittest

import torch

from cscience.features.clip.clip_datatypes.clip_tensor_batch import (
    ClipTensorBatch,
)
from cscience.features.clip.clip_datatypes.clip_tensor_batch_data import (
    ClipTensorBatchData,
)


def make_batch_data() -> ClipTensorBatchData:
    return ClipTensorBatchData(
        keys=(20, 10),
        vectors=torch.tensor(
            [
                [2.0, 2.1, 2.2],
                [1.0, 1.1, 1.2],
            ],
            dtype=torch.float32,
        ),
    )


class TestClipTensorBatch(unittest.TestCase):
    def test_stores_packed_batch(self) -> None:
        data = make_batch_data()

        batch = ClipTensorBatch(data)

        self.assertEqual(batch.keys, (20, 10))
        self.assertIs(batch.vectors, data.vectors)
        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(batch.length(), 3)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_orders_rows_by_source_key(self) -> None:
        batch = ClipTensorBatch(
            make_batch_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (10, 20),
        )

        ordered = batch.ordered_values()

        self.assertTrue(
            torch.equal(
                ordered[0],
                torch.tensor([1.0, 1.1, 1.2]),
            )
        )
        self.assertTrue(
            torch.equal(
                ordered[1],
                torch.tensor([2.0, 2.1, 2.2]),
            )
        )

    def test_rejects_wrong_outer_data_type(self) -> None:
        with self.assertRaises(TypeError):
            ClipTensorBatch(
                torch.zeros((2, 3))  # type: ignore[arg-type]
            )

    def test_rejects_non_tensor_vectors(self) -> None:
        data = ClipTensorBatchData(
            keys=(0,),
            vectors=[[1.0, 2.0]],  # type: ignore[arg-type]
        )

        with self.assertRaises(TypeError):
            ClipTensorBatch(data)

    def test_rejects_non_matrix_tensor(self) -> None:
        data = ClipTensorBatchData(
            keys=(0,),
            vectors=torch.tensor([1.0, 2.0]),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_key_row_mismatch(self) -> None:
        data = ClipTensorBatchData(
            keys=(0,),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_duplicate_keys(self) -> None:
        data = ClipTensorBatchData(
            keys=(0, 0),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_empty_batch(self) -> None:
        data = ClipTensorBatchData(
            keys=(),
            vectors=torch.empty((0, 3)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_empty_embedding_dimension(self) -> None:
        data = ClipTensorBatchData(
            keys=(0, 1),
            vectors=torch.empty((2, 0)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_integer_tensor(self) -> None:
        data = ClipTensorBatchData(
            keys=(0, 1),
            vectors=torch.tensor(
                [
                    [1, 2],
                    [3, 4],
                ]
            ),
        )

        with self.assertRaises(TypeError):
            ClipTensorBatch(data)