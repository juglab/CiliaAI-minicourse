# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "numpy",
#     "tifffile",
#     "matplotlib",
#     "scikit-image",
#     "pillow",
# ]
# ///
"""Denoising, Part 3: how close did we get to the truth?

Compares every denoised image in a folder with a clean (low-noise) version of
data/convollaria.tif, computes PSNR and SSIM, and plots the results.

Usage (from the top folder of the course material):

    uv run denoising/benchmark/benchmark.py

Options:
    --folder PATH   folder with your results (default: denoising/benchmark/submissions)
    --clean PATH    clean reference image   (default: data/convollaria-clean.tif,
                    downloaded from the 'solution' branch on the first run)

Reads   all .tif / .tiff / .png / .jpg files in the folder
Writes  denoising/benchmark/output/scores.png   PSNR and SSIM of every result
        denoising/benchmark/output/images.png   visual comparison, best first
        denoising/benchmark/output/scores.csv   the numbers, for your own plots
"""
import argparse
import csv
import urllib.request
from pathlib import Path

import numpy as np
import tifffile
from PIL import Image
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NOISY = ROOT / "data" / "convollaria.tif"
CLEAN = ROOT / "data" / "convollaria-clean.tif"
SUBMISSIONS = HERE / "submissions"
OUTPUT = HERE / "output"
EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".jpeg"}

# The clean image is not on the main branch (it would spoil Parts 1 and 2).
# It lives on the 'solution' branch and is downloaded from there when needed.
CLEAN_URL = ("https://raw.githubusercontent.com/juglab/CiliaAI-minicourse/"
             "solution/data/convollaria-clean.tif")

# Crops shown at 1:1 in images.png (y, x, size). Change them to look elsewhere!
CROPS = {
    "fine structure": (150, 400, 128),
    "bright ring + dim cells": (440, 560, 128),
}

# Error colour map: black at zero error (needs matplotlib >= 3.10, else a fallback)
ERROR_CMAP = "berlin" if "berlin" in matplotlib.colormaps else "RdBu_r"

# Colours (dark theme, like the course slides)
BG, INK, MUTED, GRID = "#000000", "#e6e6e6", "#9a9a9a", "#333333"
RESULT, BASELINE = "#3987e5", "#6b6b6b"


def load(path):
    """Load an image as 2D float64, whatever the file format."""
    if path.suffix.lower() in {".tif", ".tiff"}:
        img = tifffile.imread(path)
    else:
        img = np.asarray(Image.open(path))
    img = np.squeeze(np.asarray(img, dtype=np.float64))
    if img.ndim == 3 and img.shape[-1] in (3, 4):   # RGB(A) -> grey
        img = img[..., :3].mean(axis=-1)
    return img


def fit_to(img, ref):
    """Best brightness/contrast match a*img + b to the reference (least squares).

    Tools save results in different ranges (16-bit, float, 8-bit PNG, 0..1).
    Matching brightness and contrast first makes the comparison fair to all
    of them: only the *shape* of the signal counts, not its units.
    """
    a, b = np.polyfit(img.ravel(), ref.ravel(), 1)
    return a * img + b


def score(img, clean, data_range):
    return (peak_signal_noise_ratio(clean, img, data_range=data_range),
            structural_similarity(clean, img, data_range=data_range))


def nice_name(path):
    return path.stem.replace("_", " · ")


def collect(folder, clean):
    entries, skipped = [], []
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in EXTENSIONS or p.name.startswith("."):
            continue
        try:
            img = load(p)
        except Exception as e:  # unreadable file: report and carry on
            skipped.append((p.name, f"could not read ({e.__class__.__name__})"))
            continue
        if img.shape != clean.shape:
            skipped.append((p.name, f"size {img.shape}, expected {clean.shape}"))
            continue
        if not np.isfinite(img).all():
            skipped.append((p.name, "contains NaN or Inf values"))
            continue
        entries.append({"name": nice_name(p), "file": p.name, "img": fit_to(img, clean)})
    return entries, skipped


