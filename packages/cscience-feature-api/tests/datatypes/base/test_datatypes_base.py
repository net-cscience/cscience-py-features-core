
import unittest

from icontract import ViolationError

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase

class ExampleDatatype(DatatypeBase[int]):
    pass


class TestDatatypeBase(unittest.TestCase):
    def test_stores_data(self) -> None:
        datatype = ExampleDatatype(42)

        self.assertEqual(datatype.data(), 42)

    def test_rejects_none(self) -> None:
        with self.assertRaises(ViolationError):
            ExampleDatatype(None)  # type: ignore[arg-type]



