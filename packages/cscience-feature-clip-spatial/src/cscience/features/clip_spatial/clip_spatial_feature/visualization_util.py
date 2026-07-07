import numpy as np
import torch
from PIL import Image
from matplotlib import pyplot as plt
import seaborn as sns
import torch.nn.functional as F
from matplotlib.axis import Axis

from .MaskingGenerator import MaskingGenerator

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

