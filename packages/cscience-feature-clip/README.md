# CScience CLIP Feature

OpenCLIP text and image embeddings with stable batch keys and core vector conversion.

## Overview

| Property | Value |
|---|---|
| Distribution | `cscience-feature-clip` |
| Namespace | `clip` |
| Runtime | OpenCLIP and PyTorch |
| Entry point | `clip = cscience.features.clip:register` |

The package embeds text and Pillow images into normalized CLIP vectors. Feature datatypes retain packed Torch tensors; connector outputs use core float vectors.

## Architecture

```mermaid
flowchart LR
    A["str / PIL.Image"] --> B["ClipConnector"]
    B --> C["TextBatch / PilImageBatch"]
    C --> D["ClipFeature"]
    D --> E["ClipTensorBatch<br/>[N, D]"]
    E --> F["ClipConversionProvider"]
    F --> G["FloatVector / FloatVectorBatch"]
```

Text and image inputs share the same normalized embedding space.

## Public API

### Connector

| Method | Input | Output | Purpose |
|---|---|---|---|
| `text(data)` | `str` | `list[float]` | Embed one text |
| `text_batch(data)` | `list[str]` | `dict[int, list[float]]` | Embed texts by input position |
| `image(data)` | `PIL.Image.Image` | `list[float]` | Embed one image |
| `image_batch(data)` | `list[PIL.Image.Image]` | `dict[int, list[float]]` | Embed images by input position |

### Feature

| Method | Input datatype | Output datatype |
|---|---|---|
| `text_batch(texts)` | `TextBatch` | `ClipTensorBatch` |
| `image_batch(images)` | `PilImageBatch` | `ClipTensorBatch` |

## Datatypes

| Datatype | Stored representation | Guarantee |
|---|---|---|
| `ClipDatatype[T]` | `T` | CLIP namespace and data ownership |
| `ClipTensor` | `Tensor[D]` | Non-empty floating-point embedding |
| `ClipTensorBatchData` | keys plus `Tensor[N, D]` | Packed row-to-source mapping |
| `ClipTensorBatch` | `ClipTensorBatchData` | Non-empty uniform embedding batch |

`ClipTensorBatch.keys` preserves packed tensor row order. `ordered_keys()` provides canonical ascending source-key order.

## Configuration

| Field | Default | Meaning |
|---|---|---|
| `model_name` | `xlm-roberta-base-ViT-B-32` | OpenCLIP model architecture |
| `pretrained` | `laion5b_s13b_b90k` | Pretrained checkpoint |
| `preferred_device` | `cuda` | Requested inference device |
| `force_device` | `False` | Fail instead of falling back when the device is unavailable |

## Usage

```python
from PIL import Image

from cscience.features.clip import ClipConnector
from cscience.features.clip.clip_config import ClipConfig

connector = ClipConnector(ClipConfig())

text_vector = connector.text("a red industrial robot")
image_vector = connector.image(Image.open("robot.png").convert("RGB"))
```

## Development

```bash
uv run pytest packages/cscience-feature-clip/tests
```

Model-backed tests may download OpenCLIP weights and use the configured Torch device.

## Design Notes

- Embeddings are normalized before leaving `ClipFeature`.
- Feature datatypes keep packed tensors for efficient inference and scoring.
- Connector outputs use core `FloatVector` and `FloatVectorBatch` datatypes.
- Model selection and device policy belong to `ClipConfig`, not the datatypes.
