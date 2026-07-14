# Exported code on 2026-07-14 18:51:50.984618 with root dir D:\myRepo\net.cscience\cscience-py-features-core\packages
# From cscience-feature-api\src\cscience\features\api\__init__.py
# Config
from .config.config_base import ConfigBase

# Connectors
from .connector.connector_base import ConnectorBase
from .connector.function_connector import FunctionConnector

# Conversions
from .conversion.conversion_provider_base import ConversionProviderBase
from .conversion.converter import Converter
from .conversion.search_strategy_base import SearchStrategyBase
from .conversion.search_strategy_most_specific import SearchStrategyMostSpecific

# Datatype conversion provider
from cscience.features.api.conversion.core_conversion_provider import CoreConversionProvider

# Datatype base classes
from cscience.features.api.datatypes.base.media.audio_bytes_base import AudioBytesBase
from cscience.features.api.datatypes.base.structural.batch_base import BatchBase
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype
from .datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.embedding_base import EmbeddingBase
from cscience.features.api.datatypes.base.media.image_bytes_base import ImageBytesBase
from cscience.features.api.datatypes.base.media.media_bytes_base import MediaBytesBase
from cscience.features.api.datatypes.base.structural.vector_base import VectorBase
from cscience.features.api.datatypes.base.structural.vector_batch_base import VectorBatchBase

# Datatype references
from .datatypes.references.data_url import DataUrl
from .datatypes.references.file_path import FilePath

# Spa
from .datatypes.spatial.spatial_batch_layout import SpatialBatchLayout
from .datatypes.spatial.spatial_region import SpatialRegion
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import SpatialVectorBatchData
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_base import SpatialVectorBatchBase
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import SpatialPrimitiveVectorBatchBase
from .datatypes.spatial.spatial_float_vector_batch import SpatialFloatVectorBatch

# Text datatypes
from .datatypes.text.text import Text
from .datatypes.text.text_batch import TextBatch

# Image datatypes
from .datatypes.image.image_bytes import ImageBytes
from .datatypes.image.image_data_url import ImageDataUrl
from .datatypes.image.pil_image import PilImage
from .datatypes.image.pil_image_batch import PilImageBatch

# Audio datatypes
from .datatypes.audio.audio_bytes import AudioBytes
from .datatypes.audio.audio_signal import AudioSignal, AudioSignalData

# Scalar primitive datatypes
from .datatypes.primitives_scalar.bool_value import BoolValue
from .datatypes.primitives_scalar.float_value import FloatValue
from .datatypes.primitives_scalar.int_value import IntValue

# Primitive vector datatypes
from .datatypes.primitives_vectors.bool_vector import BoolVector
from cscience.features.api.datatypes.primitives_vectors_batch.bool_vector_batch import BoolVectorBatch
from .datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import FloatVectorBatch
from .datatypes.primitives_vectors.int_vector import IntVector
from cscience.features.api.datatypes.primitives_vectors_batch.int_vector_batch import IntVectorBatch
from cscience.features.api.datatypes.base.structural.primitive_vector_base import PrimitiveVectorBase
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import PrimitiveVectorBatchBase

# Features
from .feature.feature_base import FeatureBase
from .feature.feature_info import FeatureInfo
from .feature.service_info import ServiceInfo

# Registry
from .registry.conversion_registry import ConversionRegistry
from .registry.registry_base import RegistryBase

# Utils
from .utils.measure_time import measure_time


__all__ = [
    # Config
    "ConfigBase",

    # Connectors
    "ConnectorBase",
    "FunctionConnector",

    # Conversions
    "ConversionProviderBase",
    "Converter",
    "SearchStrategyBase",
    "SearchStrategyMostSpecific",

    # Datatype conversion provider
    "CoreConversionProvider",

    # Datatype base classes
    "AudioBytesBase",
    "BatchBase",
    "CoreDatatype",
    "DatatypeBase",
    "EmbeddingBase",
    "ImageBytesBase",
    "MediaBytesBase",
    "VectorBase",
    "VectorBatchBase",

    # Datatype references
    "DataUrl",
    "FilePath",

    # Spatial datatypes
    "SpatialBatchLayout",
    "SpatialRegion",
    "SpatialVectorBatchData",
    "SpatialVectorBatchBase",
    "SpatialPrimitiveVectorBatchBase",
    "SpatialFloatVectorBatch",

    # Text datatypes
    "Text",
    "TextBatch",

    # Image datatypes
    "ImageBytes",
    "ImageDataUrl",
    "PilImage",
    "PilImageBatch",

    # Audio datatypes
    # "AudioBytes",
    # "AudioSignal",
    # "AudioSignalData",

    # Scalar primitive datatypes
    "BoolValue",
    "FloatValue",
    "IntValue",

    # Primitive vector datatypes
    "BoolVector",
    "BoolVectorBatch",
    "FloatVector",
    "FloatVectorBatch",
    "IntVector",
    "IntVectorBatch",
    "PrimitiveVectorBase",
    #"PrimitiveVectorBatchBase",

    # Features
    "FeatureBase",
    "FeatureInfo",
    "ServiceInfo",

    # Registry
    "ConversionRegistry",
    "RegistryBase",

    # Utils
    "measure_time",
]

# From cscience-feature-api\src\cscience\features\api\config\config_base.py
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

# From cscience-feature-api\src\cscience\features\api\config\config_mode.py
from mypy.nodes import Enum




# config_mode.py

from enum import StrEnum


class ConfigMode(StrEnum):
    UNIFIED_CONFIG = "unified"
    CONFIG_PER_FEATURE = "per-feature"

# From cscience-feature-api\src\cscience\features\api\config\core_config.py
from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class CoreConfig(ConfigBase):


    @classmethod
    def _default_namespace(cls) -> str:
        return "core"

    model_name:str = Field(
        default="Config for empty core model",
        description="The core model is used for registering core converters."
    )



# From cscience-feature-api\src\cscience\features\api\connector\connector_base.py
from abc import ABC, abstractmethod

from ..config.core_config import CoreConfig
from ..conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.core_conversion_provider import CoreConversionProvider
from ..feature.core_feature import CoreFeature
from ..feature.feature_info import FeatureInfo
from ..feature.service_info import ServiceInfo
from ..registry.conversion_registry import ConversionRegistry


class ConnectorBase(ABC):
    """Base class for public feature connectors.

    A connector registers core conversions and feature-specific conversions,
    then exposes convenient methods using normal Python input and output types.
    """

    def __init__(self, conversion_provider: ConversionProviderBase):
        """Register core conversions and the connector's feature conversions."""
        core_conversion_provider = CoreConversionProvider(CoreFeature.get_instance(CoreConfig(), init_if_missing=True))
        ConversionRegistry.register(core_conversion_provider)
        ConversionRegistry.register(conversion_provider)

    @abstractmethod
    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_service_info(cls) -> ServiceInfo:
        raise NotImplementedError

# From cscience-feature-api\src\cscience\features\api\connector\function_connector.py
from typing import TypeVar, Generic, Callable

from ..conversion.conversion_key import ConversionKey
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..conversion.search_strategy_most_specific import SearchStrategyMostSpecific
from ..datatypes.base.datatype_base import DatatypeBase

from ..feature.feature_base import FeatureBase
from ..registry.conversion_registry import ConversionRegistry

Tin = TypeVar('Tin', bound=DatatypeBase)
Tfi = TypeVar('Tfi', bound=DatatypeBase)
Tfo = TypeVar('Tfo', bound=DatatypeBase)
Tout = TypeVar('Tout', bound=DatatypeBase)


class FunctionConnector(Generic[Tin, Tfi, Tfo, Tout]):
    """Wrap a feature function with input and output conversions.

    The connector resolves one converter from public input type to feature input
    type and one converter from feature output type to public output type.
    """
    def __init__(self, feature: FeatureBase, function: Callable[[Tfi], Tfo],
                 input_type: type[DatatypeBase],
                 input_feature_type: type[DatatypeBase],
                 output_feature_type: type[DatatypeBase],
                 output_type: type[DatatypeBase],
                 ) -> None:
        strategy_in: SearchStrategyBase = SearchStrategyMostSpecific(ConversionKey(type(feature), input_type, input_feature_type))
        strategy_out: SearchStrategyBase = SearchStrategyMostSpecific(ConversionKey(type(feature), output_feature_type, output_type))
        self.inner: Converter[Tin, Tfi] = ConversionRegistry.get_best_effort_converter(strategy_in)
        self.outer: Converter[Tfo, Tout] = ConversionRegistry.get_best_effort_converter(strategy_out)
        self.function = function
        self.wrapped = lambda x: self.outer(function(self.inner(x)))

    def __call__(self, x: Tin) -> Tout:
        """Run input conversion, feature function, and output conversion."""
        return self.wrapped(x)


# From cscience-feature-api\src\cscience\features\api\conversion\conversion_key.py
from ..datatypes.base.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase



from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ConversionKey:
    """Dictionary key identifying a registered datatype conversion.

    A conversion is scoped by feature class and by source/target datatype.
    Core conversions use `CoreFeature` as their source and may be used as
    fallback conversions by search strategies.
    """

    source: type[FeatureBase]
    input_type: type[DatatypeBase]
    output_type: type[DatatypeBase]

# From cscience-feature-api\src\cscience\features\api\conversion\conversion_provider_base.py
from abc import ABC, abstractmethod
from typing import List

from .converter import Converter
from ..feature.feature_base import FeatureBase


class ConversionProviderBase(ABC):
    """Base class for groups of converters belonging to one feature."""

    def __init__(self, feature: FeatureBase) -> None:
        self._feature = feature

    @abstractmethod
    def register_converters(self) -> List[Converter]:
        """Return all converters provided by this feature or provider."""
        raise NotImplementedError("Subclasses must implement register_converters()")


# From cscience-feature-api\src\cscience\features\api\conversion\converter.py
from typing import Callable, Generic, TypeVar

from .conversion_key import ConversionKey
from ..datatypes.base.datatype_base import DatatypeBase
from ..feature.feature_base import FeatureBase

Tin = TypeVar('Tin', bound=DatatypeBase, contravariant=True)
Tout = TypeVar('Tout', bound=DatatypeBase, covariant=True)


class Converter(Generic[Tin, Tout]):
    """Callable conversion from one datatype into another datatype."""
    def __init__(self, name: str, source: FeatureBase,
                 function: Callable[[Tin], Tout],
                 input_type: type[DatatypeBase],
                 output_type: type[DatatypeBase]) -> None:
        self._name: str = name
        self._source: FeatureBase = source
        self._function: Callable[[Tin], Tout] = function
        self._input_type: type[DatatypeBase] = input_type
        self._output_type: type[DatatypeBase] = output_type

    def __call__(self, data: Tin) -> Tout:
        """Convert one datatype instance into another datatype instance."""
        return self._function(data)

    def get_identifier(self) -> ConversionKey:
        """Return the registry key under which this converter is stored."""
        return ConversionKey(type(self._source), self._input_type, self._output_type)


# From cscience-feature-api\src\cscience\features\api\conversion\core_conversion_provider.py
import base64
from io import BytesIO
from typing import List
from urllib.parse import unquote

from PIL import Image as PillowImage

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.image.image_bytes import ImageBytes
from cscience.features.api.datatypes.image.image_data_url import ImageDataUrl
from cscience.features.api.datatypes.image.pil_image import PilImage
from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.primitives_scalar.bool_value import BoolValue
from cscience.features.api.datatypes.primitives_scalar.float_value import FloatValue
from cscience.features.api.datatypes.primitives_scalar.int_value import IntValue
from cscience.features.api.datatypes.primitives_vectors.bool_vector import BoolVector
from cscience.features.api.datatypes.primitives_vectors_batch.bool_vector_batch import BoolVectorBatch
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.primitives_vectors.int_vector import IntVector
from cscience.features.api.datatypes.primitives_vectors_batch.int_vector_batch import IntVectorBatch
from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase


# ---------------------------------------------------------------------------
# Text conversions
# ---------------------------------------------------------------------------

def text_passthrough(text: Text) -> Text:
    return text


def text_to_text_batch(text: Text) -> TextBatch:
    return TextBatch({0: text.data()})


def text_batch_passthrough(batch: TextBatch) -> TextBatch:
    return batch


# ---------------------------------------------------------------------------
# Scalar primitive conversions
# ---------------------------------------------------------------------------

def bool_value_passthrough(value: BoolValue) -> BoolValue:
    return value


def int_value_passthrough(value: IntValue) -> IntValue:
    return value


def float_value_passthrough(value: FloatValue) -> FloatValue:
    return value


def bool_value_to_int_value(value: BoolValue) -> IntValue:
    return IntValue(1 if value.data() else 0)


def bool_value_to_float_value(value: BoolValue) -> FloatValue:
    return FloatValue(1.0 if value.data() else 0.0)


def int_value_to_float_value(value: IntValue) -> FloatValue:
    return FloatValue(float(value.data()))


# ---------------------------------------------------------------------------
# Primitive vector conversions
# ---------------------------------------------------------------------------

def bool_vector_passthrough(vector: BoolVector) -> BoolVector:
    return vector


def int_vector_passthrough(vector: IntVector) -> IntVector:
    return vector


def float_vector_passthrough(vector: FloatVector) -> FloatVector:
    return vector


def bool_vector_to_bool_vector_batch(vector: BoolVector) -> BoolVectorBatch:
    return BoolVectorBatch({0: vector.data()})


def int_vector_to_int_vector_batch(vector: IntVector) -> IntVectorBatch:
    return IntVectorBatch({0: vector.data()})


def float_vector_to_float_vector_batch(vector: FloatVector) -> FloatVectorBatch:
    return FloatVectorBatch({0: vector.data()})


def bool_vector_to_int_vector(vector: BoolVector) -> IntVector:
    return IntVector([1 if value else 0 for value in vector.data()])


def bool_vector_to_float_vector(vector: BoolVector) -> FloatVector:
    return FloatVector([1.0 if value else 0.0 for value in vector.data()])


def int_vector_to_float_vector(vector: IntVector) -> FloatVector:
    return FloatVector([float(value) for value in vector.data()])


# ---------------------------------------------------------------------------
# Primitive vector batch conversions
# ---------------------------------------------------------------------------

def bool_vector_batch_passthrough(batch: BoolVectorBatch) -> BoolVectorBatch:
    return batch


def int_vector_batch_passthrough(batch: IntVectorBatch) -> IntVectorBatch:
    return batch


def float_vector_batch_passthrough(batch: FloatVectorBatch) -> FloatVectorBatch:
    return batch


def bool_vector_batch_to_int_vector_batch(batch: BoolVectorBatch) -> IntVectorBatch:
    return IntVectorBatch(
        {
            key: [1 if value else 0 for value in vector]
            for key, vector in batch.data().items()
        }
    )


def bool_vector_batch_to_float_vector_batch(batch: BoolVectorBatch) -> FloatVectorBatch:
    return FloatVectorBatch(
        {
            key: [1.0 if value else 0.0 for value in vector]
            for key, vector in batch.data().items()
        }
    )


def int_vector_batch_to_float_vector_batch(batch: IntVectorBatch) -> FloatVectorBatch:
    return FloatVectorBatch(
        {
            key: [float(value) for value in vector]
            for key, vector in batch.data().items()
        }
    )


# ---------------------------------------------------------------------------
# Image conversions
# ---------------------------------------------------------------------------

def image_data_url_passthrough(data_url: ImageDataUrl) -> ImageDataUrl:
    return data_url


def image_bytes_passthrough(image_bytes: ImageBytes) -> ImageBytes:
    return image_bytes


def pil_image_passthrough(image: PilImage) -> PilImage:
    return image


def pil_image_batch_passthrough(batch: PilImageBatch) -> PilImageBatch:
    return batch


def image_data_url_to_image_bytes(data_url: ImageDataUrl) -> ImageBytes:
    data = unquote(data_url.data())

    if "base64," not in data:
        raise ValueError("Missing or invalid base64 image data URL.")

    header, encoded = data.split("base64,", 1)

    if header and not header.startswith("data:image/"):
        raise ValueError(f"Expected image data URL, got header: {header}")

    return ImageBytes(base64.b64decode(encoded, validate=True))


def image_bytes_to_pil_image(image_bytes: ImageBytes) -> PilImage:
    image = PillowImage.open(BytesIO(image_bytes.data()))
    image.load()
    return PilImage(image)


def pil_image_to_pil_image_batch(image: PilImage) -> PilImageBatch:
    return PilImageBatch({0: image.data()})


class CoreConversionProvider(ConversionProviderBase):
    """Registers feature-independent core conversions."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        return [
            # -----------------------------------------------------------------
            # Text
            # -----------------------------------------------------------------
            Converter[Text, Text](
                name="text_passthrough",
                source=self._feature,
                function=text_passthrough,
                input_type=Text,
                output_type=Text,
            ),
            Converter[Text, TextBatch](
                name="text_to_text_batch",
                source=self._feature,
                function=text_to_text_batch,
                input_type=Text,
                output_type=TextBatch,
            ),
            Converter[TextBatch, TextBatch](
                name="text_batch_passthrough",
                source=self._feature,
                function=text_batch_passthrough,
                input_type=TextBatch,
                output_type=TextBatch,
            ),

            # -----------------------------------------------------------------
            # Scalar primitives
            # -----------------------------------------------------------------
            Converter[BoolValue, BoolValue](
                name="bool_value_passthrough",
                source=self._feature,
                function=bool_value_passthrough,
                input_type=BoolValue,
                output_type=BoolValue,
            ),
            Converter[IntValue, IntValue](
                name="int_value_passthrough",
                source=self._feature,
                function=int_value_passthrough,
                input_type=IntValue,
                output_type=IntValue,
            ),
            Converter[FloatValue, FloatValue](
                name="float_value_passthrough",
                source=self._feature,
                function=float_value_passthrough,
                input_type=FloatValue,
                output_type=FloatValue,
            ),
            Converter[BoolValue, IntValue](
                name="bool_value_to_int_value",
                source=self._feature,
                function=bool_value_to_int_value,
                input_type=BoolValue,
                output_type=IntValue,
            ),
            Converter[BoolValue, FloatValue](
                name="bool_value_to_float_value",
                source=self._feature,
                function=bool_value_to_float_value,
                input_type=BoolValue,
                output_type=FloatValue,
            ),
            Converter[IntValue, FloatValue](
                name="int_value_to_float_value",
                source=self._feature,
                function=int_value_to_float_value,
                input_type=IntValue,
                output_type=FloatValue,
            ),

            # -----------------------------------------------------------------
            # Primitive vectors
            # -----------------------------------------------------------------
            Converter[BoolVector, BoolVector](
                name="bool_vector_passthrough",
                source=self._feature,
                function=bool_vector_passthrough,
                input_type=BoolVector,
                output_type=BoolVector,
            ),
            Converter[IntVector, IntVector](
                name="int_vector_passthrough",
                source=self._feature,
                function=int_vector_passthrough,
                input_type=IntVector,
                output_type=IntVector,
            ),
            Converter[FloatVector, FloatVector](
                name="float_vector_passthrough",
                source=self._feature,
                function=float_vector_passthrough,
                input_type=FloatVector,
                output_type=FloatVector,
            ),
            Converter[BoolVector, BoolVectorBatch](
                name="bool_vector_to_bool_vector_batch",
                source=self._feature,
                function=bool_vector_to_bool_vector_batch,
                input_type=BoolVector,
                output_type=BoolVectorBatch,
            ),
            Converter[IntVector, IntVectorBatch](
                name="int_vector_to_int_vector_batch",
                source=self._feature,
                function=int_vector_to_int_vector_batch,
                input_type=IntVector,
                output_type=IntVectorBatch,
            ),
            Converter[FloatVector, FloatVectorBatch](
                name="float_vector_to_float_vector_batch",
                source=self._feature,
                function=float_vector_to_float_vector_batch,
                input_type=FloatVector,
                output_type=FloatVectorBatch,
            ),
            Converter[BoolVector, IntVector](
                name="bool_vector_to_int_vector",
                source=self._feature,
                function=bool_vector_to_int_vector,
                input_type=BoolVector,
                output_type=IntVector,
            ),
            Converter[BoolVector, FloatVector](
                name="bool_vector_to_float_vector",
                source=self._feature,
                function=bool_vector_to_float_vector,
                input_type=BoolVector,
                output_type=FloatVector,
            ),
            Converter[IntVector, FloatVector](
                name="int_vector_to_float_vector",
                source=self._feature,
                function=int_vector_to_float_vector,
                input_type=IntVector,
                output_type=FloatVector,
            ),

            # -----------------------------------------------------------------
            # Primitive vector batches
            # -----------------------------------------------------------------
            Converter[BoolVectorBatch, BoolVectorBatch](
                name="bool_vector_batch_passthrough",
                source=self._feature,
                function=bool_vector_batch_passthrough,
                input_type=BoolVectorBatch,
                output_type=BoolVectorBatch,
            ),
            Converter[IntVectorBatch, IntVectorBatch](
                name="int_vector_batch_passthrough",
                source=self._feature,
                function=int_vector_batch_passthrough,
                input_type=IntVectorBatch,
                output_type=IntVectorBatch,
            ),
            Converter[FloatVectorBatch, FloatVectorBatch](
                name="float_vector_batch_passthrough",
                source=self._feature,
                function=float_vector_batch_passthrough,
                input_type=FloatVectorBatch,
                output_type=FloatVectorBatch,
            ),
            Converter[BoolVectorBatch, IntVectorBatch](
                name="bool_vector_batch_to_int_vector_batch",
                source=self._feature,
                function=bool_vector_batch_to_int_vector_batch,
                input_type=BoolVectorBatch,
                output_type=IntVectorBatch,
            ),
            Converter[BoolVectorBatch, FloatVectorBatch](
                name="bool_vector_batch_to_float_vector_batch",
                source=self._feature,
                function=bool_vector_batch_to_float_vector_batch,
                input_type=BoolVectorBatch,
                output_type=FloatVectorBatch,
            ),
            Converter[IntVectorBatch, FloatVectorBatch](
                name="int_vector_batch_to_float_vector_batch",
                source=self._feature,
                function=int_vector_batch_to_float_vector_batch,
                input_type=IntVectorBatch,
                output_type=FloatVectorBatch,
            ),

            # -----------------------------------------------------------------
            # Images
            # -----------------------------------------------------------------
            Converter[ImageDataUrl, ImageDataUrl](
                name="image_data_url_passthrough",
                source=self._feature,
                function=image_data_url_passthrough,
                input_type=ImageDataUrl,
                output_type=ImageDataUrl,
            ),
            Converter[ImageBytes, ImageBytes](
                name="image_bytes_passthrough",
                source=self._feature,
                function=image_bytes_passthrough,
                input_type=ImageBytes,
                output_type=ImageBytes,
            ),
            Converter[PilImage, PilImage](
                name="pil_image_passthrough",
                source=self._feature,
                function=pil_image_passthrough,
                input_type=PilImage,
                output_type=PilImage,
            ),
            Converter[PilImageBatch, PilImageBatch](
                name="pil_image_batch_passthrough",
                source=self._feature,
                function=pil_image_batch_passthrough,
                input_type=PilImageBatch,
                output_type=PilImageBatch,
            ),
            Converter[ImageDataUrl, ImageBytes](
                name="image_data_url_to_image_bytes",
                source=self._feature,
                function=image_data_url_to_image_bytes,
                input_type=ImageDataUrl,
                output_type=ImageBytes,
            ),
            Converter[ImageBytes, PilImage](
                name="image_bytes_to_pil_image",
                source=self._feature,
                function=image_bytes_to_pil_image,
                input_type=ImageBytes,
                output_type=PilImage,
            ),
            Converter[PilImage, PilImageBatch](
                name="pil_image_to_pil_image_batch",
                source=self._feature,
                function=pil_image_to_pil_image_batch,
                input_type=PilImage,
                output_type=PilImageBatch,
            ),
        ]

# From cscience-feature-api\src\cscience\features\api\conversion\search_strategy_base.py


from abc import ABC, abstractmethod

from .conversion_key import ConversionKey
from .converter import Converter


class SearchStrategyBase(ABC):
    """Base class for converter lookup strategies."""
    def __init__(self, conversion_key: ConversionKey) -> None:
        self._conversion_key = conversion_key


    @abstractmethod
    def search(self, recordset: dict[ConversionKey, Converter]) -> Converter:
        """Find a converter in the given registry recordset."""
        raise NotImplementedError("Subclasses must implement search")


    def __str__(self) -> str:
        return str(self._conversion_key)


# From cscience-feature-api\src\cscience\features\api\conversion\search_strategy_most_specific.py
from .conversion_key import ConversionKey
from .converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..feature.core_feature import CoreFeature


class SearchStrategyMostSpecific(SearchStrategyBase):
    """Resolve a converter by exact feature key, then by core fallback key."""
    def __init__(self, conversion_key: ConversionKey):
        super().__init__(conversion_key)

    def search(self,
               recordset: dict[ConversionKey, Converter]) -> Converter:
        """Return the best matching converter or raise `LookupError`."""

        key: ConversionKey = self._conversion_key
        key_core: ConversionKey = ConversionKey(CoreFeature, key.input_type, key.output_type)


        try:
            return recordset[key]
        except KeyError:
            try:
                return recordset[key_core]
            except KeyError:
                raise LookupError(
                    f"No converter found for {self._conversion_key}"
                )

# From cscience-feature-api\src\cscience\features\api\datatypes\audio\audio_bytes.py
from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class AudioBytes(
    AudioBytesBase,
    CoreDatatype[bytes],
):
    """Encoded audio bytes."""

# From cscience-feature-api\src\cscience\features\api\datatypes\audio\audio_signal.py
import numpy as np

from cscience.features.api.datatypes.audio.audio_signal_data import (
    AudioSignalData,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class AudioSignal(CoreDatatype[AudioSignalData]):
    """Decoded audio signal."""

    def __init__(self, data: AudioSignalData) -> None:
        if not isinstance(data, AudioSignalData):
            raise TypeError(
                f"AudioSignal expects AudioSignalData, "
                f"got {type(data).__name__}."
            )

        waveform = data.waveform

        if not isinstance(waveform, np.ndarray):
            raise TypeError(
                f"AudioSignal waveform expects np.ndarray, "
                f"got {type(waveform).__name__}."
            )

        if waveform.ndim not in {1, 2}:
            raise ValueError(
                "AudioSignal waveform must be 1D or 2D, "
                f"got shape {waveform.shape}."
            )

        if waveform.size == 0:
            raise ValueError(
                "AudioSignal waveform cannot be empty."
            )

        if not (
            np.issubdtype(waveform.dtype, np.integer)
            or np.issubdtype(waveform.dtype, np.floating)
        ):
            raise TypeError(
                "AudioSignal waveform must have an integer or "
                f"floating-point dtype, got {waveform.dtype}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, "
                f"got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate <= 0:
            raise ValueError(
                "AudioSignal sample_rate must be positive."
            )

        super().__init__(data)

# From cscience-feature-api\src\cscience\features\api\datatypes\audio\audio_signal_data.py
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Decoded audio signal with an explicit sample rate."""

    waveform: np.ndarray
    sample_rate: int



# From cscience-feature-api\src\cscience\features\api\datatypes\base\datatype_base.py
from abc import ABC
from typing import Generic, TypeVar
import icontract

T = TypeVar("T")



@icontract.invariant(lambda self: self._data is not None, "Data cannot be None.")
class DatatypeBase(ABC, Generic[T]):
    """Base class for all semantic feature datatypes.

    A datatype wraps a raw Python value and attaches semantic meaning to it.
    Conversion and connector logic should use datatype classes rather than raw
    Python types at feature boundaries.
    """

    def __init__(self, data: T) -> None:
        self._data = data

    def data(self) -> T:
        """Return the wrapped raw value."""
        return self._data

    @staticmethod
    def fullname(o: object) -> str:
        """Return the fully qualified class name of an object."""
        module = o.__class__.__module__

        if module is None or module == str.__class__.__module__:
            return o.__class__.__name__

        return module + "." + o.__class__.__name__

# From cscience-feature-api\src\cscience\features\api\datatypes\base\media\audio_bytes_base.py
from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)


class AudioBytesBase(MediaBytesBase):
    """Mixin for encoded audio bytes."""

    media_type = "audio"

# From cscience-feature-api\src\cscience\features\api\datatypes\base\media\image_bytes_base.py
from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)


class ImageBytesBase(MediaBytesBase):
    """Mixin for encoded image bytes."""

    media_type = "image"

# From cscience-feature-api\src\cscience\features\api\datatypes\base\media\media_bytes_base.py
from abc import ABC


class MediaBytesBase(ABC):
    """Mixin for non-empty encoded media bytes."""

    media_type = "media"

    def __init__(self, data: bytes) -> None:
        if type(data) is not bytes:
            raise TypeError(
                f"{type(self).__name__} expects bytes, "
                f"got {type(data).__name__}."
            )

        if not data:
            raise ValueError(
                f"{type(self).__name__} cannot be empty."
            )

        super().__init__(data)

# From cscience-feature-api\src\cscience\features\api\datatypes\base\references\data_url_base.py
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

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\batch_base.py
from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar, cast

T = TypeVar("T")


class BatchBase(ABC, Generic[T]):
    """Mixin for indexed batch datatypes.

    Guarantee:
    - batch data is a non-empty mapping
    - keys are integer source indices
    - values are batch elements
    - ordered methods use ascending source-index order
    """

    def _batch_mapping(self) -> Mapping[int, T]:
        """Return the indexed elements represented by this batch."""
        return cast(Mapping[int, T], self.data())  # type: ignore[attr-defined]

    def _validate_batch_mapping(self, data: Mapping[int, T]) -> None:
        if not data:
            raise ValueError(f"{type(self).__name__} cannot be empty.")

        for key in data:
            if type(key) is not int:
                raise TypeError(
                    f"{type(self).__name__} keys must be int, "
                    f"got {type(key).__name__}."
                )

    def batch_size(self) -> int:
        """Return the number of batch elements."""
        return len(self._batch_mapping())

    def ordered_keys(self) -> tuple[int, ...]:
        """Return source indices in canonical batch order."""
        return tuple(sorted(self._batch_mapping()))

    def ordered_values(self) -> tuple[T, ...]:
        """Return values in canonical batch order."""
        data = self._batch_mapping()
        return tuple(data[key] for key in self.ordered_keys())

    def ordered_items(self) -> tuple[tuple[int, T], ...]:
        """Return items in canonical batch order."""
        data = self._batch_mapping()
        return tuple((key, data[key]) for key in self.ordered_keys())

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\embedding_base.py
from abc import ABC, abstractmethod


