import unittest

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.primitive_vector_base import PrimitiveVectorBase
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import PrimitiveVectorBatchBase


class TestPrimitiveBaseArchitecture(unittest.TestCase):
    def test_primitive_vector_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(PrimitiveVectorBase, DatatypeBase)
        )

    def test_primitive_vector_batch_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(PrimitiveVectorBatchBase, DatatypeBase)
        )