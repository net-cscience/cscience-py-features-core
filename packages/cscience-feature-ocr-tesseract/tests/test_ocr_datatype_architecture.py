import unittest

from cscience.features.api import (
    BatchBase,
    DatatypeBase,
)

from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result import (
    OcrResult,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_tesseract_datatype import (
    OcrTesseractDatatype,
)


OCR_DATATYPES = (
    OcrResult,
    OcrResultBatch,
)


class TestOcrDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_ocr_namespace(
        self,
    ) -> None:
        for datatype_class in OCR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "ocr_tesseract",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in OCR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        OcrTesseractDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in OCR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_batch_structure_precedes_namespace(
        self,
    ) -> None:
        mro = OcrResultBatch.__mro__

        self.assertLess(
            mro.index(BatchBase),
            mro.index(OcrTesseractDatatype),
        )

import unittest

from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result import (
    OcrResult,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_data import (
    OcrResultData,
)


class TestOcrResult(unittest.TestCase):
    def test_stores_ocr_result(self) -> None:
        data = OcrResultData(text="Recognized text")

        result = OcrResult(data)

        self.assertIs(result.data(), data)
        self.assertEqual(
            result.namespace,
            "ocr_tesseract",
        )

    def test_accepts_empty_text(self) -> None:
        result = OcrResult(
            OcrResultData(text="")
        )

        self.assertEqual(result.data().text, "")

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            OcrResult(
                "text"  # type: ignore[arg-type]
            )

    def test_rejects_wrong_text_type(self) -> None:
        data = OcrResultData(
            text=42,  # type: ignore[arg-type]
        )

        with self.assertRaises(TypeError):
            OcrResult(data)

import unittest

from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_batch_data import (
    OcrResultBatchData,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_data import (
    OcrResultData,
)


def make_batch_data() -> OcrResultBatchData:
    return OcrResultBatchData(
        results={
            20: OcrResultData(text="Second"),
            10: OcrResultData(text="First"),
        }
    )


class TestOcrResultBatch(unittest.TestCase):
    def test_stores_ocr_result_batch(self) -> None:
        batch = OcrResultBatch(
            make_batch_data()
        )

        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(
            batch.namespace,
            "ocr_tesseract",
        )

    def test_orders_results_by_source_key(self) -> None:
        batch = OcrResultBatch(
            make_batch_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (10, 20),
        )
        self.assertEqual(
            tuple(
                result.text
                for result in batch.ordered_values()
            ),
            ("First", "Second"),
        )

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            OcrResultBatch(
                {}  # type: ignore[arg-type]
            )

    def test_rejects_empty_batch(self) -> None:
        data = OcrResultBatchData(
            results={}
        )

        with self.assertRaises(ValueError):
            OcrResultBatch(data)

    def test_rejects_non_integer_key(self) -> None:
        data = OcrResultBatchData(
            results={
                "0": OcrResultData(text="Text"),  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            OcrResultBatch(data)

    def test_rejects_wrong_result_type(self) -> None:
        data = OcrResultBatchData(
            results={
                0: "Text",  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            OcrResultBatch(data)

    def test_rejects_invalid_result_data(self) -> None:
        data = OcrResultBatchData(
            results={
                0: OcrResultData(
                    text=42,  # type: ignore[arg-type]
                )
            }
        )

        with self.assertRaises(TypeError):
            OcrResultBatch(data)

    def test_accepts_empty_ocr_text(self) -> None:
        data = OcrResultBatchData(
            results={
                0: OcrResultData(text=""),
            }
        )

        batch = OcrResultBatch(data)

        self.assertEqual(
            batch.ordered_values()[0].text,
            "",
        )