from __future__ import annotations

import json
import pathlib
import re
from abc import ABC, abstractmethod
from threading import RLock
from typing import Any, ClassVar, Self
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, PrivateAttr

from cscience.features.api.config.config_mode import ConfigMode


class ConfigBase(ABC, BaseModel):
    """Base class for validated, namespace-addressable configurations.

    Configuration storage must be configured explicitly.

    A default directory can be set once for all configurations:

        ConfigBase.set_default_config_directory("configs")

    In CONFIG_PER_FEATURE mode, configurations are stored as:

        <default-directory>/<namespace>.json

    In UNIFIED_CONFIG mode, configurations are stored as:

        <default-directory>/configurations.json

    An individual configuration can override the default location using
    config_path.

    In CONFIG_PER_FEATURE mode, config_path refers to a directory.

    In UNIFIED_CONFIG mode, config_path refers to a JSON file.

    No package-root or current-working-directory discovery is performed.
    Generated templates and schemas are stored beside the resolved runtime
    configuration file.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    _namespace: str = PrivateAttr()
    _mode: ConfigMode = PrivateAttr()
    _config_path: pathlib.Path = PrivateAttr()
    _artifacts_enabled: bool = PrivateAttr()

    _default_config_directory: ClassVar[
        pathlib.Path | None
    ] = None

    _unified_config_filename: ClassVar[str] = (
        "configurations.json"
    )

    _unified_config_lock: ClassVar[RLock] = RLock()

    _NAMESPACE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
    )

    _WINDOWS_RESERVED_NAMES: ClassVar[frozenset[str]] = (
        frozenset(
            {"CON", "PRN", "AUX", "NUL"}
            | {
                f"COM{index}"
                for index in range(1, 10)
            }
            | {
                f"LPT{index}"
                for index in range(1, 10)
            }
        )
    )

    def __init__(
        self,
        *,
        namespace: str | None = None,
        mode: ConfigMode = ConfigMode.CONFIG_PER_FEATURE,
        config_path: str | pathlib.Path | None = None,
        generate_artifacts: bool = False,
        **data: Any,
    ) -> None:
        """Construct a configuration instance.

        Args:
            namespace:
                Optional namespace override.
            mode:
                Unified-file or per-feature-file storage.
            config_path:
                Optional per-instance path override. This is a file in
                unified mode and a directory in per-feature mode.
            generate_artifacts:
                Whether template and schema files should be generated when
                loading or persisting.
            **data:
                Values for the concrete Pydantic model.
        """
        super().__init__(**data)

        selected_namespace = (
            type(self)._default_namespace()
            if namespace is None
            else namespace
        )

        self._namespace = self._validate_namespace(
            selected_namespace
        )
        self._mode = mode
        self._artifacts_enabled = generate_artifacts
        self._config_path = self._resolve_config_path(
            mode=mode,
            config_path=config_path,
        )

    @classmethod
    def set_default_config_directory(
        cls,
        path: str | pathlib.Path,
    ) -> None:
        """Set the default directory used by all configurations."""
        directory = pathlib.Path(
            path
        ).expanduser().resolve()

        if directory.exists() and not directory.is_dir():
            raise ValueError(
                "The default configuration path must refer "
                f"to a directory: {directory}"
            )

        ConfigBase._default_config_directory = directory

    @classmethod
    def clear_default_config_directory(cls) -> None:
        """Remove the globally configured default directory."""
        ConfigBase._default_config_directory = None

    @classmethod
    def default_config_directory(cls) -> pathlib.Path:
        """Return the explicitly configured default directory."""
        directory = ConfigBase._default_config_directory

        if directory is None:
            raise RuntimeError(
                "No default configuration directory has been set. "
                "Call ConfigBase.set_default_config_directory(...) "
                "or provide config_path when constructing the config."
            )

        return directory

    def __setattr__(
        self,
        name: str,
        value: Any,
    ) -> None:
        """Prevent namespace mutation after construction."""
        if name == "_namespace":
            private_attributes = getattr(
                self,
                "__pydantic_private__",
                None,
            )

            if (
                private_attributes is not None
                and "_namespace" in private_attributes
            ):
                raise AttributeError(
                    "The configuration namespace is immutable."
                )

        super().__setattr__(name, value)

    @property
    def namespace(self) -> str:
        """Return the configuration namespace."""
        return self._namespace

    @property
    def mode(self) -> ConfigMode:
        """Return the configuration persistence mode."""
        return self._mode

    @property
    def config_path(self) -> pathlib.Path:
        """Return the resolved runtime configuration file."""
        return self._config_path

    @property
    def config_filename(self) -> str:
        """Return the filename derived from the namespace."""
        return f"{self.namespace}.json"

    def __eq__(self, other: object) -> bool:
        """Compare configurations by namespace."""
        if not isinstance(other, ConfigBase):
            return NotImplemented

        return self.namespace == other.namespace

    def __hash__(self) -> int:
        """Hash the immutable configuration namespace."""
        return hash(self.namespace)

    @classmethod
    def __pydantic_init_subclass__(
        cls,
        **kwargs: Any,
    ) -> None:
        """Validate the default namespace of concrete subclasses."""
        super().__pydantic_init_subclass__(**kwargs)

        if getattr(cls, "__abstractmethods__", None):
            return

        cls._validate_namespace(
            cls._default_namespace()
        )

    @classmethod
    @abstractmethod
    def _default_namespace(cls) -> str:
        """Return the default namespace for this config type."""
        raise NotImplementedError

    @classmethod
    def _validate_namespace(
        cls,
        namespace: str,
    ) -> str:
        """Validate and normalize a filesystem-safe namespace."""
        if not isinstance(namespace, str):
            raise TypeError(
                "The configuration namespace must be a string."
            )

        normalized = namespace.strip()

        if not normalized:
            raise ValueError(
                "The configuration namespace must not be empty."
            )

        if not cls._NAMESPACE_PATTERN.fullmatch(normalized):
            raise ValueError(
                f"Invalid configuration namespace {namespace!r}. "
                "Namespaces must begin with an alphanumeric "
                "character and may contain only letters, numbers, "
                "periods, underscores, and hyphens."
            )

        if normalized.upper() in cls._WINDOWS_RESERVED_NAMES:
            raise ValueError(
                f"Configuration namespace {normalized!r} is "
                "reserved as a filename on Windows."
            )

        return normalized

    def _resolve_config_path(
        self,
        *,
        mode: ConfigMode,
        config_path: str | pathlib.Path | None,
    ) -> pathlib.Path:
        """Resolve the runtime configuration file."""
        match mode:
            case ConfigMode.UNIFIED_CONFIG:
                return self._resolve_unified_config_path(
                    config_path
                )

            case ConfigMode.CONFIG_PER_FEATURE:
                return self._resolve_per_feature_config_path(
                    config_path
                )

            case _:
                raise ValueError(
                    f"Unknown config mode: {mode}"
                )

    def _resolve_unified_config_path(
        self,
        config_path: str | pathlib.Path | None,
    ) -> pathlib.Path:
        """Resolve the unified JSON configuration file."""
        if config_path is None:
            target = (
                type(self).default_config_directory()
                / self._unified_config_filename
            )
        else:
            target = pathlib.Path(config_path)

        target = target.expanduser().resolve()

        if target.exists() and target.is_dir():
            raise ValueError(
                "In UNIFIED_CONFIG mode, config_path must "
                f"refer to a file, not a directory: {target}"
            )

        return target

    def _resolve_per_feature_config_path(
        self,
        config_path: str | pathlib.Path | None,
    ) -> pathlib.Path:
        """Resolve the per-feature JSON configuration file."""
        if config_path is None:
            directory = type(
                self
            ).default_config_directory()
        else:
            directory = pathlib.Path(config_path)

        directory = directory.expanduser().resolve()

        if directory.exists() and not directory.is_dir():
            raise ValueError(
                "In CONFIG_PER_FEATURE mode, config_path must "
                f"refer to a directory, not a file: {directory}"
            )

        return directory / self.config_filename

    def _config_path_argument(self) -> pathlib.Path:
        """Return config_path in constructor form."""
        if self.mode == ConfigMode.UNIFIED_CONFIG:
            return self.config_path

        return self.config_path.parent

    def _artifact_directory(self) -> pathlib.Path:
        """Return the explicit artifact output directory."""
        return self.config_path.parent

    def _template_path(self) -> pathlib.Path:
        """Return the generated template path."""
        return (
            self._artifact_directory()
            / f"template_{self.config_filename}"
        )

    def _schema_path(self) -> pathlib.Path:
        """Return the generated schema path."""
        return (
            self._artifact_directory()
            / f"schema_{self.config_filename}"
        )

    def generate_config_artifacts(self) -> None:
        """Generate the default template and JSON schema."""
        required_fields = [
            name
            for name, field in type(self).model_fields.items()
            if field.is_required()
        ]

        if required_fields:
            raise TypeError(
                f"Cannot generate a default template for "
                f"{type(self).__module__}."
                f"{type(self).__qualname__}. "
                "The following fields have no default value: "
                f"{', '.join(required_fields)}."
            )

        default_config = type(self)(
            namespace=self.namespace,
            mode=self.mode,
            config_path=self._config_path_argument(),
            generate_artifacts=False,
        )

        template = default_config.model_dump(
            mode="json",
            round_trip=True,
            exclude_computed_fields=True,
        )

        schema = type(self).model_json_schema(
            mode="validation",
        )

        self._write_json_atomic(
            target=self._template_path(),
            data=template,
        )
        self._write_json_atomic(
            target=self._schema_path(),
            data=schema,
        )

    def persist(self) -> None:
        """Persist the complete current model state."""
        if self._artifacts_enabled:
            self.generate_config_artifacts()

        config_data = self.model_dump(
            mode="json",
            round_trip=True,
            exclude_computed_fields=True,
        )

        match self.mode:
            case ConfigMode.UNIFIED_CONFIG:
                self._persist_unified(
                    target=self.config_path,
                    config_data=config_data,
                )

            case ConfigMode.CONFIG_PER_FEATURE:
                self._write_json_atomic(
                    target=self.config_path,
                    data=config_data,
                )

            case _:
                raise ValueError(
                    f"Unknown config mode: {self.mode}"
                )

    def _persist_unified(
        self,
        *,
        target: pathlib.Path,
        config_data: dict[str, Any],
    ) -> None:
        """Replace this namespace in the unified document."""
        with ConfigBase._unified_config_lock:
            document = self._read_json_object(
                source=target,
                missing_ok=True,
            )

            document[self.namespace] = config_data

            self._write_json_atomic(
                target=target,
                data=document,
            )

    def load(self) -> Self:
        """Load and validate this configuration in place."""
        if self._artifacts_enabled:
            self.generate_config_artifacts()

        match self.mode:
            case ConfigMode.UNIFIED_CONFIG:
                config_data = self._load_unified_data(
                    self.config_path
                )

            case ConfigMode.CONFIG_PER_FEATURE:
                config_data = self._read_json_object(
                    source=self.config_path,
                    missing_ok=False,
                )

            case _:
                raise ValueError(
                    f"Unknown config mode: {self.mode}"
                )

        validated = self._validate_config_data(
            config_data
        )

        self._replace_state(validated)
        return self

    def _load_unified_data(
        self,
        source: pathlib.Path,
    ) -> dict[str, Any]:
        """Load this namespace from a unified document."""
        document = self._read_json_object(
            source=source,
            missing_ok=False,
        )

        if self.namespace not in document:
            raise KeyError(
                f"Configuration namespace {self.namespace!r} "
                f"was not found in {source}."
            )

        config_data = document[self.namespace]

        if not isinstance(config_data, dict):
            raise TypeError(
                f"Configuration namespace {self.namespace!r} "
                f"in {source} must contain a JSON object."
            )

        return config_data

    def _validate_config_data(
        self,
        config_data: dict[str, Any],
    ) -> Self:
        """Construct a validated config using current metadata."""
        return type(self)(
            namespace=self.namespace,
            mode=self.mode,
            config_path=self._config_path_argument(),
            generate_artifacts=False,
            **config_data,
        )

    @staticmethod
    def _read_json_object(
        *,
        source: pathlib.Path,
        missing_ok: bool,
    ) -> dict[str, Any]:
        """Read a JSON document whose root must be an object."""
        if not source.exists():
            if missing_ok:
                return {}

            raise FileNotFoundError(source)

        try:
            data = json.loads(
                source.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON configuration file: {source}"
            ) from error

        if not isinstance(data, dict):
            raise TypeError(
                f"The root of {source} must be a JSON object."
            )

        return data

    @staticmethod
    def _write_json_atomic(
        *,
        target: pathlib.Path,
        data: Any,
    ) -> None:
        """Write JSON atomically."""
        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        json_data = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ) + "\n"

        temporary = target.with_name(
            f".{target.name}.{uuid4().hex}.tmp"
        )

        try:
            temporary.write_text(
                json_data,
                encoding="utf-8",
            )
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)

    def _replace_state(
        self,
        validated: Self,
    ) -> None:
        """Replace model fields while preserving config metadata."""
        if type(validated) is not type(self):
            raise TypeError(
                f"Cannot load {type(validated).__name__} "
                f"into {type(self).__name__}."
            )

        self.__dict__.clear()
        self.__dict__.update(validated.__dict__)

        object.__setattr__(
            self,
            "__pydantic_fields_set__",
            validated.__pydantic_fields_set__.copy(),
        )

        extra = validated.__pydantic_extra__

        object.__setattr__(
            self,
            "__pydantic_extra__",
            None if extra is None else extra.copy(),
        )