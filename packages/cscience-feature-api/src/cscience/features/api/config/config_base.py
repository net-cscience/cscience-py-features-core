from __future__ import annotations

import inspect
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
    """
    Base class for validated, namespace-addressable configurations.

    Each configuration instance defines its own namespace, persistence mode,
    and persistence path. No global initialization is required.

    Concrete subclasses define a default namespace through
    :meth:`_default_namespace`. The namespace can be overridden during
    construction::

        default_config = ClipConfig()
        alternative_config = ClipConfig(namespace="clip-large")

    The namespace identifies the configuration and determines:

    - the top-level key in unified configuration mode;
    - the filename in per-feature configuration mode;
    - the generated template and schema filenames;
    - configuration equality and hashing.

    Namespaces are immutable after construction.

    In ``ConfigMode.UNIFIED_CONFIG``, ``config_path`` refers to a single JSON
    file. Each configuration instance is stored under its namespace::

        {
            "clip": {
                "model_name": "ViT-B-32"
            },
            "clip-large": {
                "model_name": "ViT-L-14"
            }
        }

    When no path is supplied, ``configurations.json`` in the current working
    directory is used.

    In ``ConfigMode.CONFIG_PER_FEATURE``, ``config_path`` refers to a
    directory. Each configuration is stored as ``<namespace>.json`` within
    that directory.

    When no directory is supplied, the configuration is stored in the
    ``resources/config`` directory of the package containing the concrete
    configuration class.

    Templates and JSON schemas are generated automatically when a
    configuration is loaded or persisted, unless artifact generation is
    disabled during construction. They are stored in the package's
    ``resources/config`` directory.

    Artifact filenames are based on the runtime configuration filename. For
    example, ``clip-large.json`` produces::

        template_clip-large.json
        schema_clip-large.json

    :meth:`persist` writes the complete validated model state atomically.

    :meth:`load` validates the stored configuration and replaces the current
    model state in place. The namespace, mode, and persistence path remain
    unchanged. If parsing or validation fails, the current state remains
    unchanged.

    Package roots are located by searching upward from the file containing the
    concrete configuration class for a directory containing
    ``pyproject.toml`` and either ``src`` or ``tests``.
    """
    def __init__(
            self,
            *,
            namespace: str | None = None,
            mode: ConfigMode = ConfigMode.CONFIG_PER_FEATURE,
            config_path: str | pathlib.Path | None = None,
            generate_artifacts: bool = False,
            **data: Any,
    ) -> None:
        """
         Construct a configuration instance.

         Args:
             namespace:
                 Optional namespace override. The concrete class's default
                 namespace is used when omitted.
             mode:
                 Persistence mode for this instance.
             config_path:
                 A JSON file in unified mode or a directory in per-feature
                 mode.
             generate_artifacts:
                 Whether template and schema files should be generated when
                 this configuration is loaded or persisted.
             **data:
                 Values for the concrete Pydantic configuration model.
         """
        super().__init__(**data)

        selected_namespace = (
            type(self)._default_namespace()
            if namespace is None
            else namespace
        )

        self._namespace = self._validate_namespace(selected_namespace)
        self._mode = mode
        self._artifacts_enabled = generate_artifacts
        self._config_path = self._resolve_config_path(
            mode=mode,
            config_path=config_path,
        )

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    _namespace: str = PrivateAttr()
    _mode: ConfigMode = PrivateAttr()
    _config_path: pathlib.Path = PrivateAttr()
    _artifacts_enabled: bool = PrivateAttr()

    _unified_config_lock: ClassVar[RLock] = RLock()

    _package_root_override: ClassVar[pathlib.Path | None] = None

    _NAMESPACE_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9._-]*$"
    )

    _WINDOWS_RESERVED_NAMES: ClassVar[frozenset[str]] = frozenset(
        {"CON", "PRN", "AUX", "NUL"}
        | {f"COM{index}" for index in range(1, 10)}
        | {f"LPT{index}" for index in range(1, 10)}
    )



    def __setattr__(
        self,
        name: str,
        value: Any,
    ) -> None:
        """
        Prevent namespace mutation after construction.
        """
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
        """
        Return the namespace identifying this configuration.
        """
        return self._namespace

    @property
    def mode(self) -> ConfigMode:
        """
        Return the persistence mode of this configuration.
        """
        return self._mode

    @property
    def config_path(self) -> pathlib.Path:
        """
        Return the resolved runtime configuration file.
        """
        return self._config_path

    @property
    def config_filename(self) -> str:
        """
        Return the configuration filename derived from the namespace.
        """
        return f"{self.namespace}.json"

    def __eq__(self, other: object) -> bool:
        """
        Compare configurations by namespace.
        """
        if not isinstance(other, ConfigBase):
            return NotImplemented

        return self.namespace == other.namespace

    def __hash__(self) -> int:
        """
        Hash the immutable configuration namespace.
        """
        return hash(self.namespace)

    @classmethod
    def __pydantic_init_subclass__(
        cls,
        **kwargs: Any,
    ) -> None:
        """
        Validate the default namespace of concrete subclasses.
        """
        super().__pydantic_init_subclass__(**kwargs)

        if inspect.isabstract(cls):
            return

        cls._validate_namespace(
            cls._default_namespace()
        )

    @classmethod
    @abstractmethod
    def _default_namespace(cls) -> str:
        """
        Return the default namespace for this configuration type.
        """
        raise NotImplementedError

    @classmethod
    def _validate_namespace(
        cls,
        namespace: str,
    ) -> str:
        """
        Validate and normalize a filesystem-safe namespace.
        """
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
                "Namespaces must begin with an alphanumeric character "
                "and may contain only letters, numbers, periods, "
                "underscores, and hyphens."
            )

        if normalized.upper() in cls._WINDOWS_RESERVED_NAMES:
            raise ValueError(
                f"Configuration namespace {normalized!r} is reserved "
                "as a filename on Windows."
            )

        return normalized

    def _resolve_config_path(
        self,
        *,
        mode: ConfigMode,
        config_path: str | pathlib.Path | None,
    ) -> pathlib.Path:
        """
        Resolve the runtime configuration file for this instance.
        """
        match mode:
            case ConfigMode.UNIFIED_CONFIG:
                target = pathlib.Path(
                    config_path
                    if config_path is not None
                    else pathlib.Path.cwd()
                    / "configurations.json"
                ).expanduser().resolve()

                if target.exists() and target.is_dir():
                    raise ValueError(
                        "In UNIFIED_CONFIG mode, config_path must refer "
                        f"to a file, not a directory: {target}"
                    )

                return target

            case ConfigMode.CONFIG_PER_FEATURE:
                directory = pathlib.Path(
                    config_path
                    if config_path is not None
                    else type(self)._config_resources_directory()
                ).expanduser().resolve()

                if directory.exists() and not directory.is_dir():
                    raise ValueError(
                        "In CONFIG_PER_FEATURE mode, config_path must "
                        f"refer to a directory, not a file: {directory}"
                    )

                return directory / self.config_filename

            case _:
                raise ValueError(
                    f"Unknown config mode: {mode}"
                )

    @classmethod
    def _package_root(cls) -> pathlib.Path:
        """
        Return the package root containing the concrete config class.

        Supported layout::

            package-root/
            ├── pyproject.toml
            ├── src/
            │   └── ...
            └── tests/
                └── ...
        """
        if cls._package_root_override is not None:
            root = (
                cls._package_root_override
                .expanduser()
                .resolve()
            )

            if not root.is_dir():
                raise RuntimeError(
                    f"The package-root override does not exist: {root}"
                )

            return root

        source_file = pathlib.Path(
            inspect.getfile(cls)
        ).resolve()

        for candidate in source_file.parents:
            if not (
                candidate / "pyproject.toml"
            ).is_file():
                continue

            possible_source_roots = (
                candidate / "src",
                candidate / "tests",
            )

            belongs_to_candidate = any(
                root.is_dir()
                and source_file.is_relative_to(root)
                for root in possible_source_roots
            )

            if belongs_to_candidate:
                return candidate

        raise RuntimeError(
            f"Could not determine the package root for "
            f"{cls.__module__}.{cls.__qualname__}. "
            f"Searched upward from {source_file} for a directory "
            f"containing pyproject.toml and either src/ or tests/."
        )

    @classmethod
    def _config_resources_directory(cls) -> pathlib.Path:
        """
        Return the package's configuration resource directory.
        """
        return (
            cls._package_root()
            / "resources"
            / "config"
        )

    def _template_path(self) -> pathlib.Path:
        """
        Return the template path derived from the config filename.
        """
        return (
            type(self)._config_resources_directory()
            / f"template_{self.config_filename}"
        )

    def _schema_path(self) -> pathlib.Path:
        """
        Return the schema path derived from the config filename.
        """
        return (
            type(self)._config_resources_directory()
            / f"schema_{self.config_filename}"
        )

    def generate_config_artifacts(self) -> None:
        """
        Generate the default template and JSON schema for this namespace.

        The template contains the model's default values rather than the
        current instance values.
        """
        required_fields = [
            name
            for name, field in type(self).model_fields.items()
            if field.is_required()
        ]

        if required_fields:
            raise TypeError(
                f"Cannot generate a default template for "
                f"{type(self).__module__}.{type(self).__qualname__}. "
                f"The following fields have no default value: "
                f"{', '.join(required_fields)}."
            )

        default_config = type(self)(
            namespace=self.namespace,
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
        """
        Persist the complete current model state.
        """
        if self._artifacts_enabled:
            self.generate_config_artifacts()

        config_data = self.model_dump(
            mode="json",
            round_trip=True,
            exclude_computed_fields=True,
        )

        match self._mode:
            case ConfigMode.UNIFIED_CONFIG:
                self._persist_unified(
                    target=self._config_path,
                    config_data=config_data,
                )

            case ConfigMode.CONFIG_PER_FEATURE:
                self._write_json_atomic(
                    target=self._config_path,
                    data=config_data,
                )

            case _:
                raise ValueError(
                    f"Unknown config mode: {self._mode}"
                )

    def _persist_unified(
        self,
        *,
        target: pathlib.Path,
        config_data: dict[str, Any],
    ) -> None:
        """
        Replace this namespace in the unified configuration document.
        """
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
        """
        Load and validate this configuration in place.
        """
        if self._artifacts_enabled:
            self.generate_config_artifacts()

        match self._mode:
            case ConfigMode.UNIFIED_CONFIG:
                validated = self._load_unified(
                    self._config_path
                )

            case ConfigMode.CONFIG_PER_FEATURE:
                validated = type(self).model_validate_json(
                    self._config_path.read_bytes()
                )

            case _:
                raise ValueError(
                    f"Unknown config mode: {self._mode}"
                )

        self._replace_state(validated)
        return self

    def _load_unified(
        self,
        source: pathlib.Path,
    ) -> Self:
        """
        Load this namespace from a unified configuration document.
        """
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

        return type(self).model_validate(config_data)

    @staticmethod
    def _read_json_object(
        *,
        source: pathlib.Path,
        missing_ok: bool,
    ) -> dict[str, Any]:
        """
        Read a JSON document whose root must be an object.
        """
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
        """
        Write JSON through a temporary file and replace the target.
        """
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
        """
        Replace validated model fields while preserving instance metadata.
        """
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