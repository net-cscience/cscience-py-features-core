from pathlib import Path

from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class FilePath(CoreDatatype[Path]):
    """Filesystem path reference.

    FilePath stores a path-like reference. It does not open, read, or validate
    the file contents.
    """

    def __init__(self, data: str | Path) -> None:
        if not isinstance(data, str | Path):
            raise TypeError(f"FilePath expects str or Path, got {type(data).__name__}.")

        path = Path(data)

        if not str(path):
            raise ValueError("FilePath cannot be empty.")

        super().__init__(path)

    def exists(self) -> bool:
        """Return whether the referenced path currently exists."""
        return self.data().exists()

    def is_file(self) -> bool:
        """Return whether the referenced path currently points to a file."""
        return self.data().is_file()

    def suffix(self) -> str:
        """Return the file suffix."""
        return self.data().suffix

    def name(self) -> str:
        """Return the final path component."""
        return self.data().name