def style(ax):
    ax.set_facecolor(BG)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=10, length=0)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def plot_scores(rows, out):
    """Two dot plots (PSNR, SSIM) that share one row per result, best first."""
    n = len(rows)
    fig, axes = plt.subplots(1, 2, figsize=(12, 1.3 + 0.42 * n), facecolor=BG, sharey=True)
    y = np.arange(n)[::-1]
    base = next(r for r in rows if r["baseline"])
    for ax, key, title, fmt in [(axes[0], "psnr", "PSNR in dB (higher is better)", "{:.1f}"),
                                (axes[1], "ssim", "SSIM (higher is better, max 1)", "{:.3f}")]:
        style(ax)
        vals = np.array([r[key] for r in rows])
        pad = (vals.max() - vals.min()) * 0.12 + 1e-9
        ax.set_xlim(vals.min() - pad, vals.max() + 2.2 * pad)
        ax.axvline(base[key], color=BASELINE, lw=1, ls=(0, (3, 3)))
        for yi, v, r in zip(y, vals, rows):
            c = BASELINE if r["baseline"] else RESULT
            ax.plot([ax.get_xlim()[0], v], [yi, yi], color=GRID, lw=1, zorder=1)
            ax.scatter([v], [yi], s=70, color=c, edgecolor=BG, linewidth=2, zorder=3)
            ax.text(v + pad * 0.35, yi, fmt.format(v), va="center", color=INK, fontsize=10)
        ax.set_title(title, color=INK, fontsize=12, loc="left", pad=10)
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([r["name"] for r in rows], color=INK, fontsize=10)
    axes[0].set_ylim(-0.7, n - 0.3)
    fig.text(0.01, 0.005, "Grey dot and dashed line: the noisy input, i.e. no denoising at all. "
             "Every image was brightness/contrast-matched to the clean image before scoring.",
             color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(out, dpi=150, facecolor=BG)
    plt.close(fig)


def plot_images(rows, clean, out):
    vmin, vmax = np.percentile(clean, [0.5, 99.8])
    elim = 150   # error display range: -elim .. +elim (intensity units)
    show = [{"name": "clean reference", "img": clean, "psnr": None, "ssim": None}] + rows
    ncols = 1 + 2 * len(CROPS)
    fig, axes = plt.subplots(len(show), ncols, figsize=(2.3 * ncols, 2.45 * len(show)),
                             facecolor=BG, squeeze=False)
    titles = ["full image"]
    for t in CROPS:
        titles += [t, "error: result − clean"]
    for i, (row, r) in enumerate(zip(axes, show)):
        img = r["img"]
        panels = [(img, "gray", vmin, vmax)]
        for (y, x, s) in CROPS.values():
            c = img[y:y + s, x:x + s]
            panels.append((c, "gray", vmin, vmax))
            panels.append((c - clean[y:y + s, x:x + s], ERROR_CMAP, -elim, elim))
        for j, (ax, (data, cmap, lo, hi)) in enumerate(zip(row, panels)):
            ax.imshow(data, cmap=cmap, vmin=lo, vmax=hi, interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_color("#444444")
            if i == 0:
                ax.set_title(titles[j], color=MUTED, fontsize=9)
            if i == 0 and cmap == ERROR_CMAP:
                ax.set_facecolor(BG); ax.images[0].remove()   # no error for the reference itself
                ax.text(0.5, 0.5, "(reference)", color=MUTED, fontsize=9,
                        ha="center", va="center", transform=ax.transAxes)
        for (y, x, s) in CROPS.values():
            row[0].add_patch(plt.Rectangle((x, y), s, s, fill=False, ec="#e8c547", lw=0.8))
        label = r["name"] if r["psnr"] is None else f"{r['name']}\n{r['psnr']:.1f} dB · SSIM {r['ssim']:.3f}"
        row[0].set_ylabel(label, color=INK, fontsize=9, rotation=0, ha="right", va="center", labelpad=8)
    fig.suptitle(f"Same display range for all images ({vmin:.0f} .. {vmax:.0f}). "
                 f"Error maps from −{elim} (blue, too dark) over 0 (black) "
                 f"to +{elim} (red, too bright): visible structure there means signal was removed or invented.", color=MUTED, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.985))
    fig.savefig(out, dpi=120, facecolor=BG)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--folder", type=Path, default=SUBMISSIONS)
    ap.add_argument("--clean", type=Path, default=CLEAN)
    args = ap.parse_args()

    if not args.clean.exists() and args.clean == CLEAN:
        print(f"Downloading the clean reference image from the 'solution' branch ...")
        try:
            with urllib.request.urlopen(CLEAN_URL, timeout=60) as r:
                data = r.read()
            CLEAN.write_bytes(data)
        except Exception as e:
            raise SystemExit(f"Could not download {CLEAN_URL}\n({e})\n"
                             f"Download it in your browser and save it as {CLEAN}.")
    if not args.clean.exists():
        raise SystemExit(f"Clean reference not found: {args.clean}")
    if not args.folder.is_dir():
        raise SystemExit(f"Folder not found: {args.folder}")

    clean = load(args.clean)
    data_range = clean.max() - clean.min()
    entries, skipped = collect(args.folder, clean)
    if not entries:
        raise SystemExit(f"No usable images found in {args.folder}. "
                         "Copy your denoised .tif files there first.")

    rows = []
    noisy = fit_to(load(NOISY), clean)
    p, s = score(noisy, clean, data_range)
    rows.append({"name": "noisy input (no denoising)", "file": NOISY.name, "img": noisy,
                 "psnr": p, "ssim": s, "baseline": True})
    for e in entries:
        p, s = score(e["img"], clean, data_range)
        rows.append({**e, "psnr": p, "ssim": s, "baseline": False})
    rows.sort(key=lambda r: r["psnr"], reverse=True)

    OUTPUT.mkdir(exist_ok=True)
    with open(OUTPUT / "scores.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "name", "file", "psnr_db", "ssim"])
        for i, r in enumerate(rows, 1):
            w.writerow([i, r["name"], r["file"], f"{r['psnr']:.2f}", f"{r['ssim']:.4f}"])
    plot_scores(rows, OUTPUT / "scores.png")
    plot_images(rows, clean, OUTPUT / "images.png")

    width = max(len(r["name"]) for r in rows)
    print(f"\n{'#':>3}  {'result':<{width}}  {'PSNR (dB)':>9}  {'SSIM':>6}")
    for i, r in enumerate(rows, 1):
        print(f"{i:>3}  {r['name']:<{width}}  {r['psnr']:9.2f}  {r['ssim']:6.3f}")
    for name, why in skipped:
        print(f"  skipped {name}: {why}")
    print(f"\nWrote {OUTPUT / 'scores.png'}, {OUTPUT / 'images.png'} and {OUTPUT / 'scores.csv'}")


if __name__ == "__main__":
    main()
