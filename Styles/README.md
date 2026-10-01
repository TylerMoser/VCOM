# Styles

Candidate visual styles for VCOM's combat map, rendered from the real game on 2026-09-26. **Style `05`, Colour Bounce, was applied to the game on 2026-10-01.** [REVERT.md](REVERT.md) restores the original look (style `00`).

| File | What it is |
|---|---|
| [VISUAL_VARIANTS.md](VISUAL_VARIANTS.md) | The catalog: every kept style with its screenshot, description, cost and exact settings. |
| [APPLYING.md](APPLYING.md) | How to make a style permanent, how to verify it, and the decisions to make first. |
| [REVERT.md](REVERT.md) | The original look, value by value as of 2026-10-01, and how to return to it after a style has been applied. `REVERT-*.png` are its reference renders. |
| [LEDGES.md](LEDGES.md) | Making grass levels easier to tell apart: the options compared on top of 05 (pictures in `ledges/`), the recommendation (a height tint), and how to apply it. Not applied yet. |
| [harness/](harness/) | The render harness: previews any style from the live game, holds the values (the source of truth), and contains the two shaders. |
| [TRANSCRIPT.md](TRANSCRIPT.md) | The conversation in which these were researched, rendered and chosen. |
| `NN-*.png` | Screenshots. Left panel: the game as it starts. Right panel: a closer view with the HUD and tile highlights hidden. |
| [GoogleSearch.png](GoogleSearch.png) | A saved search summary of "vibrant voxel Godot" advice: Filmic/ACES + saturation, glow, SSAO/SSIL, VoxelGI. |

## Kept styles

`01` Sunlit Diorama · `04` Soft GI Render (SDFGI) · `05` Colour Bounce (SSIL) · `07` Soft Pastel · `10` Split-Tone Grade · `11` Tilt-Shift Miniature · `15` Toon Shading · `19` Tactical Readability · `21` Ink Outlines · `22` Cartoon · `23` Bevelled Edge Highlights · `27` Long-Lens Diorama · `28` Recommended Blend

## Dropped styles

Rendered and reviewed, then set aside: `02` Warm Sun, Cool Shade · `03` AgX Punch · `06` Golden Hour · `08` High-Contrast Tactical · `09` Vibrance Grade (3D LUT) · `12` Height Haze · `13` Dreamy Bloom · `14` Toy Plastic · `16` Cel Bands + Violet Shadows · `17` Hand-Shaded Faces · `18` Tamed Greens · `20` Flat Colour · `24` 3D Pixel Art · `25` Twin Suns · `26` Alien Twilight.
Their definitions remain in `harness/VariantList.gd`, so any of them can be re-rendered with `Styles/harness/render.sh <id>`. Style 28 reuses ideas from 09, 17 and 18, but its own settings are complete.

## Background

The goal, from the project's todo list, was a vibrant look that isn't over-saturated, with more readable terrain. The biggest finding: the current sun comes from only ~10° off the camera's view direction, so every face is front-lit and flat. Every style fixes that first. The catalog explains it in full.
