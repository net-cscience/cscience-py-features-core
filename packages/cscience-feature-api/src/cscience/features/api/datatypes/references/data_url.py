from cscience.features.api.datatypes.base.core_datatype import CoreDatatype


class DataUrl(CoreDatatype[str]):
    """Generic data URL reference.

    A DataUrl stores a string such as:

        data:image/png;base64,...

    It does not decode the payload. Decoding belongs to converters.
    """

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(f"DataUrl expects str, got {type(data).__name__}.")

        if not data:
            raise ValueError("DataUrl cannot be empty.")

        if not data.startswith("data:"):
            raise ValueError("DataUrl must start with 'data:'.")

        if "," not in data:
            raise ValueError("DataUrl must contain a header and payload separated by ','.")

        super().__init__(data)

    def header(self) -> str:
        """Return the data URL header without the payload."""
        return self.data().split(",", 1)[0]

    def payload(self) -> str:
        """Return the encoded payload part without decoding it."""
        return self.data().split(",", 1)[1]

    def media_type(self) -> str | None:
        """Return the declared media type, if present."""
        header = self.header()

        # Examples:
        # data:image/png;base64
        # data:text/plain;charset=utf-8
        prefix = "data:"
        if not header.startswith(prefix):
            return None

        rest = header[len(prefix):]
        if not rest:
            return None

        return rest.split(";", 1)[0] or None

    def is_base64(self) -> bool:
        """Return whether the data URL declares base64 encoding."""
        return ";base64" in self.header()