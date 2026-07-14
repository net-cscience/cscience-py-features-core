import unittest
from pathlib import Path

from cscience.features.api.datatypes.references.file_path import (
    FilePath,
)


class TestFilePath(unittest.TestCase):
    def test_normalizes_string_to_path(self) -> None:
        file_path = FilePath("directory/file.txt")

        self.assertEqual(
            file_path.data(),
            Path("directory/file.txt"),
        )

    def test_accepts_path(self) -> None:
        source = Path("directory/file.txt")

        file_path = FilePath(source)

        self.assertEqual(file_path.data(), source)

    def test_rejects_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            FilePath("")