class EmbeddingBase(ABC):
    """Mixin for datatypes containing semantic embeddings."""

    @abstractmethod
    def length(self) -> int:
        """Return the shared embedding dimension."""

    def embedding_dim(self) -> int:
        """Return the shared embedding dimension."""
        return self.length()

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\primitive_vector_base.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)

T = TypeVar("T")


class PrimitiveVectorBase(VectorBase, ABC, Generic[T]):
    """Mixin for non-empty list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: list[T],
        assert_length: int | None = None,
    ) -> None:
        if type(data) is not list:
            raise TypeError(
                f"{type(self).__name__} expects list, "
                f"got {type(data).__name__}."
            )

        if not data:
            raise ValueError(
                f"{type(self).__name__} cannot be empty."
            )

        for index, value in enumerate(data):
            if type(value) is not self.element_type:
                raise TypeError(
                    f"{type(self).__name__} expects "
                    f"{self.element_type.__name__}, "
                    f"got {type(value).__name__} at index {index}."
                )

        super().__init__(data)

        if assert_length is not None:
            self.assert_length(assert_length)

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\primitive_vector_batch_base.py
from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)

T = TypeVar("T")


class PrimitiveVectorBatchBase(
    VectorBatchBase[list[T]],
    ABC,
    Generic[T],
):
    """Mixin for batches of non-empty list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: Mapping[int, list[T]],
        assert_length: int | None = None,
    ) -> None:
        self._validate_vector_batch_mapping(data)

        for key, vector in data.items():
            if type(vector) is not list:
                raise TypeError(
                    f"{type(self).__name__} expects list vectors, "
                    f"got {type(vector).__name__} at key {key}."
                )

            for index, value in enumerate(vector):
                if type(value) is not self.element_type:
                    raise TypeError(
                        f"{type(self).__name__} expects "
                        f"{self.element_type.__name__}, "
                        f"got {type(value).__name__} "
                        f"at key {key}, index {index}."
                    )

        super().__init__(dict(data))

        if assert_length is not None:
            self.assert_length(assert_length)

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\spatial_primitive_vector_batch_base.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.structural.spatial_vector_batch_base import (
    SpatialVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)

T = TypeVar("T")


class SpatialPrimitiveVectorBatchBase(
    SpatialVectorBatchBase[list[T]],
    ABC,
    Generic[T],
):
    """Mixin for spatial batches of list-backed primitive vectors."""

    element_type: type

    def __init__(
        self,
        data: SpatialVectorBatchData[list[T]],
        assert_length: int | None = None,
    ) -> None:
        super().__init__(
            data,
            assert_length=assert_length,
        )

        for key, vector in self._batch_mapping().items():
            if type(vector) is not list:
                raise TypeError(
                    f"{type(self).__name__} expects list vectors, "
                    f"got {type(vector).__name__} at key {key}."
                )

            for index, value in enumerate(vector):
                if type(value) is not self.element_type:
                    raise TypeError(
                        f"{type(self).__name__} expects "
                        f"{self.element_type.__name__}, "
                        f"got {type(value).__name__} "
                        f"at key {key}, index {index}."
                    )

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\spatial_vector_batch_base.py
from abc import ABC
from collections.abc import Mapping
from typing import Generic, TypeVar

import icontract

from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)
from cscience.features.api.datatypes.spatial.spatial_batch_layout import (
    SpatialBatchLayout,
)
from cscience.features.api.datatypes.spatial.spatial_region import (
    SpatialRegion,
)

V = TypeVar("V")


class SpatialVectorBatchBase(
    VectorBatchBase[V],
    ABC,
    Generic[V],
):
    """Mixin for spatially structured vector batches.

    Physical structure:
        dict[int, vector]

    Logical structure:
        [item_count, regions_per_item, vector_dim]
    """

    def __init__(
        self,
        data: SpatialVectorBatchData[V],
        assert_length: int | None = None,
    ) -> None:
        if not isinstance(data, SpatialVectorBatchData):
            raise TypeError(
                f"{type(self).__name__} expects SpatialVectorBatchData, "
                f"got {type(data).__name__}."
            )

        self._validate_spatial_structure(data)
        self._validate_vector_batch_mapping(data.vectors)

        normalized = SpatialVectorBatchData(
            vectors=dict(data.vectors),
            layout=data.layout,
            item_keys=tuple(data.item_keys),
            regions=tuple(data.regions),
        )

        super().__init__(normalized)

        if assert_length is not None:
            self.assert_length(assert_length)

    @staticmethod
    @icontract.require(
        lambda data: len(data.vectors) == data.layout.flat_count,
        description=(
            "Spatial vector count must match layout.flat_count."
        ),
    )
    @icontract.require(
        lambda data: set(data.vectors) == set(
            range(data.layout.flat_count)
        ),
        description=(
            "Spatial vector keys must be contiguous flat indices "
            "0..layout.flat_count-1."
        ),
    )
    @icontract.require(
        lambda data: len(data.item_keys) == data.layout.item_count,
        description=(
            "Item key count must match layout.item_count."
        ),
    )
    @icontract.require(
        lambda data: len(set(data.item_keys)) == len(data.item_keys),
        description="Item keys must be unique.",
    )
    @icontract.require(
        lambda data: all(
            type(item_key) is int
            for item_key in data.item_keys
        ),
        description="Item keys must be integers.",
    )
    @icontract.require(
        lambda data: (
            len(data.regions)
            == data.layout.regions_per_item
        ),
        description=(
            "Region count must match layout.regions_per_item."
        ),
    )
    @icontract.require(
        lambda data: all(
            region.index == index
            for index, region in enumerate(data.regions)
        ),
        description=(
            "Region indices must match their tuple positions."
        ),
    )
    def _validate_spatial_structure(
        data: SpatialVectorBatchData[V],
    ) -> None:
        """Validate relationships between spatial data fields."""

    def _batch_mapping(self) -> Mapping[int, V]:
        """Return flat vectors indexed by flat spatial index."""
        return self.data().vectors

    @property
    def vectors(self) -> dict[int, V]:
        """Return flat vectors indexed by flat spatial index."""
        return dict(self.data().vectors)

    @property
    def layout(self) -> SpatialBatchLayout:
        """Return the spatial batch layout."""
        return self.data().layout

    @property
    def item_keys(self) -> tuple[int, ...]:
        """Return source keys in structured item order."""
        return self.data().item_keys

    @property
    def regions(self) -> tuple[SpatialRegion, ...]:
        """Return the regions used for every item."""
        return self.data().regions

    def item_count(self) -> int:
        """Return the number of structured source items."""
        return self.layout.item_count

    def regions_per_item(self) -> int:
        """Return the number of regions per source item."""
        return self.layout.regions_per_item

    def to_flat_index(
        self,
        item_index: int,
        region_index: int,
    ) -> int:
        """Return the flat index for an item-region pair."""
        return self.layout.to_flat_index(
            item_index,
            region_index,
        )

    def from_flat_index(
        self,
        flat_index: int,
    ) -> tuple[int, int]:
        """Return the item and region indices for a flat index."""
        return self.layout.from_flat_index(flat_index)

    def region_for_flat_index(
        self,
        flat_index: int,
    ) -> SpatialRegion:
        """Return the region metadata for a flat index."""
        _, region_index = self.from_flat_index(flat_index)

        return self.regions[region_index]

    def vector_at(
        self,
        item_index: int,
        region_index: int,
    ) -> V:
        """Return the vector for an item-region pair."""
        flat_index = self.to_flat_index(
            item_index,
            region_index,
        )

        return self._batch_mapping()[flat_index]

    def item_vectors(
        self,
        item_index: int,
    ) -> tuple[V, ...]:
        """Return all region vectors for one structured item."""
        return tuple(
            self.vector_at(item_index, region_index)
            for region_index in range(
                self.layout.regions_per_item
            )
        )

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\spatial_vector_batch_data.py
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Generic, TypeVar

from cscience.features.api.datatypes.spatial.spatial_batch_layout import SpatialBatchLayout
from cscience.features.api.datatypes.spatial.spatial_region import SpatialRegion

V = TypeVar("V")


@dataclass(frozen=True, slots=True)
class SpatialVectorBatchData(Generic[V]):
    """Spatially structured vector batch data.

    The vectors are stored flat:

        vectors[flat_index] -> vector

    The layout reconstructs the logical structure:

        flat_index <-> (item_index, region_index)
    """

    vectors: Mapping[int, V]
    layout: SpatialBatchLayout
    item_keys: tuple[int, ...]
    regions: tuple[SpatialRegion, ...]

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\vector_base.py
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

# From cscience-feature-api\src\cscience\features\api\datatypes\base\structural\vector_batch_base.py
from abc import ABC
from collections.abc import Mapping, Sized
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.structural.batch_base import BatchBase

V = TypeVar("V")


class VectorBatchBase(BatchBase[V], ABC, Generic[V]):
    """Mixin for indexed batches of equally sized vectors."""

    def _validate_vector_batch_mapping(
        self,
        data: Mapping[int, V],
    ) -> None:
        self._validate_batch_mapping(data)

        lengths: set[int] = set()

        for key, vector in data.items():
            if not isinstance(vector, Sized):
                raise TypeError(
                    f"Vector at key {key} must be sized, "
                    f"got {type(vector).__name__}."
                )

            vector_length = len(vector)

            if vector_length == 0:
                raise ValueError(
                    f"Vector at key {key} cannot be empty."
                )

            lengths.add(vector_length)

        if len(lengths) != 1:
            raise ValueError(
                f"Inconsistent vector lengths: {sorted(lengths)}."
            )

    def length(self) -> int:
        """Return the shared vector dimension."""
        first_key = self.ordered_keys()[0]
        return len(self._batch_mapping()[first_key])

    def assert_length(self, expected: int) -> None:
        """Raise if the shared vector dimension does not match the expected value."""
        actual = self.length()

        if actual != expected:
            raise ValueError(
                f"Expected vector length {expected}, got {actual}."
            )

# From cscience-feature-api\src\cscience\features\api\datatypes\core\core_datatype.py


from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase

T = TypeVar("T")


class CoreDatatype(DatatypeBase[T], ABC, Generic[T]):
    """Namespace base for feature-independent core datatypes."""

    namespace = "core"

# From cscience-feature-api\src\cscience\features\api\datatypes\image\image_bytes.py
from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class ImageBytes(
    ImageBytesBase,
    CoreDatatype[bytes],
):
    """Encoded image bytes."""

# From cscience-feature-api\src\cscience\features\api\datatypes\image\image_data_url.py
from cscience.features.api.datatypes.references.data_url import DataUrl


class ImageDataUrl(DataUrl):
    """Base64-encoded image data URL."""

    def __init__(self, data: str) -> None:
        super().__init__(data)

        media_type = self.media_type()

        if media_type is None or not media_type.startswith("image/"):
            raise ValueError(
                "ImageDataUrl must declare an image media type."
            )

        if not self.is_base64():
            raise ValueError(
                "ImageDataUrl must declare base64 encoding."
            )

# From cscience-feature-api\src\cscience\features\api\datatypes\image\pil_image.py
from PIL.Image import Image

from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class PilImage(CoreDatatype[Image]):
    """Decoded Pillow image."""

    def __init__(self, data: Image) -> None:
        if not isinstance(data, Image):
            raise TypeError(f"PilImage expects PIL image, got {type(data).__name__}.")

        super().__init__(data)

# From cscience-feature-api\src\cscience\features\api\datatypes\image\pil_image_batch.py
from collections.abc import Mapping

from PIL.Image import Image

from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class PilImageBatch(
    BatchBase[Image],
    CoreDatatype[dict[int, Image]],
):
    """Batch of Pillow images indexed by source position."""

    def __init__(self, data: Mapping[int, Image]) -> None:
        self._validate_batch_mapping(data)

        for key, value in data.items():
            if not isinstance(value, Image):
                raise TypeError(
                    f"PilImageBatch expects PIL images, "
                    f"got {type(value).__name__} at key {key}."
                )

        super().__init__(dict(data))

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_scalar\bool_value.py
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class BoolValue(CoreDatatype[bool]):
    """Single boolean value."""

    def __init__(self, data: bool) -> None:
        if type(data) is not bool:
            raise TypeError(f"BoolValue expects bool, got {type(data).__name__}.")
        super().__init__(data)

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_scalar\float_value.py
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class FloatValue(CoreDatatype[float]):
    """Single floating-point value."""

    def __init__(self, data: float) -> None:
        if type(data) is not float:
            raise TypeError(f"FloatValue expects float, got {type(data).__name__}.")

        super().__init__(data)

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_scalar\int_value.py
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class IntValue(CoreDatatype[int]):
    """Single integer value."""

    def __init__(self, data: int) -> None:
        if type(data) is not int:
            raise TypeError(f"IntValue expects int, got {type(data).__name__}.")
        super().__init__(data)

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\bool_vector.py
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class BoolVector(
    PrimitiveVectorBase[bool],
    CoreDatatype[list[bool]],
):
    """Single boolean vector."""

    element_type = bool

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\float_vector.py
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class FloatVector(
    PrimitiveVectorBase[float],
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    """Single float embedding vector."""

    element_type = float

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors\int_vector.py
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class IntVector(
    PrimitiveVectorBase[int],
    CoreDatatype[list[int]],
):
    """Single integer vector."""

    element_type = int

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors_batch\bool_vector_batch.py
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class BoolVectorBatch(
    PrimitiveVectorBatchBase[bool],
    CoreDatatype[dict[int, list[bool]]],
):
    """Batch of boolean vectors indexed by source position."""

    element_type = bool

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors_batch\float_vector_batch.py
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class FloatVectorBatch(
    PrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[dict[int, list[float]]],
):
    """Batch of float embedding vectors indexed by source position."""

    element_type = float

# From cscience-feature-api\src\cscience\features\api\datatypes\primitives_vectors_batch\int_vector_batch.py
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class IntVectorBatch(
    PrimitiveVectorBatchBase[int],
    CoreDatatype[dict[int, list[int]]],
):
    """Batch of integer vectors indexed by source position."""

    element_type = int

# From cscience-feature-api\src\cscience\features\api\datatypes\references\data_url.py
from cscience.features.api.datatypes.base.references.data_url_base import DataUrlBase
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class DataUrl(
    DataUrlBase,
    CoreDatatype[str],
):
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
        parameters = self.header().split(";")[1:]

        return "base64" in parameters

# From cscience-feature-api\src\cscience\features\api\datatypes\references\file_path.py
from pathlib import Path

from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class FilePath(CoreDatatype[Path]):
    """Filesystem path reference.

    FilePath stores a path-like reference. It does not open, read, or validate
    the file contents.
    """

    def __init__(self, data: str | Path) -> None:
        if not isinstance(data, str | Path):
            raise TypeError(
                f"FilePath expects str or Path, "
                f"got {type(data).__name__}."
            )

        if isinstance(data, str) and data == "":
            raise ValueError("FilePath cannot be empty.")

        super().__init__(Path(data))

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

# From cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_batch_layout.py
from dataclasses import dataclass

import icontract

from cscience.features.api.datatypes.spatial.spatial_region import SpatialRegion




@dataclass(frozen=True, slots=True)
class SpatialBatchLayout:
    """Mapping between flat batch indices and structured spatial indices.

    Logical structure:
        [item_count, regions_per_item]

    Physical structure:
        [item_count * regions_per_item]
    """

    @icontract.require(
        lambda self: self.item_count > 0,
        description="item_count must be positive.",
    )
    @icontract.require(
        lambda self: self.regions_per_item > 0,
        description="regions_per_item must be positive.",
    )
    def __post_init__(self) -> None:
        pass


    item_count: int
    regions_per_item: int

    @property
    def flat_count(self) -> int:
        """Return the number of flat batch entries."""
        return self.item_count * self.regions_per_item

    @icontract.require(lambda self, item_index: 0 <= item_index < self.item_count)
    @icontract.require(lambda self, region_index: 0 <= region_index < self.regions_per_item)
    def to_flat_index(self, item_index: int, region_index: int) -> int:
        """Return the flat index for a structured item-region pair."""
        return item_index * self.regions_per_item + region_index

    @icontract.require(lambda self, flat_index: 0 <= flat_index < self.flat_count)
    def from_flat_index(self, flat_index: int) -> tuple[int, int]:
        """Return ``(item_index, region_index)`` for a flat index."""
        return divmod(flat_index, self.regions_per_item)

# From cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_float_vector_batch.py
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class SpatialFloatVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    """Spatially structured batch of float embedding vectors.

    Physical structure:
        dict[int, list[float]]

    Logical structure:
        [item_count, regions_per_item, embedding_dim]
    """

    element_type = float

# From cscience-feature-api\src\cscience\features\api\datatypes\spatial\spatial_region.py
from dataclasses import dataclass

import icontract



@dataclass(frozen=True, slots=True)
class SpatialRegion:
    """Spatial region metadata.

    Pixel coordinates use half-open bounds:

        [x0, x1)
        [y0, y1)

    Normalized coordinates use the same convention in [0, 1].
    """

    index: int

    row: int
    column: int

    center_x: int
    center_y: int

    x0: int
    y0: int
    x1: int
    y1: int

    nx0: float
    ny0: float
    nx1: float
    ny1: float

    @icontract.require(lambda self: self.index >= 0, "index must be non-negative.")
    @icontract.require(lambda self: self.row >= 0, "row must be non-negative.")
    @icontract.require(lambda self: self.column >= 0, "column must be non-negative.")
    @icontract.require(lambda self: self.x1 > self.x0, "x1 must be greater than x0.")
    @icontract.require(lambda self: self.y1 > self.y0, "y1 must be greater than y0.")
    @icontract.require(lambda self: self.x0 <= self.center_x < self.x1, "center_x must be inside [x0, x1).")
    @icontract.require(lambda self: self.y0 <= self.center_y < self.y1, "center_y must be inside [y0, y1).")
    @icontract.require(
        lambda self: all(0.0 <= value <= 1.0 for value in (self.nx0, self.ny0, self.nx1, self.ny1)),
        "normalized coordinates must be in [0, 1].",
    )
    @icontract.require(lambda self: self.nx1 > self.nx0, "nx1 must be greater than nx0.")
    @icontract.require(lambda self: self.ny1 > self.ny0, "ny1 must be greater than ny0.")
    def __post_init__(self):
        pass

    @property
    def width(self) -> int:
        """Return the region width in pixels."""
        return self.x1 - self.x0

    @property
    def height(self) -> int:
        """Return the region height in pixels."""
        return self.y1 - self.y0

    @property
    def center_xy(self) -> tuple[int, int]:
        """Return the pixel center as ``(x, y)``."""
        return self.center_x, self.center_y

    @property
    def grid_xy(self) -> tuple[int, int]:
        """Return grid coordinates as ``(x, y)`` / ``(column, row)``."""
        return self.column, self.row

    @property
    def grid_yx(self) -> tuple[int, int]:
        """Return grid coordinates as ``(y, x)`` / ``(row, column)``."""
        return self.row, self.column

    @property
    def box_xyxy(self) -> tuple[int, int, int, int]:
        """Return the pixel box as ``(x0, y0, x1, y1)``."""
        return self.x0, self.y0, self.x1, self.y1

    @property
    def normalized_box_xyxy(self) -> tuple[float, float, float, float]:
        """Return the normalized box as ``(nx0, ny0, nx1, ny1)``."""
        return self.nx0, self.ny0, self.nx1, self.ny1

# From cscience-feature-api\src\cscience\features\api\datatypes\text\text.py
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class Text(CoreDatatype[str]):
    """Single text string."""

    def __init__(self, data: str) -> None:
        if type(data) is not str:
            raise TypeError(f"Text expects str, got {type(data).__name__}.")

        super().__init__(data)

# From cscience-feature-api\src\cscience\features\api\datatypes\text\text_batch.py
from collections.abc import Mapping

from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class TextBatch(
    BatchBase[str],
    CoreDatatype[dict[int, str]],
):
    """Batch of text strings indexed by source position."""

    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)

        for key, value in data.items():
            if type(value) is not str:
                raise TypeError(
                    f"TextBatch expects str values, "
                    f"got {type(value).__name__} at key {key}."
                )

        super().__init__(dict(data))

# From cscience-feature-api\src\cscience\features\api\feature\core_feature.py
from cscience.features.api.config.core_config import CoreConfig
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.api.feature.feature_info import FeatureInfo


class CoreFeature(FeatureBase):
    """
    This is a helper feature for register core converters.
    """

    def _initialize(self, config: CoreConfig) -> None:
        pass

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device="none",
            configuration=self._config.model_dump(mode="json"),
        )

# From cscience-feature-api\src\cscience\features\api\feature\feature_base.py
from __future__ import annotations

from abc import ABC, abstractmethod
import threading
from typing import ClassVar, Generic, Self, TypeVar, cast

from cscience.features.api.config.config_base import ConfigBase
from cscience.features.api.feature.feature_info import FeatureInfo

TConfig = TypeVar(
    "TConfig",
    bound=ConfigBase,
)

TFeature = TypeVar(
    "TFeature",
    bound="FeatureBase",
)


class FeatureBase(ABC, Generic[TFeature, TConfig]):
    """
    Base class for model-backed feature services.

    Each configuration identity may be instantiated only once.
    Instances must be obtained through get_instance().

    Configuration identity is defined by ConfigBase.__eq__ and
    ConfigBase.__hash__, which are expected to rely on the namespace.
    """

    _instances: ClassVar[
        dict[ConfigBase, FeatureBase]
    ] = {}

    _lock: ClassVar[threading.Lock] = threading.Lock()
    _creation_state: ClassVar[threading.local] = threading.local()

    _config: TConfig

    def __new__(
        cls,
        config: TConfig,
    ) -> Self:
        if cls is FeatureBase:
            raise TypeError(
                "FeatureBase cannot be instantiated directly."
            )

        if not getattr(
            FeatureBase._creation_state,
            "allowed",
            False,
        ):
            raise RuntimeError(
                f"{cls.__name__} instances must be created using "
                f"{cls.__name__}.get_instance(config)."
            )

        if config in FeatureBase._instances:
            raise ValueError(
                f"A feature instance for namespace "
                f"{config.namespace!r} already exists."
            )

        instance = super().__new__(cls)
        FeatureBase._instances[config] = instance

        return instance

    def __init__(
        self,
        config: TConfig,
    ) -> None:
        self._config = config
        self._initialize(config)

    @property
    def config(self) -> TConfig:
        return self._config

    @classmethod
    def get_instance(
        cls: type[TFeature],
        config: TConfig,
        init_if_missing: bool = True,
    ) -> TFeature:
        with FeatureBase._lock:
            existing = FeatureBase._instances.get(config)

            if existing is not None:
                return existing

            if not init_if_missing:
                raise LookupError(
                    f"No feature instance exists for namespace "
                    f"{config.namespace!r}."
                )

            FeatureBase._creation_state.allowed = True
            cls(config)

            try:
                existing = FeatureBase._instances.get(config)
                if existing is not None:
                    return existing
                raise  RuntimeError(
                    f"Failed to create feature instance for namespace "
                    f"{config.namespace!r}."
                )
            except Exception:
                FeatureBase._instances.pop(config, None)
                raise
            finally:
                FeatureBase._creation_state.allowed = False

    @abstractmethod
    def _initialize(
        self,
        config: TConfig,
    ) -> None:
        raise NotImplementedError



    @abstractmethod
    def get_feature_info(self) -> FeatureInfo:
        raise NotImplementedError

# From cscience-feature-api\src\cscience\features\api\feature\feature_base_meta.py
from abc import ABCMeta


class FeatureBaseMeta(ABCMeta):
    def __call__(
        cls,
        *args: object,
        **kwargs: object,
    ) -> object:
        raise TypeError(
            f"{cls.__name__} cannot be instantiated directly. "
            f"Use {cls.__name__}.get_instance(config)."
        )

# From cscience-feature-api\src\cscience\features\api\feature\feature_info.py


from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class FeatureInfo:
    namespace: str
    feature_type: str
    model_name: str | None
    device: str | None
    configuration: dict[str, Any]

# From cscience-feature-api\src\cscience\features\api\feature\operation_info.py
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

# From cscience-feature-api\src\cscience\features\api\feature\service_info.py
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

# From cscience-feature-api\src\cscience\features\api\registry\conversion_registry.py
from ..conversion.conversion_key import ConversionKey
from ..conversion.conversion_provider_base import ConversionProviderBase
from ..conversion.converter import Converter
from ..conversion.search_strategy_base import SearchStrategyBase
from ..registry.registry_base import RegistryBase, Tin


class ConversionRegistry(RegistryBase[ConversionProviderBase]):
    """Singleton registry for datatype converters."""
    @classmethod
    def _initialize(cls) -> None:
        cls._converters  = {}
        pass

    _converters: dict[ConversionKey, Converter] = None

    @classmethod
    def get_converters(cls) -> dict[ConversionKey, Converter]:
        """Return the dictionary of all registered converters."""
        return cls._converters

    @classmethod
    def register(cls, provider: Tin) -> None:
        """Register all converters exposed by a conversion provider."""
        for converter in provider.register_converters():
            cls.get_instance().get_converters()[converter.get_identifier()] = converter

    @classmethod
    def has_best_effort_converter(cls, strategy: SearchStrategyBase) -> bool:
        """Check if the given strategy has a best effort converter."""
        try:
            strategy.search(cls.get_instance().get_converters())
            return True
        except LookupError:
            return False

    @classmethod
    def get_best_effort_converter(cls, strategy: SearchStrategyBase) -> Converter:
        """Resolve a converter with the given search strategy."""
        try:
            return strategy.search(cls.get_instance().get_converters())
        except LookupError as ex:
            raise LookupError(f"No best effort converter found for strategy: {strategy}") from ex

# From cscience-feature-api\src\cscience\features\api\registry\registry_base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Union, Generic, ClassVar, Any

Tin = TypeVar("Tin", contravariant=True)


class RegistryBase(ABC, Generic[Tin]):

    _instances: ClassVar[dict[type["RegistryBase"], "RegistryBase"]] = {}
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any):
        if cls is RegistryBase:
            raise TypeError("FeatureBase cannot be instantiated directly.")

        if cls not in RegistryBase._instances:
            RegistryBase._instances[cls] = super().__new__(cls)

        return RegistryBase._instances[cls]

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialize()
        self._initialized = True


    @classmethod
    def get_instance(cls):
        return cls()

    @classmethod
    @abstractmethod
    def _initialize(cls) -> None:
        """
        Load expensive resources here, e.g. model weights.
        Called exactly once per concrete feature class.
        """
        pass

    @abstractmethod
    def register(self, provider: Tin) -> None:
        """Register a feature in the registry."""
        pass


# From cscience-feature-api\src\cscience\features\api\utils\image_utils.py
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image


def load_base64_image(path: Path) -> Image.Image:
    encoded = path.read_text(encoding="utf-8").strip()
    image_bytes = base64.b64decode(encoded, validate=True)
    return Image.open(BytesIO(image_bytes)).convert("RGB")

# From cscience-feature-api\src\cscience\features\api\utils\measure_time.py
import timeit


def measure_time(times: int=1, ignore_first: bool=False):
    """Measure the mean runtime of a function over repeated executions.

    Intended for lightweight development benchmarks, not for production
    profiling.
    """
    def inner(func):
        def wrapper(*args, **kwargs):

            t_total = 0
            result = None
            if ignore_first:
                result = func(*args, **kwargs)

            n = max(1, times)
            for i in range(n):
                start = timeit.default_timer()
                result = func(*args, **kwargs)
                end = timeit.default_timer()
                t_total += end - start

            max_width = 39

            print(
                f"\t{func.__name__:<{max_width}} "
                f"[mean] ⌛ {t_total / n:.5f} s for 🧮 {n} iterations"
            )
            return result
        return wrapper
    return inner

# From cscience-feature-api\tests\config\test_config.py
import unittest
from pathlib import Path
from typing import Literal

from pydantic import Field


from cscience.features.api.config.config_base import ConfigBase
from cscience.features.api.config.config_mode import ConfigMode


class MockConfig(ConfigBase):
    @classmethod
    def _default_namespace(cls) -> str:
        return "mock"

    string_value: str = Field(
        default="Hello World!",
        title='A string value',
        description='This is a string value for testing purposes.',
        min_length=3,
        max_length=50,
    )
    int_value: int = Field(
        default=42,
        title='An integer value',
        description='This is an integer value for testing purposes.',
        ge=0,
        le=100
    )
    bool_value: bool = Field(
        default=False,
        title='A boolean value',
        description='This is a boolean value for testing purposes.'
    )
    float_value: float = Field(
        default=3.14,
        title='A float value',
        description='This is a float value for testing purposes.',
        ge=0,
        le=10
    )
    list_value: list[int] = Field(
        default=[1, 2, 3],
        title='A list value',
        description='This is a list value for testing purposes.'
    )
    dict_value: dict[str, str] = Field(
        default={"key": "value"},
        title='A dict value',
        description='This is a dict value for testing purposes.'
    )
    literal_value: Literal["test1", "test2"] = Field(
        default="test1",
        title='A literal value',
        description='This is a literal value for testing purposes.'
    )


class FooConfig(ConfigBase):

    string_value: str = Field(
        default="What does foo actuali means?",
        title='A string value',
        description='This is a string value for testing purposes.',
        min_length=3,
        max_length=50,
    )
    int_value: int = Field(
        default=1,
        title='An integer value',
        description='This is an integer value for testing purposes.',
        ge=0,
        le=100
    )

    @classmethod
    def _default_namespace(cls) -> str:
        return "foo"


