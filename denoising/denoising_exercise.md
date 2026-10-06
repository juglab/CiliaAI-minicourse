# Denoising, Part 2 (local track): BM3D and Noise2Void on your laptop

> This is the **local track** of Part 2. It needs the setup from the main [README](../README.md#before-the-course-get-ready). Prefer not to install anything? Do the **Colab track** instead: [open the notebook in Colab](https://colab.research.google.com/github/juglab/CiliaAI-minicourse/blob/main/denoising/CAREamics_Noise2Void_2D_ZeroCostDL4Mic.ipynb).

In this exercise you denoise the fluorescence image `data/convollaria.tif` (a section through a *Convallaria* rhizome) with two very different methods and compare what they do:

1. **BM3D**, a classical, hand-designed denoiser. It assumes additive Gaussian noise of known strength `sigma` and averages similar-looking patches across the image.
2. **Noise2Void (N2V)**, a self-supervised neural network. It learns to denoise from the noisy image itself, without ever seeing a clean image.

Our goal is not the smoothest-looking image. A good denoiser removes noise **and keeps the real biological structure**, without inventing anything or shifting intensities.

About the image: 2D, 16-bit, 1024 × 1024 pixels, intensities roughly 330 to 1850 (most signal between 400 and 1200). A rough estimate of the noise standard deviation is ~50 intensity units.

> Before you start: install uv as described in the main [README](../README.md).
> All commands below are run in a terminal. Lines starting with `#` are comments.

---

## Step 0: Get oriented

Open a terminal and go to the `denoising` folder of the course material:

```bash
cd path/to/CiliaAI-minicourse/denoising
```

You will see two sub-projects. They have **separate Python environments** on purpose: BM3D runs on a modern Python, while the original N2V needs an older TensorFlow stack (Python 3.9, TensorFlow 2.13, NumPy 1.24). Mixing both in one environment would not work.

Optional, but nice: open `../data/convollaria.tif` in Fiji and look at it. Zoom in. Where do you see noise? Is it equally strong in bright and dark regions?

---

## Part 1: BM3D

### 1.1 Create the environment

```bash
cd denoise-bm3d
uv sync
```

`uv sync` reads `pyproject.toml` and `uv.lock`, downloads Python 3.12 if needed, and installs `bm3d`, `numpy`, `tifffile` and `matplotlib` into a local `.venv` folder. This takes a minute the first time.

### 1.2 Run BM3D at three noise levels

BM3D needs to be told how strong the noise is (`sigma`, in the image's own intensity units). We do not know the exact value, so we try three:

```bash
uv run bm3d_denoise.py ../../data/convollaria.tif 25 40 55
```

Each sigma takes roughly half a minute. The results are written to `denoising/results/`:

```text
convollaria_bm3d_sigma25.tif
convollaria_bm3d_sigma40.tif
convollaria_bm3d_sigma55.tif
```

Have a look at `bm3d_denoise.py`. The actual denoising is a single line: `bm3d(img, sigma_psd=sigma)`.

> **Think about it**
> - What do you expect to happen if sigma is too small? Too large?
> - Open the three results in Fiji. Which one would you trust for measuring membrane intensities?

---

## Part 2: Noise2Void

### 2.1 Create the environment

```bash
cd ../denoise-n2v
uv sync
```

This downloads Python 3.9 and the TensorFlow 2.13 stack (a large download of several hundred MB, so be patient). The `pyproject.toml` picks the correct TensorFlow package for your platform automatically (Apple Silicon Macs, for example, need `tensorflow-macos`).

Check that everything imports:

```bash
uv run python -c "import tensorflow as tf, numpy as np, n2v; print('TF', tf.__version__, '| NumPy', np.__version__, '| N2V OK')"
```

You should see `TF 2.13.x | NumPy 1.24.3 | N2V OK`. TensorFlow likes to print informational messages (for example that no GPU or CUDA was found); you can ignore those. A Python traceback, however, means something went wrong; ask a tutor.

### 2.2 Train N2V and denoise

```bash
uv run n2v_denoise.py ../../data/convollaria.tif
```

What happens inside `n2v_denoise.py`:

1. The image is cut into 64 × 64 patches (plus rotated and flipped copies), 90 % for training and 10 % for validation.
2. A small U-Net is trained with the **blind-spot** trick: a few pixels per patch are hidden and the network has to predict them from their neighbours. Because noise is (ideally) independent from pixel to pixel, the network cannot predict the noise, only the signal.
3. The trained network denoises the full image.

By default it trains for 20 epochs, which takes a few minutes on a laptop CPU. Watch `loss` and `val_loss` go down while it runs. The result is written to `denoising/results/convollaria_n2v.tif`, and the trained model to `denoise-n2v/models/`.

If you have time (or a GPU), train longer and compare:

```bash
uv run n2v_denoise.py ../../data/convollaria.tif --epochs 100
```

> **Think about it**
> - N2V never saw a clean image. Why can it still learn to denoise?
> - Which assumption about the noise does the blind-spot trick rely on? What would happen if neighbouring pixels had correlated noise (for example after some camera processing)?

---

## Part 3: Compare the results

### 3.1 The comparison figure

Go back to the `denoising` folder and run the comparison script with the BM3D environment (it already has matplotlib):

```bash
cd ..
uv run --project denoise-bm3d compare_results.py
```

This writes:

- `results/comparison.png`: one row per image (original, the three BM3D results, N2V). Columns show the full image, three 1:1 crops (bright structure, fine structure, dim region) and the **residual** `original − denoised`. All images use **the same display range**, otherwise comparisons are meaningless.
- `results/residuals/*_residual.tif`: the residual images, for closer inspection.
- A small table in the terminal (residual mean and standard deviation, and the remaining standard deviation in the dim crop).

Want to look at other regions? Change the `CROPS` at the top of `compare_results.py` and run it again.

### 3.2 Explore in Fiji (recommended)

The figure is a fixed snapshot. Fiji lets you explore much more flexibly:

1. Open the original and all files from `results/` (drag and drop them onto Fiji).
2. `Image › Stacks › Images to Stack` puts them into one stack. A stack shares **one** display range, so `Image › Adjust › Brightness/Contrast` now applies identically to all images. Scroll through the slices to flip between methods.
3. Alternatively, keep separate windows and use `Analyze › Tools › Synchronize Windows` to zoom and pan in all of them at once.
4. Open the residuals from `results/residuals/` the same way. Use a symmetric display range (for example −200 to +200).
5. Draw a line across a membrane and use `Analyze › Plot Profile` on the original and the denoised images. Are edges preserved? Are peak intensities preserved?

### 3.3 How to read residuals

The residual is what a method **removed**. Ideally it is pure noise: no visible structure, no change of mean with intensity.

- **Structure visible in the residual** (cell outlines, rings) means the method removed real signal: over-smoothing.
- **Residual stronger in bright regions** is expected for fluorescence images, because photon (shot) noise grows with intensity. A method that removes only a constant amount of noise everywhere leaves bright regions noisy.
- **A non-zero residual mean** in some regions means the method biased intensities, which matters if you want to measure them later.

---

## Discussion

Discuss these with your neighbour; there is no single right answer.

1. **Which BM3D sigma would you choose, and why?** Look at both the dim crop and the bright crop.
2. **BM3D vs N2V in bright regions.** BM3D assumes the same Gaussian noise everywhere. Fluorescence images are dominated by shot noise, whose strength depends on the signal. How does this show up in the residuals? (One classical fix is a variance-stabilising transform such as the generalised Anscombe transform before BM3D.)
3. **Is the N2V residual "just noise"?** Look closely at the bright rings. Is the residual there unstructured noise that happens to be stronger, or do you see sharp features that were removed? How would you test this more rigorously?
4. **Smooth is not the same as correct.** Which result looks nicest? Which would you trust most for (a) counting cells, (b) measuring membrane intensity, (c) a figure in a paper?
5. **Hallucinations.** Can a neural network add structure that is not there? Where would you look for evidence of this?
6. **Training data.** Here N2V was trained on a single image. What would you do if you had 50 images from the same microscope with the same settings?

---

## Going further

- Train N2V on several images acquired under the same conditions instead of a single one.
- Try **N2V2**, which reduces the checkerboard artifacts sometimes seen with N2V.
- The original `n2v` package depends on an old TensorFlow. For real projects use [**CAREamics**](https://careamics.github.io/), the modern PyTorch-based successor that implements N2V, N2V2 and more.
- Quantitative checks beyond eyeballing: spatial autocorrelation of residuals, residual vs. intensity, preservation of edge gradients and local maxima.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `uv: command not found` | Close and reopen the terminal after installing uv. |
| `No module named 'tensorflow'` | Make sure you ran `uv sync` **inside** `denoise-n2v`, not in `denoise-bm3d`. |
| N2V is very slow | Use fewer epochs (`--epochs 5`); the result will be a bit noisier but the exercise still works. |
| N2V on Windows with an NVIDIA GPU | This old TensorFlow version has no native Windows GPU support. CPU works fine for this exercise; for GPU use WSL2. |
| `compare_results.py` says "No results found" | Run the BM3D and/or N2V steps first; results go to `denoising/results/`. |

Note: the denoised images are saved as 32-bit float TIFFs, so no information is lost by rounding back to 16-bit integers.
