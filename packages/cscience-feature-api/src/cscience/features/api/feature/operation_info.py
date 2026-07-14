from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OperationInfo:
    parameters: tuple[str, ...]
    return_type: str
    description: str

    @property
    def signature(self) -> str:
        parameters = ", ".join(self.parameters)
        return f"{parameters} -> {self.return_type}"