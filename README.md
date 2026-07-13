# CScience Feature Core

Core Python feature infrastructure for CScience feature extraction packages.

The project separates the feature API from concrete feature implementations. The API package defines datatypes, conversion handling, feature lifecycle management, connectors, and registries. Feature packages, such as `cscience-feature-clip`, implement concrete models and expose them through typed connectors.

Configuration loading, `FeatureInfo`, and `ServiceInfo` are intentionally not implemented yet. These parts are planned for a later step.

## Package Structure

```text
packages/
  cscience-feature-api/
    src/cscience/features/api/
      config/          # Config base types; runtime loading is deferred
      connector/       # Public connector abstraction and function wrapper
      conversion/      # Converter, conversion keys, and search strategies
      datatypes/       # Core datatype hierarchy and core conversions
      feature/         # Feature singleton lifecycle and metadata placeholders
      registry/        # Conversion registry
      utils/           # Small development utilities

  cscience-feature-clip/
    src/cscience/features/clip/
      clip_datatypes/  # CLIP-specific datatypes
      clip_feature.py  # Model loading and batch embedding
      clip_connector.py
      clip_conversion_provider.py
      clip_config.py   # Config schema only; loading is deferred
```

## Core Concepts

### Datatypes

All data passed through the feature system is wrapped in explicit datatype classes.

Examples:

```text
Text
TextBatch
FloatVector
FloatVectorBatch
ClipImage
ClipImageBatch
ClipTensorBatch
```

This keeps raw Python types separate from semantic feature types. For example, `list[float]` alone does not describe whether a vector is a CLIP embedding, a YOLO feature, or another embedding type.

### Features

A feature is a singleton service object that owns expensive resources such as model weights.

Example:

```python
feature = ClipFeature.get_instance()
```

Feature initialization happens once per concrete feature class.

### Conversions

A converter maps one datatype into another datatype.

Example:

```text
Text -> TextBatch
ClipImage -> ClipImageBatch
ClipTensorBatch -> FloatVector
```

Converters are registered through a `ConversionProviderBase`.

### Connectors

A connector is the public user-facing API of a feature package.

Example:

```python
clip = ClipConnector()
vector = clip.text("Hello World")
vectors = clip.image_batch(images)
```

Internally, a connector builds a conversion chain:

```text
input datatype -> feature input datatype -> feature output datatype -> output datatype
```

## CLIP Feature Flow

The current CLIP package uses one batch-oriented model path.

```text
Text
  -> TextBatch
  -> ClipTensorBatch
  -> FloatVector

TextBatch
  -> TextBatch
  -> ClipTensorBatch
  -> FloatVectorBatch

ClipImage
  -> ClipImageBatch
  -> ClipTensorBatch
  -> FloatVector

ClipImageBatch
  -> ClipImageBatch
  -> ClipTensorBatch
  -> FloatVectorBatch
```

`ClipFeature` performs the actual model inference. `ClipConnector` exposes convenient methods for normal Python inputs and outputs.

## Adding a New Feature

Create a new package:

```text
packages/cscience-feature-example/
  pyproject.toml
  src/cscience/features/example/
    __init__.py
    example_datatype.py
    example_feature.py
    example_connector.py
    example_conversion_provider.py
    example_datatypes/
      example_input.py
      example_tensor_batch.py
```

### 1. Define feature-specific datatypes

```python
class ExampleDatatype(DatatypeBase, ABC):
    namespace = "example"
```

Then define concrete input and output datatypes:

```python
class ExampleInput(ExampleDatatype):
    pass

class ExampleTensorBatch(ExampleDatatype):
    pass
```

Use core datatypes such as `Text`, `TextBatch`, `FloatVector`, and `FloatVectorBatch` when possible.

### 2. Implement the feature

```python
class ExampleFeature(FeatureBase):

    def _initialize(self) -> None:
        # Load model weights or other expensive resources here.
        pass

    @classmethod
    def embed_batch(cls, data: ExampleInputBatch) -> ExampleTensorBatch:
        service = cls.get_instance()
        # Run inference here.
        ...
```

Feature methods should consume and return datatype classes, not raw Python values.

### 3. Register conversions

```python
class ExampleConversionProvider(ConversionProviderBase):

    def register_converters(self) -> list[Converter]:
        return [
            Converter(
                name="example_tensor_batch_to_float_vector_batch",
                source=self._feature,
                function=lambda x: FloatVectorBatch(...),
                input_type=ExampleTensorBatch,
                output_type=FloatVectorBatch,
            ),
        ]
```

Add converters for all public input and output forms the connector should support.

### 4. Implement the connector

```python
class ExampleConnector(ConnectorBase):

    def __init__(self) -> None:
        self.feature = ExampleFeature.get_instance()
        super().__init__("example", ExampleConversionProvider(self.feature))

    def text(self, data: str) -> list[float]:
        function = FunctionConnector(
            feature=self.feature,
            function=self.feature.embed_batch,
            input_type=Text,
            input_feature_type=TextBatch,
            output_feature_type=ExampleTensorBatch,
            output_type=FloatVector,
        )
        return function(Text(data)).data()
```

The connector should expose normal Python input and output types.

### 5. Add package entry-point registration

In the feature package `__init__.py`:

```python
def register(registry: RegistryBase) -> None:
    registry.register("example", ExampleConversionProvider)
```

In `pyproject.toml`:

```toml
[project.entry-points."cscience.features"]
example = "cscience.features.example:register"
```

## CUDA Support

CUDA dependencies belong to feature packages, not to `cscience-feature-api`.

The CLIP package maps PyTorch to the CUDA 12.8 wheel index through `tool.uv.sources` and `[[tool.uv.index]]`. The API package intentionally stays lightweight and only depends on Pydantic.

## Development Notes

Run tests from the package or workspace root:

```bash
uv run pytest
```

Verify CUDA availability:

```bash
uv run python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available())"
```

Use the timing decorator only for local benchmarking and development tests.

### PyCharm Support

When using PyCharm, install the **Pydantic** plugin to improve type inference and constructor completion for Pydantic models.

Without the plugin, PyCharm may incorrectly report inherited custom constructor arguments such as `namespace`, `mode`, or `config_path` as unexpected, although the code runs correctly.