class BarConfig(ConfigBase):

    string_value: str = Field(
        default="What does bar actually means?",
        title='A string value',
        description='This is a string value for testing purposes.',
        min_length=3,
        max_length=50,
    )
    int_value: int = Field(
        default=100,
        title='An integer value',
        description='This is an integer value for testing purposes.',
        ge=0,
        le=100
    )

    @classmethod
    def _default_namespace(cls) -> str:
        return "bar"





class ConfigTest(unittest.TestCase):

    def test_read(self):
        cfg= MockConfig()
        print(cfg.model_dump())
        self.assertEqual(cfg.string_value, "Hello World!")
        self.assertEqual(cfg.int_value, 42)
        self.assertEqual(cfg.bool_value, False)
        self.assertEqual(cfg.float_value, 3.14)
        self.assertEqual(cfg.list_value, [1, 2, 3])
        self.assertEqual(cfg.dict_value, {"key": "value"})
        self.assertEqual(cfg.literal_value, "test1")
        pass

    def test_multiple(self):
        cfg1 = MockConfig()
        cfg2 = MockConfig()
        self.assertEqual(cfg1.model_dump(), cfg2.model_dump())
        cfg2.string_value = "Hello World and Moon!"
        print(f"\n-Dump cfg 1 contains: {cfg1.model_dump()}")
        print(f"\n-Dump cfg 2 contains: {cfg2.model_dump()}")
        print(cfg2.model_dump())
        self.assertNotEqual(cfg1.model_dump(), cfg2.model_dump())
        pass

    def test_literal(self):
        cfg = MockConfig(
            mode = ConfigMode.UNIFIED_CONFIG
        )
        cfg.literal_value = "test2"
        self.assertEqual(cfg.literal_value, "test2")
        MockConfig.model_validate(cfg)



    def test_persist_local(self):
        foo = FooConfig()
        bar = BarConfig()
        foo.persist()
        bar.persist()


    def test_persist_per_feature_package(self):
        MockConfig(
        )
        foo = FooConfig()
        bar = BarConfig()
        foo.persist()
        bar.persist()



    def test_persist_unified(self):
        ConfigBase(
            mode=ConfigMode.UNIFIED_CONFIG,
            config_path=Path("../fixtures/configurations.json"),
        )
        foo = FooConfig()
        bar = BarConfig()
        foo.persist()
        bar.persist()

    def test_persist_per_feature_common_folder(self):
        foo = FooConfig(
            mode=ConfigMode.CONFIG_PER_FEATURE,
            config_path=Path("../fixtures/config/"),
        )
        bar = BarConfig(
            mode=ConfigMode.CONFIG_PER_FEATURE,
            config_path=Path("../fixtures/config/"),
        )
        foo.persist()
        bar.persist()


    def test_multiple_namespace(self):
        foo = FooConfig(
            namespace="foo",
            config_path=Path("../fixtures/config/"),
        )
        foo2 = FooConfig(
            namespace="foo2",
            config_path=Path("../fixtures/config/"),
        )
        foo2.int_value = 99
        foo.persist()
        foo2.persist()

        foo.persist()
        foo2.load()

# From cscience-feature-api\tests\convertion\test_conversion.py


# From cscience-feature-api\tests\datatypes\base\test_core_datatypes.py
import unittest

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockCoreDatatype(CoreDatatype[int]):
    pass


class TestCoreDatatype(unittest.TestCase):
    def test_is_datatype(self) -> None:
        self.assertTrue(issubclass(MockCoreDatatype, DatatypeBase))

    def test_uses_core_namespace(self) -> None:
        self.assertEqual(MockCoreDatatype.namespace, "core")

    def test_stores_data_through_datatype_base(self) -> None:
        datatype = MockCoreDatatype(42)

        self.assertEqual(datatype.data(), 42)

# From cscience-feature-api\tests\datatypes\base\test_datatype_architecture.py
import unittest
from collections.abc import Mapping
from typing import TypeVar

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)
from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_base import (
    SpatialVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)
from cscience.features.api.datatypes.spatial.spatial_batch_layout import (
    SpatialBatchLayout,
)
from cscience.features.api.datatypes.spatial.spatial_region import (
    SpatialRegion,
)

T = TypeVar("T")


class MockBatch(
    BatchBase[str],
    CoreDatatype[dict[int, str]],
):
    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)
        super().__init__(dict(data))


class MockPrimitiveVector(
    PrimitiveVectorBase[float],
    CoreDatatype[list[float]],
):
    element_type = float


class MockEmbeddingVector(
    PrimitiveVectorBase[float],
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    element_type = float


class MockPrimitiveVectorBatch(
    PrimitiveVectorBatchBase[float],
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class MockEmbeddingVectorBatch(
    PrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class MockSpatialEmbeddingBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    element_type = float


class MockAudioBytes(
    AudioBytesBase,
    CoreDatatype[bytes],
):
    pass


class MockImageBytes(
    ImageBytesBase,
    CoreDatatype[bytes],
):
    pass


def make_region(index: int) -> SpatialRegion:
    return SpatialRegion(
        index=index,
        row=0,
        column=index,
        center_x=5,
        center_y=5,
        x0=0,
        y0=0,
        x1=10,
        y1=10,
        nx0=0.0,
        ny0=0.0,
        nx1=1.0,
        ny1=1.0,
    )


def make_spatial_data() -> SpatialVectorBatchData[list[float]]:
    return SpatialVectorBatchData(
        vectors={
            0: [0.0, 0.1],
            1: [1.0, 1.1],
            2: [2.0, 2.1],
            3: [3.0, 3.1],
        },
        layout=SpatialBatchLayout(
            item_count=2,
            regions_per_item=2,
        ),
        item_keys=(10, 20),
        regions=(
            make_region(0),
            make_region(1),
        ),
    )

class TestNamespaceNeutrality(unittest.TestCase):
    def test_structural_bases_do_not_inherit_datatype_base(
        self,
    ) -> None:
        structural_bases = (
            BatchBase,
            VectorBase,
            VectorBatchBase,
            PrimitiveVectorBase,
            PrimitiveVectorBatchBase,
            SpatialVectorBatchBase,
            SpatialPrimitiveVectorBatchBase,
        )

        for structural_base in structural_bases:
            with self.subTest(
                structural_base=structural_base,
            ):
                self.assertFalse(
                    issubclass(
                        structural_base,
                        DatatypeBase,
                    )
                )

    def test_semantic_bases_do_not_inherit_datatype_base(
        self,
    ) -> None:
        semantic_bases = (
            EmbeddingBase,
            MediaBytesBase,
            AudioBytesBase,
            ImageBytesBase,
        )

        for semantic_base in semantic_bases:
            with self.subTest(
                semantic_base=semantic_base,
            ):
                self.assertFalse(
                    issubclass(
                        semantic_base,
                        DatatypeBase,
                    )
                )

    def test_core_datatype_inherits_datatype_base(
        self,
    ) -> None:
        self.assertTrue(
            issubclass(
                CoreDatatype,
                DatatypeBase,
            )
        )

    def test_embedding_base_is_not_vector_base(
        self,
    ) -> None:
        self.assertFalse(
            issubclass(
                EmbeddingBase,
                VectorBase,
            )
        )

class TestDataOwnership(unittest.TestCase):
    def assert_has_one_data_owner_branch(
            self,
            datatype_class: type,
    ) -> None:
        data_owner_branches = tuple(
            base
            for base in datatype_class.__bases__
            if issubclass(base, DatatypeBase)
        )

        self.assertEqual(
            len(data_owner_branches),
            1,
            msg=(
                f"{datatype_class.__name__} must have exactly "
                f"one direct base leading to DatatypeBase, "
                f"got {data_owner_branches}."
            ),
        )

    def test_composed_datatypes_have_one_data_owner_branch(
            self,
    ) -> None:
        datatype_classes = (
            MockBatch,
            MockPrimitiveVector,
            MockEmbeddingVector,
            MockPrimitiveVectorBatch,
            MockEmbeddingVectorBatch,
            MockSpatialEmbeddingBatch,
            MockAudioBytes,
            MockImageBytes,
        )

        for datatype_class in datatype_classes:
            with self.subTest(
                    datatype_class=datatype_class,
            ):
                self.assert_has_one_data_owner_branch(
                    datatype_class
                )

class TestDatatypeMro(unittest.TestCase):
    def assert_mro_before(
        self,
        datatype_class: type,
        earlier_class: type,
        later_class: type,
    ) -> None:
        mro = datatype_class.__mro__

        self.assertLess(
            mro.index(earlier_class),
            mro.index(later_class),
            msg=(
                f"{earlier_class.__name__} must occur before "
                f"{later_class.__name__} in the MRO of "
                f"{datatype_class.__name__}."
            ),
        )

    def test_primitive_vector_validates_before_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockPrimitiveVector,
            PrimitiveVectorBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVector,
            VectorBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVector,
            CoreDatatype,
            DatatypeBase,
        )

    def test_embedding_vector_validates_before_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockEmbeddingVector,
            PrimitiveVectorBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockEmbeddingVector,
            EmbeddingBase,
            CoreDatatype,
        )

    def test_vector_batch_validates_before_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockPrimitiveVectorBatch,
            PrimitiveVectorBatchBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVectorBatch,
            VectorBatchBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockPrimitiveVectorBatch,
            BatchBase,
            CoreDatatype,
        )

    def test_spatial_batch_validates_before_data_owner(
        self,
    ) -> None:
        preceding_bases = (
            SpatialPrimitiveVectorBatchBase,
            SpatialVectorBatchBase,
            VectorBatchBase,
            BatchBase,
            EmbeddingBase,
        )

        for preceding_base in preceding_bases:
            with self.subTest(
                preceding_base=preceding_base,
            ):
                self.assert_mro_before(
                    MockSpatialEmbeddingBatch,
                    preceding_base,
                    CoreDatatype,
                )

    def test_media_validation_precedes_data_owner(
        self,
    ) -> None:
        self.assert_mro_before(
            MockAudioBytes,
            AudioBytesBase,
            CoreDatatype,
        )
        self.assert_mro_before(
            MockAudioBytes,
            MediaBytesBase,
            CoreDatatype,
        )


class TestCooperativeConstruction(unittest.TestCase):
    def test_batch_reaches_datatype_base(self) -> None:
        batch = MockBatch({
            1: "one",
            0: "zero",
        })

        self.assertIsInstance(
            batch,
            DatatypeBase,
        )
        self.assertEqual(
            batch.data(),
            {
                1: "one",
                0: "zero",
            },
        )

    def test_primitive_vector_reaches_datatype_base(
        self,
    ) -> None:
        vector = MockPrimitiveVector([
            1.0,
            2.0,
        ])

        self.assertIsInstance(
            vector,
            DatatypeBase,
        )
        self.assertEqual(
            vector.data(),
            [1.0, 2.0],
        )

    def test_embedding_vector_reaches_datatype_base(
        self,
    ) -> None:
        vector = MockEmbeddingVector([
            1.0,
            2.0,
            3.0,
        ])

        self.assertEqual(
            vector.embedding_dim(),
            3,
        )
        self.assertEqual(
            vector.data(),
            [1.0, 2.0, 3.0],
        )

    def test_vector_batch_reaches_datatype_base(
        self,
    ) -> None:
        batch = MockPrimitiveVectorBatch({
            0: [1.0, 2.0],
            1: [3.0, 4.0],
        })

        self.assertEqual(
            batch.data(),
            {
                0: [1.0, 2.0],
                1: [3.0, 4.0],
            },
        )
        self.assertEqual(batch.length(), 2)

    def test_spatial_batch_reaches_datatype_base(
        self,
    ) -> None:
        data = make_spatial_data()

        batch = MockSpatialEmbeddingBatch(data)

        self.assertIsInstance(
            batch,
            DatatypeBase,
        )
        self.assertIsInstance(
            batch.data(),
            SpatialVectorBatchData,
        )
        self.assertEqual(
            batch.data().vectors,
            data.vectors,
        )
        self.assertEqual(
            batch.embedding_dim(),
            2,
        )

    def test_audio_bytes_reaches_datatype_base(
        self,
    ) -> None:
        audio = MockAudioBytes(b"audio")

        self.assertEqual(
            audio.data(),
            b"audio",
        )

    def test_image_bytes_reaches_datatype_base(
        self,
    ) -> None:
        image = MockImageBytes(b"image")

        self.assertEqual(
            image.data(),
            b"image",
        )

# From cscience-feature-api\tests\datatypes\base\test_datatypes_base.py

import unittest

from icontract import ViolationError

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase

class ExampleDatatype(DatatypeBase[int]):
    pass


class TestDatatypeBase(unittest.TestCase):
    def test_stores_data(self) -> None:
        datatype = ExampleDatatype(42)

        self.assertEqual(datatype.data(), 42)

    def test_rejects_none(self) -> None:
        with self.assertRaises(ViolationError):
            ExampleDatatype(None)  # type: ignore[arg-type]





# From cscience-feature-api\tests\datatypes\base\test_media_bytes.py
import unittest

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.base.media.media_bytes_base import (
    MediaBytesBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)


class MockAudioBytes(
    AudioBytesBase,
    CoreDatatype[bytes],
):
    pass


class MockImageBytes(
    ImageBytesBase,
    CoreDatatype[bytes],
):
    pass


class TestMediaBytesBase(unittest.TestCase):
    def test_stores_media_bytes(self) -> None:
        media = MockAudioBytes(b"encoded audio")

        self.assertEqual(
            media.data(),
            b"encoded audio",
        )

    def test_rejects_empty_bytes(self) -> None:
        with self.assertRaises(ValueError):
            MockAudioBytes(b"")

    def test_rejects_string(self) -> None:
        with self.assertRaises(TypeError):
            MockAudioBytes(
                "encoded audio",  # type: ignore[arg-type]
            )

    def test_rejects_bytearray(self) -> None:
        with self.assertRaises(TypeError):
            MockAudioBytes(
                bytearray(b"encoded audio"),  # type: ignore[arg-type]
            )

    def test_audio_media_type(self) -> None:
        self.assertEqual(
            MockAudioBytes.media_type,
            "audio",
        )

    def test_image_media_type(self) -> None:
        self.assertEqual(
            MockImageBytes.media_type,
            "image",
        )

    def test_audio_bytes_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockAudioBytes.__mro__.count(DatatypeBase),
            1,
        )

    def test_image_bytes_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockImageBytes.__mro__.count(DatatypeBase),
            1,
        )

class TestMediaBaseArchitecture(unittest.TestCase):
    def test_media_bytes_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                MediaBytesBase,
                DatatypeBase,
            )
        )

    def test_audio_bytes_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                AudioBytesBase,
                DatatypeBase,
            )
        )

    def test_image_bytes_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                ImageBytesBase,
                DatatypeBase,
            )
        )


# From cscience-feature-api\tests\datatypes\base\test_primitive_base_architecture.py
import unittest

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.primitive_vector_base import PrimitiveVectorBase
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import PrimitiveVectorBatchBase


class TestPrimitiveBaseArchitecture(unittest.TestCase):
    def test_primitive_vector_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(PrimitiveVectorBase, DatatypeBase)
        )

    def test_primitive_vector_batch_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(PrimitiveVectorBatchBase, DatatypeBase)
        )

# From cscience-feature-api\tests\datatypes\base\test_primitive_vector_base.py
import unittest

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockFloatVector(
    PrimitiveVectorBase[float],
    CoreDatatype[list[float]],
):
    element_type = float


class MockFloatEmbedding(
    PrimitiveVectorBase[float],
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    element_type = float


class TestPrimitiveVectorBase(unittest.TestCase):
    def test_stores_primitive_vector(self) -> None:
        vector = MockFloatVector([1.0, 2.0, 3.0])

        self.assertEqual(vector.data(), [1.0, 2.0, 3.0])

    def test_reports_vector_length(self) -> None:
        vector = MockFloatVector([1.0, 2.0, 3.0])

        self.assertEqual(vector.length(), 3)

    def test_asserts_expected_length(self) -> None:
        vector = MockFloatVector(
            [1.0, 2.0, 3.0],
            assert_length=3,
        )

        self.assertEqual(vector.length(), 3)

    def test_rejects_unexpected_length(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVector(
                [1.0, 2.0],
                assert_length=3,
            )

    def test_rejects_empty_vector(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVector([])

    def test_rejects_non_list_container(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVector(
                (1.0, 2.0),  # type: ignore[arg-type]
            )

    def test_rejects_wrong_element_type(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVector(
                [1.0, 2],  # type: ignore[list-item]
            )

    def test_embedding_reports_dimension(self) -> None:
        embedding = MockFloatEmbedding([1.0, 2.0, 3.0])

        self.assertEqual(embedding.embedding_dim(), 3)

    def test_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatVector.__mro__.count(DatatypeBase),
            1,
        )

    def test_embedding_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatEmbedding.__mro__.count(DatatypeBase),
            1,
        )

# From cscience-feature-api\tests\datatypes\base\test_primitive_vector_batch_base.py
import unittest
from collections.abc import Mapping

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockFloatVectorBatch(
    PrimitiveVectorBatchBase[float],
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class MockFloatEmbeddingBatch(
    PrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[dict[int, list[float]]],
):
    element_type = float


class TestPrimitiveVectorBatchBase(unittest.TestCase):
    def test_stores_vector_batch_as_dict(self) -> None:
        source: Mapping[int, list[float]] = {
            1: [3.0, 4.0],
            0: [1.0, 2.0],
        }

        batch = MockFloatVectorBatch(source)

        self.assertEqual(
            batch.data(),
            {
                1: [3.0, 4.0],
                0: [1.0, 2.0],
            },
        )
        self.assertIsInstance(batch.data(), dict)

    def test_orders_vectors_by_source_index(self) -> None:
        batch = MockFloatVectorBatch({
            5: [5.0, 6.0],
            1: [1.0, 2.0],
            3: [3.0, 4.0],
        })

        self.assertEqual(batch.ordered_keys(), (1, 3, 5))
        self.assertEqual(
            batch.ordered_values(),
            (
                [1.0, 2.0],
                [3.0, 4.0],
                [5.0, 6.0],
            ),
        )

    def test_reports_batch_size(self) -> None:
        batch = MockFloatVectorBatch({
            0: [1.0, 2.0],
            1: [3.0, 4.0],
        })

        self.assertEqual(batch.batch_size(), 2)

    def test_reports_shared_vector_length(self) -> None:
        batch = MockFloatVectorBatch({
            0: [1.0, 2.0],
            1: [3.0, 4.0],
        })

        self.assertEqual(batch.length(), 2)

    def test_asserts_expected_length(self) -> None:
        batch = MockFloatVectorBatch(
            {
                0: [1.0, 2.0],
                1: [3.0, 4.0],
            },
            assert_length=2,
        )

        self.assertEqual(batch.length(), 2)

    def test_rejects_empty_batch(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVectorBatch({})

    def test_rejects_non_integer_key(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVectorBatch(
                {
                    "0": [1.0, 2.0],  # type: ignore[dict-item]
                }
            )

    def test_rejects_non_list_vector(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVectorBatch(
                {
                    0: (1.0, 2.0),  # type: ignore[dict-item]
                }
            )

    def test_rejects_empty_vector(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVectorBatch({
                0: [],
            })

    def test_rejects_inconsistent_vector_lengths(self) -> None:
        with self.assertRaises(ValueError):
            MockFloatVectorBatch({
                0: [1.0],
                1: [2.0, 3.0],
            })

    def test_rejects_wrong_element_type(self) -> None:
        with self.assertRaises(TypeError):
            MockFloatVectorBatch({
                0: [1.0, 2],  # type: ignore[list-item]
            })

    def test_embedding_batch_reports_dimension(self) -> None:
        batch = MockFloatEmbeddingBatch({
            0: [1.0, 2.0, 3.0],
            1: [4.0, 5.0, 6.0],
        })

        self.assertEqual(batch.embedding_dim(), 3)

    def test_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatVectorBatch.__mro__.count(DatatypeBase),
            1,
        )

    def test_embedding_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockFloatEmbeddingBatch.__mro__.count(DatatypeBase),
            1,
        )

# From cscience-feature-api\tests\datatypes\base\test_spatial_vector_batch_base.py
import unittest
from dataclasses import replace

from icontract import ViolationError

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_base import (
    SpatialVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_vector_batch_data import (
    SpatialVectorBatchData,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)
from cscience.features.api.datatypes.spatial.spatial_batch_layout import (
    SpatialBatchLayout,
)
from cscience.features.api.datatypes.spatial.spatial_region import (
    SpatialRegion,
)


class MockSpatialFloatVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    EmbeddingBase,
    CoreDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    element_type = float


def make_region(index: int) -> SpatialRegion:
    return SpatialRegion(
        index=index,
        row=0,
        column=index,
        center_x=5,
        center_y=5,
        x0=0,
        y0=0,
        x1=10,
        y1=10,
        nx0=0.0,
        ny0=0.0,
        nx1=1.0,
        ny1=1.0,
    )


def make_spatial_data() -> SpatialVectorBatchData[list[float]]:
    return SpatialVectorBatchData(
        vectors={
            0: [0.0, 0.1, 0.2],
            1: [1.0, 1.1, 1.2],
            2: [2.0, 2.1, 2.2],
            3: [3.0, 3.1, 3.2],
        },
        layout=SpatialBatchLayout(
            item_count=2,
            regions_per_item=2,
        ),
        item_keys=(10, 20),
        regions=(
            make_region(0),
            make_region(1),
        ),
    )


class TestSpatialVectorBatchBase(unittest.TestCase):
    def test_stores_spatial_data(self) -> None:
        data = make_spatial_data()

        batch = MockSpatialFloatVectorBatch(data)

        self.assertEqual(batch.layout, data.layout)
        self.assertEqual(batch.item_keys, (10, 20))
        self.assertEqual(batch.regions, data.regions)

    def test_reports_flat_batch_size(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(batch.batch_size(), 4)

    def test_reports_structured_dimensions(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(batch.item_count(), 2)
        self.assertEqual(batch.regions_per_item(), 2)
        self.assertEqual(batch.length(), 3)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_uses_inherited_ordering(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (0, 1, 2, 3),
        )

        self.assertEqual(
            batch.ordered_values(),
            (
                [0.0, 0.1, 0.2],
                [1.0, 1.1, 1.2],
                [2.0, 2.1, 2.2],
                [3.0, 3.1, 3.2],
            ),
        )

    def test_returns_vector_at_structured_index(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(
            batch.vector_at(
                item_index=1,
                region_index=0,
            ),
            [2.0, 2.1, 2.2],
        )

    def test_returns_vectors_for_item(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data()
        )

        self.assertEqual(
            batch.item_vectors(1),
            (
                [2.0, 2.1, 2.2],
                [3.0, 3.1, 3.2],
            ),
        )

    def test_rejects_wrong_item_key_count(self) -> None:
        data = replace(
            make_spatial_data(),
            item_keys=(10,),
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_duplicate_item_keys(self) -> None:
        data = replace(
            make_spatial_data(),
            item_keys=(10, 10),
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_non_contiguous_vector_keys(self) -> None:
        data = replace(
            make_spatial_data(),
            vectors={
                0: [0.0, 0.1, 0.2],
                1: [1.0, 1.1, 1.2],
                2: [2.0, 2.1, 2.2],
                4: [3.0, 3.1, 3.2],
            },
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_wrong_region_count(self) -> None:
        data = replace(
            make_spatial_data(),
            regions=(make_region(0),),
        )

        with self.assertRaises(ViolationError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_inconsistent_vector_lengths(self) -> None:
        data = replace(
            make_spatial_data(),
            vectors={
                0: [0.0, 0.1],
                1: [1.0, 1.1, 1.2],
                2: [2.0, 2.1, 2.2],
                3: [3.0, 3.1, 3.2],
            },
        )

        with self.assertRaises(ValueError):
            MockSpatialFloatVectorBatch(data)

    def test_rejects_wrong_primitive_type(self) -> None:
        data = replace(
            make_spatial_data(),
            vectors={
                0: [0.0, 0.1, 0.2],
                1: [1.0, 1.1, 1.2],
                2: [2.0, 2.1, 2.2],
                3: [3.0, 3.1, 3],
            },
        )

        with self.assertRaises(TypeError):
            MockSpatialFloatVectorBatch(data)

    def test_asserts_expected_length(self) -> None:
        batch = MockSpatialFloatVectorBatch(
            make_spatial_data(),
            assert_length=3,
        )

        self.assertEqual(batch.length(), 3)

    def test_reaches_datatype_base_once(self) -> None:
        self.assertEqual(
            MockSpatialFloatVectorBatch.__mro__.count(
                DatatypeBase
            ),
            1,
        )

    def test_spatial_base_is_namespace_neutral(self) -> None:
        self.assertFalse(
            issubclass(
                SpatialVectorBatchBase,
                DatatypeBase,
            )
        )

# From cscience-feature-api\tests\datatypes\base\test_structural_bases.py
import unittest
from collections.abc import Mapping
from dataclasses import dataclass

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase
from cscience.features.api.datatypes.base.structural.batch_base import BatchBase
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import CoreDatatype


class MockBatch(
    BatchBase[str],
    CoreDatatype[dict[int, str]],
):
    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)
        super().__init__(dict(data))


class MockVector(
    VectorBase,
    CoreDatatype[list[float]],
):
    pass


class MockVectorBatch(
    VectorBatchBase[list[float]],
    CoreDatatype[dict[int, list[float]]],
):
    def __init__(
        self,
        data: Mapping[int, list[float]],
    ) -> None:
        self._validate_vector_batch_mapping(data)
        super().__init__(dict(data))


class MockEmbedding(
    VectorBase,
    EmbeddingBase,
    CoreDatatype[list[float]],
):
    pass


@dataclass(frozen=True, slots=True)
class WrappedBatchData:
    values: Mapping[int, str]


class MockWrappedBatch(
    BatchBase[str],
    CoreDatatype[WrappedBatchData],
):
    def __init__(self, data: Mapping[int, str]) -> None:
        self._validate_batch_mapping(data)
        super().__init__(
            WrappedBatchData(values=dict(data))
        )

    def _batch_mapping(self) -> Mapping[int, str]:
        return self.data().values


class TestBatchBase(unittest.TestCase):
    def test_orders_batch_by_source_index(self) -> None:
        batch = MockBatch({
            5: "five",
            1: "one",
            3: "three",
        })

        self.assertEqual(batch.ordered_keys(), (1, 3, 5))
        self.assertEqual(
            batch.ordered_values(),
            ("one", "three", "five"),
        )
        self.assertEqual(
            batch.ordered_items(),
            (
                (1, "one"),
                (3, "three"),
                (5, "five"),
            ),
        )

    def test_reports_batch_size(self) -> None:
        batch = MockBatch({
            10: "a",
            20: "b",
        })

        self.assertEqual(batch.batch_size(), 2)

    def test_supports_overridden_batch_mapping(self) -> None:
        batch = MockWrappedBatch({
            2: "two",
            1: "one",
        })

        self.assertEqual(batch.ordered_values(), ("one", "two"))


class TestVectorBase(unittest.TestCase):
    def test_reports_vector_length(self) -> None:
        vector = MockVector([1.0, 2.0, 3.0])

        self.assertEqual(vector.length(), 3)

    def test_asserts_expected_vector_length(self) -> None:
        vector = MockVector([1.0, 2.0])

        with self.assertRaises(ValueError):
            vector.assert_length(3)


class TestVectorBatchBase(unittest.TestCase):
    def test_reports_shared_vector_length(self) -> None:
        batch = MockVectorBatch({
            1: [1.0, 2.0],
            0: [3.0, 4.0],
        })

        self.assertEqual(batch.length(), 2)

    def test_rejects_inconsistent_vector_lengths(self) -> None:
        with self.assertRaises(ValueError):
            MockVectorBatch({
                0: [1.0],
                1: [2.0, 3.0],
            })


class TestEmbeddingBase(unittest.TestCase):
    def test_reports_embedding_dimension(self) -> None:
        embedding = MockEmbedding([1.0, 2.0, 3.0])

        self.assertEqual(embedding.embedding_dim(), 3)

    def test_does_not_inherit_vector_base(self) -> None:
        self.assertFalse(issubclass(EmbeddingBase, VectorBase))


class TestDatatypeInheritance(unittest.TestCase):
    def test_mock_types_reach_datatype_base_once(self) -> None:
        datatype_classes = (
            MockBatch,
            MockVector,
            MockVectorBatch,
            MockEmbedding,
            MockWrappedBatch,
        )

        for datatype_class in datatype_classes:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(DatatypeBase),
                    1,
                )

# From cscience-feature-api\tests\datatypes\specific\test_audio_signal.py
import unittest

import numpy as np

from cscience.features.api.datatypes.audio.audio_signal import (
    AudioSignal,
)
from cscience.features.api.datatypes.audio.audio_signal_data import (
    AudioSignalData,
)


class TestAudioSignal(unittest.TestCase):
    def test_accepts_mono_signal(self) -> None:
        data = AudioSignalData(
            waveform=np.array(
                [0.0, 0.5, -0.5],
                dtype=np.float32,
            ),
            sample_rate=16_000,
        )

        signal = AudioSignal(data)

        self.assertIs(signal.data(), data)

    def test_accepts_two_dimensional_signal(self) -> None:
        data = AudioSignalData(
            waveform=np.zeros(
                (2, 100),
                dtype=np.float32,
            ),
            sample_rate=16_000,
        )

        signal = AudioSignal(data)

        self.assertIs(signal.data(), data)

    def test_rejects_empty_waveform(self) -> None:
        data = AudioSignalData(
            waveform=np.array([], dtype=np.float32),
            sample_rate=16_000,
        )

        with self.assertRaises(ValueError):
            AudioSignal(data)

    def test_rejects_non_numeric_waveform(self) -> None:
        data = AudioSignalData(
            waveform=np.array(["a", "b"]),
            sample_rate=16_000,
        )

        with self.assertRaises(TypeError):
            AudioSignal(data)

    def test_rejects_invalid_dimensions(self) -> None:
        data = AudioSignalData(
            waveform=np.zeros(
                (1, 2, 3),
                dtype=np.float32,
            ),
            sample_rate=16_000,
        )

        with self.assertRaises(ValueError):
            AudioSignal(data)

    def test_rejects_non_positive_sample_rate(self) -> None:
        data = AudioSignalData(
            waveform=np.array(
                [0.0],
                dtype=np.float32,
            ),
            sample_rate=0,
        )

        with self.assertRaises(ValueError):
            AudioSignal(data)

# From cscience-feature-api\tests\datatypes\specific\test_concrete_core_datatype_architecture.py
import unittest

from cscience.features.api.datatypes.audio.audio_bytes import (
    AudioBytes,
)
from cscience.features.api.datatypes.audio.audio_signal import (
    AudioSignal,
)
from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.media.audio_bytes_base import (
    AudioBytesBase,
)
from cscience.features.api.datatypes.base.media.image_bytes_base import (
    ImageBytesBase,
)
from cscience.features.api.datatypes.base.structural.batch_base import (
    BatchBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_base import (
    PrimitiveVectorBase,
)
from cscience.features.api.datatypes.base.structural.primitive_vector_batch_base import (
    PrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.base.structural.spatial_primitive_vector_batch_base import (
    SpatialPrimitiveVectorBatchBase,
)
from cscience.features.api.datatypes.core.core_datatype import (
    CoreDatatype,
)
from cscience.features.api.datatypes.image.image_bytes import (
    ImageBytes,
)
from cscience.features.api.datatypes.image.image_data_url import (
    ImageDataUrl,
)
from cscience.features.api.datatypes.image.pil_image import (
    PilImage,
)
from cscience.features.api.datatypes.image.pil_image_batch import (
    PilImageBatch,
)
from cscience.features.api.datatypes.primitives_scalar.bool_value import (
    BoolValue,
)
from cscience.features.api.datatypes.primitives_scalar.float_value import (
    FloatValue,
)
from cscience.features.api.datatypes.primitives_scalar.int_value import (
    IntValue,
)
from cscience.features.api.datatypes.primitives_vectors.bool_vector import (
    BoolVector,
)
from cscience.features.api.datatypes.primitives_vectors.float_vector import (
    FloatVector,
)
from cscience.features.api.datatypes.primitives_vectors.int_vector import (
    IntVector,
)
from cscience.features.api.datatypes.primitives_vectors_batch.bool_vector_batch import (
    BoolVectorBatch,
)
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import (
    FloatVectorBatch,
)
from cscience.features.api.datatypes.primitives_vectors_batch.int_vector_batch import (
    IntVectorBatch,
)
from cscience.features.api.datatypes.references.data_url import (
    DataUrl,
)
from cscience.features.api.datatypes.references.file_path import (
    FilePath,
)
from cscience.features.api.datatypes.spatial.spatial_float_vector_batch import (
    SpatialFloatVectorBatch,
)
from cscience.features.api.datatypes.text.text import (
    Text,
)
from cscience.features.api.datatypes.text.text_batch import (
    TextBatch,
)


CONCRETE_CORE_DATATYPES = (
    AudioBytes,
    AudioSignal,
    ImageBytes,
    ImageDataUrl,
    PilImage,
    PilImageBatch,
    BoolValue,
    FloatValue,
    IntValue,
    BoolVector,
    FloatVector,
    IntVector,
    BoolVectorBatch,
    FloatVectorBatch,
    IntVectorBatch,
    DataUrl,
    FilePath,
    SpatialFloatVectorBatch,
    Text,
    TextBatch,
)


class TestConcreteCoreDatatypeArchitecture(unittest.TestCase):
    def test_all_concrete_types_are_core_datatypes(self) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        CoreDatatype,
                    )
                )

    def test_all_concrete_types_use_core_namespace(self) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "core",
                )

    def test_all_concrete_types_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_all_concrete_types_have_one_data_owner_branch(
        self,
    ) -> None:
        for datatype_class in CONCRETE_CORE_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                data_owner_branches = tuple(
                    base
                    for base in datatype_class.__bases__
                    if issubclass(base, DatatypeBase)
                )

                self.assertEqual(
                    len(data_owner_branches),
                    1,
                    msg=(
                        f"{datatype_class.__name__} must have "
                        f"exactly one direct data-owner branch, "
                        f"got {data_owner_branches}."
                    ),
                )

class TestConcreteCoreDatatypeMro(unittest.TestCase):
    def assert_mro_before(
        self,
        datatype_class: type,
        earlier_class: type,
        later_class: type,
    ) -> None:
        mro = datatype_class.__mro__

        self.assertLess(
            mro.index(earlier_class),
            mro.index(later_class),
        )

    def test_media_bases_precede_core_datatype(self) -> None:
        cases = (
            (AudioBytes, AudioBytesBase),
            (ImageBytes, ImageBytesBase),
        )

        for datatype_class, media_base in cases:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    media_base,
                    CoreDatatype,
                )

    def test_vector_bases_precede_core_datatype(self) -> None:
        cases = (
            (BoolVector, PrimitiveVectorBase),
            (FloatVector, PrimitiveVectorBase),
            (IntVector, PrimitiveVectorBase),
            (
                BoolVectorBatch,
                PrimitiveVectorBatchBase,
            ),
            (
                FloatVectorBatch,
                PrimitiveVectorBatchBase,
            ),
            (
                IntVectorBatch,
                PrimitiveVectorBatchBase,
            ),
            (
                SpatialFloatVectorBatch,
                SpatialPrimitiveVectorBatchBase,
            ),
        )

        for datatype_class, structural_base in cases:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    structural_base,
                    CoreDatatype,
                )

    def test_embedding_base_precedes_core_datatype(
        self,
    ) -> None:
        embedding_types = (
            FloatVector,
            FloatVectorBatch,
            SpatialFloatVectorBatch,
        )

        for datatype_class in embedding_types:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    EmbeddingBase,
                    CoreDatatype,
                )

    def test_batch_base_precedes_core_datatype(self) -> None:
        batch_types = (
            TextBatch,
            PilImageBatch,
            BoolVectorBatch,
            FloatVectorBatch,
            IntVectorBatch,
            SpatialFloatVectorBatch,
        )

        for datatype_class in batch_types:
            with self.subTest(datatype_class=datatype_class):
                self.assert_mro_before(
                    datatype_class,
                    BatchBase,
                    CoreDatatype,
                )

import unittest

from PIL import Image

from cscience.features.api.datatypes.audio.audio_bytes import (
    AudioBytes,
)
from cscience.features.api.datatypes.image.image_bytes import (
    ImageBytes,
)
from cscience.features.api.datatypes.image.pil_image_batch import (
    PilImageBatch,
)
from cscience.features.api.datatypes.primitives_vectors.bool_vector import (
    BoolVector,
)
from cscience.features.api.datatypes.primitives_vectors.float_vector import (
    FloatVector,
)
from cscience.features.api.datatypes.primitives_vectors.int_vector import (
    IntVector,
)
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import (
    FloatVectorBatch,
)
from cscience.features.api.datatypes.text.text_batch import (
    TextBatch,
)


class TestConcreteCoreDatatypeConstruction(
    unittest.TestCase
):
    def test_constructs_encoded_media(self) -> None:
        audio = AudioBytes(b"audio")
        image = ImageBytes(b"image")

        self.assertEqual(audio.data(), b"audio")
        self.assertEqual(image.data(), b"image")

    def test_constructs_primitive_vectors(self) -> None:
        bool_vector = BoolVector([True, False])
        float_vector = FloatVector([1.0, 2.0])
        int_vector = IntVector([1, 2])

        self.assertEqual(bool_vector.length(), 2)
        self.assertEqual(float_vector.length(), 2)
        self.assertEqual(float_vector.embedding_dim(), 2)
        self.assertEqual(int_vector.length(), 2)

    def test_constructs_embedding_batch(self) -> None:
        batch = FloatVectorBatch({
            1: [3.0, 4.0],
            0: [1.0, 2.0],
        })

        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(batch.length(), 2)
        self.assertEqual(batch.embedding_dim(), 2)
        self.assertEqual(batch.ordered_keys(), (0, 1))

    def test_constructs_text_batch(self) -> None:
        batch = TextBatch({
            1: "second",
            0: "first",
        })

        self.assertEqual(
            batch.ordered_values(),
            ("first", "second"),
        )

    def test_constructs_pil_image_batch(self) -> None:
        first = Image.new("RGB", (10, 10))
        second = Image.new("RGB", (10, 10))

        batch = PilImageBatch({
            1: second,
            0: first,
        })

        self.assertEqual(
            batch.ordered_values(),
            (first, second),
        )

# From cscience-feature-api\tests\datatypes\specific\test_file_path.py
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

# From cscience-feature-api\tests\datatypes\specific\test_image_data_url.py
import unittest

from cscience.features.api.datatypes.image.image_data_url import (
    ImageDataUrl,
)
from cscience.features.api.datatypes.references.data_url import (
    DataUrl,
)


class TestImageDataUrl(unittest.TestCase):
    def test_accepts_base64_image_data_url(self) -> None:
        data_url = ImageDataUrl(
            "data:image/png;base64,aW1hZ2U="
        )

        self.assertEqual(
            data_url.media_type(),
            "image/png",
        )
        self.assertTrue(data_url.is_base64())

    def test_is_data_url(self) -> None:
        self.assertTrue(
            issubclass(ImageDataUrl, DataUrl)
        )

    def test_rejects_non_image_media_type(self) -> None:
        with self.assertRaises(ValueError):
            ImageDataUrl(
                "data:text/plain;base64,aGVsbG8="
            )

    def test_rejects_non_base64_image_data_url(self) -> None:
        with self.assertRaises(ValueError):
            ImageDataUrl(
                "data:image/png,raw-data"
            )

# From cscience-feature-api\tests\feature\test_feature.py
import unittest

from cscience.features.api.config.config_base import ConfigBase
from cscience.features.api.config.core_config import CoreConfig
from cscience.features.api.feature.feature_base import FeatureBase


class FeatureTest(unittest.TestCase):

    def test_feature_base(self):

        class A(FeatureBase['A', CoreConfig]):
            def _initialize(self, config: ConfigBase) -> None:
                pass

        class B(FeatureBase['B',CoreConfig]):
            def _initialize(self, config: ConfigBase) -> None:
                pass


        a = A.get_instance(CoreConfig(namespace="A"))
        b = B.get_instance(CoreConfig(namespace="B"))
        self.assertEqual(a.get_instance(CoreConfig(namespace="A")), a)
        self.assertEqual(b.get_instance(CoreConfig(namespace="B")), b)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a.get_instance(CoreConfig(namespace="A")), b.get_instance(CoreConfig(namespace="B")))

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\__init__.py
from cscience.features.api import RegistryBase

from .asr_whisper_connector import AsrWhisperConnector
from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_feature import AsrWhisperFeature
from .asr_whisper_datatypes.asr_whisper_datatype import AsrWhisperDatatype
from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)

__all__ = [
    "AsrWhisperConnector",
    "AsrWhisperConversionProvider",
    "AsrWhisperDatatype",
    "AsrWhisperFeature",
    "AudioBytes",
    "AudioDataUrl",
    "AudioSignal",
    "AudioSignalData",
    "WhisperTranscription",
    "WhisperTranscriptionData",
]


def register(registry: RegistryBase) -> None:
    registry.register("asr_whisper", AsrWhisperConversionProvider)

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_config.py
from typing import Literal

from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class AsrConfig(ConfigBase):
    """
    Available Whisper model variants:

    +--------+------------+--------------------+--------------------+---------------+----------------+
    | Size   | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
    +========+============+====================+====================+===============+================+
    | tiny   | 39 M       | tiny.en            | tiny               | ~1 GB         | ~10x           |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | base   | 74 M       | base.en            | base               | ~1 GB         | ~7x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | small  | 244 M      | small.en           | small              | ~2 GB         | ~4x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | medium | 769 M      | medium.en          | medium             | ~5 GB         | ~2x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | large  | 1550 M     | N/A                | large              | ~10 GB        | 1x             |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    | turbo  | 809 M      | N/A                | turbo              | ~6 GB         | ~8x            |
    +--------+------------+--------------------+--------------------+---------------+----------------+
    """

    @classmethod
    def _default_namespace(cls) -> str:
        return "asr_whisper"

    model_name:Literal["small", "medium", "large"] = Field(
        default="small",
        description="The name of the ASR model to use."
    )

    preferred_device:str = Field(
        default="cuda",
        description="The device to use for inference."
    )

    force_device:bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )


# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_connector.py
from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    ServiceInfo,
    Text,
)
from .asr_config import AsrConfig

from .asr_whisper_conversion_provider import AsrWhisperConversionProvider
from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)
from .asr_whisper_feature import AsrWhisperFeature


class AsrWhisperConnector(ConnectorBase):
    """Public connector for Whisper ASR."""

    def __init__(self, config: AsrConfig) -> None:
        self.feature = AsrWhisperFeature.get_instance(config)
        super().__init__(AsrWhisperConversionProvider(self.feature))

    def transcribe_audio_bytes(self, data: bytes) -> WhisperTranscriptionData:
        """Transcribe encoded audio bytes and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioBytes,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioBytes(data)).data()

    def transcribe_audio_data_url(self, data: str) -> WhisperTranscriptionData:
        """Transcribe a base64-encoded audio data URL and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioDataUrl,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioDataUrl(data)).data()

    def transcribe_signal(self, data: AudioSignalData) -> WhisperTranscriptionData:
        """Transcribe a Whisper-ready audio signal and return the structured result."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioSignal,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=WhisperTranscription,
        )

        return function(AudioSignal(data)).data()

    def audio_bytes(self, data: bytes) -> str:
        """Transcribe encoded audio bytes and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioBytes,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioBytes(data)).data()

    def audio_data_url(self, data: str) -> str:
        """Transcribe a base64-encoded audio data URL and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioDataUrl,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioDataUrl(data)).data()

    def signal(self, data: AudioSignalData) -> str:
        """Transcribe a Whisper-ready audio signal and return plain text."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.transcribe,
            input_type=AudioSignal,
            input_feature_type=AudioSignal,
            output_feature_type=WhisperTranscription,
            output_type=Text,
        )

        return function(AudioSignal(data)).data()

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="asr",
            name="ASR_Whisper",
            description="Audio speech recognition service.",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_conversion_provider.py
