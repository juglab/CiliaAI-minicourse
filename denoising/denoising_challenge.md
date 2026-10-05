# Denoising, Part 1: solve it with AI

In this part you get **no recipe**. You get an image, a goal and a short list of what to deliver. How you get there is up to you, and you are explicitly invited to use AI to help you:

- chat assistants such as ChatGPT, Claude or Gemini (ask, copy the code, run it yourself), or
- coding agents such as Claude Code, Codex or Cursor (they write and run code for you).

Work in pairs. Tutors will help you with installation problems, but not with choosing or tuning a method.

Please do not open the other files in the `denoising/` folder yet: they belong to Part 2. If you use a coding agent, start it in a new, empty folder of its own, not inside the course repository.

---

## The image

`data/convollaria.tif`: a fluorescence microscopy image of a section through a *Convallaria* (lily of the valley) rhizome.

- 2D, 16-bit, 1024 × 1024 pixels
- intensities roughly 330 to 1850, most of the signal between 400 and 1200
- the image is noisy, and **no clean (noise-free) version of it exists**

Open it in Fiji first and zoom in. What do you see?

## The goal

Produce a denoised version of this image.

A good result is not simply the smoothest-looking image. A good denoiser removes noise **and keeps the real biological structure**: it must not remove real structure, must not invent structure that is not there, and must not shift intensities. Imagine that someone will use your result to measure membrane intensities and to make a figure for a paper.

## What to deliver

Put everything in one folder, for example `denoising-<your names>/`.

1. **The denoised image** as a TIFF with the same size as the original.
2. **One figure** that would convince a sceptical colleague that you removed noise and not biology.
3. **Three sentences** in a file `notes.md`: which method you used, and why you trust the result.
4. **Your AI log.** Save or export your conversation(s) with the AI tools, or at least write down your most important prompts.

## Time

About 30 minutes. Aim for a first result after 15 minutes, then improve it.

## Practical notes

- If you ran `uv run check_setup.py` before the course, you already have [uv](https://docs.astral.sh/uv/) and Python available. You may tell your AI tools to use it, but you do not have to. Google Colab works too.
- [Fiji](https://fiji.sc/) is very useful for looking at images: zooming, comparing and plotting intensity profiles.
