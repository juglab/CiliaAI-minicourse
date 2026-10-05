"""Denoise a 2D TIFF with BM3D at one or more noise levels (sigma).

Usage (from the denoise-bm3d folder):
    uv run bm3d_denoise.py ../../data/convollaria.tif 25 40 55
"""
from pathlib import Path
import sys
import time

import numpy as np
import tifffile
from bm3d import bm3d

RESULTS = Path(__file__).resolve().parent.parent / "results"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)

    path = Path(sys.argv[1])
    sigmas = [float(s) for s in sys.argv[2:]] or [40.0]

    original = tifffile.imread(path)
    if original.ndim != 2:
        raise ValueError(f"Expected a 2D image, got shape {original.shape}")
    img = original.astype(np.float32)

    print(f"Image: {img.shape}, {original.dtype}, range {img.min():.0f} .. {img.max():.0f}")
    RESULTS.mkdir(exist_ok=True)

    for sigma in sigmas:
        # sigma is in the image's own intensity units (no normalisation!)
        t0 = time.time()
        denoised = bm3d(img, sigma_psd=sigma)
        out = RESULTS / f"{path.stem}_bm3d_sigma{sigma:g}.tif"
        tifffile.imwrite(out, denoised.astype(np.float32))
        print(f"sigma={sigma:g}: wrote {out.name} ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