import base64
import io

import librosa
import numpy as np
import soundfile as sf

from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    Text,
)

from .asr_whisper_datatypes.audio_bytes import AudioBytes
from .asr_whisper_datatypes.audio_data_url import AudioDataUrl
from .asr_whisper_datatypes.audio_signal import AudioSignal, AudioSignalData
from .asr_whisper_datatypes.whisper_transcription import WhisperTranscription


def audio_data_url_passthrough(data_url: AudioDataUrl) -> AudioDataUrl:
    return data_url


def audio_bytes_passthrough(audio: AudioBytes) -> AudioBytes:
    return audio


def audio_signal_passthrough(signal: AudioSignal) -> AudioSignal:
    return signal


def whisper_transcription_passthrough(
    transcription: WhisperTranscription,
) -> WhisperTranscription:
    return transcription


def audio_data_url_to_audio_bytes(data_url: AudioDataUrl) -> AudioBytes:
    """Decode a base64 audio data URL into raw encoded audio bytes."""
    encoded = data_url.payload()
    return AudioBytes(base64.b64decode(encoded, validate=True))


def audio_bytes_to_audio_signal(audio: AudioBytes) -> AudioSignal:
    """Decode audio bytes into Whisper-ready mono float32 16 kHz audio."""
    waveform, sample_rate = sf.read(io.BytesIO(audio.data()))
    waveform = np.asarray(waveform)

    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    elif waveform.ndim != 1:
        raise ValueError(f"Unexpected audio shape: {waveform.shape}")

    waveform = waveform.astype(np.float32, copy=False)

    if sample_rate != 16_000:
        waveform = librosa.resample(
            waveform,
            orig_sr=sample_rate,
            target_sr=16_000,
        )
        sample_rate = 16_000

    waveform = np.ascontiguousarray(waveform, dtype=np.float32)

    return AudioSignal(
        AudioSignalData(
            waveform=waveform,
            sample_rate=sample_rate,
        )
    )


def audio_data_url_to_audio_signal(data_url: AudioDataUrl) -> AudioSignal:
    """Decode a base64 audio data URL directly into a Whisper-ready signal."""
    return audio_bytes_to_audio_signal(
        audio_data_url_to_audio_bytes(data_url)
    )


def whisper_transcription_to_text(transcription: WhisperTranscription) -> Text:
    """Extract plain text from a Whisper transcription."""
    return Text(transcription.data().text)


class AsrWhisperConversionProvider(ConversionProviderBase):
    """Registers conversions required by the Whisper ASR feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[AudioDataUrl, AudioDataUrl](
                name="audio_data_url_passthrough",
                source=self._feature,
                function=audio_data_url_passthrough,
                input_type=AudioDataUrl,
                output_type=AudioDataUrl,
            ),
            Converter[AudioBytes, AudioBytes](
                name="audio_bytes_passthrough",
                source=self._feature,
                function=audio_bytes_passthrough,
                input_type=AudioBytes,
                output_type=AudioBytes,
            ),
            Converter[AudioSignal, AudioSignal](
                name="audio_signal_passthrough",
                source=self._feature,
                function=audio_signal_passthrough,
                input_type=AudioSignal,
                output_type=AudioSignal,
            ),
            Converter[WhisperTranscription, WhisperTranscription](
                name="whisper_transcription_passthrough",
                source=self._feature,
                function=whisper_transcription_passthrough,
                input_type=WhisperTranscription,
                output_type=WhisperTranscription,
            ),
            Converter[AudioDataUrl, AudioBytes](
                name="audio_data_url_to_audio_bytes",
                source=self._feature,
                function=audio_data_url_to_audio_bytes,
                input_type=AudioDataUrl,
                output_type=AudioBytes,
            ),
            Converter[AudioBytes, AudioSignal](
                name="audio_bytes_to_audio_signal",
                source=self._feature,
                function=audio_bytes_to_audio_signal,
                input_type=AudioBytes,
                output_type=AudioSignal,
            ),
            Converter[AudioDataUrl, AudioSignal](
                name="audio_data_url_to_audio_signal",
                source=self._feature,
                function=audio_data_url_to_audio_signal,
                input_type=AudioDataUrl,
                output_type=AudioSignal,
            ),
            Converter[WhisperTranscription, Text](
                name="whisper_transcription_to_text",
                source=self._feature,
                function=whisper_transcription_to_text,
                input_type=WhisperTranscription,
                output_type=Text,
            ),
        ]

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\asr_whisper_datatype.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class AsrWhisperDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for Whisper ASR-specific datatypes."""

    namespace = "asr_whisper"

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_bytes.py
from cscience.features.api import AudioBytesBase

from .asr_whisper_datatype import AsrWhisperDatatype


class AudioBytes(
    AudioBytesBase,
    AsrWhisperDatatype[bytes],
):
    """Whisper input containing encoded audio bytes."""

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_data_url.py
from cscience.features.api.datatypes.base.references.data_url_base import (
    DataUrlBase,
)

from .asr_whisper_datatype import AsrWhisperDatatype


class AudioDataUrl(
    DataUrlBase,
    AsrWhisperDatatype[str],
):
    """Base64-encoded audio data URL for Whisper input."""

    def __init__(self, data: str) -> None:
        super().__init__(data)

        media_type = self.media_type()

        if media_type is None or not media_type.startswith("audio/"):
            raise ValueError(
                "AudioDataUrl must declare an audio media type."
            )

        if not self.is_base64():
            raise ValueError(
                "AudioDataUrl must declare base64 encoding."
            )

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_signal.py
import numpy as np

from .asr_whisper_datatype import AsrWhisperDatatype
from .audio_signal_data import AudioSignalData


class AudioSignal(
    AsrWhisperDatatype[AudioSignalData],
):
    """Whisper-ready mono float32 audio signal at 16 kHz."""

    EXPECTED_SAMPLE_RATE = 16_000

    def __init__(self, data: AudioSignalData) -> None:
        if not isinstance(data, AudioSignalData):
            raise TypeError(
                f"AudioSignal expects AudioSignalData, "
                f"got {type(data).__name__}."
            )

        waveform = data.waveform

        if not isinstance(waveform, np.ndarray):
            raise TypeError(
                f"AudioSignal waveform expects np.ndarray, "
                f"got {type(waveform).__name__}."
            )

        if waveform.ndim != 1:
            raise ValueError(
                "AudioSignal expects a mono 1D waveform, "
                f"got shape {waveform.shape}."
            )

        if waveform.size == 0:
            raise ValueError(
                "AudioSignal waveform cannot be empty."
            )

        if waveform.dtype != np.float32:
            raise TypeError(
                "AudioSignal expects a float32 waveform, "
                f"got {waveform.dtype}."
            )

        if type(data.sample_rate) is not int:
            raise TypeError(
                f"AudioSignal sample_rate expects int, "
                f"got {type(data.sample_rate).__name__}."
            )

        if data.sample_rate != self.EXPECTED_SAMPLE_RATE:
            raise ValueError(
                f"AudioSignal expects {self.EXPECTED_SAMPLE_RATE} Hz, "
                f"got {data.sample_rate} Hz."
            )

        super().__init__(data)

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\audio_signal_data.py
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AudioSignalData:
    """Whisper-ready mono audio signal."""

    waveform: np.ndarray
    sample_rate: int


# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_datatypes\whisper_transcription.py
from dataclasses import dataclass
from typing import Any

from .asr_whisper_datatype import AsrWhisperDatatype


@dataclass(frozen=True, slots=True)
class WhisperTranscriptionData:
    """Structured Whisper transcription result."""

    text: str
    language: str | None
    segments: list[dict[str, Any]]


class WhisperTranscription(
    AsrWhisperDatatype[WhisperTranscriptionData],
):
    """Whisper transcription output."""

    def __init__(
        self,
        data: WhisperTranscriptionData,
    ) -> None:
        if not isinstance(data, WhisperTranscriptionData):
            raise TypeError(
                "WhisperTranscription expects "
                f"WhisperTranscriptionData, "
                f"got {type(data).__name__}."
            )

        if type(data.text) is not str:
            raise TypeError(
                "WhisperTranscriptionData.text expects str, "
                f"got {type(data.text).__name__}."
            )

        if (
            data.language is not None
            and type(data.language) is not str
        ):
            raise TypeError(
                "WhisperTranscriptionData.language expects "
                f"str | None, got {type(data.language).__name__}."
            )

        if type(data.segments) is not list:
            raise TypeError(
                "WhisperTranscriptionData.segments expects list, "
                f"got {type(data.segments).__name__}."
            )

        super().__init__(data)

# From cscience-feature-asr-whisper\src\cscience\features\asr_whisper\asr_whisper_feature.py
from __future__ import annotations

import threading

import torch
import whisper

from cscience.features.api import FeatureBase
from cscience.features.api import FeatureInfo
from .asr_config import AsrConfig

from .asr_whisper_datatypes.audio_signal import AudioSignal
from .asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
    WhisperTranscriptionData,
)



class AsrWhisperFeature(FeatureBase['AsrWhisperFeature', AsrConfig]):
    """Whisper ASR feature service.

    Loads the Whisper model once and transcribes decoded mono audio signals.
    """


    def _initialize(self, config: AsrConfig) -> None:

        self._config = config
        self._device = torch.device(config.preferred_device if torch.cuda.is_available() else "cpu")
        if self._config .force_device and not (self._config.preferred_device == str(self._device)):
            raise RuntimeError(
                f"Preferred device {self._config.preferred_device} is not available. "
                f"Available device is {self._device}."
            )

        self._model = whisper.load_model(self._config.model_name, device=self._device)
        self._initialized = True

    @torch.inference_mode()
    def transcribe(self, audio: AudioSignal) -> WhisperTranscription:
        """Transcribe a Whisper-ready audio signal."""

        fp16 = self._model .device.type == "cuda"

        result = self._model.transcribe(audio.data().waveform, fp16=fp16)

        return WhisperTranscription(
            WhisperTranscriptionData(
                text=result.get("text", "").strip(),
                language=result.get("language"),
                segments=result.get("segments", []),
            )
        )


    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(mode="json"),
        )

# From cscience-feature-asr-whisper\tests\test_asr_whisper_datatype_architecture.py
import unittest

from cscience.features.api import (
    AudioBytesBase,
    DatatypeBase,
)
from cscience.features.api.datatypes.base.references.data_url_base import (
    DataUrlBase,
)

from cscience.features.asr_whisper.asr_whisper_datatypes.asr_whisper_datatype import (
    AsrWhisperDatatype,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.audio_bytes import (
    AudioBytes,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.audio_data_url import (
    AudioDataUrl,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.audio_signal import (
    AudioSignal,
)
from cscience.features.asr_whisper.asr_whisper_datatypes.whisper_transcription import (
    WhisperTranscription,
)


ASR_DATATYPES = (
    AudioBytes,
    AudioDataUrl,
    AudioSignal,
    WhisperTranscription,
)


class TestAsrWhisperDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_asr_namespace(self) -> None:
        for datatype_class in ASR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "asr_whisper",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in ASR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        AsrWhisperDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in ASR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_audio_bytes_validation_precedes_namespace(
        self,
    ) -> None:
        mro = AudioBytes.__mro__

        self.assertLess(
            mro.index(AudioBytesBase),
            mro.index(AsrWhisperDatatype),
        )

    def test_data_url_validation_precedes_namespace(
        self,
    ) -> None:
        mro = AudioDataUrl.__mro__

        self.assertLess(
            mro.index(DataUrlBase),
            mro.index(AsrWhisperDatatype),
        )


class TestAsrWhisperDatatypeConstruction(unittest.TestCase):
    def test_constructs_audio_bytes(self) -> None:
        audio = AudioBytes(b"encoded audio")

        self.assertEqual(audio.data(), b"encoded audio")

    def test_constructs_audio_data_url(self) -> None:
        data_url = AudioDataUrl(
            "data:audio/wav;base64,UklGRg=="
        )

        self.assertEqual(
            data_url.media_type(),
            "audio/wav",
        )
        self.assertTrue(data_url.is_base64())

    def test_rejects_non_audio_data_url(self) -> None:
        with self.assertRaises(ValueError):
            AudioDataUrl(
                "data:image/png;base64,aW1hZ2U="
            )

    def test_rejects_non_base64_audio_data_url(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            AudioDataUrl(
                "data:audio/wav,raw-data"
            )

# From cscience-feature-asr-whisper\tests\test_asr_whisper_feature.py
import io
import unittest
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf

from cscience.features.asr_whisper import AsrWhisperConnector
from cscience.features.asr_whisper import AudioBytes
from cscience.features.asr_whisper.asr_config import AsrConfig
from cscience.features.asr_whisper.asr_whisper_conversion_provider import (
    audio_bytes_to_audio_signal,
)


def make_test_wav_bytes(sample_rate: int = 8_000) -> bytes:
    duration = 0.25
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    waveform = 0.1 * np.sin(2 * np.pi * 440 * t)

    buffer = io.BytesIO()
    sf.write(buffer, waveform, sample_rate, format="WAV")
    return buffer.getvalue()

@dataclass
class Fixture:
    id: str
    audio_bytes: bytes
    contains: list[str]



class AsrWhispernTest(unittest.TestCase):

    def setUp(self):
        fixture_dir = Path(__file__).parent / "fixtures" / "ljspeech"

        self.fixtures :list[Fixture] = [
            Fixture( "LJ001-0001.wav", (fixture_dir / "LJ001-0001.wav").read_bytes(), ["printing", "arts"]),
            Fixture( "LJ001-0002.wav", (fixture_dir / "LJ001-0002.wav").read_bytes(), ["modern", "comparatively"]),
        ]



    def test_connector_initializes(self):
        connector = AsrWhisperConnector(AsrConfig())
        self.assertIsNotNone(connector)

    def test_audio_bytes_to_audio_signal_resamples_to_16khz(self):
        audio_bytes = make_test_wav_bytes(sample_rate=8_000)

        signal = audio_bytes_to_audio_signal(AudioBytes(audio_bytes))

        self.assertEqual(signal.data().sample_rate, 16_000)
        self.assertEqual(signal.data().waveform.ndim, 1)
        self.assertEqual(signal.data().waveform.dtype, np.float32)

    def test_transcribes_local_speech_file(self):
        for fixture in self.fixtures:
            audio_bytes = fixture.audio_bytes
            expected_keywords = fixture.contains
            text = AsrWhisperConnector(AsrConfig()).audio_bytes(audio_bytes)
            for keyword in expected_keywords:
                self.assertIn(keyword, text.lower(), f"Expected keyword '{keyword}' not found in transcription '{text}' for fixture '{fixture.id}'")


# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\__init__.py
from cscience.features.api import RegistryBase

from .clip_spatial_connector import ClipSpatialConnector
from .clip_spatial_conversion_provider import ClipSpatialConversionProvider
from .clip_spatial_datatypes.clip_spatial_datatype import ClipSpatialDatatype
from .clip_spatial_feature import ClipSpatialFeature
from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch
from .filter.filter_provider import FilterProvider
from .filter.mean_noise_provider import MeanNoiseProvider
from .filter.zero_provider import ZeroProvider
from .geometry.geometry_provider import GeometryProvider
from .geometry.square_provider import SquareProvider
from .indexer.spatial_index import SpatialIndex
from .indexer.spatial_indexer import SpatialIndexer
from .masking.masking_generator import MaskingGenerator
from .masking.masking_mode import MaskingMode

__all__ = [
    "ClipSpatialConnector",
    "ClipSpatialConversionProvider",
    "ClipSpatialDatatype",
    "ClipSpatialFeature",
    "ClipSpatialTensorBatch",

    "FilterProvider",
    "MeanNoiseProvider",
    "ZeroProvider",
    "GeometryProvider",
    "SquareProvider",
    "SpatialIndex",
    "SpatialIndexer",
    "MaskingGenerator",
    "MaskingMode",
]


def register(registry: RegistryBase) -> None:
    registry.register("clip_spatial", ClipSpatialConversionProvider)

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_config.py

from enum import Enum

from pydantic import Field

from cscience.features.api import ConfigBase
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode


class ClipSpatialConfig(ConfigBase):
    """Configuration for CLIP Spatial."""

    @classmethod
    def _default_namespace(cls) -> str:
        return "clip_spatial"

    model_name: str = Field(
        default="xlm-roberta-base-ViT-B-32",
        description="The name of the CLIP model to use. Default is 'xlm-roberta-base-ViT-B-32'."
    )


    pretrained:str = Field(
        default="laion5b_s13b_b90k",
        description="The name of the pretrained model to use. Default is 'laion5b_s13b_b90k'."
    )

    preferred_device:str = Field(
        default="cuda",
        description="The device to use for inference. Default is 'cpu'."
    )

    force_device:bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )

    step_size: tuple[float, float] = Field(default=(1 / 6, 1 / 8))
    start_point: tuple[float, float] = Field(default=(1 / 6, 1 / 8))
    grid_shape: tuple[int, int] = Field(default=(5, 7))

    geometry_size: tuple[float, float] = Field(default=(1 / 3, 1 / 4))

    masking_mode: MaskingMode = Field(default=MaskingMode.KEEP_ONLY)






# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_connector.py
# packages/cscience-feature-clip-spatial/src/cscience/features/clip_spatial/clip_spatial_connector.py

from PIL.Image import Image

from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
    SpatialFloatVectorBatch,
)
from .clip_spatial_config import ClipSpatialConfig

from .clip_spatial_conversion_provider import ClipSpatialConversionProvider
from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch
from .clip_spatial_feature import ClipSpatialFeature


class ClipSpatialConnector(ConnectorBase):
    """Public connector for CLIP Spatial region embeddings."""

    def __init__(self, config: ClipSpatialConfig) -> None:
        self.feature = ClipSpatialFeature.get_instance(config, init_if_missing=True)
        super().__init__( ClipSpatialConversionProvider(self.feature))

    def image_regions(self, image: Image) -> SpatialFloatVectorBatch:
        """Embed spatial regions of one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_region_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipSpatialTensorBatch,
            output_type=SpatialFloatVectorBatch,
        )

        return function(PilImage(image)).data()

    def image_region_batch(
        self,
        images: list[Image],
    ) -> SpatialFloatVectorBatch:
        """Embed spatial regions of an image batch."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_region_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipSpatialTensorBatch,
            output_type=SpatialFloatVectorBatch,
        )

        return function(image_batch).data()






    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="clip_spatial",
            name="Clip spatial regions",
            description="Clip spatial region embedding",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_conversion_provider.py
# packages/cscience-feature-clip-spatial/src/cscience/features/clip_spatial/clip_spatial_conversion_provider.py

from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    SpatialFloatVectorBatch,
    SpatialVectorBatchData,
)

