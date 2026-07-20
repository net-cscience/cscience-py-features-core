from typing import Literal

import torch


def resolve_device(
        preferred_device: Literal["cpu", "cuda", "cuda:1"],
        force_device: bool = False
) -> torch.device:
    device = torch.device(preferred_device if torch.cuda.is_available() else "cpu")
    if force_device and not (preferred_device == str(device)):
        raise RuntimeError(
            f"Preferred device {preferred_device} is not available. "
            f"Available device is {str(device)}."
        )
    return device