import base64
from io import BytesIO
from pathlib import Path

from PIL import Image


def load_base64_image(path: Path) -> Image.Image:
    encoded = path.read_text(encoding="utf-8").strip()
    image_bytes = base64.b64decode(encoded, validate=True)
    return Image.open(BytesIO(image_bytes)).convert("RGB")