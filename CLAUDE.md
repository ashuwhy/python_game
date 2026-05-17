# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the game
source robo_venv/bin/activate && python main.py

# Install dependencies (venv already present)
source robo_venv/bin/activate && pip install -r requirements.txt
```

No tests, no build step. Python 3.14 + pygame via `robo_venv/`.

## Architecture

Everything lives in `main.py` — a single-file pygame game with no external assets. All sprites are drawn procedurally with `pygame.draw.*`.

**Physics constants** (documented in-source above `LEVELS`):
- `jump_power = -9.5`, `gravity = 0.48`, `speed = 3.8`
- Max jump height ≈ 94px (safe: 75px), max air reach ≈ 152px (safe: 115px)
- `GND = H - 50` — ground surface y-coordinate used in all level definitions

**Rendering pipeline** (inside `main()` each frame):
1. Draw to `game_surface` (960×540 internal resolution)
2. Scale to actual window size with letterboxing
3. Apply camera shake offset on blit to `screen`

**Camera**: `cam_x` tracks `robot.x`, clamped to `[0, world_w - W]`. All world objects draw at `obj.x - cam_x`. Background city scrolls at 0.5× parallax.

**State machine**: `ST_MENU → ST_TRANS → ST_INTRO → ST_PLAY`. Transitions via `overlay_alpha` fade. `intro_done` skips the boot sequence on subsequent levels.

**Level format** (`LEVELS` list of dicts):
```python
{
    "name": str, "hint": str, "world_w": int,
    "robot": (x, y), "exit": (x, y),
    "platforms": [(x, y, w, h), ...],          # solid, permanent
    "memory_platforms": [(x, y, w, h), ...],   # only solid; visible 15/240 frames (glitch)
    "hazards": [(x, y, w, h), ...],            # instant death / box respawn
    "switches": [{"x","y","w","h","id","timed","type"}, ...],  # type: "button"|"plate"
    "gates": [{"x","y","w","h","id"}, ...],    # blocked unless switch id matches
    "boxes": [(x, y), ...]
}
```

**Key classes**:
- `Robot` — player. `move_x`/`move_y` are separate to avoid corner-sticking. `carried` holds a `Box` reference; carried box is pinned above head each frame.
- `Box` — physics object. Pushed by robot in `move_x`; collides with platforms and gates.
- `Switch` / `Gate` — linked by `switch_id`. Gates check all switches each frame.
- `MemoryPlatform` — solid collision, but only rendered during `flashback_active` (15-frame glitch window every 240 frames).
- `Particle` — pooled via list comprehension (`[p for p in particles if p.update()]`). Four kinds: `dust`, `spark`, `ember`, `rain`.
- `_particle_cache` — pre-rendered circle surfaces keyed by `(radius, color_rgba)` to avoid per-frame surface allocation.

**Squash-and-stretch**: `Robot.scale_x`/`scale_y` set on jump/land, lerped back to 1.0 each frame at rate 0.15.

**Fullscreen**: `F11` toggles; game always renders to 960×540 then scales.