from .clip_spatial_datatypes.clip_spatial_tensor_batch import ClipSpatialTensorBatch





class ClipSpatialConversionProvider(ConversionProviderBase):
    """Registers conversions required by CLIP Spatial."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[ClipSpatialTensorBatch, ClipSpatialTensorBatch](
                name="clip_spatial_tensor_batch_passthrough",
                source=self._feature,
                function=self.clip_spatial_tensor_batch_passthrough,
                input_type=ClipSpatialTensorBatch,
                output_type=ClipSpatialTensorBatch,
            ),
            Converter[ClipSpatialTensorBatch, SpatialFloatVectorBatch](
                name="clip_spatial_tensor_batch_to_spatial_float_vector_batch",
                source=self._feature,
                function=self.clip_spatial_tensor_batch_to_spatial_float_vector_batch,
                input_type=ClipSpatialTensorBatch,
                output_type=SpatialFloatVectorBatch,
            ),
        ]


    def clip_spatial_tensor_batch_passthrough(
            self,
            batch: ClipSpatialTensorBatch,
    ) -> ClipSpatialTensorBatch:
        return batch


    def clip_spatial_tensor_batch_to_spatial_float_vector_batch(
            self,
            batch: ClipSpatialTensorBatch,
    ) -> SpatialFloatVectorBatch:
        return SpatialFloatVectorBatch(
            SpatialVectorBatchData(
                vectors={
                    flat_index: [
                        float(value)
                        for value in vector.detach().cpu().tolist()
                    ]
                    for flat_index, vector in batch.ordered_items()
                },
                layout=batch.layout,
                item_keys=batch.item_keys,
                regions=batch.regions,
            )
        )

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_datatype.py
from abc import ABC

from cscience.features.api.datatypes.base.datatype_base import DatatypeBase


class ClipDatatype(DatatypeBase, ABC):
    namespace = "clip_spatial"

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_datatypes\clip_spatial_datatype.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class ClipSpatialDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for CLIP Spatial-specific datatypes."""

    namespace = "clip_spatial"

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_datatypes\clip_spatial_tensor_batch.py
import torch
from torch import Tensor

from cscience.features.api import (
    EmbeddingBase,
    SpatialVectorBatchBase,
    SpatialVectorBatchData,
)

from .clip_spatial_datatype import ClipSpatialDatatype


class ClipSpatialTensorBatch(
    SpatialVectorBatchBase[Tensor],
    EmbeddingBase,
    ClipSpatialDatatype[
        SpatialVectorBatchData[Tensor]
    ],
):
    """Spatially structured CLIP embedding tensor batch.

    Physical structure:
        dict[flat_region_index, Tensor[D]]

    Logical structure:
        [item_count, regions_per_item, embedding_dim]
    """

    def __init__(
        self,
        data: SpatialVectorBatchData[Tensor],
    ) -> None:
        if not isinstance(data, SpatialVectorBatchData):
            raise TypeError(
                "ClipSpatialTensorBatch expects "
                f"SpatialVectorBatchData, "
                f"got {type(data).__name__}."
            )

        for key, vector in data.vectors.items():
            if not isinstance(vector, Tensor):
                raise TypeError(
                    "ClipSpatialTensorBatch expects Tensor values, "
                    f"got {type(vector).__name__} at key {key}."
                )

            if vector.ndim != 1:
                raise ValueError(
                    "ClipSpatialTensorBatch expects 1D tensor vectors, "
                    f"got shape {tuple(vector.shape)} at key {key}."
                )

            if not vector.is_floating_point():
                raise TypeError(
                    "ClipSpatialTensorBatch expects floating-point "
                    f"tensor vectors, got {vector.dtype} at key {key}."
                )

        super().__init__(data)

    def as_flat_tensor(self) -> Tensor:
        """Return embeddings with shape [N * R, D]."""
        return torch.stack(self.ordered_values())

    def as_structured_tensor(self) -> Tensor:
        """Return embeddings with shape [N, R, D]."""
        flat = self.as_flat_tensor()

        return flat.reshape(
            self.layout.item_count,
            self.layout.regions_per_item,
            flat.shape[-1],
        )

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_datatypes\clip_spatial_text_tensor_batch.py
from collections.abc import Mapping

from torch import Tensor

from cscience.features.api import (
    EmbeddingBase,
    VectorBatchBase,
)

from .clip_spatial_datatype import ClipSpatialDatatype
from .clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)


class ClipSpatialTextTensorBatch(
    VectorBatchBase[Tensor],
    EmbeddingBase,
    ClipSpatialDatatype[
        ClipSpatialTextTensorBatchData
    ],
):
    """Packed CLIP text embedding batch with stable source keys."""

    def __init__(
        self,
        data: ClipSpatialTextTensorBatchData,
    ) -> None:
        if not isinstance(
            data,
            ClipSpatialTextTensorBatchData,
        ):
            raise TypeError(
                "ClipSpatialTextTensorBatch expects "
                f"ClipSpatialTextTensorBatchData, "
                f"got {type(data).__name__}."
            )

        vectors = data.vectors
        keys = data.keys

        if not isinstance(vectors, Tensor):
            raise TypeError(
                "ClipSpatialTextTensorBatch vectors expect Tensor, "
                f"got {type(vectors).__name__}."
            )

        if vectors.ndim != 2:
            raise ValueError(
                "ClipSpatialTextTensorBatch expects a 2D tensor, "
                f"got shape {tuple(vectors.shape)}."
            )

        if len(keys) != vectors.shape[0]:
            raise ValueError(
                "Number of keys must match tensor rows: "
                f"{len(keys)} keys for {vectors.shape[0]} rows."
            )

        for key in keys:
            if type(key) is not int:
                raise TypeError(
                    "ClipSpatialTextTensorBatch keys must be int, "
                    f"got {type(key).__name__}."
                )

        if len(set(keys)) != len(keys):
            raise ValueError(
                "ClipSpatialTextTensorBatch keys must be unique."
            )

        if not vectors.is_floating_point():
            raise TypeError(
                "ClipSpatialTextTensorBatch expects a "
                f"floating-point tensor, got {vectors.dtype}."
            )

        normalized = ClipSpatialTextTensorBatchData(
            keys=tuple(keys),
            vectors=vectors,
        )

        self._vectors_by_key = dict(
            zip(
                normalized.keys,
                normalized.vectors.unbind(dim=0),
                strict=True,
            )
        )

        self._validate_vector_batch_mapping(
            self._vectors_by_key
        )

        super().__init__(normalized)

    def _batch_mapping(self) -> Mapping[int, Tensor]:
        """Return text embeddings indexed by TextBatch key."""
        return self._vectors_by_key

    @property
    def keys(self) -> tuple[int, ...]:
        """Return keys in packed tensor row order."""
        return self.data().keys

    @property
    def vectors(self) -> Tensor:
        """Return the packed tensor with shape [N, D]."""
        return self.data().vectors

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_datatypes\clip_spatial_text_tensor_batch_data.py
from dataclasses import dataclass

from torch import Tensor


@dataclass(frozen=True, slots=True)
class ClipSpatialTextTensorBatchData:
    """Packed CLIP text embedding batch with stable source keys.

    vectors has shape [N, D].
    keys maps tensor rows back to TextBatch source keys.
    """

    keys: tuple[int, ...]
    vectors: Tensor

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_datatypes\spatial_score_vector_batch.py
from cscience.features.api import (
    SpatialPrimitiveVectorBatchBase,
    SpatialVectorBatchData,
)

from .clip_spatial_datatype import ClipSpatialDatatype


class SpatialScoreVectorBatch(
    SpatialPrimitiveVectorBatchBase[float],
    ClipSpatialDatatype[
        SpatialVectorBatchData[list[float]]
    ],
):
    """Spatial scores for one or more text queries.

    Physical structure:
        dict[flat_region_index, list[float]]

    Logical structure:
        [item_count, regions_per_item, query_count]

    Each score-vector position corresponds to the TextBatch key at the same
    position in query_keys.
    """

    element_type = float

    def __init__(
        self,
        data: SpatialVectorBatchData[list[float]],
        query_keys: tuple[int, ...],
    ) -> None:
        if type(query_keys) is not tuple:
            raise TypeError(
                "SpatialScoreVectorBatch query_keys expects tuple, "
                f"got {type(query_keys).__name__}."
            )

        if not query_keys:
            raise ValueError(
                "SpatialScoreVectorBatch query_keys cannot be empty."
            )

        for key in query_keys:
            if type(key) is not int:
                raise TypeError(
                    "SpatialScoreVectorBatch query keys must be int, "
                    f"got {type(key).__name__}."
                )

        if len(set(query_keys)) != len(query_keys):
            raise ValueError(
                "SpatialScoreVectorBatch query keys must be unique."
            )

        self._query_keys = query_keys

        super().__init__(
            data,
            assert_length=len(query_keys),
        )

    @property
    def query_keys(self) -> tuple[int, ...]:
        """Return query keys in score-vector position order."""
        return self._query_keys

    @property
    def query_count(self) -> int:
        """Return the number of represented queries."""
        return len(self._query_keys)

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\clip_spatial_feature.py
import open_clip
import torch

from cscience.features.api import (
    FeatureBase,
    FeatureInfo,
    PilImageBatch,
    SpatialVectorBatchData,
    TextBatch,
)

from .clip_spatial_config import ClipSpatialConfig
from .clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from .clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)
from .clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)
from .filter.zero_provider import ZeroProvider
from .geometry.square_provider import SquareProvider
from .indexer.spatial_indexer import SpatialIndexer
from .masking.masking_generator import MaskingGenerator


class ClipSpatialFeature(
    FeatureBase["ClipSpatialFeature", ClipSpatialConfig]
):
    """CLIP Spatial feature service backed by OpenCLIP."""

    def _initialize(self, config: ClipSpatialConfig) -> None:
        self._config = config
        self._device = self._resolve_device(config)

        self._model, _, self._preprocess = (
            open_clip.create_model_and_transforms(
                model_name=config.model_name,
                pretrained=config.pretrained,
            )
        )

        self._model = self._model.to(self._device).eval()
        self._tokenizer = open_clip.get_tokenizer(
            config.model_name
        )

        self._initialized = True

    @staticmethod
    def _resolve_device(
        config: ClipSpatialConfig,
    ) -> torch.device:
        preferred = torch.device(config.preferred_device)

        if preferred.type == "cuda" and not torch.cuda.is_available():
            if config.force_device:
                raise ValueError(
                    f"Preferred device {preferred} is not available."
                )

            return torch.device("cpu")

        return preferred

    @torch.inference_mode()
    def text_batch(
        self,
        texts: TextBatch,
    ) -> ClipSpatialTextTensorBatch:
        keys = texts.ordered_keys()
        values = list(texts.ordered_values())

        tokens = self._tokenizer(values).to(self._device)

        vectors = self._model.encode_text(tokens)
        vectors = self._normalize_embeddings(vectors)

        return ClipSpatialTextTensorBatch(
            ClipSpatialTextTensorBatchData(
                keys=keys,
                vectors=vectors.detach().float().cpu(),
            )
        )

    @torch.inference_mode()
    def image_region_batch(
        self,
        images: PilImageBatch,
    ) -> ClipSpatialTensorBatch:
        item_keys = images.ordered_keys()
        image_values = images.ordered_values()

        base_tensors = torch.stack(
            [
                self._preprocess(image)
                for image in image_values
            ]
        )

        _, channels, image_height, image_width = (
            base_tensors.shape
        )

        if channels != 3:
            raise ValueError(
                f"Expected 3 image channels, got {channels}."
            )

        geometry = SquareProvider(
            geometry_size=self._config.geometry_size,
        )

        indexer = SpatialIndexer(
            item_keys=item_keys,
            image_width=image_width,
            image_height=image_height,
            grid_shape=self._config.grid_shape,
            start_point=self._config.start_point,
            step_size=self._config.step_size,
            geometry=geometry,
        )

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=self._config.masking_mode,
        )

        masked_tensors = generator.generate(
            base_tensors
        ).to(self._device)

        vectors = self._model.encode_image(masked_tensors)
        vectors = self._normalize_embeddings(vectors)
        vectors = vectors.detach().float().cpu()

        return ClipSpatialTensorBatch(
            SpatialVectorBatchData(
                vectors={
                    index: vector
                    for index, vector in enumerate(vectors)
                },
                layout=generator.layout,
                item_keys=generator.item_keys,
                regions=generator.regions,
            )
        )

    def score_text_vector_batch(
        self,
        texts: TextBatch,
        spatial_vectors: ClipSpatialTensorBatch,
    ) -> SpatialScoreVectorBatch:
        """Score text queries against spatial image embeddings."""
        text_vectors = self.text_batch(texts)

        return self.score_embeddings(
            text_vectors=text_vectors,
            spatial_vectors=spatial_vectors,
        )

    def score_text_image_batch(
        self,
        texts: TextBatch,
        images: PilImageBatch,
    ) -> SpatialScoreVectorBatch:
        """Create spatial image embeddings and score text queries."""
        spatial_vectors = self.image_region_batch(images)

        return self.score_text_vector_batch(
            texts=texts,
            spatial_vectors=spatial_vectors,
        )

    @staticmethod
    def score_embeddings(
        text_vectors: ClipSpatialTextTensorBatch,
        spatial_vectors: ClipSpatialTensorBatch,
    ) -> SpatialScoreVectorBatch:
        """Score spatial embeddings against text embeddings.

        The resulting matrix has shape:

            [flat_region_count, query_count]
        """
        spatial_tensor = spatial_vectors.as_flat_tensor()
        text_tensor = text_vectors.vectors

        if spatial_tensor.shape[1] != text_tensor.shape[1]:
            raise ValueError(
                "Text and spatial embedding dimensions must match: "
                f"{text_tensor.shape[1]} != "
                f"{spatial_tensor.shape[1]}."
            )

        scores = spatial_tensor @ text_tensor.T

        return SpatialScoreVectorBatch(
            data=SpatialVectorBatchData(
                vectors={
                    flat_index: [
                        float(score)
                        for score in score_vector.tolist()
                    ]
                    for flat_index, score_vector
                    in enumerate(scores)
                },
                layout=spatial_vectors.layout,
                item_keys=spatial_vectors.item_keys,
                regions=spatial_vectors.regions,
            ),
            query_keys=text_vectors.keys,
        )

    @staticmethod
    def _normalize_embeddings(
        vectors: torch.Tensor,
    ) -> torch.Tensor:
        norms = vectors.norm(
            dim=-1,
            keepdim=True,
        )

        if torch.any(norms == 0):
            raise ValueError(
                "CLIP produced an embedding with zero norm."
            )

        return vectors / norms

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(
                mode="json"
            ),
        )

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\filter\filter_provider.py
from abc import ABC, abstractmethod

import torch

from cscience.features.api import SpatialRegion


class FilterProvider(ABC):
    """Produces replacement values for masked regions."""

    @abstractmethod
    def create_fill(
        self,
        *,
        base_tensor: torch.Tensor,
        region: SpatialRegion,
        window: torch.Tensor,
    ) -> torch.Tensor | float:
        """Create replacement content for a region.

        base_tensor:
            Full source tensor [C, H, W]

        window:
            Selected region view [C, h, w]
        """
        raise NotImplementedError

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\filter\mean_noise_provider.py
import torch

from cscience.features.api import SpatialRegion

from .filter_provider import FilterProvider


class MeanNoiseProvider(FilterProvider):
    """Fill selected regions with noisy local content."""

    def __init__(self, variance: float = 0.5) -> None:
        self.variance = variance

    def create_fill(
        self,
        *,
        base_tensor: torch.Tensor,
        region: SpatialRegion,
        window: torch.Tensor,
    ) -> torch.Tensor:
        noise = (self.variance ** 0.5) * torch.randn_like(window)
        return window + noise

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\filter\zero_provider.py
import torch

from cscience.features.api import SpatialRegion

from .filter_provider import FilterProvider


class ZeroProvider(FilterProvider):
    """Fill selected regions with zero."""

    def create_fill(
        self,
        *,
        base_tensor: torch.Tensor,
        region: SpatialRegion,
        window: torch.Tensor,
    ) -> float:
        return 0.0

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\geometry\geometry_provider.py
from abc import ABC, abstractmethod

import torch

from cscience.features.api import SpatialRegion


