from abc import ABC


class DataUrlBase(ABC):
    """Mixin for structured data URL references."""

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(
                f"{type(self).__name__} expects str, "
                f"got {type(data).__name__}."
            )

        if not data:
            raise ValueError(
                f"{type(self).__name__} cannot be empty."
            )

        if not data.startswith("data:"):
            raise ValueError(
                f"{type(self).__name__} must start with 'data:'."
            )

        if "," not in data:
            raise ValueError(
                f"{type(self).__name__} must contain a header "
                "and payload separated by ','."
            )

        super().__init__(data)

    def header(self) -> str:
        """Return the data URL header without the payload."""
        return self.data().split(",", 1)[0]  # type: ignore[attr-defined]

    def payload(self) -> str:
        """Return the encoded payload without decoding it."""
        return self.data().split(",", 1)[1]  # type: ignore[attr-defined]

    def media_type(self) -> str | None:
        """Return the declared media type, if present."""
        rest = self.header()[len("data:"):]

        if not rest:
            return None

        return rest.split(";", 1)[0] or None

    def is_base64(self) -> bool:
        """Return whether the data URL declares base64 encoding."""
        parameters = self.header().split(";")[1:]

        return "base64" in parameters