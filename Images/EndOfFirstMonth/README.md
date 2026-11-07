# End of First Month — November 5, 2026

Open **index.html** for the searchable thumbnail gallery. All original screenshots are PNGs directly in this folder. Contact sheets, a file manifest, logs, and the repeatable capture harness are in `capture/`.

## Coverage

- Fresh combat: battlefield, movement/cover, overwatch, targeting, grenade preview, reaction window, day/dusk/night.
- Busy combat: shots, grenades, explosions, broken ground, crate debris, casualties and blood, including clean destruction views.
- Lighting: matching day, dusk and night views of TestMap's house and two street lamps, plus close views and building cutaways.
- World map: overview, roads and settlements, a navigation route with destination visible, travel progress, controller navigation and regional detail.
- Pause menu: Campaign, all three quest categories, Roster details/equipment/skills, all Inventory categories, System and its in-combat restrictions.
- Settlement menus: Details, courts of Count/Duke/King, Quest Board, Hiring Board's three pages, and every Buy/Sell market category.
- Squad selection: details, equipment and skills.
- Other UI: controller prompts, reaction offers, melee and medkit targeting, floor selector, result banners and the Godot voxel level editor.

## Capture provenance

Actual game-rendered viewport captures from the current local source, using Godot 4.7 stable, Forward+ / D3D12 on the RTX 3060. Game frames are 1280 × 720; the live editor capture is 1920 × 1032. PNGs have not been composited or retouched.

These are staged feature demonstrations, not a continuous saved campaign. The harness sets camera framing and time of day, opens the real interfaces, positions units, supplies existing equipment for melee/healing demonstrations, and invokes the game's actions, damage, destruction and effects. Victory/Defeat images demonstrate the real banner component; they are not evidence that a complete battle was played to those outcomes. The current authored quest board and journal are empty, which is what their screenshots show. Empty inventory categories are also retained for complete UI coverage.

The existing EndOfFirstWeek collection and pre-existing source edits were preserved. Capture scripts ran in a temporary `vcom/_month_capture/` folder, removed afterward; archived source remains here. No game assets or gameplay code were changed for this collection.

## Repeating the capture

Copy `capture/Capture.gd` and `capture/Capture.tscn` to `vcom/_month_capture/`. Run from the repository root:

```powershell
& 'C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe' --path vcom --resolution 1280x720 --fixed-fps 60 res://_month_capture/Capture.tscn
```

Repeat with `-- combat`, `-- extras`, and `-- details` appended, in that order. The harness writes to this folder using an absolute output path. Remove only that temporary harness directory after Godot exits. The editor screenshot is captured separately from the live editor using the computer-use tool. Run `python Images/EndOfFirstMonth/capture/build_catalog.py` to refresh the gallery, contact sheets and manifest.