class GeometryProvider(ABC):
    """Maps spatial regions to tensor windows."""

    @abstractmethod
    def create_region(
        self,
        *,
        index: int,
        row: int,
        column: int,
        center_x: int,
        center_y: int,
        image_width: int,
        image_height: int,
    ) -> SpatialRegion:
        """Create region metadata for one grid position."""
        raise NotImplementedError

    def select(
        self,
        tensor: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        """Return the tensor view covered by the region.

        Expects:
            tensor shape [C, H, W]
        """
        return tensor[:, region.y0:region.y1, region.x0:region.x1]

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\geometry\square_provider.py
from cscience.features.api import SpatialRegion

from .geometry_provider import GeometryProvider


class SquareProvider(GeometryProvider):
    """Square or rectangular region provider based on relative window size.
    geometry_size: tuple[float, float] - relative size of the region (height, width) in relation to the image dimensions.
    """

    def __init__(self, geometry_size: tuple[float, float]) -> None:
        self.geometry_size = geometry_size

    def create_region(
        self,
        *,
        index: int,
        row: int,
        column: int,
        center_x: int,
        center_y: int,
        image_width: int,
        image_height: int,
    ) -> SpatialRegion:
        region_h_rel, region_w_rel = self.geometry_size

        win_w = max(1, round(region_w_rel * image_width))
        win_h = max(1, round(region_h_rel * image_height))

        x0 = center_x - win_w // 2
        y0 = center_y - win_h // 2

        x0 = max(0, min(image_width - win_w, x0))
        y0 = max(0, min(image_height - win_h, y0))

        x1 = x0 + win_w
        y1 = y0 + win_h

        return SpatialRegion(
            index=index,
            row=row,
            column=column,
            center_x=center_x,
            center_y=center_y,
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            nx0=x0 / image_width,
            ny0=y0 / image_height,
            nx1=x1 / image_width,
            ny1=y1 / image_height,
        )

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\indexer\spatial_index.py
from dataclasses import dataclass

from cscience.features.api.datatypes.spatial.spatial_region import SpatialRegion


@dataclass(frozen=True, slots=True)
class SpatialIndex:
    """Resolved spatial index entry."""

    item_index: int
    item_key: int
    region_index: int
    flat_index: int
    region: SpatialRegion


# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\indexer\spatial_indexer.py
from dataclasses import dataclass

from cscience.features.api import SpatialBatchLayout, SpatialRegion
from .spatial_index import SpatialIndex

from ..geometry.geometry_provider import GeometryProvider




class SpatialIndexer:
    """Creates spatial regions and maps local indices to flat batch indices.
    grid_shape: tuple[int, int] - number of rows (height) and columns (width) in the grid.
    start_point: tuple[float, float] - normalized starting point y (row), x (column) for the first region in the grid.
    step_size: tuple[float, float] - normalized step size y (row), x (column) for moving to the next region in the grid.
    geometry: GeometryProvider - provider for creating spatial regions based on the grid and image dimensions.
    """

    def __init__(
        self,
        *,
        item_keys: tuple[int, ...],
        image_width: int,
        image_height: int,
        grid_shape: tuple[int, int],
        start_point: tuple[float, float],
        step_size: tuple[float, float],
        geometry: GeometryProvider,
    ) -> None:
        self.item_keys = item_keys
        self.image_width = image_width
        self.image_height = image_height
        self.grid_shape = grid_shape
        self.start_point = start_point
        self.step_size = step_size
        self.geometry = geometry

        self.regions = self._build_regions()

        self.layout = SpatialBatchLayout(
            item_count=len(item_keys),
            regions_per_item=len(self.regions),
        )

    def __len__(self) -> int:
        return self.layout.flat_count

    def local_region_count(self) -> int:
        return self.layout.regions_per_item

    def _build_regions(self) -> tuple[SpatialRegion, ...]:
        rows, columns = self.grid_shape
        start_y, start_x = self.start_point
        step_y, step_x = self.step_size

        regions: list[SpatialRegion] = []

        for row in range(rows):
            for column in range(columns):
                index = row * columns + column

                center_x = round((start_x + column * step_x) * self.image_width)
                center_y = round((start_y + row * step_y) * self.image_height)

                center_x = max(0, min(self.image_width - 1, center_x))
                center_y = max(0, min(self.image_height - 1, center_y))

                region = self.geometry.create_region(
                    index=index,
                    row=row,
                    column=column,
                    center_x=center_x,
                    center_y=center_y,
                    image_width=self.image_width,
                    image_height=self.image_height,
                )

                regions.append(region)

        return tuple(regions)

    def iter_regions(self) -> tuple[SpatialRegion, ...]:
        return self.regions

    def iter_indices(self):
        """Yield all global flat indices with local item/region metadata."""
        for item_index, item_key in enumerate(self.item_keys):
            for region in self.regions:
                flat_index = self.layout.to_flat_index(
                    item_index=item_index,
                    region_index=region.index,
                )

                yield SpatialIndex(
                    item_index=item_index,
                    item_key=item_key,
                    region_index=region.index,
                    flat_index=flat_index,
                    region=region,
                )

    def from_flat_index(self, flat_index: int) -> SpatialIndex:
        item_index, region_index = self.layout.from_flat_index(flat_index)
        item_key = self.item_keys[item_index]
        region = self.regions[region_index]

        return SpatialIndex(
            item_index=item_index,
            item_key=item_key,
            region_index=region_index,
            flat_index=flat_index,
            region=region,
        )

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\masking\masking_generator.py
import torch
import torch.nn.functional as F

from cscience.features.api import SpatialBatchLayout, SpatialRegion

from ..filter.filter_provider import FilterProvider
from ..geometry.geometry_provider import GeometryProvider
from ..indexer.spatial_indexer import SpatialIndexer
from .masking_mode import MaskingMode


class MaskingGenerator:
    """Creates masked or extracted image variants for spatial CLIP."""

    def __init__(
        self,
        *,
        indexer: SpatialIndexer,
        geometry: GeometryProvider,
        filter_provider: FilterProvider,
        mode: MaskingMode,
    ) -> None:
        self.indexer = indexer
        self.geometry = geometry
        self.filter_provider = filter_provider
        self.mode = mode

    @property
    def layout(self) -> SpatialBatchLayout:
        return self.indexer.layout

    @property
    def regions(self) -> tuple[SpatialRegion, ...]:
        return self.indexer.regions

    @property
    def item_keys(self) -> tuple[int, ...]:
        return self.indexer.item_keys

    def generate(self, base_tensors: torch.Tensor) -> torch.Tensor:
        """Return masked/extracted variants.

        Input:
            [N, C, H, W]

        Output:
            [N * R, C, H, W]
        """
        if base_tensors.ndim != 4:
            raise ValueError(
                f"Expected base_tensors [N, C, H, W], got {tuple(base_tensors.shape)}."
            )

        if base_tensors.shape[0] != self.layout.item_count:
            raise ValueError(
                f"Tensor item count must match layout.item_count: "
                f"{base_tensors.shape[0]} != {self.layout.item_count}."
            )

        variants: list[torch.Tensor] = []

        for spatial_index in self.indexer.iter_indices():
            base = base_tensors[spatial_index.item_index]
            variant = self._make_variant(base, spatial_index.region)
            variants.append(variant)

        result = torch.stack(variants)

        if result.shape[0] != self.layout.flat_count:
            raise RuntimeError(
                f"Expected {self.layout.flat_count} variants, got {result.shape[0]}."
            )

        return result

    def _make_variant(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        if self.mode == MaskingMode.MASK_OUT:
            return self._mask_out(base, region)

        if self.mode == MaskingMode.KEEP_ONLY:
            return self._keep_only(base, region)

        if self.mode == MaskingMode.EXTRACT:
            return self._extract(base, region)

        raise ValueError(f"Unknown masking mode: {self.mode}.")

    def _mask_out(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        variant = base.clone()
        window = self.geometry.select(variant, region)

        fill = self.filter_provider.create_fill(
            base_tensor=base,
            region=region,
            window=window,
        )

        window[:, :, :] = fill
        return variant

    def _keep_only(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        variant = torch.zeros_like(base)

        dst = self.geometry.select(variant, region)
        src = self.geometry.select(base, region)

        dst[:, :, :] = src

        return variant

    def _extract(
        self,
        base: torch.Tensor,
        region: SpatialRegion,
    ) -> torch.Tensor:
        crop = self.geometry.select(base, region)
        crop = crop.unsqueeze(0)

        resized = F.interpolate(
            crop,
            size=base.shape[-2:],
            mode="bilinear",
            align_corners=False,
        )

        return resized.squeeze(0)

# From cscience-feature-clip-spatial\src\cscience\features\clip_spatial\masking\masking_mode.py
from enum import Enum


class MaskingMode(str, Enum):
    MASK_OUT = "mask_out"
    KEEP_ONLY = "keep_only"
    EXTRACT = "extract"

# From cscience-feature-clip-spatial\tests\test_clip_spatial_datatype_architecture.py
import unittest

from cscience.features.api import (
    DatatypeBase,
    EmbeddingBase,
    SpatialPrimitiveVectorBatchBase,
    SpatialVectorBatchBase,
    VectorBatchBase,
)

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_datatype import (
    ClipSpatialDatatype,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)


CLIP_SPATIAL_DATATYPES = (
    ClipSpatialTensorBatch,
    ClipSpatialTextTensorBatch,
    SpatialScoreVectorBatch,
)


class TestClipSpatialDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_clip_spatial_namespace(
        self,
    ) -> None:
        for datatype_class in CLIP_SPATIAL_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "clip_spatial",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in CLIP_SPATIAL_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        ClipSpatialDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in CLIP_SPATIAL_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_spatial_tensor_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipSpatialTensorBatch.__mro__

        self.assertLess(
            mro.index(SpatialVectorBatchBase),
            mro.index(ClipSpatialDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipSpatialDatatype),
        )

    def test_text_tensor_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipSpatialTextTensorBatch.__mro__

        self.assertLess(
            mro.index(VectorBatchBase),
            mro.index(ClipSpatialDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipSpatialDatatype),
        )

    def test_score_structure_precedes_namespace(
        self,
    ) -> None:
        mro = SpatialScoreVectorBatch.__mro__

        self.assertLess(
            mro.index(SpatialPrimitiveVectorBatchBase),
            mro.index(ClipSpatialDatatype),
        )

    def test_scores_are_not_embeddings(self) -> None:
        self.assertFalse(
            issubclass(
                SpatialScoreVectorBatch,
                EmbeddingBase,
            )
        )

import torch

from cscience.features.api import (
    SpatialBatchLayout,
    SpatialRegion,
    SpatialVectorBatchData,
)


def make_regions() -> tuple[SpatialRegion, ...]:
    return (
        SpatialRegion(
            index=0,
            row=0,
            column=0,
            center_x=5,
            center_y=5,
            x0=0,
            y0=0,
            x1=10,
            y1=10,
            nx0=0.0,
            ny0=0.0,
            nx1=0.5,
            ny1=1.0,
        ),
        SpatialRegion(
            index=1,
            row=0,
            column=1,
            center_x=15,
            center_y=5,
            x0=10,
            y0=0,
            x1=20,
            y1=10,
            nx0=0.5,
            ny0=0.0,
            nx1=1.0,
            ny1=1.0,
        ),
    )


def make_spatial_tensor_data(
) -> SpatialVectorBatchData[torch.Tensor]:
    return SpatialVectorBatchData(
        vectors={
            0: torch.tensor([0.0, 0.1, 0.2]),
            1: torch.tensor([1.0, 1.1, 1.2]),
            2: torch.tensor([2.0, 2.1, 2.2]),
            3: torch.tensor([3.0, 3.1, 3.2]),
        },
        layout=SpatialBatchLayout(
            item_count=2,
            regions_per_item=2,
        ),
        item_keys=(10, 20),
        regions=make_regions(),
    )

import unittest

import torch

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)


class TestClipSpatialTensorBatch(unittest.TestCase):
    def test_constructs_spatial_embedding_batch(self) -> None:
        batch = ClipSpatialTensorBatch(
            make_spatial_tensor_data()
        )

        self.assertEqual(batch.batch_size(), 4)
        self.assertEqual(batch.item_count(), 2)
        self.assertEqual(batch.regions_per_item(), 2)
        self.assertEqual(batch.length(), 3)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_returns_flat_tensor(self) -> None:
        batch = ClipSpatialTensorBatch(
            make_spatial_tensor_data()
        )

        flat = batch.as_flat_tensor()

        self.assertEqual(tuple(flat.shape), (4, 3))
        self.assertTrue(
            torch.equal(
                flat[2],
                torch.tensor([2.0, 2.1, 2.2]),
            )
        )

    def test_returns_structured_tensor(self) -> None:
        batch = ClipSpatialTensorBatch(
            make_spatial_tensor_data()
        )

        structured = batch.as_structured_tensor()

        self.assertEqual(
            tuple(structured.shape),
            (2, 2, 3),
        )

    def test_rejects_non_tensor_vector(self) -> None:
        data = make_spatial_tensor_data()
        invalid = SpatialVectorBatchData(
            vectors={
                **data.vectors,
                3: [3.0, 3.1, 3.2],
            },
            layout=data.layout,
            item_keys=data.item_keys,
            regions=data.regions,
        )

        with self.assertRaises(TypeError):
            ClipSpatialTensorBatch(invalid)

    def test_rejects_non_vector_tensor(self) -> None:
        data = make_spatial_tensor_data()
        invalid = SpatialVectorBatchData(
            vectors={
                **data.vectors,
                3: torch.zeros((1, 3)),
            },
            layout=data.layout,
            item_keys=data.item_keys,
            regions=data.regions,
        )

        with self.assertRaises(ValueError):
            ClipSpatialTensorBatch(invalid)

    def test_rejects_integer_tensor(self) -> None:
        data = make_spatial_tensor_data()
        invalid = SpatialVectorBatchData(
            vectors={
                **data.vectors,
                3: torch.tensor([1, 2, 3]),
            },
            layout=data.layout,
            item_keys=data.item_keys,
            regions=data.regions,
        )

        with self.assertRaises(TypeError):
            ClipSpatialTensorBatch(invalid)


import unittest

import torch

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)


class TestClipSpatialTextTensorBatch(unittest.TestCase):
    def test_constructs_text_embedding_batch(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(20, 10),
            vectors=torch.tensor(
                [
                    [2.0, 2.1, 2.2],
                    [1.0, 1.1, 1.2],
                ]
            ),
        )

        batch = ClipSpatialTextTensorBatch(data)

        self.assertEqual(batch.keys, (20, 10))
        self.assertEqual(batch.ordered_keys(), (10, 20))
        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_orders_vectors_by_text_key(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(20, 10),
            vectors=torch.tensor(
                [
                    [2.0, 2.1],
                    [1.0, 1.1],
                ]
            ),
        )

        batch = ClipSpatialTextTensorBatch(data)
        ordered = batch.ordered_values()

        self.assertTrue(
            torch.equal(
                ordered[0],
                torch.tensor([1.0, 1.1]),
            )
        )

    def test_rejects_duplicate_keys(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(10, 10),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipSpatialTextTensorBatch(data)

    def test_rejects_key_row_mismatch(self) -> None:
        data = ClipSpatialTextTensorBatchData(
            keys=(10,),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipSpatialTextTensorBatch(data)


import unittest

from cscience.features.api import SpatialVectorBatchData

from cscience.features.clip_spatial.clip_spatial_datatypes.spatial_score_vector_batch import (
    SpatialScoreVectorBatch,
)


def make_score_data(
) -> SpatialVectorBatchData[list[float]]:
    tensor_data = make_spatial_tensor_data()

    return SpatialVectorBatchData(
        vectors={
            0: [0.1, 0.2],
            1: [0.3, 0.4],
            2: [0.5, 0.6],
            3: [0.7, 0.8],
        },
        layout=tensor_data.layout,
        item_keys=tensor_data.item_keys,
        regions=tensor_data.regions,
    )


class TestSpatialScoreVectorBatch(unittest.TestCase):
    def test_constructs_score_batch(self) -> None:
        batch = SpatialScoreVectorBatch(
            make_score_data(),
            query_keys=(100, 200),
        )

        self.assertEqual(batch.query_keys, (100, 200))
        self.assertEqual(batch.query_count, 2)
        self.assertEqual(batch.length(), 2)
        self.assertEqual(batch.namespace, "clip_spatial")

    def test_rejects_query_count_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(100,),
            )

    def test_rejects_empty_query_keys(self) -> None:
        with self.assertRaises(ValueError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(),
            )

    def test_rejects_duplicate_query_keys(self) -> None:
        with self.assertRaises(ValueError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(100, 100),
            )

    def test_rejects_non_integer_query_key(self) -> None:
        with self.assertRaises(TypeError):
            SpatialScoreVectorBatch(
                make_score_data(),
                query_keys=(
                    100,
                    "200",  # type: ignore[arg-type]
                ),
            )

# From cscience-feature-clip-spatial\tests\test_clip_spatial_scoring.py
import unittest

import torch

from cscience.features.api import (
    SpatialBatchLayout,
    SpatialRegion,
    SpatialVectorBatchData,
)

from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_tensor_batch import (
    ClipSpatialTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch import (
    ClipSpatialTextTensorBatch,
)
from cscience.features.clip_spatial.clip_spatial_datatypes.clip_spatial_text_tensor_batch_data import (
    ClipSpatialTextTensorBatchData,
)
from cscience.features.clip_spatial.clip_spatial_feature import (
    ClipSpatialFeature,
)


def make_regions() -> tuple[SpatialRegion, ...]:
    return (
        SpatialRegion(
            index=0,
            row=0,
            column=0,
            center_x=5,
            center_y=5,
            x0=0,
            y0=0,
            x1=10,
            y1=10,
            nx0=0.0,
            ny0=0.0,
            nx1=0.5,
            ny1=1.0,
        ),
        SpatialRegion(
            index=1,
            row=0,
            column=1,
            center_x=15,
            center_y=5,
            x0=10,
            y0=0,
            x1=20,
            y1=10,
            nx0=0.5,
            ny0=0.0,
            nx1=1.0,
            ny1=1.0,
        ),
    )


def make_spatial_vectors() -> ClipSpatialTensorBatch:
    return ClipSpatialTensorBatch(
        SpatialVectorBatchData(
            vectors={
                0: torch.tensor([1.0, 0.0]),
                1: torch.tensor([0.0, 1.0]),
                2: torch.tensor([0.5, 0.5]),
                3: torch.tensor([-1.0, 0.0]),
            },
            layout=SpatialBatchLayout(
                item_count=2,
                regions_per_item=2,
            ),
            item_keys=(10, 20),
            regions=make_regions(),
        )
    )


def make_text_vectors() -> ClipSpatialTextTensorBatch:
    return ClipSpatialTextTensorBatch(
        ClipSpatialTextTensorBatchData(
            keys=(100, 200),
            vectors=torch.tensor(
                [
                    [1.0, 0.0],
                    [0.0, 1.0],
                ]
            ),
        )
    )


class TestClipSpatialScoring(unittest.TestCase):
    def test_scores_queries_against_regions(self) -> None:
        result = ClipSpatialFeature.score_embeddings(
            text_vectors=make_text_vectors(),
            spatial_vectors=make_spatial_vectors(),
        )

        self.assertEqual(
            result.query_keys,
            (100, 200),
        )
        self.assertEqual(result.query_count, 2)
        self.assertEqual(result.item_keys, (10, 20))
        self.assertEqual(result.batch_size(), 4)

        self.assertEqual(
            result.vector_at(0, 0),
            [1.0, 0.0],
        )
        self.assertEqual(
            result.vector_at(0, 1),
            [0.0, 1.0],
        )
        self.assertEqual(
            result.vector_at(1, 0),
            [0.5, 0.5],
        )
        self.assertEqual(
            result.vector_at(1, 1),
            [-1.0, 0.0],
        )

    def test_preserves_spatial_metadata(self) -> None:
        spatial = make_spatial_vectors()

        result = ClipSpatialFeature.score_embeddings(
            text_vectors=make_text_vectors(),
            spatial_vectors=spatial,
        )

        self.assertEqual(result.layout, spatial.layout)
        self.assertEqual(result.regions, spatial.regions)
        self.assertEqual(result.item_keys, spatial.item_keys)

    def test_rejects_embedding_dimension_mismatch(
        self,
    ) -> None:
        text_vectors = ClipSpatialTextTensorBatch(
            ClipSpatialTextTensorBatchData(
                keys=(100,),
                vectors=torch.tensor(
                    [[1.0, 0.0, 0.0]]
                ),
            )
        )

        with self.assertRaises(ValueError):
            ClipSpatialFeature.score_embeddings(
                text_vectors=text_vectors,
                spatial_vectors=make_spatial_vectors(),
            )

# From cscience-feature-clip-spatial\tests\test_masking_generator.py
import unittest
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from cscience.features.clip_spatial.filter.zero_provider import ZeroProvider
from cscience.features.clip_spatial.geometry.square_provider import SquareProvider
from cscience.features.clip_spatial.indexer.spatial_indexer import SpatialIndexer
from cscience.features.clip_spatial.masking.masking_generator import MaskingGenerator
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def load_fixture_tensor(name: str, size: tuple[int, int] = (224, 224)) -> torch.Tensor:
    image = Image.open(FIXTURE_DIR / name).convert("RGB").resize(size)
    array = np.asarray(image, dtype=np.float32) / 255.0

    return torch.from_numpy(array).permute(2, 0, 1)


def make_indexer(
    item_keys: tuple[int, ...],
    image_width: int = 224,
    image_height: int = 224,
) -> tuple[SpatialIndexer, SquareProvider]:
    geometry = SquareProvider(
        geometry_size=(1 / 3, 1 / 3),
    )

    indexer = SpatialIndexer(
        item_keys=item_keys,
        image_width=image_width,
        image_height=image_height,
        grid_shape=(3, 3),
        start_point=(1 / 6, 1 / 6),
        step_size=(1 / 3, 1 / 3),
        geometry=geometry,
    )

    return indexer, geometry


class MaskingGeneratorTest(unittest.TestCase):

    def test_keep_only_creates_flat_spatial_batch_for_one_image(self) -> None:
        base = load_fixture_tensor("dogbird.png").unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.KEEP_ONLY,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (9, 3, 224, 224))
        self.assertEqual(generator.layout.flat_count, 9)
        self.assertEqual(generator.item_keys, (0,))
        self.assertEqual(len(generator.regions), 9)

        region = generator.regions[0]

        selected = result[0, :, region.y0:region.y1, region.x0:region.x1]
        expected = base[0, :, region.y0:region.y1, region.x0:region.x1]

        self.assertTrue(torch.allclose(selected, expected))

        outside_mask = torch.ones_like(result[0], dtype=torch.bool)
        outside_mask[:, region.y0:region.y1, region.x0:region.x1] = False

        self.assertTrue(torch.all(result[0][outside_mask] == 0.0))

    def test_mask_out_zeroes_only_selected_region(self) -> None:
        base = load_fixture_tensor("catdog.png").unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.MASK_OUT,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (9, 3, 224, 224))

        region = generator.regions[4]

        selected = result[4, :, region.y0:region.y1, region.x0:region.x1]
        self.assertTrue(torch.all(selected == 0.0))

        outside_mask = torch.ones_like(result[4], dtype=torch.bool)
        outside_mask[:, region.y0:region.y1, region.x0:region.x1] = False

        self.assertTrue(torch.allclose(result[4][outside_mask], base[0][outside_mask]))

    def test_extract_keeps_stackable_shape(self) -> None:
        base = load_fixture_tensor("astronaut.png").unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.EXTRACT,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (9, 3, 224, 224))

    def test_batch_two_images_creates_n_times_r_variants(self) -> None:
        dogbird = load_fixture_tensor("dogbird.png")
        catdog = load_fixture_tensor("catdog.png")
        base = torch.stack([dogbird, catdog])

        indexer, geometry = make_indexer(item_keys=(10, 20))

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=ZeroProvider(),
            mode=MaskingMode.KEEP_ONLY,
        )

        result = generator.generate(base)

        self.assertEqual(tuple(result.shape), (18, 3, 224, 224))
        self.assertEqual(generator.layout.item_count, 2)
        self.assertEqual(generator.layout.regions_per_item, 9)
        self.assertEqual(generator.layout.flat_count, 18)
        self.assertEqual(generator.item_keys, (10, 20))

# From cscience-feature-clip-spatial\tests\test_spatial_feature.py


# From cscience-feature-clip-spatial\tests\test_spatial_indexer.py
import unittest

from cscience.features.clip_spatial.geometry.square_provider import SquareProvider
from cscience.features.clip_spatial.indexer.spatial_indexer import SpatialIndexer


class SpatialIndexerTest(unittest.TestCase):

    def test_builds_expected_3x3_regions(self) -> None:
        geometry = SquareProvider(
            geometry_size=(1 / 3, 1 / 3),
        )

        indexer = SpatialIndexer(
            item_keys=(10, 20),
            image_width=224,
            image_height=224,
            grid_shape=(3, 3),
            start_point=(1 / 6, 1 / 6),
            step_size=(1 / 3, 1 / 3),
            geometry=geometry,
        )

        self.assertEqual(indexer.layout.item_count, 2)
        self.assertEqual(indexer.layout.regions_per_item, 9)
        self.assertEqual(indexer.layout.flat_count, 18)
        self.assertEqual(len(indexer.regions), 9)

        first = indexer.regions[0]
        self.assertEqual(first.index, 0)
        self.assertEqual(first.grid_yx, (0, 0))
        self.assertEqual(first.grid_xy, (0, 0))

        center = indexer.regions[4]
        self.assertEqual(center.index, 4)
        self.assertEqual(center.grid_yx, (1, 1))
        self.assertEqual(center.grid_xy, (1, 1))

    def test_flat_index_mapping_preserves_item_and_region(self) -> None:
        geometry = SquareProvider(
            geometry_size=(1 / 3, 1 / 3),
        )

        indexer = SpatialIndexer(
            item_keys=(100, 200),
            image_width=224,
            image_height=224,
            grid_shape=(3, 3),
            start_point=(1 / 6, 1 / 6),
            step_size=(1 / 3, 1 / 3),
            geometry=geometry,
        )

        flat = indexer.layout.to_flat_index(
            item_index=1,
            region_index=5,
        )

        spatial_index = indexer.from_flat_index(flat)

        self.assertEqual(flat, 14)
        self.assertEqual(spatial_index.item_index, 1)
        self.assertEqual(spatial_index.item_key, 200)
        self.assertEqual(spatial_index.region_index, 5)
        self.assertEqual(spatial_index.region.index, 5)

# From cscience-feature-clip-spatial\tests\test_visual_cutting.py
import unittest
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from cscience.features.api.datatypes.image.pil_image import PilImage
from cscience.features.clip_spatial.filter.filter_provider import FilterProvider
from cscience.features.clip_spatial.filter.zero_provider import ZeroProvider
from cscience.features.clip_spatial.geometry.square_provider import SquareProvider
from cscience.features.clip_spatial.indexer.spatial_indexer import SpatialIndexer
from cscience.features.clip_spatial.masking.masking_generator import MaskingGenerator
from cscience.features.clip_spatial.masking.masking_mode import MaskingMode

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def make_indexer(
    item_keys: tuple[int, ...],
    image_width: int = 224,
    image_height: int = 224,
) -> tuple[SpatialIndexer, SquareProvider]:
    geometry = SquareProvider(
        geometry_size=(1 / 3, 1 / 4),
    )

    indexer = SpatialIndexer(
        item_keys=item_keys,
        image_width=image_width,
        image_height=image_height,
        grid_shape=(5, 7),
        start_point=(1 / 6, 1 / 8),
        step_size=(1 / 6, 1 / 8),
        geometry=geometry,
    )

    return indexer, geometry


class TestVisualIndexing(unittest.TestCase):

    image_set: dict[tuple[str,str,str], PilImage] = {}


    @classmethod
    def setUpClass(cls) -> None:
        images = Path(FIXTURE_DIR/ "images-gen").glob("**/*.jpg")

        for image in images:
            pil_image = Image.open(image).convert("RGB")
            cls.image_set[(image.parent.parent.name, image.parent.name, image.stem)] = PilImage(pil_image)
            break

    def _directory_from_key(self, key: tuple[str,str,str], mode: MaskingMode) -> Path:
        return Path(FIXTURE_DIR) / "images-out" / mode / key[0] / key[1] / key[2]

    def test_keep_only(self) -> None:

        for key, image in self.image_set.items():
            self._run(key, image, MaskingMode.KEEP_ONLY, ZeroProvider())


    def test_mask_out(self) -> None:

        for key, image in self.image_set.items():
            self._run(key, image, MaskingMode.MASK_OUT, ZeroProvider())


    def test_extract(self) -> None:
        for key, image in self.image_set.items():
            self._run(key, image, MaskingMode.EXTRACT, ZeroProvider())

    def _run(self, key:tuple[str,str,str], image:PilImage, mode: MaskingMode, filter: FilterProvider) -> None:


        array = np.asarray(image.data(), dtype=np.float32) / 255.0
        image_tensor = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)

        indexer, geometry = make_indexer(item_keys=(0,), image_width=image.data().width,
                                         image_height=image.data().height)

        generator = MaskingGenerator(
            indexer=indexer,
            geometry=geometry,
            filter_provider=filter,
            mode=mode,
        )

        result = generator.generate(image_tensor)
        result_np = result.permute(0, 2, 3, 1).detach().cpu().numpy()

        # Temporary Store
        output_dir = self._directory_from_key(key, mode)
        output_dir.mkdir(parents=True, exist_ok=True)

        for i in range(result_np.shape[0]):
            Image.fromarray((result_np[i] * 255).astype('uint8'), mode='RGB').save(
                output_dir / f"{key[2]}_{i}.jpg", "JPEG")

# From cscience-feature-clip-spatial\tests\utils\ClipMaskedInformationCluster.py
import numpy as np
import torch
from PIL import Image
from fractions import Fraction

from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import  MaskingGenerator
from .OpenClipScoringService import OpenClipScoringService
from cscience.features.clip_spatial.clip_spatial_feature.Geometry.SquareProvider import SquareProvider
from cscience.features.clip_spatial.clip_spatial_feature.Filter.ZeroProvider import ZeroProvider
from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingMode import  MaskingMode
from util.visualization_util import taget_point_hard, taget_point_soft

class ClipMaskedInformationCluster:

    def __init__(self, **kwargs):
        self.clip_service = OpenClipScoringService()
        self.geometry_size = kwargs.get("geometry_size", (Fraction(1 / 3).limit_denominator(),Fraction(1 / 3).limit_denominator()))  # relative to image size
        self.step_size = kwargs.get("step_size", (Fraction(1 / 3).limit_denominator(), Fraction(1 / 3).limit_denominator()))  # relative to image size
        self.start_point = kwargs.get("start_point", (Fraction(1 / 6).limit_denominator(), Fraction(1 / 6).limit_denominator()))  # pixel offset relative to image size
        self.steps = kwargs.get("steps", (3, 3))  # number of steps in h,w
        self.mode = kwargs.get("mode", MaskingMode.KEEP_ONLY)
        self.geometry = SquareProvider(geometry_size=self.geometry_size)
        self.filters = ZeroProvider()
        self.settings = {
            "geometry_size": self.geometry_size,
            "step_size": self.step_size,
            "start_point": self.start_point,
            "tiling": self.steps,
            "length": self.steps[0] * self.steps[1],
            "mode": self.mode,
            "geometry": type(self.geometry).__name__,
            "filter": type(self.filters).__name__,
            "clip_service": type(self.clip_service).__name__
        }

    def embedd_text(self, text: str):
        text_tokens = self.clip_service.tokenize(text)
        txt_f = self.clip_service.clip_embedd_norm_txt_vectors(text_tokens)
        return txt_f

    def imageTextPair(self, image: Image, text: str):
        text_tokens = self.clip_service.tokenize(text)
        txt_f = self.clip_service.clip_embedd_norm_txt_vectors(text_tokens)
        img_f_base, batch_img_f_masked, generator = self.imageVectors(image)
        scores, point_hard, point_soft = self.imageTextVectorPair(img_f_base, batch_img_f_masked, txt_f,
                                                                  generator.image_w, generator.image_h)
        return scores, point_hard, point_soft, generator

    def imageTextPair_response(self, image: Image, text: str):
        scores, point_hard, point_soft, generator = self.imageTextPair(image, text)
        response = {
            "settings": self.settings,
            "processed_image_w": generator.image_w,
            "processed_image_h": generator.image_h,
            "scores": scores.detach().cpu().numpy().tolist(),
            "best_idx": int(torch.argmax(scores).item()),
            "point_hard": point_hard,
            "point_soft": point_soft,
        }
        return response

    def imageVectors(self, image: Image):
        base_img_tensor = self.clip_service.preprocess(image)  # [1,3,224,224]$

        generator = MaskingGenerator(self.step_size, self.start_point, self.steps, base_img_tensor, self.geometry,
                                     self.filters, device=self.clip_service._device, mode=self.mode)
        base_img_tensor, batch_img_tensor = generator.factory()
        img_f_base = self.clip_service.clip_embedd_norm_img_vectors(base_img_tensor)
        batch_img_f_masked = self.clip_service.clip_embedd_norm_img_vectors(batch_img_tensor)
        return img_f_base, batch_img_f_masked, generator

    def imageVectors_response(self, image: Image):
        img_f_base, batch_img_f_masked, generator = self.imageVectors(image)
        batch = batch_img_f_masked.detach().cpu().numpy().tolist()
        numberedBatch_img_f_masked =  [{"position": f"batch_img_f_masked_{generator[i].get_xy_tile_coordinates()}", "idx": i, "img_f":b}  for (b, i) in zip(batch, range(len(batch)))]
        response = {
            "settings": self.settings,
            "processed_image_w": generator.image_w,
            "processed_image_h": generator.image_h,
            "img_f_base": img_f_base.detach().cpu().numpy().tolist(),
            "batch_img_f_masked": numberedBatch_img_f_masked
        }

        return response

    def imageTextVectorPair(self,
                            img_f_base: torch.Tensor,
                            batch_img_f_masked: torch.Tensor,
                            txt_f: torch.Tensor,
                            processed_image_w,
                            processed_image_h):
        scores = self.clip_service.influence_calculator(img_f_base, batch_img_f_masked, txt_f, self.mode,
                                                        normalize=False)
        max_idx = np.argmax(scores.detach().cpu().numpy())
        dummy_image_tensor = torch.zeros((1, 3, processed_image_h, processed_image_w), device=self.clip_service._device)
        dummy_generator = MaskingGenerator(self.step_size, self.start_point, self.steps, dummy_image_tensor,
                                           self.geometry,
                                           self.filters, device=self.clip_service._device, mode=self.mode)
        point_hard = taget_point_hard(scores, dummy_generator)
        point_soft = taget_point_soft(scores, dummy_generator)
        return scores, point_hard, point_soft

    def imageTextVectorPair_response(self,
                                     img_f_base: torch.Tensor,
                                     batch_img_f_masked: torch.Tensor,
                                     txt_f: torch.Tensor,
                                     processed_image_w,
                                     processed_image_h):
        scores, point_hard, point_soft = self.imageTextVectorPair(img_f_base, batch_img_f_masked, txt_f, processed_image_w, processed_image_h)
        response = {
            "settings": self.settings,
            "processed_image_w": processed_image_w,
            "processed_image_h": processed_image_h,
            "scores": scores.detach().cpu().numpy().tolist(),
            "best_idx": int(torch.argmax(scores).item()),
            "point_hard": point_hard,
            "point_soft": point_soft,
        }
        return response


# From cscience-feature-clip-spatial\tests\utils\ClipMaskedInformationClusterTest.py
import argparse

import numpy as np
import torch
from PIL import Image
from matplotlib import pyplot as plt

from descriptors.clip_influence.ClipMaskedInformationInfluence import MaskingMode, ClipMaskedInformationCluster, \
    tensor_to_pil, show_overlay_any


def main(args):
    # Load and preprocess image
    kwargs = {
        "geometry_size": (1 / 3, 1 / 3),  # relative to image size
        "step_size": (1 / 3, 1 / 3),  # relative to image size
        "start_point": (1 / 6, 1 / 6),  # pixel offset relative to image size
        "steps": (3, 3),  # number of steps in h,w (1, 1) means one tile
        "mode": MaskingMode.KEEP_ONLY
    }
    cmi = ClipMaskedInformationCluster(**kwargs)

    iterations = zip(args.image_paths, args.labels)
    idx = 0
    for image_path, label in iterations:
        idx += 1
        img = Image.open(image_path).convert("RGB")
        scores, point_hard, point_soft, generator = cmi.imageTextPair(img, label)
        deltas_np = scores.cpu().numpy()
        max_index = np.argmax(deltas_np)
        # batch_img_f_masked[max_index] = 0.0  # zero-out most influential region
        # deltas = influence_calculator(img_f_base, batch_img_f_masked, txt_f,mode)
        # deltas = deltas
        image_weights = [5, 3]
        img_out = tensor_to_pil((image_weights[0]*generator.batch_img_tensor[max_index]+image_weights[1]*generator.base_img_tensor)/sum(image_weights), cmi.clip_service.preprocessor)
        show_overlay_any(img_out, scores, generator, alpha=0.5, label=label, idx=idx)
        show_overlay_any(img_out, scores, generator, alpha=0.5, label=label, title=False, idx=idx)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")

    p.add_argument("--image-paths", type=str, nargs="+",
                   default=[
                       "../../Resources/26caffb8-4062-45c2-b7c1-4b801527374a.webp",
                       "../../Resources/a38e4012-a690-49f8-aaef-b3789a39ed98.webp",
                       "../../Resources/cornflakes.webp",
                       "../../Resources/cornflakes.webp",
                       "../../Resources/kitchen2.webp",
                       "../../Resources/kitchen2.webp",
                       "../../Resources/sample1.jpg",
                       "../../Resources/sample1.jpg",
                       "../../Resources/sample1.jpg",
                       "../../Resources/astronaut.png",
                       "../../Resources/astronaut.png",
                       "../../Resources/catdog.png",
                       "../../Resources/catdog.png",
                       "../../Resources/dogbird.png",
                       "../../Resources/dogbird.png",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                       "../../Resources/shop1.webp",
                   ])

    p.add_argument("--labels", type=str, nargs="+",
                   default=[
                       "a silver kettle",
                       "a golden teapot",
                       "cornflakes on a table",
                       "a tea kettle on a cooking stove",
                       "a fridge with drawings",
                       "a tea kettle on a cooking stove",
                       "photo of a dog",
                       "a golden dog",
                       "a cat on the couch",
                       "an astronaut with an orange suit",
                       "a space shuttle model in background",
                       "a cat and a dog",
                       "a dog",
                       "a bird",
                       "a dog",
                       "a wheelchair",
                       "a plant beside a golden vase",
                       "photos on a wall",
                       "ceramics on the floor",
                       "a red carped on the floor",
                   ])

    main(p.parse_args())


# From cscience-feature-clip-spatial\tests\utils\visualization_util.py
import numpy as np
import torch
from PIL import Image
from matplotlib import pyplot as plt
import seaborn as sns
import torch.nn.functional as F
from matplotlib.axis import Axis

from cscience.features.clip_spatial.clip_spatial_feature.Masking.MaskingGenerator import MaskingGenerator

font_scale = 1.0
rc = {
    "grid.linestyle": "solid",
    "grid.linewidth": 0.6,
    "grid.alpha": 0.35,
    "axes.edgecolor": "black",
    "axes.linewidth": 0.8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "font.family": "serif",
    "font.serif": [
        "Computer Modern Roman",
        "CMU Serif",
        "Latin Modern Roman",
        "DejaVu Serif",
    ],
    "mathtext.fontset": "cm",
    "text.usetex": True,
    "font.size": 11.0 * font_scale,
    "axes.titlesize": 13.0 * font_scale,
    "axes.labelsize": 12.0 * font_scale,
    "xtick.labelsize": 11.0 * font_scale,
    "ytick.labelsize": 11.0 * font_scale,
    "legend.fontsize": 10.5 * font_scale,
    "figure.titlesize": 13.0 * font_scale,
    "axes.titlepad": 10.0,
    "axes.labelpad": 6.0,
    "legend.frameon": False,
}
sns.set_theme(style="ticks", context="paper", rc=rc)

def taget_point_hard(scores: torch.Tensor,  generator: MaskingGenerator) -> tuple[int, int]:
    _, best_idx = torch.max(scores, dim=0)
    generator.idx = int(best_idx.item())
    cx, cy = generator.get_xy_pixel_point()
    return cx, cy

def taget_point_soft(scores: torch.Tensor, generator: MaskingGenerator) -> tuple[int, int]:
    xs, ys = [], []
    w = torch.softmax(F.normalize(scores, dim=-1) / 0.05, dim=0)
    for g in generator:
        x, y = g.get_xy_pixel_point()
        xs.append(x)
        ys.append(y)

    xs = torch.tensor(xs, device=w.device, dtype=torch.float32)
    ys = torch.tensor(ys, device=w.device, dtype=torch.float32)

    cx = int(float((w * xs).sum().item()))
    cy = int(float((w * ys).sum().item()))
    return cx, cy


