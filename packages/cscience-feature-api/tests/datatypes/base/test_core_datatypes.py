import unittest

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockCoreDatatype(CoreDatatype[int]):
    pass


class TestCoreDatatype(unittest.TestCase):
    def test_is_datatype(self) -> None:
        self.assertTrue(issubclass(MockCoreDatatype, DatatypeBase))

    def test_uses_core_namespace(self) -> None:
        self.assertEqual(MockCoreDatatype.namespace, "core")

    def test_stores_data_through_datatype_base(self) -> None:
        datatype = MockCoreDatatype(42)

        self.assertEqual(datatype.data(), 42)