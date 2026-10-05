"""Train Noise2Void on a single 2D TIFF and denoise it.

Usage (from the denoise-n2v folder):
    uv run n2v_denoise.py ../../data/convollaria.tif            # quick run
    uv run n2v_denoise.py ../../data/convollaria.tif --epochs 100  # longer run
"""
from pathlib import Path
import argparse

import numpy as np
import tifffile
from n2v.models import N2VConfig, N2V
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator

RESULTS = Path(__file__).resolve().parent.parent / "results"
MODELS = Path(__file__).resolve().parent / "models"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input", type=Path)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--patch", type=int, default=64)
    parser.add_argument("--batch", type=int, default=32)
    args = parser.parse_args()

    original = tifffile.imread(args.input)
    if original.ndim != 2:
        raise ValueError(f"Expected a 2D image, got shape {original.shape}")
    img = original.astype(np.float32)
    print(f"Image: {img.shape}, {original.dtype}, range {img.min():.0f} .. {img.max():.0f}")

    # 1. Cut the image into patches (with flips/rotations as augmentation)
    datagen = N2V_DataGenerator()
    patches = datagen.generate_patches_from_list(
        [img[np.newaxis, ..., np.newaxis]], shape=(args.patch, args.patch))
    rng = np.random.default_rng(42)
    rng.shuffle(patches, axis=0)
    n_val = max(1, int(0.1 * len(patches)))
    X_val, X = patches[:n_val], patches[n_val:]
    print(f"Patches: {len(X)} for training, {len(X_val)} for validation")

    # 2. Configure and train the network
    config = N2VConfig(
        X,
        unet_kern_size=3,
        train_steps_per_epoch=max(1, len(X) // args.batch),
        train_epochs=args.epochs,
        train_loss="mse",
        batch_norm=True,
        train_batch_size=args.batch,
        n2v_perc_pix=1.6,
        n2v_patch_shape=(args.patch, args.patch),
        n2v_manipulator="uniform_withCP",
        n2v_neighborhood_radius=5,
    )
    model = N2V(config=config, name=f"{args.input.stem}_n2v", basedir=str(MODELS))
    model.train(X, X_val)

    # 3. Denoise the full image with the trained network
    pred = model.predict(img, axes="YX")

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"{args.input.stem}_n2v.tif"
    tifffile.imwrite(out, pred.astype(np.float32))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
