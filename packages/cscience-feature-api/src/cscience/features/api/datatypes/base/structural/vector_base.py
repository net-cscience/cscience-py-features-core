from abc import ABC
from collections.abc import Sized


class VectorBase(ABC):
    """Mixin for datatypes containing one vector."""

    def length(self) -> int:
        """Return the vector dimension."""
        data = self.data()  # type: ignore[attr-defined]

        if not isinstance(data, Sized):
            raise TypeError(
                f"Cannot infer vector length from {type(data).__name__}."
            )

        return len(data)

    def assert_length(self, expected: int) -> None:
        """Raise if the vector dimension does not match the expected value."""
        actual = self.length()

        if actual != expected:
            raise ValueError(
                f"Expected vector length {expected}, got {actual}."
            )