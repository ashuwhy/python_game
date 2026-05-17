# Level Generator — Design Spec
**Date:** 2026-05-18
**Scope:** Phase 1 — runtime infinite level generation (platforming only, no enemies)

---

## Problem

Five handcrafted levels exist. After level 5 the game ends. Goal: infinite runtime-generated levels (6, 7, 8, …) with monotonically increasing difficulty, using the same mechanic vocabulary as the handcrafted set.

---

## Approach: Difficulty-Parameterized Template Filler

A `DifficultyProfile` dataclass scales numeric parameters by level index `n`. Four template functions consume a profile and return a valid level dict. A `generate_level(n)` dispatcher picks the right template. A `get_level(idx)` wrapper replaces direct `LEVELS[idx]` access throughout `main()`.

---

## Section 1: DifficultyProfile

Computed from level index `n` (1-based; n=6 is first generated level):

| Parameter | Formula | Clamp |
|---|---|---|
| `world_w` | `1400 + n*220` | [1400, 6000] |
| `hazard_cover` | `n * 0.06` | [0.0, 0.75] — fraction of world width covered by hazards |
| `mem_plat_count` | `n // 2` | [0, 14] |
| `gap_max_px` | `80 + n*6` | [80, 180] — physics max safe gap is ~152px |
| `timer_frames` | `600 - n*20` | [180, 600] — timed switch countdown |
| `box_count` | `1 + (n // 8)` | min 1 — second box unlocks ~level 8 |

### Milestone combo unlocks

| Level | Unlock |
|---|---|
| n ≥ 6 | Scale only (wider world, more hazards, more mem platforms) |
| n ≥ 8 | `tmpl_combo` — box carry over timed memory platforms with hazards |
| n ≥ 11 | `tmpl_multi_gate` — two switches, two gates, two boxes |

---

## Section 2: Templates

Each template is a function `tmpl_*(profile) -> dict` returning a level dict with all required keys:
`name`, `hint`, `world_w`, `robot`, `exit`, `platforms`, `memory_platforms`, `hazards`, `switches`, `gates`, `boxes`.

All positions use `GND = H - 50`. All gaps stay within `profile.gap_max_px` (≤152px physics hard limit).

### `tmpl_navigation(p)`
Pure memory/hazard crossing. Large hazard zone across most of world. Memory platforms step across at increasing heights. No boxes, no switches, no gates. Mirrors level 2 structure scaled up.

### `tmpl_box_puzzle(p)`
Box + pressure plate + gate. Safe platform sections on each side of world, hazard-filled gap in middle. Box must reach plate to open gate blocking exit. Mirrors levels 1/3 scaled.

### `tmpl_memory_traverse(p)`
Memory platforms over hazard, exit behind timed gate. Button at world start. Player memorizes platform positions during 15-frame flash window, then crosses before `profile.timer_frames` expires. Mirrors level 4 scaled.

### `tmpl_combo(p)` — unlocks n ≥ 8
Box carry over memory platforms over hazard, timed switch, gate blocking exit. Player must carry box across memory path before timer expires. No equivalent in handcrafted levels — first appearance of this combo.

### Template rotation

```python
def pick_template(n):
    if n % 4 == 2: return tmpl_navigation
    if n % 4 == 3: return tmpl_box_puzzle
    if n % 4 == 0: return tmpl_memory_traverse
    if n % 4 == 1: return tmpl_combo if n >= 8 else tmpl_navigation
```

### Determinism
All template geometry computed from `n` directly (no `random` calls). Level `n` always produces identical layout — player retrying the same level gets the same layout.

---

## Section 3: Integration into `main.py`

### New code (~120 lines)
- `DifficultyProfile` dataclass
- `generate_level(n) -> dict` — builds profile, dispatches to template
- `get_level(idx) -> dict` — returns `LEVELS[idx]` if `idx < 5`, else `generate_level(idx + 1)`
- Four template functions

### Changed code
- `load_level(idx)`: replace `LEVELS[idx]` with `get_level(idx)` — **one line change**
- Menu level list: show `len(LEVELS)` handcrafted + "∞" indicator. `unlocked_level` is unbounded int (already is).
- Menu selection: keys 1–5 select handcrafted; ENTER always continues to next unlocked level (works for generated levels automatically).

### What does NOT change
- `Robot`, `Box`, `Switch`, `Gate`, `Platform`, `MemoryPlatform`, `Hazard` classes — untouched
- Physics constants — untouched
- Rendering pipeline — untouched
- Level dict schema — generated levels use identical schema

---

## Out of Scope (Phase 1)

- Enemy viruses / virus AI
- Electricity shooting weapon
- Boss fight at level 10
- New visual assets or particle types

These are Phase 2 and Phase 3, each with their own spec.
