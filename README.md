# CiliaAI mini-course: hands-on exercises

Material for the hands-on part of the Cilia-AI / CiliaConnect mini-course on image analysis and AI.

## Exercises

| Exercise | Folder | What you do |
|---|---|---|
| Denoising | [`denoising/`](denoising/) | Denoise a fluorescence microscopy image with a classical method (BM3D) and a self-supervised deep learning method (Noise2Void), then compare the results. |

More exercises will be added. Each one lives in its own folder and comes with step-by-step instructions.

## Repository layout

```text
CiliaAI-minicourse/
├── README.md                  this file
├── data/
│   └── convollaria.tif        example image (2D, 16-bit, 1024 × 1024)
└── denoising/
    ├── denoising_exercise.md  start here
    ├── compare_results.py     side-by-side comparison figure
    ├── denoise-bm3d/          BM3D environment + script
    └── denoise-n2v/           Noise2Void environment + script
```

## What you need

- A laptop (macOS, Linux or Windows) with ~5 GB of free disk space.
- [uv](https://docs.astral.sh/uv/), a fast Python package and project manager. You do **not** need to install Python yourself: uv downloads the right Python version for each exercise.
- Optional but recommended: [Fiji](https://fiji.sc/) for looking at images.

Installing uv:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen your terminal afterwards, then check with `uv --version`.

Each exercise folder contains one or more small uv projects (a `pyproject.toml` plus a `uv.lock`). Running `uv sync` inside such a folder creates a local `.venv` with exactly the tested package versions.
