# CiliaAI mini-course: hands-on exercises

Material for the hands-on part of the Cilia-AI / CiliaConnect mini-course on image analysis and AI.

**Before the course,** please follow the steps in [Before the course: get ready](#before-the-course-get-ready) to install everything on your laptop.

## Program

Detailed timing is announced on site.

**Wednesday, 7 October (afternoon)**

- Welcome and overview of the three days
- What is an image? What is image analysis?
- Classical image analysis: tools (Fiji, napari, Imaris) and community (image.sc, I2K)
- The deep learning revolution, and what agentic AI has changed since
- Denoising: a short introduction
- Hands-on: the [denoising exercise](#exercises), in two parts
- What was your experience? (discussion)

**Thursday, 8 October**

- Recap: what is the right tool for the job? What should I learn? (FJ, NJY)
- Segmentation: introduction and tools for 3D (thresholding, Cellpose, ...) (FJ, NJY)
- Cilia segmentation: CiliaQ, the Q suite and CiliaQ Explorer (NJY, DB)
- Segmentation projects in groups (DB)
- Building an analysis pipeline: combining denoising, segmentation and plotting (FJ, NJY, DB)
- Demonstration: CiliaQ Explorer and ciliation analysis (NJY, DB)
- Pipeline projects in groups (DB)
- Presentation of the project outcomes and reflection on the process
- Evening: pizza, drinks and a debate on how AI influences our work as scientists

**Friday, 9 October (morning)**

- Predicting ciliary protein structures and complexes with AlphaFold: how to trust them (EL)
- Final words

Instructors: Florian Jug (FJ), Nathalie Jurisch-Yaksi (NJY), Esben Lorentzen (EL), Daniel Burgdorf (DB).

## What you need

- A laptop (macOS, Linux or Windows) with ~5 GB of free disk space.
- [git](https://git-scm.com/), to download the course material and to get updates during the course.
- [uv](https://docs.astral.sh/uv/), a fast Python package and project manager. You do **not** need to install Python yourself: uv downloads the right Python version for each exercise.
- Optional but recommended: [Fiji](https://fiji.sc/) for looking at images.
- An account for at least one AI assistant (for example ChatGPT, Claude or Gemini). Free accounts are fine.
- A Google account, for the Colab notebook.

## Before the course: get ready

Please do these steps **before Wednesday**, at home or in your lab, where the internet is fast. Never used a terminal, git or GitHub? No problem, just follow the steps one by one and copy the commands exactly.

### Step 1: Open a terminal

A terminal is a window in which you type commands instead of clicking.

- **macOS:** press `Cmd + Space`, type `Terminal` and press Enter.
- **Windows:** open the Start menu, type `PowerShell` and click on *Windows PowerShell*.
- **Linux:** open the *Terminal* app (on many systems `Ctrl + Alt + T`).

Type a command, then press Enter to run it.

### Step 2: Install git

First check whether git is already installed:

```bash
git --version
```

If this prints something like `git version 2.x.x`, go to Step 3. Otherwise:

- **macOS:** run `xcode-select --install` and click *Install* in the window that appears (this installs Apple's command line tools, which include git). Running `git --version` may also open this window by itself.
- **Windows:** download *Git for Windows* from [git-scm.com/downloads/win](https://git-scm.com/downloads/win) and run the installer. The default settings are fine, just keep clicking *Next*. Alternatively, run this in PowerShell:

  ```powershell
  winget install --id Git.Git -e --source winget
  ```

- **Linux:** `sudo apt install git` (Ubuntu, Debian) or `sudo dnf install git` (Fedora).

Then **close the terminal, open a new one** and check again with `git --version`.

### Step 3: Download the course material

The course material lives on GitHub, a website that hosts git repositories. Downloading a copy of a repository is called *cloning*. You do not need a GitHub account for this.

Go to the folder where you want the course material, for example your home folder, and clone the repository:

```bash
cd ~
git clone https://github.com/juglab/CiliaAI-minicourse.git
cd CiliaAI-minicourse
```

This creates a folder `CiliaAI-minicourse` with everything in it, and moves you into it. These commands are the same on macOS, Linux and Windows (PowerShell).

> **Tip:** avoid folders that are synced to the cloud (OneDrive, iCloud Drive, Dropbox). The Python environments created later contain thousands of small files, which makes syncing slow and can break things. On many laptops `Documents` and `Desktop` are such folders; your home folder (`~`) usually is not.

Next time you open a terminal, get back into the course folder with:

```bash
cd ~/CiliaAI-minicourse
```

### Step 4: Install uv

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

### Step 5: Check your setup

This installs both Python environments of the denoising exercise (several hundred MB, mostly TensorFlow) and tests them. The first run can take 5 to 15 minutes.

```bash
cd ~/CiliaAI-minicourse
uv run check_setup.py
```

At the end it prints a summary. If it says *"Everything works"*, you are ready. If not, try the hints it prints. If you are still stuck, bring your laptop and the full output of the script to the course, and we will help you.

## Exercises

### Wednesday: denoising, in two parts

#### Part 1: solve it with AI (about 30 minutes)

Denoise a microscopy image with whatever AI help you like. Instructions: [`denoising/denoising_challenge.md`](denoising/denoising_challenge.md).

#### Part 2: a clean restart (about 30 minutes)

Now do it again, step by step, and understand what happens. Choose one of two tracks:

| Track | What you do | What you need |
|---|---|---|
| **Colab** (recommended) | Train Noise2Void on a cloud GPU and look at what it removed. [**Open the notebook in Colab**](https://colab.research.google.com/github/juglab/CiliaAI-minicourse/blob/main/denoising/CAREamics_Noise2Void_2D_ZeroCostDL4Mic.ipynb) | A Google account, nothing to install |
| **Local** | Denoise with a classical method (BM3D) and with Noise2Void on your laptop, then compare both. Instructions: [`denoising/denoising_exercise.md`](denoising/denoising_exercise.md) | The setup from [Before the course](#before-the-course-get-ready) |

In Colab you upload the image `data/convollaria.tif` from your course folder; the notebook explains how. The install step at the top of the notebook takes several minutes, so we will ask you to start it early.

More exercises will be added. Each one lives in its own folder and comes with step-by-step instructions.

## During the course: getting updates

We may add or fix material during the course. To get the latest version, go to the course folder and *pull* the changes:

```bash
cd ~/CiliaAI-minicourse
git pull
```

If git refuses because *"your local changes would be overwritten"* (for example because you edited one of the scripts), put your changes aside, pull, and then bring them back:

```bash
git stash
git pull
git stash pop
```

Your own new files and all results in `denoising/results/` are never touched by `git pull`.

**No git at all?** On the [GitHub page of the course](https://github.com/juglab/CiliaAI-minicourse), click the green *Code* button and then *Download ZIP*, and unpack it. This works too, but to get updates you have to download the ZIP again.

## Repository layout

```text
CiliaAI-minicourse/
├── README.md                  this file
├── check_setup.py             run this before the course
├── data/
│   └── convollaria.tif        example image (2D, 16-bit, 1024 × 1024)
└── denoising/
    ├── denoising_challenge.md Part 1: solve it with AI
    ├── CAREamics_Noise2Void_2D_ZeroCostDL4Mic.ipynb  Part 2, Colab track
    ├── denoising_exercise.md  Part 2, local track
    ├── compare_results.py     side-by-side comparison figure
    ├── denoise-bm3d/          BM3D environment + script
    └── denoise-n2v/           Noise2Void environment + script
```
