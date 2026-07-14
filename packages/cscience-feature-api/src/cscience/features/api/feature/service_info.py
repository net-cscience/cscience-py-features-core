from __future__ import annotations

import inspect
import types
from dataclasses import dataclass
from typing import (
    Any,
    ClassVar,
    Self,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from cscience.features.api.feature.operation_info import OperationInfo


@dataclass(frozen=True, slots=True)
class ServiceInfo:
    identifier: str
    name: str
    description: str
    operations: dict[str, OperationInfo]

    _EXCLUDED_OPERATIONS: ClassVar[frozenset[str]] = frozenset(
        {
            "get_feature_info",
            "get_service_info",
        }
    )

    @classmethod
    def from_connector(
        cls,
        *,
        connector_type: type,
        identifier: str,
        name: str,
        description: str,
    ) -> Self:
        return cls(
            identifier=identifier,
            name=name,
            description=description,
            operations=cls.generate_operations(connector_type),
        )

    @classmethod
    def generate_operations(
        cls,
        connector_type: type,
    ) -> dict[str, OperationInfo]:
        operations: dict[str, OperationInfo] = {}

        for name, member in connector_type.__dict__.items():
            if name.startswith("_") or name in cls._EXCLUDED_OPERATIONS:
                continue

            if not inspect.isfunction(member):
                continue

            hints = get_type_hints(member)
            signature = inspect.signature(member)

            parameters = tuple(
                cls._format_type(
                    hints.get(parameter.name, Any)
                )
                for parameter in signature.parameters.values()
                if parameter.name not in {"self", "cls"}
            )

            return_type = cls._format_type(
                hints.get("return", Any)
            )

            operations[name] = OperationInfo(
                parameters=parameters,
                return_type=return_type,
                description=inspect.getdoc(member) or "",
            )

        return operations

    @classmethod
    def _format_type(
        cls,
        annotation: object,
    ) -> str:
        if annotation is Any:
            return "Any"

        if annotation is None or annotation is type(None):
            return "None"

        origin = get_origin(annotation)
        arguments = get_args(annotation)

        if origin in {types.UnionType, Union}:
            return " | ".join(
                cls._format_type(argument)
                for argument in arguments
            )

        if origin is not None:
            name = getattr(
                origin,
                "__name__",
                str(origin).removeprefix("typing."),
            )

            if not arguments:
                return name

            formatted_arguments = ", ".join(
                cls._format_type(argument)
                for argument in arguments
            )

            return f"{name}[{formatted_arguments}]"

        if isinstance(annotation, type):
            return annotation.__name__

        return str(annotation).removeprefix("typing.")