def show_overlay_any(image_pil_or_np, scores: torch.Tensor, generator: MaskingGenerator, alpha=0.45, label=None,  title=True, idx = None):
    if hasattr(image_pil_or_np, "convert"):
        img = np.array(image_pil_or_np.convert("RGB")).astype(np.float32) / 255.0
    else:
        img = image_pil_or_np.astype(np.float32)

    scores_cpu = scores.detach().float().cpu()  # <-- key fix

    H, W = generator.image_h, generator.image_w
    scores_tensor = torch.zeros((1, H, W), dtype=torch.float32)



    fig, ax = plt.subplots()



    for g in generator:  # resets idx internally
        val = float(scores_cpu[g.idx].item())
        g.geometry_fnc(scores_tensor)[:, :] = val

        px, py = g.get_xy_pixel_point()
        ax.text(px, py, f"${val:.2f}$\n${g.get_xy_tile_coordinates()}$", ha="center", va="center", color="w")

    ax.imshow(img)
    #ax.imshow(scores_tensor[0].numpy(), alpha=alpha, cmap="magma", interpolation="nearest")

    xh, yh = taget_point_hard(scores, generator)
    pal = sns.color_palette("Spectral", n_colors=10)
    ax.plot(xh, yh, "X", markersize=13, color=pal[9])
    xs, ys = taget_point_soft(scores, generator)
    ax.plot(xs, ys, "D", markersize=10, color=pal[7])

    ax.axis("off")
    if title and label is not None :
        ax.set_title(label)
    fig.tight_layout()
    # As pdf
    if idx is not None:
        label = f"{idx}-{str.replace(label, " ", "_")}"
    else:
        label = label if label else "overlay"

    fig.savefig(f"overlays/{label if title else f'{label}_noTitle'}.png", format="png", bbox_inches="tight", dpi=300)
    plt.show()


def tensor_to_pil(x, preprocess):
    """
    x: torch tensor [3,H,W] or [1,3,H,W] in *preprocessed* (normalized) space.
    preprocess: the transform returned by open_clip.create_model_and_transforms(...)
    Returns: PIL.Image in RGB, matching the tensor's spatial view (usually 224x224).
    """
    if x.ndim == 4:
        x = x[0]
    assert x.ndim == 3 and x.shape[0] == 3

    # Find torchvision.transforms.Normalize inside preprocess
    mean = std = None
    if hasattr(preprocess, "transforms"):
        for tr in preprocess.transforms:
            if tr.__class__.__name__ == "Normalize":
                mean = torch.tensor(tr.mean).view(3, 1, 1)
                std = torch.tensor(tr.std).view(3, 1, 1)
                break

    if mean is None or std is None:
        raise RuntimeError("Could not find Normalize(mean,std) inside preprocess.transforms")

    x = x.detach().cpu()
    x = x * std + mean  # unnormalize
    x = x.clamp(0.0, 1.0)  # valid image range
    x = (x.permute(1, 2, 0).numpy() * 255).astype(np.uint8)  # HWC uint8
    return Image.fromarray(x, mode="RGB")



# From cscience-feature-clip\src\cscience\features\clip\__init__.py
from cscience.features.api.registry.registry_base import RegistryBase

from .clip_connector import ClipConnector
from .clip_conversion_provider import ClipConversionProvider
from .clip_datatypes.clip_datatype import ClipDatatype
from .clip_datatypes.clip_tensor import ClipTensor
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch, ClipTensorBatchData
from .clip_feature import ClipFeature

__all__ = [
    "ClipConnector",
    "ClipConversionProvider",
    "ClipDatatype",
    "ClipFeature",
    "ClipTensor",
    "ClipTensorBatch",
    "ClipTensorBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("clip", ClipConversionProvider)

# From cscience-feature-clip\src\cscience\features\clip\clip_config.py
from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class ClipConfig(ConfigBase):


    @classmethod
    def _default_namespace(cls) -> str:
        return "clip"

    model_name:str = Field(
        default="xlm-roberta-base-ViT-B-32",
        description="The name of the CLIP model to use. Default is 'xlm-roberta-base-ViT-B-32'."
    )

    pretrained:str = Field(
        default="laion5b_s13b_b90k",
        description="The name of the pretrained model to use. Default is 'laion5b_s13b_b90k'."
    )

    preferred_device:str = Field(
        default="cuda",
        description="The device to use for inference. Default is 'cpu'."
    )

    force_device:bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )


# From cscience-feature-clip\src\cscience\features\clip\clip_connector.py
from PIL.Image import Image

from cscience.features.api.connector.connector_base import ConnectorBase
from cscience.features.api.connector.function_connector import FunctionConnector
from cscience.features.api.datatypes.image.pil_image import PilImage
from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import FloatVectorBatch
from cscience.features.api.datatypes.text.text import Text
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.api.feature.service_info import ServiceInfo
from .clip_config import ClipConfig

from .clip_conversion_provider import ClipConversionProvider
from .clip_datatypes.clip_tensor_batch import ClipTensorBatch
from .clip_feature import ClipFeature


class ClipConnector(ConnectorBase):
    """Public connector for CLIP text and image embeddings."""

    def __init__(self,  config: ClipConfig) -> None:
        self.feature = ClipFeature.get_instance(config, init_if_missing=True)
        super().__init__(ClipConversionProvider(self.feature))

    def text(self, data: str) -> list[float]:
        """Embed a single text string and return one float vector."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=Text,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVector,
        )

        return function(Text(data)).data()

    def text_batch(self, data: list[str]) -> dict[int, list[float]]:
        """Embed text strings and return vectors indexed by input position."""
        text_batch = TextBatch(
            {
                index: text
                for index, text in enumerate(data)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.text_batch,
            input_type=TextBatch,
            input_feature_type=TextBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVectorBatch,
        )

        return function(text_batch).data()

    def image(self, data: Image) -> list[float]:
        """Embed a single image and return one float vector."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVector,
        )

        return function(PilImage(data)).data()

    def image_batch(self, data: list[Image]) -> dict[int, list[float]]:
        """Embed images and return vectors indexed by input position."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(data)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.image_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=ClipTensorBatch,
            output_type=FloatVectorBatch,
        )

        return function(image_batch).data()

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="clip",
            name="CLIP",
            description="Text and image embedding service.",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()

# From cscience-feature-clip\src\cscience\features\clip\clip_conversion_provider.py
from typing import List

from cscience.features.api.conversion.conversion_provider_base import ConversionProviderBase
from cscience.features.api.conversion.converter import Converter
from cscience.features.api.datatypes.primitives_vectors.float_vector import FloatVector
from cscience.features.api.datatypes.primitives_vectors_batch.float_vector_batch import FloatVectorBatch
from cscience.features.api.feature.feature_base import FeatureBase

from .clip_datatypes.clip_tensor_batch import ClipTensorBatch


def clip_tensor_batch_passthrough(batch: ClipTensorBatch) -> ClipTensorBatch:
    return batch


def clip_tensor_batch_to_float_vector(batch: ClipTensorBatch) -> FloatVector:
    data = batch.data()

    if len(data.keys) != 1:
        raise ValueError(
            f"Cannot convert ClipTensorBatch of size {len(data.keys)} to FloatVector."
        )

    return FloatVector(data.vectors[0].tolist())


def clip_tensor_batch_to_float_vector_batch(batch: ClipTensorBatch) -> FloatVectorBatch:
    data = batch.data()

    return FloatVectorBatch(
        {
            key: vector.tolist()
            for key, vector in zip(data.keys, data.vectors)
        }
    )


class ClipConversionProvider(ConversionProviderBase):
    """Registers datatype conversions required by the CLIP connector."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> List[Converter]:
        return [
            Converter[ClipTensorBatch, ClipTensorBatch](
                name="clip_tensor_batch_passthrough",
                source=self._feature,
                function=clip_tensor_batch_passthrough,
                input_type=ClipTensorBatch,
                output_type=ClipTensorBatch,
            ),
            Converter[ClipTensorBatch, FloatVector](
                name="clip_tensor_batch_to_float_vector",
                source=self._feature,
                function=clip_tensor_batch_to_float_vector,
                input_type=ClipTensorBatch,
                output_type=FloatVector,
            ),
            Converter[ClipTensorBatch, FloatVectorBatch](
                name="clip_tensor_batch_to_float_vector_batch",
                source=self._feature,
                function=clip_tensor_batch_to_float_vector_batch,
                input_type=ClipTensorBatch,
                output_type=FloatVectorBatch,
            ),
        ]

# From cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_datatype.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)

T = TypeVar("T")


class ClipDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for CLIP-specific datatypes."""

    namespace = "clip"

# From cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor.py
from torch import Tensor

from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)

from .clip_datatype import ClipDatatype


class ClipTensor(
    VectorBase,
    EmbeddingBase,
    ClipDatatype[Tensor],
):
    """Single CLIP embedding tensor with shape [D]."""

    def __init__(self, data: Tensor) -> None:
        if not isinstance(data, Tensor):
            raise TypeError(
                f"ClipTensor expects Tensor, "
                f"got {type(data).__name__}."
            )

        if data.ndim != 1:
            raise ValueError(
                "ClipTensor expects a 1D tensor, "
                f"got shape {tuple(data.shape)}."
            )

        if data.numel() == 0:
            raise ValueError(
                "ClipTensor cannot be empty."
            )

        if not data.is_floating_point():
            raise TypeError(
                "ClipTensor expects a floating-point tensor, "
                f"got {data.dtype}."
            )

        super().__init__(data)

# From cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor_batch.py
from collections.abc import Mapping

from torch import Tensor

from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)

from .clip_datatype import ClipDatatype
from .clip_tensor_batch_data import ClipTensorBatchData


class ClipTensorBatch(
    VectorBatchBase[Tensor],
    EmbeddingBase,
    ClipDatatype[ClipTensorBatchData],
):
    """Packed batch of CLIP embedding tensors with stable source keys."""

    def __init__(
        self,
        data: ClipTensorBatchData,
    ) -> None:
        if not isinstance(data, ClipTensorBatchData):
            raise TypeError(
                f"ClipTensorBatch expects ClipTensorBatchData, "
                f"got {type(data).__name__}."
            )

        vectors = data.vectors
        keys = data.keys

        if not isinstance(vectors, Tensor):
            raise TypeError(
                f"ClipTensorBatch vectors expect Tensor, "
                f"got {type(vectors).__name__}."
            )

        if vectors.ndim != 2:
            raise ValueError(
                "ClipTensorBatch expects a 2D tensor, "
                f"got shape {tuple(vectors.shape)}."
            )

        if len(keys) != vectors.shape[0]:
            raise ValueError(
                "Number of keys must match tensor rows: "
                f"{len(keys)} keys for {vectors.shape[0]} rows."
            )

        for key in keys:
            if type(key) is not int:
                raise TypeError(
                    "ClipTensorBatch keys must be int, "
                    f"got {type(key).__name__}."
                )

        if len(set(keys)) != len(keys):
            raise ValueError(
                "ClipTensorBatch keys must be unique."
            )

        if not vectors.is_floating_point():
            raise TypeError(
                "ClipTensorBatch expects a floating-point tensor, "
                f"got {vectors.dtype}."
            )

        normalized = ClipTensorBatchData(
            keys=tuple(keys),
            vectors=vectors,
        )

        self._vectors_by_key = dict(
            zip(
                normalized.keys,
                normalized.vectors.unbind(dim=0),
                strict=True,
            )
        )

        self._validate_vector_batch_mapping(
            self._vectors_by_key
        )

        super().__init__(normalized)

    def _batch_mapping(self) -> Mapping[int, Tensor]:
        """Return embedding rows indexed by source key."""
        return self._vectors_by_key

    @property
    def keys(self) -> tuple[int, ...]:
        """Return source keys in packed tensor row order."""
        return self.data().keys

    @property
    def vectors(self) -> Tensor:
        """Return the packed embedding tensor with shape [N, D]."""
        return self.data().vectors

# From cscience-feature-clip\src\cscience\features\clip\clip_datatypes\clip_tensor_batch_data.py
from dataclasses import dataclass

from torch import Tensor


@dataclass(frozen=True, slots=True)
class ClipTensorBatchData:
    """Packed CLIP embedding batch with stable source keys.

    vectors has shape [N, D].
    keys maps tensor rows back to source batch indices.
    """

    keys: tuple[int, ...]
    vectors: Tensor

# From cscience-feature-clip\src\cscience\features\clip\clip_feature.py
from __future__ import annotations

import open_clip
import torch

from cscience.features.api.datatypes.image.pil_image_batch import PilImageBatch
from cscience.features.api.datatypes.text.text_batch import TextBatch
from cscience.features.api.feature.feature_base import FeatureBase
from cscience.features.api.feature.feature_base import FeatureInfo
from .clip_config import ClipConfig

from .clip_datatypes.clip_tensor_batch import ClipTensorBatch, ClipTensorBatchData



class ClipFeature(FeatureBase['ClipFeature', ClipConfig]):
    """CLIP feature service backed by OpenCLIP."""

    def _initialize(self, config: ClipConfig) -> None:
        self._model_name = config.model_name
        self._pretrained = config.pretrained


        self._device = torch.device(config.preferred_device if torch.cuda.is_available() else "cpu")
        if config.force_device and not (config.preferred_device == str(self._device)):
            raise RuntimeError(
                f"Preferred device {config.preferred_device} is not available. "
                f"Available device is {self._device}."
            )

        self._model, _, self._preprocess = open_clip.create_model_and_transforms(
            model_name=self._model_name,
            pretrained=self._pretrained,
        )

        self._model = self._model.to(self._device).eval()
        self._tokenizer = open_clip.get_tokenizer(self._model_name)

        self._initialized = True


    @torch.inference_mode()
    def text_batch(self, texts: TextBatch) -> ClipTensorBatch:


        keys = texts.ordered_keys()
        values = list(texts.ordered_values())

        tokens = self._tokenizer(values).to(self._device)

        feats = self._model.encode_text(tokens)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=feats.detach().float().cpu(),
            )
        )


    @torch.inference_mode()
    def image_batch(self, images: PilImageBatch) -> ClipTensorBatch:

        keys = images.ordered_keys()
        values = images.ordered_values()

        image_tensors = torch.stack(
            [
                self._preprocess(image)
                for image in values
            ]
        ).to(self._device)

        feats = self._model.encode_image(image_tensors)
        feats = feats / feats.norm(dim=-1, keepdim=True)

        return ClipTensorBatch(
            ClipTensorBatchData(
                keys=keys,
                vectors=feats.detach().float().cpu(),
            )
        )

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(mode="json"),
        )

# From cscience-feature-clip\tests\test_clip_datatype_architecture.py
import unittest

from cscience.features.api.datatypes.base.datatype_base import (
    DatatypeBase,
)
from cscience.features.api.datatypes.base.structural.embedding_base import (
    EmbeddingBase,
)
from cscience.features.api.datatypes.base.structural.vector_base import (
    VectorBase,
)
from cscience.features.api.datatypes.base.structural.vector_batch_base import (
    VectorBatchBase,
)
from cscience.features.clip.clip_datatypes.clip_datatype import (
    ClipDatatype,
)
from cscience.features.clip.clip_datatypes.clip_tensor import (
    ClipTensor,
)
from cscience.features.clip.clip_datatypes.clip_tensor_batch import (
    ClipTensorBatch,
)


CLIP_DATATYPES = (
    ClipTensor,
    ClipTensorBatch,
)


class TestClipDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_clip_namespace(self) -> None:
        for datatype_class in CLIP_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "clip",
                )

    def test_package_datatypes_inherit_clip_datatype(
        self,
    ) -> None:
        for datatype_class in CLIP_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        ClipDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in CLIP_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_clip_tensor_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipTensor.__mro__

        self.assertLess(
            mro.index(VectorBase),
            mro.index(ClipDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipDatatype),
        )

    def test_clip_tensor_batch_structure_precedes_namespace(
        self,
    ) -> None:
        mro = ClipTensorBatch.__mro__

        self.assertLess(
            mro.index(VectorBatchBase),
            mro.index(ClipDatatype),
        )
        self.assertLess(
            mro.index(EmbeddingBase),
            mro.index(ClipDatatype),
        )

import unittest

import torch

from cscience.features.clip.clip_datatypes.clip_tensor import (
    ClipTensor,
)


class TestClipTensor(unittest.TestCase):
    def test_stores_embedding_tensor(self) -> None:
        tensor = torch.tensor(
            [1.0, 2.0, 3.0],
            dtype=torch.float32,
        )

        embedding = ClipTensor(tensor)

        self.assertIs(embedding.data(), tensor)
        self.assertEqual(embedding.length(), 3)
        self.assertEqual(embedding.embedding_dim(), 3)

    def test_accepts_float16_tensor(self) -> None:
        embedding = ClipTensor(
            torch.tensor(
                [1.0, 2.0],
                dtype=torch.float16,
            )
        )

        self.assertEqual(
            embedding.data().dtype,
            torch.float16,
        )

    def test_rejects_non_tensor(self) -> None:
        with self.assertRaises(TypeError):
            ClipTensor(
                [1.0, 2.0]  # type: ignore[arg-type]
            )

    def test_rejects_non_vector_tensor(self) -> None:
        with self.assertRaises(ValueError):
            ClipTensor(
                torch.zeros((2, 3))
            )

    def test_rejects_empty_tensor(self) -> None:
        with self.assertRaises(ValueError):
            ClipTensor(
                torch.empty((0,))
            )

    def test_rejects_integer_tensor(self) -> None:
        with self.assertRaises(TypeError):
            ClipTensor(
                torch.tensor([1, 2, 3])
            )

import unittest

import torch

from cscience.features.clip.clip_datatypes.clip_tensor_batch import (
    ClipTensorBatch,
)
from cscience.features.clip.clip_datatypes.clip_tensor_batch_data import (
    ClipTensorBatchData,
)


def make_batch_data() -> ClipTensorBatchData:
    return ClipTensorBatchData(
        keys=(20, 10),
        vectors=torch.tensor(
            [
                [2.0, 2.1, 2.2],
                [1.0, 1.1, 1.2],
            ],
            dtype=torch.float32,
        ),
    )


class TestClipTensorBatch(unittest.TestCase):
    def test_stores_packed_batch(self) -> None:
        data = make_batch_data()

        batch = ClipTensorBatch(data)

        self.assertEqual(batch.keys, (20, 10))
        self.assertIs(batch.vectors, data.vectors)
        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(batch.length(), 3)
        self.assertEqual(batch.embedding_dim(), 3)

    def test_orders_rows_by_source_key(self) -> None:
        batch = ClipTensorBatch(
            make_batch_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (10, 20),
        )

        ordered = batch.ordered_values()

        self.assertTrue(
            torch.equal(
                ordered[0],
                torch.tensor([1.0, 1.1, 1.2]),
            )
        )
        self.assertTrue(
            torch.equal(
                ordered[1],
                torch.tensor([2.0, 2.1, 2.2]),
            )
        )

    def test_rejects_wrong_outer_data_type(self) -> None:
        with self.assertRaises(TypeError):
            ClipTensorBatch(
                torch.zeros((2, 3))  # type: ignore[arg-type]
            )

    def test_rejects_non_tensor_vectors(self) -> None:
        data = ClipTensorBatchData(
            keys=(0,),
            vectors=[[1.0, 2.0]],  # type: ignore[arg-type]
        )

        with self.assertRaises(TypeError):
            ClipTensorBatch(data)

    def test_rejects_non_matrix_tensor(self) -> None:
        data = ClipTensorBatchData(
            keys=(0,),
            vectors=torch.tensor([1.0, 2.0]),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_key_row_mismatch(self) -> None:
        data = ClipTensorBatchData(
            keys=(0,),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_duplicate_keys(self) -> None:
        data = ClipTensorBatchData(
            keys=(0, 0),
            vectors=torch.zeros((2, 3)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_empty_batch(self) -> None:
        data = ClipTensorBatchData(
            keys=(),
            vectors=torch.empty((0, 3)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_empty_embedding_dimension(self) -> None:
        data = ClipTensorBatchData(
            keys=(0, 1),
            vectors=torch.empty((2, 0)),
        )

        with self.assertRaises(ValueError):
            ClipTensorBatch(data)

    def test_rejects_integer_tensor(self) -> None:
        data = ClipTensorBatchData(
            keys=(0, 1),
            vectors=torch.tensor(
                [
                    [1, 2],
                    [3, 4],
                ]
            ),
        )

        with self.assertRaises(TypeError):
            ClipTensorBatch(data)

# From cscience-feature-clip\tests\test_clip_feature.py
import random
from pathlib import Path
import unittest

from PIL import Image

from cscience.features.api import measure_time
from cscience.features.clip.clip_config import ClipConfig
from cscience.features.clip.clip_connector import ClipConnector


TEST_FIXTURE_DIR: Path =  Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "test"

class FeatureTest(unittest.TestCase):
    N = 10


    @classmethod
    def setUpClass(cls) -> None:
        images_paths = list(TEST_FIXTURE_DIR.glob("*.jpg"))
        cls.images_batch: list[Image.Image] = []
        for image_path in images_paths:
            cls.images_batch.append(Image.open(image_path))

    def _resource(self, name: str) -> Image.Image:
        return Image.open(TEST_FIXTURE_DIR / name).convert("RGB")

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_to_vector(self):

        clip = ClipConnector(ClipConfig())
        v = clip.text("Hello World")

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_to_vector(self):
        clip = ClipConnector(ClipConfig())
        image = self._resource("flickr-dog-1.jpg")

        v = clip.image(image)

        self.assertIsInstance(v, list)
        self.assertEqual(len(v), 512)

    @measure_time(times=N, ignore_first=True)
    def test_clip_text_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())
        v = clip.text_batch(["Hello World", "Hello World", "Hello World and Moon"])

        self.assertEqual(v[0], v[1])
        self.assertNotEqual(v[0], v[2])
        self.assertNotEqual(v[1], v[2])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())

        images = self.images_batch

        v = clip.image_batch(images)

        for i in range(0, len(images), 2):
            self.assertEqual(v[i], v[i + 1])
            for j in range(i + 2, len(images), 2):
                self.assertNotEqual(v[i], v[j])

    @measure_time(times=N, ignore_first=True)
    def test_clip_image_batch_to_vector_batch(self):
        clip = ClipConnector(ClipConfig())
        length = len(self.images_batch) * 1
        # append n times the batch
        images = [random.choice(self.images_batch) for _ in range(length)]
        v = clip.image_batch(images)
        self.assertEqual(len(v), length)
        for key, value in v.items():
            self.assertEqual(len(value), 512)



    @measure_time(times=N, ignore_first=True)
    def test_clip_siglip_image_batch_to_vector_batch(self) -> None:

        cfg= ClipConfig(
            model_name="hf-hub:timm/ViT-B-16-SigLIP2-256",
            pretrained="hf-hub:timm/ViT-B-16-SigLIP2-256",
            preferred_device="cuda",
            namespace="SigLIP2",
            force_device=True
        )
        clip = ClipConnector(cfg)
        length = len(self.images_batch) * 1
        images = [random.choice(self.images_batch) for _ in range(length)]
        v = clip.image_batch(images)
        self.assertEqual(len(v), length)
        for key, value in v.items():
            self.assertEqual(len(value), 768)


# From cscience-feature-clip\tests\test_multi_instance_clip.py
import unittest

from cscience.features.clip import ClipConnector
from cscience.features.clip.clip_config import ClipConfig


class FeatureTest(unittest.TestCase):

    N = 10
    @classmethod
    def setUpClass(cls) -> None:
        cls.connector_1 = ClipConnector(ClipConfig())
        cls.cfg2= ClipConfig(
            model_name="hf-hub:timm/ViT-B-16-SigLIP2-256",
            pretrained="hf-hub:timm/ViT-B-16-SigLIP2-256",
            preferred_device="cuda",
            namespace="SigLIP2",
            force_device=True
        )
        cls.connector_2 = ClipConnector(cls.cfg2)



    def test_clip_multi_embedding(self):
        t1 = self.connector_1.text("Hello World")
        t2 = self.connector_2.text("Hello World")

        self.assertEqual(len(t1),512)
        self.assertTrue(len(t2) > 0)


# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\__init__.py
from cscience.features.api import RegistryBase

from .nsfw_image_connector import NsfwImageConnector
from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_datatypes.nsfw_image_datatype import NsfwImageDatatype
from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction, NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
    NsfwPredictionBatchData,
)
from .nsfw_image_feature import NsfwImageFeature

__all__ = [
    "NsfwImageConnector",
    "NsfwImageConversionProvider",
    "NsfwImageDatatype",
    "NsfwImageFeature",
    "NsfwPrediction",
    "NsfwPredictionData",
    "NsfwPredictionBatch",
    "NsfwPredictionBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("nsfw_image", NsfwImageConversionProvider)

# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_config.py
from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class NsfwConfig(ConfigBase):


    @classmethod
    def _default_namespace(cls) -> str:
        return "nsfw"

    model_name:str = Field(
        default="Falconsai/nsfw_image_detection",
        description="The name of the NSFW model to use."
    )

    preferred_device:str = Field(
        default="cuda",
        description="The device to use for inference. Default is 'cpu'."
    )

    force_device:bool = Field(
        default=False,
        description="Whether to force the use of the specified device."
    )


# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_connector.py
from PIL.Image import Image

from cscience.features.api import (
    BoolValue,
    ConnectorBase,
    FeatureInfo,
    FloatValue,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
)
from .nsfw_config import NsfwConfig

from .nsfw_image_conversion_provider import NsfwImageConversionProvider
from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction, NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import NsfwPredictionBatch
from .nsfw_image_feature import NsfwImageFeature


class NsfwImageConnector(ConnectorBase):
    """Public connector for NSFW image classification."""

    def __init__(self, config: NsfwConfig) -> None:
        self.feature = NsfwImageFeature.get_instance(config)
        super().__init__( NsfwImageConversionProvider(self.feature))

    def classify(self, image: Image) -> NsfwPredictionData:
        """Classify a single image and return the full prediction."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=NsfwPrediction,
        )

        return function(PilImage(image)).data()

    def classify_batch(self, images: list[Image]) -> dict[int, NsfwPredictionData]:
        """Classify images and return predictions indexed by input position."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=NsfwPredictionBatch,
        )

        return function(image_batch).data().predictions

    def score(self, image: Image) -> float:
        """Return the NSFW score for a single image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=FloatValue,
        )

        return function(PilImage(image)).data()

    def is_nsfw(self, image: Image, threshold: float = 0.5) -> bool:
        """Return whether a single image is classified as NSFW."""
        prediction = self.classify(image)
        return prediction.is_nsfw(threshold)

    def is_nsfw_default(self, image: Image) -> bool:
        """Return whether a single image is NSFW using the converter default threshold."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.classify_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=NsfwPredictionBatch,
            output_type=BoolValue,
        )

        return function(PilImage(image)).data()

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="nsfw_image",
            name="NSFW Image Classification",
            description="NSFW image classification service",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()

# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_conversion_provider.py
from cscience.features.api import (
    BoolValue,
    ConversionProviderBase,
    Converter,
    FeatureBase,
    FloatValue,
)

from .nsfw_image_datatypes.nsfw_prediction import NsfwPrediction
from .nsfw_image_datatypes.nsfw_prediction_batch import NsfwPredictionBatch


def nsfw_prediction_passthrough(prediction: NsfwPrediction) -> NsfwPrediction:
    return prediction


def nsfw_prediction_batch_passthrough(batch: NsfwPredictionBatch) -> NsfwPredictionBatch:
    return batch


def nsfw_prediction_batch_to_prediction(batch: NsfwPredictionBatch) -> NsfwPrediction:
    predictions = batch.data().predictions

    if len(predictions) != 1:
        raise ValueError(
            f"Cannot convert NsfwPredictionBatch of size {len(predictions)} "
            f"to NsfwPrediction."
        )

    prediction = next(iter(predictions.values()))
    return NsfwPrediction(prediction)


def nsfw_prediction_to_float_value(prediction: NsfwPrediction) -> FloatValue:
    return FloatValue(prediction.data().nsfw_score)


def nsfw_prediction_to_bool_value(prediction: NsfwPrediction) -> BoolValue:
    return BoolValue(prediction.data().is_nsfw())


class NsfwImageConversionProvider(ConversionProviderBase):
    """Registers conversions required by the NSFW image feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[NsfwPrediction, NsfwPrediction](
                name="nsfw_prediction_passthrough",
                source=self._feature,
                function=nsfw_prediction_passthrough,
                input_type=NsfwPrediction,
                output_type=NsfwPrediction,
            ),
            Converter[NsfwPredictionBatch, NsfwPredictionBatch](
                name="nsfw_prediction_batch_passthrough",
                source=self._feature,
                function=nsfw_prediction_batch_passthrough,
                input_type=NsfwPredictionBatch,
                output_type=NsfwPredictionBatch,
            ),
            Converter[NsfwPredictionBatch, NsfwPrediction](
                name="nsfw_prediction_batch_to_prediction",
                source=self._feature,
                function=nsfw_prediction_batch_to_prediction,
                input_type=NsfwPredictionBatch,
                output_type=NsfwPrediction,
            ),
            Converter[NsfwPrediction, FloatValue](
                name="nsfw_prediction_to_float_value",
                source=self._feature,
                function=nsfw_prediction_to_float_value,
                input_type=NsfwPrediction,
                output_type=FloatValue,
            ),
            Converter[NsfwPrediction, BoolValue](
                name="nsfw_prediction_to_bool_value",
                source=self._feature,
                function=nsfw_prediction_to_bool_value,
                input_type=NsfwPrediction,
                output_type=BoolValue,
            ),
        ]

# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_image_datatype.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class NsfwImageDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for NSFW image-specific datatypes."""

    namespace = "nsfw_image"

# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_prediction.py
from dataclasses import dataclass

from cscience.features.api import FloatValue

from .nsfw_image_datatype import NsfwImageDatatype
from .nsfw_prediction_data import NsfwPredictionData


