from __future__ import annotations

import inspect
import json
import pathlib
from abc import ABC, abstractmethod
from threading import RLock
from typing import Any, ClassVar, Self
from uuid import uuid4

from pydantic import BaseModel, ConfigDict

from cscience.features.api.config.config_mode import ConfigMode


class ConfigBase(BaseModel, ABC):
    """
    Base class for validated and persistable feature configurations.

    The configuration system must be initialized exactly once through
    :meth:`ConfigBase.initialize` before any configuration is loaded or
    persisted. The selected storage mode applies globally to all subclasses and
    cannot be changed per configuration type or instance.

    Two storage modes are supported:

    `ConfigMode.UNIFIED_CONFIG`
    All configurations are stored in a single JSON file. Each concrete
    configuration occupies one top-level object identified by its namespace.

    Example::

        {
            "api": {
                "host": "localhost",
                "port": 8080
            },
            "clip": {
                "model_name": "ViT-B-32"
            }
        }

    In this mode, ``config_path`` passed to :meth:`initialize` refers to the
    unified JSON file. When omitted, ``configurations.json`` in the current
    working directory is used.


    `ConfigMode.CONFIG_PER_FEATURE`
    Each configuration is stored in a separate JSON file named after its
    namespace, for example `api.json` or `clip.json`.


    When ``config_path`` is provided, it must refer to a directory in which
    all configuration files are stored.

    When ``config_path`` is omitted, each configuration is stored in the
    ``resources/config`` directory of the package containing its concrete
    configuration class.

    Concrete subclasses must implement :meth:`_namespace` and return a unique,
    filesystem-safe namespace. The namespace is used both as the top-level key in
    a unified configuration and as the filename in per-feature mode.

    :meth:`persist` serializes the complete validated model state and writes it
    atomically. In unified mode, only the current namespace is replaced; all other
    configuration sections are preserved.

    :meth:`load` reads the applicable configuration, validates it using the
    concrete Pydantic model, and replaces the current instance state in place.
    The existing instance remains unchanged when parsing or validation fails.

    Concrete configuration classes are registered automatically. During explicit
    system initialization, JSON templates and schemas may be generated for all
    registered configuration classes. These artifacts are written to the
    `resources/config` directory of the package containing the concrete class.

    Package roots are determined from the file defining the concrete
    configuration class by searching upward for a directory containing
    `pyproject.toml` and either `src` or `tests`.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )



    _mode: ClassVar[ConfigMode | None] = None

    # Used only in UNIFIED_CONFIG mode.
    _unified_config_path: ClassVar[pathlib.Path | None] = None

    # Optional common directory used in CONFIG_PER_FEATURE mode.
    # When None, each package uses its own resources/config directory.
    _per_feature_config_directory: ClassVar[pathlib.Path | None] = None

    _initialized: ClassVar[bool] = False

    # Concrete configuration classes register themselves here.
    _registered_config_types: ClassVar[set[type[ConfigBase]]] = set()

    # Protects initialization and unified read-modify-write operations
    # within the current process.
    _initialization_lock: ClassVar[RLock] = RLock()
    _unified_config_lock: ClassVar[RLock] = RLock()

    # May be overridden on a concrete class for tests or non-standard
    # package layouts.
    _package_root_override: ClassVar[pathlib.Path | None] = None

    # Test-only or auxiliary config classes can disable artifact generation.
    _generate_artifacts: ClassVar[bool] = True

    @classmethod
    def __pydantic_init_subclass__(
        cls,
        **kwargs: Any,
    ) -> None:
        """
        Register concrete configuration classes after Pydantic has finished
        constructing them.
        """
        super().__pydantic_init_subclass__(**kwargs)

        if inspect.isabstract(cls):
            return

        ConfigBase._registered_config_types.add(cls)

        # Handles config classes imported after system initialization.
        if (
            ConfigBase._initialized
            and cls._generate_artifacts
        ):
            cls.generate_config_artifacts()

    @classmethod
    def initialize(
            cls,
            *,
            mode: ConfigMode,
            config_path: str | pathlib.Path | None = None,
            generate_artifacts: bool = True,
    ) -> None:
        """
        Initialize the complete configuration system.

        Path semantics depend on the selected mode:

        - UNIFIED_CONFIG:
          `config_path` is the unified JSON file. If omitted,
          `./configurations.json` is used.

        - CONFIG_PER_FEATURE:
          `config_path` is an optional directory. Each configuration is
          stored as `<namespace>.json` in this directory. If omitted, each
          feature package uses its own `resources/config` directory.

        Repeated initialization with identical arguments is allowed.
        Reinitialization with different arguments is rejected.
        """
        if cls is not ConfigBase:
            raise TypeError(
                "The configuration system must be initialized through "
                "ConfigBase.initialize(), not through a subclass."
            )

        resolved_unified_path: pathlib.Path | None = None
        resolved_per_feature_directory: pathlib.Path | None = None

        match mode:
            case ConfigMode.UNIFIED_CONFIG:
                resolved_unified_path = pathlib.Path(
                    config_path
                    if config_path is not None
                    else pathlib.Path.cwd() / "configurations.json"
                ).expanduser().resolve()

                if (
                        resolved_unified_path.exists()
                        and resolved_unified_path.is_dir()
                ):
                    raise ValueError(
                        "In UNIFIED_CONFIG mode, config_path must refer "
                        f"to a JSON file, not a directory: "
                        f"{resolved_unified_path}"
                    )

            case ConfigMode.CONFIG_PER_FEATURE:
                if config_path is not None:
                    resolved_per_feature_directory = pathlib.Path(
                        config_path
                    ).expanduser().resolve()

                    if (
                            resolved_per_feature_directory.exists()
                            and not resolved_per_feature_directory.is_dir()
                    ):
                        raise ValueError(
                            "In CONFIG_PER_FEATURE mode, config_path must "
                            f"refer to a directory, not a file: "
                            f"{resolved_per_feature_directory}"
                        )

            case _:
                raise ValueError(
                    f"Unknown config mode: {mode}"
                )

        with ConfigBase._initialization_lock:
            if ConfigBase._initialized:
                same_configuration = (
                        ConfigBase._mode == mode
                        and ConfigBase._unified_config_path
                        == resolved_unified_path
                        and ConfigBase._per_feature_config_directory
                        == resolved_per_feature_directory
                )

                if not same_configuration:
                    raise RuntimeError(
                        "ConfigBase has already been initialized with "
                        "different configuration-system settings."
                    )

                return

            ConfigBase._mode = mode
            ConfigBase._unified_config_path = resolved_unified_path
            ConfigBase._per_feature_config_directory = (
                resolved_per_feature_directory
            )
            ConfigBase._initialized = True

        if generate_artifacts:
            ConfigBase.generate_all_config_artifacts()

    @classmethod
    def generate_all_config_artifacts(cls) -> None:
        """
        Generate templates and schemas for all imported config classes.
        """
        if cls is not ConfigBase:
            raise TypeError(
                "Generate all artifacts through "
                "ConfigBase.generate_all_config_artifacts()."
            )

        config_types = sorted(
            ConfigBase._registered_config_types,
            key=lambda config_type: (
                config_type.__module__,
                config_type.__qualname__,
            ),
        )

        for config_type in config_types:
            if config_type._generate_artifacts:
                config_type.generate_config_artifacts()

    @classmethod
    def generate_config_artifacts(cls) -> None:
        """
        Generate the default template and JSON schema for this config class.
        """
        if cls is ConfigBase or inspect.isabstract(cls):
            raise TypeError(
                "Artifacts can only be generated for a concrete "
                "configuration class."
            )

        required_fields = [
            name
            for name, field in cls.model_fields.items()
            if field.is_required()
        ]

        if required_fields:
            raise TypeError(
                f"Cannot generate a default template for "
                f"{cls.__module__}.{cls.__qualname__}. "
                f"The following fields have no default value: "
                f"{', '.join(required_fields)}."
            )

        # Creating a real instance evaluates default factories and validates
        # the resulting default configuration.
        default_config = cls()

        template = default_config.model_dump(
            mode="json",
            round_trip=True,
            exclude_computed_fields=True,
        )

        schema = cls.model_json_schema(
            mode="validation",
        )

        cls._write_json_atomic(
            target=cls._template_path(),
            data=template,
        )

        cls._write_json_atomic(
            target=cls._schema_path(),
            data=schema,
        )

    @classmethod
    def _require_initialization(cls) -> ConfigMode:
        """
        Return the global mode or fail when the system is uninitialized.
        """
        if (
            not ConfigBase._initialized
            or ConfigBase._mode is None
        ):
            raise RuntimeError(
                "The configuration system has not been initialized. "
                "Call ConfigBase.initialize(...) before loading or "
                "persisting configurations."
            )

        return ConfigBase._mode

    @classmethod
    def _config_path(cls) -> pathlib.Path:
        """
        Return the runtime configuration file for this config class.
        """
        mode = cls._require_initialization()

        match mode:
            case ConfigMode.UNIFIED_CONFIG:
                path = ConfigBase._unified_config_path

                if path is None:
                    raise RuntimeError(
                        "The unified configuration path is not initialized."
                    )

                return path

            case ConfigMode.CONFIG_PER_FEATURE:
                directory = (
                    ConfigBase._per_feature_config_directory
                    if ConfigBase._per_feature_config_directory is not None
                    else cls._config_resources_directory()
                )

                return directory / cls._config_filename()

            case _:
                raise ValueError(
                    f"Unknown config mode: {mode}"
                )

    @classmethod
    def _config_filename(cls) -> str:
        """
        Return the configuration filename derived from the namespace.
        """
        namespace = cls.namespace().strip()

        if not namespace:
            raise ValueError(
                f"{cls.__qualname__} returned an empty configuration namespace."
            )

        if namespace in {".", ".."}:
            raise ValueError(
                f"Invalid configuration namespace: {namespace!r}."
            )

        if "/" in namespace or "\\" in namespace:
            raise ValueError(
                f"Configuration namespace {namespace!r} must not contain "
                "path separators."
            )

        return f"{namespace}.json"

    @classmethod
    def _package_root(cls) -> pathlib.Path:
        """
        Find the package root containing the concrete config class.

        Supported package layout:

            package-root/
            ├── pyproject.toml
            ├── src/
            │   └── ...
            └── tests/
                └── ...
        """
        if cls._package_root_override is not None:
            root = cls._package_root_override.resolve()

            if not root.is_dir():
                raise RuntimeError(
                    f"The package-root override does not exist: {root}"
                )

            return root

        source_file = pathlib.Path(
            inspect.getfile(cls)
        ).resolve()

        for candidate in source_file.parents:
            if not (candidate / "pyproject.toml").is_file():
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
        Return the feature package's configuration resource directory.
        """
        return (
            cls._package_root()
            / "resources"
            / "config"
        )

    @classmethod
    def _template_path(cls) -> pathlib.Path:
        return (
            cls._config_resources_directory()
            / f"template_{cls.namespace()}.json"
        )

    @classmethod
    def _schema_path(cls) -> pathlib.Path:
        return (
            cls._config_resources_directory()
            / f"schema_{cls.namespace()}.json"
        )

    @classmethod
    @abstractmethod
    def namespace(cls) -> str:
        """
        Return the unique namespace used in unified configuration files.
        """
        raise NotImplementedError

    def persist(self) -> None:
        """
        Persist the complete current model state.
        """
        target = type(self)._config_path()

        config_data = self.model_dump(
            mode="json",
            round_trip=True,
            exclude_computed_fields=True,
        )

        mode = type(self)._require_initialization()

        match mode:
            case ConfigMode.UNIFIED_CONFIG:
                self._persist_unified(
                    target=target,
                    config_data=config_data,
                )

            case ConfigMode.CONFIG_PER_FEATURE:
                self._write_json_atomic(
                    target=target,
                    data=config_data,
                )

            case _:
                raise ValueError(
                    f"Unknown config mode: {mode}"
                )

    def _persist_unified(
        self,
        *,
        target: pathlib.Path,
        config_data: dict[str, Any],
    ) -> None:
        """
        Replace only this config's section in the unified document.
        """
        namespace = type(self).namespace()

        with ConfigBase._unified_config_lock:
            document = self._read_json_object(
                source=target,
                missing_ok=True,
            )

            document[namespace] = config_data

            self._write_json_atomic(
                target=target,
                data=document,
            )

    def load(self) -> Self:
        """
        Load and validate this configuration in place.
        """
        source = type(self)._config_path()
        mode = type(self)._require_initialization()

        match mode:
            case ConfigMode.UNIFIED_CONFIG:
                validated = self._load_unified(source)

            case ConfigMode.CONFIG_PER_FEATURE:
                validated = type(self).model_validate_json(
                    source.read_bytes()
                )

            case _:
                raise ValueError(
                    f"Unknown config mode: {mode}"
                )

        self._replace_state(validated)
        return self

    def _load_unified(
        self,
        source: pathlib.Path,
    ) -> Self:
        """
        Load and validate this config's section from the unified file.
        """
        document = self._read_json_object(
            source=source,
            missing_ok=False,
        )

        namespace = type(self).namespace()

        if namespace not in document:
            raise KeyError(
                f"Configuration namespace {namespace!r} "
                f"was not found in {source}."
            )

        config_data = document[namespace]

        if not isinstance(config_data, dict):
            raise TypeError(
                f"Configuration namespace {namespace!r} "
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
        Write JSON through a temporary file and atomically replace the target.
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
        Replace the validated model state in place.
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