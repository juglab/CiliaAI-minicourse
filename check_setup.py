# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Check that your laptop is ready for the CiliaAI mini-course.

Run this from the top folder of the course material, ideally BEFORE the course:

    uv run check_setup.py

It installs the two Python environments used in the denoising exercise and
tests that they work. The first run needs internet and downloads several
hundred MB (mostly TensorFlow), so it can take 5 to 15 minutes. Later runs
are fast.
"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "convollaria.tif"
MIN_FREE_GB = 5

BM3D_TEST = r"""
import sys
import numpy as np, tifffile, matplotlib
from bm3d import bm3d
img = tifffile.imread(sys.argv[1]).astype(np.float32)
assert img.shape == (1024, 1024), img.shape
out = bm3d(img[:64, :64], sigma_psd=50)
assert out.shape == (64, 64)
print("bm3d ran on a small crop, matplotlib", matplotlib.__version__)
"""

N2V_TEST = r"""
import os, sys, tempfile
import numpy as np, tifffile, tensorflow as tf
from n2v.models import N2VConfig, N2V
img = tifffile.imread(sys.argv[1]).astype(np.float32)
X = img[np.newaxis, :64, :64, np.newaxis]
config = N2VConfig(X, unet_kern_size=3, train_steps_per_epoch=1, train_epochs=1,
                   n2v_patch_shape=(64, 64), train_batch_size=1)
with tempfile.TemporaryDirectory() as tmp:
    model = N2V(config=config, name="setup_check", basedir=tmp)
    pred = model.predict(img[:64, :64], axes="YX")
assert pred.shape == (64, 64)
print("TensorFlow", tf.__version__, "| NumPy", np.__version__,
      "| an (untrained) N2V network ran on a small crop")
"""

ENVIRONMENTS = [
    ("BM3D environment", ROOT / "denoising" / "denoise-bm3d", BM3D_TEST),
    ("Noise2Void environment", ROOT / "denoising" / "denoise-n2v", N2V_TEST),
]

results = []


def report(name, ok, detail=""):
    results.append((name, ok))
    tag = "[ OK ]" if ok else "[FAIL]"
    print(f"{tag} {name}" + (f": {detail}" if detail else ""))


def heading(text):
    print()
    print(text)
    print("-" * len(text))


def main():
    heading("Your system")
    print(f"Operating system: {platform.system()} {platform.release()} ({platform.machine()})")

    uv = shutil.which("uv")
    if uv is None:
        report("uv is installed", False,
               "not found. Install it as described in README.md, then reopen your terminal.")
        return
    version = subprocess.run([uv, "--version"], capture_output=True, text=True).stdout.strip()
    report("uv is installed", True, version)

    free_gb = shutil.disk_usage(ROOT).free / 1e9
    report("Free disk space", free_gb >= MIN_FREE_GB,
           f"{free_gb:.1f} GB" + ("" if free_gb >= MIN_FREE_GB else f" (please free up at least {MIN_FREE_GB} GB)"))

    report("Example image is present", DATA.is_file(), str(DATA.relative_to(ROOT)))
    if not DATA.is_file():
        return

    env = dict(os.environ, TF_CPP_MIN_LOG_LEVEL="2")  # hide TensorFlow info messages
    env.pop("VIRTUAL_ENV", None)  # set by "uv run" for this script; not meant for the exercise projects
    for name, project, test in ENVIRONMENTS:
        heading(f"{name} ({project.relative_to(ROOT)})")
        print("Installing (uv sync). The first time this downloads packages, please be patient...")
        sync = subprocess.run([uv, "sync"], cwd=project, env=env)
        if sync.returncode != 0:
            report(f"{name}: installation", False, "uv sync failed, see the messages above")
            continue
        report(f"{name}: installation", True)

        print("Testing...")
        run = subprocess.run([uv, "run", "python", "-c", test, str(DATA)],
                             cwd=project, env=env, capture_output=True, text=True)
        if run.returncode == 0:
            report(f"{name}: test", True, run.stdout.strip().splitlines()[-1])
        else:
            print(run.stdout)
            print(run.stderr[-3000:])
            report(f"{name}: test", False, "see the error messages above")
            arm = platform.machine().lower() in ("arm64", "aarch64")
            if "BM3D" in name and arm and platform.system() != "Darwin":
                print("       Note: the bm3d package ships no compiled library for ARM processors on")
                print("       Linux or Windows. You can still do the Noise2Void part of the exercise.")


if __name__ == "__main__":
    main()
    heading("Summary")
    failed = [name for name, ok in results if not ok]
    if not failed:
        print("Everything works. You are ready for the course!")
    else:
        print("Something is not working yet:")
        for name in failed:
            print(f"  - {name}")
        print("Try to fix it with the hints above. If you are stuck, bring your laptop")
        print("and the full output of this script to the course, and we will help you.")
    sys.exit(1 if failed else 0)