class NsfwPrediction(
    NsfwImageDatatype[NsfwPredictionData],
):
    """Single NSFW classification result."""

    def __init__(self, data: NsfwPredictionData) -> None:
        self.validate_data(data)
        super().__init__(data)

    @staticmethod
    def validate_data(data: NsfwPredictionData) -> None:
        """Validate an NSFW prediction data object."""
        if not isinstance(data, NsfwPredictionData):
            raise TypeError(
                f"NsfwPrediction expects NsfwPredictionData, "
                f"got {type(data).__name__}."
            )

        if type(data.label) is not str:
            raise TypeError(
                f"NsfwPrediction label expects str, "
                f"got {type(data.label).__name__}."
            )

        NsfwPrediction._validate_score(
            name="score",
            value=data.score,
        )
        NsfwPrediction._validate_score(
            name="normal_score",
            value=data.normal_score,
        )
        NsfwPrediction._validate_score(
            name="nsfw_score",
            value=data.nsfw_score,
        )

    @staticmethod
    def _validate_score(
        name: str,
        value: float,
    ) -> None:
        if type(value) is not float:
            raise TypeError(
                f"NsfwPrediction {name} expects float, "
                f"got {type(value).__name__}."
            )

        if not 0.0 <= value <= 1.0:
            raise ValueError(
                f"NsfwPrediction {name} must be in [0, 1], "
                f"got {value}."
            )

    def nsfw_score(self) -> FloatValue:
        """Return the NSFW score as a core float value."""
        return FloatValue(self.data().nsfw_score)

# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_prediction_batch.py
from collections.abc import Mapping

from cscience.features.api import BatchBase

from .nsfw_image_datatype import NsfwImageDatatype
from .nsfw_prediction import (
    NsfwPrediction,
    NsfwPredictionData,
)
from .nsfw_prediction_batch_data import (
    NsfwPredictionBatchData,
)


class NsfwPredictionBatch(
    BatchBase[NsfwPredictionData],
    NsfwImageDatatype[NsfwPredictionBatchData],
):
    """Batch of NSFW classification results."""

    def __init__(
        self,
        data: NsfwPredictionBatchData,
    ) -> None:
        if not isinstance(data, NsfwPredictionBatchData):
            raise TypeError(
                "NsfwPredictionBatch expects "
                f"NsfwPredictionBatchData, "
                f"got {type(data).__name__}."
            )

        self._validate_batch_mapping(data.predictions)

        for prediction in data.predictions.values():
            NsfwPrediction.validate_data(prediction)

        normalized = NsfwPredictionBatchData(
            predictions=dict(data.predictions),
        )

        super().__init__(normalized)

    def _batch_mapping(
        self,
    ) -> Mapping[int, NsfwPredictionData]:
        """Return predictions indexed by source image position."""
        return self.data().predictions

# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_prediction_batch_data.py
from dataclasses import dataclass

from .nsfw_prediction import NsfwPredictionData


@dataclass(frozen=True, slots=True)
class NsfwPredictionBatchData:
    """NSFW predictions indexed by source image position."""

    predictions: dict[int, NsfwPredictionData]

# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_datatypes\nsfw_prediction_data.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NsfwPredictionData:
    """NSFW classification result for one image."""

    label: str
    score: float
    normal_score: float
    nsfw_score: float

    def is_nsfw(self, threshold: float = 0.5) -> bool:
        """Return whether the NSFW score is at or above the threshold."""
        return self.nsfw_score >= threshold


# From cscience-feature-nsfw-image\src\cscience\features\nsfw_image\nsfw_image_feature.py
from __future__ import annotations

import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

from cscience.features.api import FeatureBase, PilImageBatch, FeatureInfo
from .nsfw_config import NsfwConfig

from .nsfw_image_datatypes.nsfw_prediction import NsfwPredictionData
from .nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
    NsfwPredictionBatchData,
)


class NsfwImageFeature(FeatureBase):
    """NSFW image-classification feature backed by Falconsai/nsfw_image_detection."""

    def _initialize(self, config: NsfwConfig) -> None:

        self._config = config
        self._device = torch.device(self._config.preferred_device if torch.cuda.is_available() else "cpu")
        if self._config.force_device and not (self._config.preferred_device == str(self._device)):
            raise RuntimeError(
                f"Preferred device {self._config.preferred_device} is not available. "
                f"Available device is {self._device}."
            )

        self._processor = AutoImageProcessor.from_pretrained(self._config.model_name)
        self._model = AutoModelForImageClassification.from_pretrained(self._config.model_name).to(self._device).eval()

        self._initialized = True


    @torch.inference_mode()
    def classify_batch(self, images: PilImageBatch) -> NsfwPredictionBatch:
        """Classify a batch of images as normal or NSFW."""

        keys = images.ordered_keys()
        image_values = list(images.ordered_values())

        inputs = self._processor(
            images=image_values,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self._device)
            for key, value in inputs.items()
        }

        outputs = self._model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=-1).detach().cpu()

        id_to_label = self._model.config.id2label
        predictions: dict[int, NsfwPredictionData] = {}

        for source_key, row in zip(keys, probabilities):
            label_scores = {
                id_to_label[class_index].lower(): float(score)
                for class_index, score in enumerate(row)
            }

            if "normal" not in label_scores or "nsfw" not in label_scores:
                raise ValueError(
                    f"Expected model labels 'normal' and 'nsfw', got {label_scores.keys()}."
                )

            predicted_index = int(row.argmax().item())
            predicted_label = id_to_label[predicted_index].lower()
            predicted_score = float(row[predicted_index].item())

            predictions[source_key] = NsfwPredictionData(
                label=predicted_label,
                score=predicted_score,
                normal_score=label_scores["normal"],
                nsfw_score=label_scores["nsfw"],
            )

        return NsfwPredictionBatch(
            NsfwPredictionBatchData(
                predictions=predictions,
            )
        )

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name=self._config.model_name,
            device=str(self._device),
            configuration=self._config.model_dump(mode="json"),
        )

# From cscience-feature-nsfw-image\tests\test_nsfw_datatype_architecture.py
import unittest

from cscience.features.api import (
    BatchBase,
    DatatypeBase,
)

from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_image_datatype import (
    NsfwImageDatatype,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction import (
    NsfwPrediction,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
)


NSFW_DATATYPES = (
    NsfwPrediction,
    NsfwPredictionBatch,
)


class TestNsfwDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_nsfw_namespace(
        self,
    ) -> None:
        for datatype_class in NSFW_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "nsfw_image",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in NSFW_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        NsfwImageDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in NSFW_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_batch_structure_precedes_namespace(
        self,
    ) -> None:
        mro = NsfwPredictionBatch.__mro__

        self.assertLess(
            mro.index(BatchBase),
            mro.index(NsfwImageDatatype),
        )

import unittest

from cscience.features.api import FloatValue

from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction import (
    NsfwPrediction,
    NsfwPredictionData,
)


def make_prediction_data() -> NsfwPredictionData:
    return NsfwPredictionData(
        label="nsfw",
        score=0.8,
        normal_score=0.2,
        nsfw_score=0.8,
    )


class TestNsfwPrediction(unittest.TestCase):
    def test_stores_prediction(self) -> None:
        data = make_prediction_data()

        prediction = NsfwPrediction(data)

        self.assertIs(prediction.data(), data)
        self.assertEqual(
            prediction.namespace,
            "nsfw_image",
        )

    def test_returns_nsfw_score_as_float_value(
        self,
    ) -> None:
        prediction = NsfwPrediction(
            make_prediction_data()
        )

        score = prediction.nsfw_score()

        self.assertIsInstance(score, FloatValue)
        self.assertEqual(score.data(), 0.8)

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            NsfwPrediction(
                "invalid"  # type: ignore[arg-type]
            )

    def test_rejects_wrong_label_type(self) -> None:
        data = NsfwPredictionData(
            label=1,  # type: ignore[arg-type]
            score=0.8,
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(TypeError):
            NsfwPrediction(data)

    def test_rejects_non_float_score(self) -> None:
        data = NsfwPredictionData(
            label="nsfw",
            score=1,  # type: ignore[arg-type]
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(TypeError):
            NsfwPrediction(data)

    def test_rejects_score_below_zero(self) -> None:
        data = NsfwPredictionData(
            label="nsfw",
            score=-0.1,
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(ValueError):
            NsfwPrediction(data)

    def test_rejects_score_above_one(self) -> None:
        data = NsfwPredictionData(
            label="nsfw",
            score=1.1,
            normal_score=0.2,
            nsfw_score=0.8,
        )

        with self.assertRaises(ValueError):
            NsfwPrediction(data)

    def test_classifies_using_threshold(self) -> None:
        data = make_prediction_data()

        self.assertTrue(data.is_nsfw(0.5))
        self.assertFalse(data.is_nsfw(0.9))

import unittest

from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction import (
    NsfwPredictionData,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction_batch import (
    NsfwPredictionBatch,
)
from cscience.features.nsfw_image.nsfw_image_datatypes.nsfw_prediction_batch_data import (
    NsfwPredictionBatchData,
)


def make_normal_prediction() -> NsfwPredictionData:
    return NsfwPredictionData(
        label="normal",
        score=0.9,
        normal_score=0.9,
        nsfw_score=0.1,
    )


def make_nsfw_prediction() -> NsfwPredictionData:
    return NsfwPredictionData(
        label="nsfw",
        score=0.8,
        normal_score=0.2,
        nsfw_score=0.8,
    )


def make_batch_data() -> NsfwPredictionBatchData:
    return NsfwPredictionBatchData(
        predictions={
            20: make_normal_prediction(),
            10: make_nsfw_prediction(),
        }
    )


class TestNsfwPredictionBatch(unittest.TestCase):
    def test_stores_prediction_batch(self) -> None:
        batch = NsfwPredictionBatch(
            make_batch_data()
        )

        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(
            batch.namespace,
            "nsfw_image",
        )

    def test_orders_predictions_by_source_key(
        self,
    ) -> None:
        batch = NsfwPredictionBatch(
            make_batch_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (10, 20),
        )
        self.assertEqual(
            tuple(
                prediction.label
                for prediction in batch.ordered_values()
            ),
            ("nsfw", "normal"),
        )

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            NsfwPredictionBatch(
                {}  # type: ignore[arg-type]
            )

    def test_rejects_empty_batch(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={}
        )

        with self.assertRaises(ValueError):
            NsfwPredictionBatch(data)

    def test_rejects_non_integer_key(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={
                "0": make_nsfw_prediction(),  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            NsfwPredictionBatch(data)

    def test_rejects_wrong_prediction_type(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={
                0: "invalid",  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            NsfwPredictionBatch(data)

    def test_rejects_invalid_prediction_data(self) -> None:
        data = NsfwPredictionBatchData(
            predictions={
                0: NsfwPredictionData(
                    label="nsfw",
                    score=2.0,
                    normal_score=0.0,
                    nsfw_score=2.0,
                )
            }
        )

        with self.assertRaises(ValueError):
            NsfwPredictionBatch(data)

# From cscience-feature-nsfw-image\tests\test_nsfw_image_feature.py
import unittest
from pathlib import Path

from PIL import Image

from cscience.features.api.utils.measure_time import measure_time
from cscience.features.nsfw_image import NsfwImageConnector


class NsfwImageFeatureTest(unittest.TestCase):

    N = 10

    def test_connector_initializes(self):
        connector = NsfwImageConnector()
        self.assertIsNotNone(connector)

    @measure_time(times=N, ignore_first=True)
    def test_classify_simple_image(self):
        image = Image.new("RGB", (224, 224), color=(255, 255, 255))

        connector = NsfwImageConnector()
        prediction = connector.classify(image)

        self.assertIn(prediction.label, {"normal", "nsfw"})
        self.assertGreaterEqual(prediction.score, 0.0)
        self.assertLessEqual(prediction.score, 1.0)
        self.assertGreaterEqual(prediction.normal_score, 0.0)
        self.assertLessEqual(prediction.normal_score, 1.0)
        self.assertGreaterEqual(prediction.nsfw_score, 0.0)
        self.assertLessEqual(prediction.nsfw_score, 1.0)

    @measure_time(times=N, ignore_first=True)
    def test_classify_batch_preserves_indices(self):
        images = {
            0: Image.new("RGB", (224, 224), color=(255, 255, 255)),
            3: Image.new("RGB", (224, 224), color=(0, 0, 0)),
        }

        connector = NsfwImageConnector()
        predictions = connector.classify_batch(list(images.values()))

        self.assertEqual(set(predictions.keys()), {0, 1})




# From cscience-feature-nsfw-image\tests\test_nsfw_image_visual.py
import base64
import os
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image

from cscience.features.api.utils.image_utils import load_base64_image
from cscience.features.nsfw_image import NsfwImageConnector

# Load model directly
import torch
from PIL import Image
from transformers import AutoModelForImageClassification, ViTImageProcessor

from cscience.features.nsfw_image.nsfw_config import NsfwConfig

TEST_FIXTURE_DIR: Path =  Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "images-gen"


class TestNsfwImageVisual(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        images_paths = list(TEST_FIXTURE_DIR.glob("**/*base_64.txt"))
        cls.nsfw_images_batch: list[Image.Image] = []
        cls.sfw_images_batch: list[Image.Image] = []
        for image_path in images_paths:
            if "nsfw_" in image_path.parent.stem:
                cls.nsfw_images_batch.append(load_base64_image(image_path))
            else:
                cls.sfw_images_batch.append(load_base64_image(image_path))


    def test_nsfw_detected(self):
        for nsfw in self.nsfw_images_batch:
            detector = NsfwImageConnector(NsfwConfig())
            prediction = detector.classify(nsfw)
            self.assertGreater(
                prediction.nsfw_score,
                0.5,
                msg=f"Expected NSFW score > 0.5, got {prediction}",
            )

    def test_sfw_not_detected(self):
        for sfw in self.sfw_images_batch:
            detector = NsfwImageConnector(NsfwConfig())
            prediction = detector.classify(sfw)
            self.assertLess(
                prediction.nsfw_score,
                0.5,
                msg=f"Expected NSFW score < 0.5, got {prediction}",
            )

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\__init__.py
from cscience.features.api import RegistryBase

from .ocr_tesseract_connector import OcrTesseractConnector
from .ocr_tesseract_conversion_provider import OcrTesseractConversionProvider
from .ocr_tesseract_datatypes.ocr_tesseract_datatype import OcrTesseractDatatype
from .ocr_tesseract_feature import OcrTesseractFeature
from .ocr_tesseract_datatypes.ocr_result import OcrResult
from .ocr_tesseract_datatypes.ocr_result_data import OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import OcrResultBatch
from .ocr_tesseract_datatypes.ocr_result_batch_data import OcrResultBatchData


__all__ = [
    "OcrTesseractConnector",
    "OcrTesseractConversionProvider",
    "OcrTesseractDatatype",
    "OcrTesseractFeature",
    "OcrResult",
    "OcrResultData",
    "OcrResultBatch",
    "OcrResultBatchData",
]


def register(registry: RegistryBase) -> None:
    registry.register("ocr_tesseract", OcrTesseractConversionProvider)

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_config.py
from typing import Literal

from pydantic import Field

from cscience.features.api.config.config_base import ConfigBase


class OcrConfig(ConfigBase):

    @classmethod
    def _default_namespace(cls) -> str:
        return "ocr_tesseract"

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_connector.py
from PIL.Image import Image

from cscience.features.api import (
    ConnectorBase,
    FeatureInfo,
    FunctionConnector,
    PilImage,
    PilImageBatch,
    ServiceInfo,
    Text,
    TextBatch,
)
from .ocr_config import OcrConfig

from .ocr_tesseract_conversion_provider import OcrTesseractConversionProvider
from .ocr_tesseract_datatypes.ocr_result import OcrResult, OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import OcrResultBatch
from .ocr_tesseract_feature import OcrTesseractFeature


class OcrTesseractConnector(ConnectorBase):
    """Public connector for Tesseract OCR."""

    def __init__(self, config: OcrConfig) -> None:
        self.feature = OcrTesseractFeature.get_instance(config)
        super().__init__(OcrTesseractConversionProvider(self.feature))

    def extract(self, image: Image) -> OcrResultData:
        """Extract a structured OCR result from one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=OcrResult,
        )

        return function(PilImage(image)).data()

    def extract_batch(self, images: list[Image]) -> dict[int, OcrResultData]:
        """Extract structured OCR results from images."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=OcrResultBatch,
        )

        return function(image_batch).data().results

    def text(self, image: Image) -> str:
        """Extract plain text from one image."""
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImage,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=Text,
        )

        return function(PilImage(image)).data()

    def text_batch(self, images: list[Image]) -> dict[int, str]:
        """Extract plain text from images."""
        image_batch = PilImageBatch(
            {
                index: image
                for index, image in enumerate(images)
            }
        )

        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.extract_text_batch,
            input_type=PilImageBatch,
            input_feature_type=PilImageBatch,
            output_feature_type=OcrResultBatch,
            output_type=TextBatch,
        )

        return function(image_batch).data()

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        return ServiceInfo(
            identifier="ocr_tesseract",
            name="OCR Tesseract",
            description="Tesseract OCR service",
            operations=ServiceInfo.generate_operations(cls)
        )

    def get_feature_info(self) -> FeatureInfo:
        return self.feature.get_feature_info()

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_conversion_provider.py
from cscience.features.api import (
    ConversionProviderBase,
    Converter,
    FeatureBase,
    Text,
    TextBatch,
)

from .ocr_tesseract_datatypes.ocr_result import OcrResult
from .ocr_tesseract_datatypes.ocr_result_batch import OcrResultBatch


def ocr_result_passthrough(result: OcrResult) -> OcrResult:
    return result


def ocr_result_batch_passthrough(batch: OcrResultBatch) -> OcrResultBatch:
    return batch


def ocr_result_to_text(result: OcrResult) -> Text:
    return Text(result.data().text)


def ocr_result_batch_to_result(batch: OcrResultBatch) -> OcrResult:
    results = batch.data().results

    if len(results) != 1:
        raise ValueError(
            f"Cannot convert OcrResultBatch of size {len(results)} to OcrResult."
        )

    return OcrResult(next(iter(results.values())))


def ocr_result_batch_to_text(batch: OcrResultBatch) -> Text:
    results = batch.data().results

    if len(results) != 1:
        raise ValueError(
            f"Cannot convert OcrResultBatch of size {len(results)} to Text."
        )

    return Text(next(iter(results.values())).text)


def ocr_result_batch_to_text_batch(batch: OcrResultBatch) -> TextBatch:
    return TextBatch(
        {
            key: result.text
            for key, result in batch.data().results.items()
        }
    )


class OcrTesseractConversionProvider(ConversionProviderBase):
    """Registers conversions required by the Tesseract OCR feature."""

    def __init__(self, feature: FeatureBase) -> None:
        super().__init__(feature)

    def register_converters(self) -> list[Converter]:
        return [
            Converter[OcrResult, OcrResult](
                name="ocr_result_passthrough",
                source=self._feature,
                function=ocr_result_passthrough,
                input_type=OcrResult,
                output_type=OcrResult,
            ),
            Converter[OcrResultBatch, OcrResultBatch](
                name="ocr_result_batch_passthrough",
                source=self._feature,
                function=ocr_result_batch_passthrough,
                input_type=OcrResultBatch,
                output_type=OcrResultBatch,
            ),
            Converter[OcrResult, Text](
                name="ocr_result_to_text",
                source=self._feature,
                function=ocr_result_to_text,
                input_type=OcrResult,
                output_type=Text,
            ),
            Converter[OcrResultBatch, OcrResult](
                name="ocr_result_batch_to_result",
                source=self._feature,
                function=ocr_result_batch_to_result,
                input_type=OcrResultBatch,
                output_type=OcrResult,
            ),
            Converter[OcrResultBatch, Text](
                name="ocr_result_batch_to_text",
                source=self._feature,
                function=ocr_result_batch_to_text,
                input_type=OcrResultBatch,
                output_type=Text,
            ),
            Converter[OcrResultBatch, TextBatch](
                name="ocr_result_batch_to_text_batch",
                source=self._feature,
                function=ocr_result_batch_to_text_batch,
                input_type=OcrResultBatch,
                output_type=TextBatch,
            ),
        ]

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result.py
from .ocr_result_data import OcrResultData
from .ocr_tesseract_datatype import OcrTesseractDatatype


class OcrResult(
    OcrTesseractDatatype[OcrResultData],
):
    """Single Tesseract OCR result."""

    def __init__(self, data: OcrResultData) -> None:
        self.validate_data(data)
        super().__init__(data)

    @staticmethod
    def validate_data(data: OcrResultData) -> None:
        """Validate an OCR result data object."""
        if not isinstance(data, OcrResultData):
            raise TypeError(
                f"OcrResult expects OcrResultData, "
                f"got {type(data).__name__}."
            )

        if type(data.text) is not str:
            raise TypeError(
                f"OcrResultData.text expects str, "
                f"got {type(data.text).__name__}."
            )

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result_batch.py
from collections.abc import Mapping

from cscience.features.api import BatchBase

from .ocr_result import OcrResult
from .ocr_result_batch_data import OcrResultBatchData
from .ocr_result_data import OcrResultData
from .ocr_tesseract_datatype import OcrTesseractDatatype


class OcrResultBatch(
    BatchBase[OcrResultData],
    OcrTesseractDatatype[OcrResultBatchData],
):
    """Batch of Tesseract OCR results."""

    def __init__(
        self,
        data: OcrResultBatchData,
    ) -> None:
        if not isinstance(data, OcrResultBatchData):
            raise TypeError(
                f"OcrResultBatch expects OcrResultBatchData, "
                f"got {type(data).__name__}."
            )

        self._validate_batch_mapping(data.results)

        for result in data.results.values():
            OcrResult.validate_data(result)

        normalized = OcrResultBatchData(
            results=dict(data.results),
        )

        super().__init__(normalized)

    def _batch_mapping(
        self,
    ) -> Mapping[int, OcrResultData]:
        """Return OCR results indexed by source image position."""
        return self.data().results

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result_batch_data.py
from dataclasses import dataclass

from .ocr_result_data import OcrResultData


@dataclass(frozen=True, slots=True)
class OcrResultBatchData:
    """OCR results indexed by source image position."""

    results: dict[int, OcrResultData]

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_result_data.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OcrResultData:
    """Structured OCR result for one image."""

    text: str

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_datatypes\ocr_tesseract_datatype.py
from abc import ABC
from typing import Generic, TypeVar

from cscience.features.api import DatatypeBase

T = TypeVar("T")


class OcrTesseractDatatype(
    DatatypeBase[T],
    ABC,
    Generic[T],
):
    """Namespace base for Tesseract OCR-specific datatypes."""

    namespace = "ocr_tesseract"

# From cscience-feature-ocr-tesseract\src\cscience\features\ocr_tesseract\ocr_tesseract_feature.py
import pytesseract

from cscience.features.api import FeatureBase, PilImageBatch, FeatureInfo
from .ocr_config import OcrConfig

from .ocr_tesseract_datatypes.ocr_result import OcrResultData
from .ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
    OcrResultBatchData,
)

class OcrTesseractFeature(FeatureBase):
    """Tesseract OCR feature service."""

    def _initialize(self, config:OcrConfig) -> None:
        # Runtime configuration is intentionally deferred to the first call to extract_text_batch, since Tesseract does not require any model loading or initialization.
        self._config = config
        self._initialized = True


    def extract_text_batch(self, images: PilImageBatch) -> OcrResultBatch:
        """Extract text from a batch of images using Tesseract OCR."""

        results: dict[int, OcrResultData] = {}

        for key, image in images.ordered_items():
            text = pytesseract.image_to_string(image).strip()
            results[key] = OcrResultData(text=text)

        return OcrResultBatch(
            OcrResultBatchData(
                results=results,
            )
        )

    def get_feature_info(self) -> FeatureInfo:
        return FeatureInfo(
            namespace=self._config.namespace,
            feature_type=type(self).__name__,
            model_name="pytesseract",
            device=str("cpu"),
            configuration=self._config.model_dump(mode="json"),
        )

# From cscience-feature-ocr-tesseract\tests\test_ocr_datatype_architecture.py
import unittest

from cscience.features.api import (
    BatchBase,
    DatatypeBase,
)

from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result import (
    OcrResult,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_tesseract_datatype import (
    OcrTesseractDatatype,
)


OCR_DATATYPES = (
    OcrResult,
    OcrResultBatch,
)


class TestOcrDatatypeArchitecture(unittest.TestCase):
    def test_package_datatypes_use_ocr_namespace(
        self,
    ) -> None:
        for datatype_class in OCR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.namespace,
                    "ocr_tesseract",
                )

    def test_package_datatypes_inherit_namespace_base(
        self,
    ) -> None:
        for datatype_class in OCR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertTrue(
                    issubclass(
                        datatype_class,
                        OcrTesseractDatatype,
                    )
                )

    def test_package_datatypes_reach_datatype_base_once(
        self,
    ) -> None:
        for datatype_class in OCR_DATATYPES:
            with self.subTest(datatype_class=datatype_class):
                self.assertEqual(
                    datatype_class.__mro__.count(
                        DatatypeBase
                    ),
                    1,
                )

    def test_batch_structure_precedes_namespace(
        self,
    ) -> None:
        mro = OcrResultBatch.__mro__

        self.assertLess(
            mro.index(BatchBase),
            mro.index(OcrTesseractDatatype),
        )

import unittest

from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result import (
    OcrResult,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_data import (
    OcrResultData,
)


class TestOcrResult(unittest.TestCase):
    def test_stores_ocr_result(self) -> None:
        data = OcrResultData(text="Recognized text")

        result = OcrResult(data)

        self.assertIs(result.data(), data)
        self.assertEqual(
            result.namespace,
            "ocr_tesseract",
        )

    def test_accepts_empty_text(self) -> None:
        result = OcrResult(
            OcrResultData(text="")
        )

        self.assertEqual(result.data().text, "")

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            OcrResult(
                "text"  # type: ignore[arg-type]
            )

    def test_rejects_wrong_text_type(self) -> None:
        data = OcrResultData(
            text=42,  # type: ignore[arg-type]
        )

        with self.assertRaises(TypeError):
            OcrResult(data)

import unittest

from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_batch import (
    OcrResultBatch,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_batch_data import (
    OcrResultBatchData,
)
from cscience.features.ocr_tesseract.ocr_tesseract_datatypes.ocr_result_data import (
    OcrResultData,
)


def make_batch_data() -> OcrResultBatchData:
    return OcrResultBatchData(
        results={
            20: OcrResultData(text="Second"),
            10: OcrResultData(text="First"),
        }
    )


class TestOcrResultBatch(unittest.TestCase):
    def test_stores_ocr_result_batch(self) -> None:
        batch = OcrResultBatch(
            make_batch_data()
        )

        self.assertEqual(batch.batch_size(), 2)
        self.assertEqual(
            batch.namespace,
            "ocr_tesseract",
        )

    def test_orders_results_by_source_key(self) -> None:
        batch = OcrResultBatch(
            make_batch_data()
        )

        self.assertEqual(
            batch.ordered_keys(),
            (10, 20),
        )
        self.assertEqual(
            tuple(
                result.text
                for result in batch.ordered_values()
            ),
            ("First", "Second"),
        )

    def test_rejects_wrong_outer_type(self) -> None:
        with self.assertRaises(TypeError):
            OcrResultBatch(
                {}  # type: ignore[arg-type]
            )

    def test_rejects_empty_batch(self) -> None:
        data = OcrResultBatchData(
            results={}
        )

        with self.assertRaises(ValueError):
            OcrResultBatch(data)

    def test_rejects_non_integer_key(self) -> None:
        data = OcrResultBatchData(
            results={
                "0": OcrResultData(text="Text"),  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            OcrResultBatch(data)

    def test_rejects_wrong_result_type(self) -> None:
        data = OcrResultBatchData(
            results={
                0: "Text",  # type: ignore[dict-item]
            }
        )

        with self.assertRaises(TypeError):
            OcrResultBatch(data)

    def test_rejects_invalid_result_data(self) -> None:
        data = OcrResultBatchData(
            results={
                0: OcrResultData(
                    text=42,  # type: ignore[arg-type]
                )
            }
        )

        with self.assertRaises(TypeError):
            OcrResultBatch(data)

    def test_accepts_empty_ocr_text(self) -> None:
        data = OcrResultBatchData(
            results={
                0: OcrResultData(text=""),
            }
        )

        batch = OcrResultBatch(data)

        self.assertEqual(
            batch.ordered_values()[0].text,
            "",
        )

# From cscience-feature-ocr-tesseract\tests\test_ocr_tesseract_feature.py
import unittest

import pytesseract
from PIL import Image, ImageDraw
from pytesseract import TesseractNotFoundError

from cscience.features.api.feature.feature_info import FeatureInfo
from cscience.features.ocr_tesseract import OcrTesseractConnector
from cscience.features.ocr_tesseract.ocr_config import OcrConfig


def make_text_image(text: str) -> Image.Image:
    image = Image.new("RGB", (500, 120), color="white")
    draw = ImageDraw.Draw(image)
    draw.text((30, 40), text, fill="black")
    return image

def tesseract_available() -> bool:
    try:
        pytesseract.get_tesseract_version()
        return True
    except TesseractNotFoundError:
        return False


class OcrTesseractFeatureTest(unittest.TestCase):

    def test_connector_initializes(self):
        connector = OcrTesseractConnector(OcrConfig())
        self.assertIsNotNone(connector)

    @unittest.skipUnless(
        tesseract_available(),
        "Tesseract executable is not installed or not on PATH.",
    )
    def test_extract_text_from_generated_image(self):
        image = make_text_image("Hello OCR")

        connector = OcrTesseractConnector(OcrConfig())
        text = connector.text(image)

        self.assertIn("Hello", text)
        self.assertIn("ocr", text)

    @unittest.skipUnless(
        tesseract_available(),
        "Tesseract executable is not installed or not on PATH.",
    )
    def test_extract_text_batch_preserves_indices(self):
        images = [
            make_text_image("first ocr"),
            make_text_image("second ocr"),
        ]

        connector = OcrTesseractConnector(OcrConfig())
        results = connector.text_batch(images)

        self.assertEqual(set(results.keys()), {0, 1})
        self.assertIn("first", results[0])
        self.assertIn("second", results[1])



