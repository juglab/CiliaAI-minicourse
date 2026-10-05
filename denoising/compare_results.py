"""Compare the original image with all denoised results.

Usage (from the denoising folder, using the BM3D environment):
    uv run --project denoise-bm3d compare_results.py

Reads   ../data/convollaria.tif  and  results/*.tif
Writes  results/comparison.png            (one row per image)
        results/residuals/*_residual.tif  (original - denoised, for Fiji)
"""
from pathlib import Path

import numpy as np
import tifffile
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / "data" / "convollaria.tif"
RESULTS = HERE / "results"

# Crops shown at 1:1 (y, x, size). Change these to look at other regions!
CROPS = {
    "bright structure": (400, 520, 128),
    "fine structure": (560, 20, 128),
    "dim region": (700, 850, 128),
}


def crop(img, y, x, s):
    return img[y:y + s, x:x + s]


def main():
    original = tifffile.imread(ORIGINAL).astype(np.float32)
    files = sorted(p for p in RESULTS.glob(f"{ORIGINAL.stem}_*.tif"))
    if not files:
        raise SystemExit(f"No results found in {RESULTS}. Run the denoising first.")
    images = {"original": original}
    images.update({p.stem.replace(f"{ORIGINAL.stem}_", ""): tifffile.imread(p).astype(np.float32)
                   for p in files})

    # ONE display range for every image, taken from the original
    vmin, vmax = np.percentile(original, [1, 99.8])
    rlim = 200  # residual display range: -rlim .. +rlim

    (RESULTS / "residuals").mkdir(exist_ok=True)
    first_crop = next(iter(CROPS.values()))
    ncols = 2 + len(CROPS) + 1
    fig, axes = plt.subplots(len(images), ncols, figsize=(2.6 * ncols, 2.6 * len(images)))

    print(f"{'image':>16} | {'residual mean':>13} | {'residual std':>12} | {'std in dim crop':>17}")
    for i, (row, (name, img)) in enumerate(zip(axes, images.items())):
        residual = original - img
        if name != "original":
            tifffile.imwrite(RESULTS / "residuals" / f"{name}_residual.tif", residual)
        dim = crop(img, *CROPS["dim region"])
        print(f"{name:>16} | {residual.mean():13.1f} | {residual.std():12.1f} | {dim.std():17.1f}")

        panels = [(img, "full image", "gray", vmin, vmax)]
        panels += [(crop(img, *c), title, "gray", vmin, vmax) for title, c in CROPS.items()]
        panels += [(residual, "residual (full)", "RdBu_r", -rlim, rlim),
                   (crop(residual, *first_crop), "residual (bright crop)", "RdBu_r", -rlim, rlim)]
        for ax, (data, title, cmap, lo, hi) in zip(row, panels):
            ax.imshow(data, cmap=cmap, vmin=lo, vmax=hi, interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            if i == 0:
                ax.set_title(title, fontsize=9)
        row[0].set_ylabel(name, fontsize=10)

    fig.suptitle(f"Same display range for all images: {vmin:.0f} .. {vmax:.0f}", fontsize=10)
    fig.tight_layout()
    out = RESULTS / "comparison.png"
    fig.savefig(out, dpi=150)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
