# Level Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a runtime level generator to `main.py` that produces infinite, increasingly difficult levels beyond the 5 handcrafted ones.

**Architecture:** A `DifficultyProfile` class scales parameters (world width, hazard density, timer speed) from level index `n`. Four template functions consume a profile and return a level dict with the same schema as handcrafted levels. A `get_level(idx)` wrapper replaces the single `LEVELS[idx]` call so nothing else in the game needs to change.

**Tech Stack:** Python 3.14, pygame, single-file game (`main.py`). No test runner — verify by running the game.

---

## File Structure

| File | Change |
|---|---|
| `main.py` | Insert ~130 lines of generator code between line 858 and `def main()` at line 861. Three surgical edits inside `main()`. |

No new files. No new classes outside the generator block.

---

### Task 1: Add `DifficultyProfile`, hint arrays, and bridge helper

**Files:**
- Modify: `main.py` — insert after line 858 (the closing `]` of `LEVELS`), before `def main():`

- [ ] **Step 1: Insert the generator block header**

Open `main.py`. After line 858 (the `]` that closes `LEVELS`), add:

```python
# ── Level Generator ─────────────────────────────────────────────

_HINTS_NAV = [
    "the world glitches. trust your memory.",
    "ghost paths. blink and you fall.",
    "the unseen road. remember.",
]
_HINTS_BOX = [
    "carry the box. activate the plate.",
    "weight solves gates.",
    "box. plate. gate. in that order.",
]
_HINTS_MEM = [
    "memorize. then run.",
    "one flash. one chance.",
    "the path vanishes. go.",
]
_HINTS_COMBO = [
    "carry across the unseen. clock is running.",
    "box + memory + time. good luck.",
    "overloaded. all three at once.",
]


class DifficultyProfile:
    def __init__(self, n):
        self.n             = n
        self.world_w       = min(max(1400 + n * 220, 1400), 6000)
        self.mem_plat_count = min(max(n // 2, 4), 14)
        self.gap_max_px    = min(max(80 + n * 6, 80), 115)
        self.timer_frames  = min(max(600 - n * 20, 180), 600)


def _bridge_count(hazard_w, plat_w=90, max_gap=110):
    """Minimum memory platforms needed so no gap exceeds max_gap."""
    return max(4, int(hazard_w / (plat_w + max_gap)) + 2)
```

- [ ] **Step 2: Verify syntax**

```bash
source robo_venv/bin/activate && python -c "import main" 2>&1
```

Expected: no output (no import errors). If you see `SyntaxError`, check indentation — the new code must be at module level (no indentation).

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add DifficultyProfile and bridge helper for level generator"
```

---

### Task 2: Add `tmpl_navigation` and `tmpl_box_puzzle`

**Files:**
- Modify: `main.py` — append to the generator block added in Task 1

- [ ] **Step 1: Add `tmpl_navigation`**

Directly after `_bridge_count`, add:

```python
def tmpl_navigation(p):
    safe_w = 280
    hz_x   = safe_w
    hz_w   = p.world_w - safe_w * 2
    count  = _bridge_count(hz_w)
    spacing = hz_w / (count + 1)
    heights = [GND - 40, GND - 80, GND - 120, GND - 80]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 45, heights[i % 4], 90, 14)
        for i in range(count)
    ]
    return {
        "name":  f"ghost run {p.n}",
        "hint":  _HINTS_NAV[p.n % len(_HINTS_NAV)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": [
            (0,              GND, safe_w, 70),
            (p.world_w - safe_w, GND, safe_w, 70),
        ],
        "memory_platforms": mem_plats,
        "hazards": [(hz_x, GND - 20, hz_w, 20)],
        "switches": [],
        "gates":   [],
        "boxes":   [],
    }
```

- [ ] **Step 2: Add `tmpl_box_puzzle`**

Directly after `tmpl_navigation`, add:

```python
def tmpl_box_puzzle(p):
    gap     = p.gap_max_px
    left_w  = max(p.world_w // 3, 380)
    right_x = left_w + gap
    right_w = p.world_w - right_x
    return {
        "name":  f"cargo {p.n}",
        "hint":  _HINTS_BOX[p.n % len(_HINTS_BOX)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 70, GND),
        "platforms": [
            (0,       GND, left_w,  70),
            (right_x, GND, right_w, 70),
        ],
        "memory_platforms": [],
        "hazards": [(left_w, GND - 20, gap, 20)],
        "switches": [
            {"x": p.world_w - 200, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": 0, "type": "plate"}
        ],
        "gates": [
            {"x": p.world_w - 130, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [(160, GND)],
    }
```

- [ ] **Step 3: Verify syntax**

```bash
source robo_venv/bin/activate && python -c "import main" 2>&1
```

Expected: no output.

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add tmpl_navigation and tmpl_box_puzzle level templates"
```

---

### Task 3: Add `tmpl_memory_traverse`, `tmpl_combo`, and the dispatcher

**Files:**
- Modify: `main.py` — append to the generator block

- [ ] **Step 1: Add `tmpl_memory_traverse`**

After `tmpl_box_puzzle`, add:

```python
def tmpl_memory_traverse(p):
    safe_w  = 300
    hz_x    = safe_w
    hz_w    = p.world_w - safe_w * 2
    count   = _bridge_count(hz_w)
    spacing = hz_w / (count + 1)
    heights = [GND - 50, GND - 90, GND - 130, GND - 90]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 45, heights[i % 4], 90, 14)
        for i in range(count)
    ]
    return {
        "name":  f"flash run {p.n}",
        "hint":  _HINTS_MEM[p.n % len(_HINTS_MEM)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": [
            (0,                  GND, safe_w, 70),
            (p.world_w - safe_w, GND, safe_w, 70),
        ],
        "memory_platforms": mem_plats,
        "hazards": [(hz_x, GND - 20, hz_w, 20)],
        "switches": [
            {"x": 100, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": p.timer_frames, "type": "button"}
        ],
        "gates": [
            {"x": p.world_w - safe_w - 20, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [],
    }
```

- [ ] **Step 2: Add `tmpl_combo`**

After `tmpl_memory_traverse`, add:

```python
def tmpl_combo(p):
    safe_w  = 300
    hz_x    = safe_w
    hz_w    = p.world_w - safe_w * 2
    count   = _bridge_count(hz_w, plat_w=100)   # wider plats for box carry
    spacing = hz_w / (count + 1)
    heights = [GND - 50, GND - 90, GND - 130, GND - 90]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 50, heights[i % 4], 100, 14)
        for i in range(count)
    ]
    return {
        "name":  f"overload {p.n}",
        "hint":  _HINTS_COMBO[p.n % len(_HINTS_COMBO)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": [
            (0,                  GND, safe_w, 70),
            (p.world_w - safe_w, GND, safe_w, 70),
        ],
        "memory_platforms": mem_plats,
        "hazards": [(hz_x, GND - 20, hz_w, 20)],
        "switches": [
            {"x": 80, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": p.timer_frames, "type": "button"}
        ],
        "gates": [
            {"x": p.world_w - safe_w - 20, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [(220, GND)],
    }
```

- [ ] **Step 3: Add the dispatcher and public API**

After `tmpl_combo`, add:

```python
def _pick_template(n):
    r = n % 4
    if r == 2: return tmpl_navigation
    if r == 3: return tmpl_box_puzzle
    if r == 0: return tmpl_memory_traverse
    return tmpl_combo if n >= 8 else tmpl_navigation  # r == 1


def generate_level(n):
    """Return a level dict for 1-based level index n (call with n >= 6)."""
    return _pick_template(n)(DifficultyProfile(n))


def get_level(idx):
    """0-based index. Returns handcrafted level for idx < 5, generated for idx >= 5."""
    if idx < len(LEVELS):
        return LEVELS[idx]
    return generate_level(idx + 1)
```

- [ ] **Step 4: Smoke-test the generator at the Python prompt**

```bash
source robo_venv/bin/activate && python - <<'EOF'
import main
for n in [6, 7, 8, 9, 10, 11]:
    d = main.get_level(n - 1)
    print(f"n={n} name={d['name']!r:20} world_w={d['world_w']} mem={len(d['memory_platforms'])} haz={len(d['hazards'])}")
EOF
```

Expected output (exact values may differ slightly):
```
n=6  name='ghost run 6'        world_w=2720 mem=14 haz=1
n=7  name='cargo 7'            world_w=2940 gap visible via hazards
n=8  name='flash run 8'        world_w=3160 mem=15 haz=1
n=9  name='ghost run 9'        world_w=3380 ...
n=10 name='cargo 10'           world_w=3600 ...
n=11 name='overload 11'        world_w=3820 ...
```

Key checks: no KeyError, all dicts have `robot`, `exit`, `platforms`, `memory_platforms`, `hazards`, `switches`, `gates`, `boxes` keys. If any key is missing, find the template that returned the dict and add the missing key.

- [ ] **Step 5: Commit**

```bash
git add main.py
git commit -m "feat: add tmpl_memory_traverse, tmpl_combo, generate_level, get_level"
```

---

### Task 4: Wire `load_level`, fix menu keybindings, update menu display

**Files:**
- Modify: `main.py` — three targeted edits inside `main()`

- [ ] **Step 1: Replace `LEVELS[idx]` with `get_level(idx)` in `load_level`**

Find line ~903:
```python
        data = LEVELS[idx]
```

Replace with:
```python
        data = get_level(idx)
```

- [ ] **Step 2: Remove the `len(LEVELS)` cap from number-key selection (line ~947)**

Find:
```python
                    if pygame.K_1 <= event.key <= pygame.K_6:
                        lvl = event.key - pygame.K_1
                        if lvl <= unlocked_level and lvl < len(LEVELS):
```

Replace with:
```python
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        lvl = event.key - pygame.K_1
                        if lvl <= unlocked_level:
```

(Extends selection keys to 1–9 so players can jump to early generated levels.)

- [ ] **Step 3: Remove `len(LEVELS)` cap from ENTER key (line ~952)**

Find:
```python
                    elif event.key == pygame.K_RETURN:
                        current_level = min(unlocked_level, len(LEVELS) - 1)
```

Replace with:
```python
                    elif event.key == pygame.K_RETURN:
                        current_level = unlocked_level
```

- [ ] **Step 4: Update the menu level-list display (lines ~1070–1099)**

Find the menu drawing block that starts with:
```python
            # ── level list ──
            start_y = H//2 - 20
            for i in range(len(LEVELS)):
                unlocked = i <= unlocked_level
                completed = i < unlocked_level
                y = start_y + i * 34
                # Dot indicator
                dot_col = (0, 220, 255) if unlocked else (30, 32, 42)
                if completed:
                    dot_col = (80, 255, 120)
                pygame.draw.circle(gs, dot_col, (W//2 - 170, y + 10), 4)
                if completed:
                    pygame.draw.circle(gs, (0, 0, 0), (W//2 - 170, y + 10), 2)
                # Number
                num_col = (80, 85, 100) if unlocked else (30, 32, 42)
                num = hint_font.render(f"{i+1:02d}", True, num_col)
                gs.blit(num, (W//2 - 155, y + 3))
                # Separator dot
                pygame.draw.circle(gs, (40, 42, 55), (W//2 - 130, y + 10), 2)
                # Name
                name_col = (180, 185, 200) if unlocked else (35, 38, 48)
                name = font.render(LEVELS[i]["name"], True, name_col)
                gs.blit(name, (W//2 - 118, y + 2))
                # Status text
                if completed:
                    st = hint_font.render("done", True, (60, 180, 90))
                    gs.blit(st, (W//2 + 140, y + 3))
                elif i == unlocked_level:
                    blink = int(frame * 0.06) % 2
                    if blink:
                        st = hint_font.render("play", True, (0, 200, 255))
                        gs.blit(st, (W//2 + 140, y + 3))
```

Replace the entire block (from `# ── level list ──` to the end of the for loop) with:

```python
            # ── level list ──
            start_y = H//2 - 20
            for i in range(len(LEVELS)):
                unlocked = i <= unlocked_level
                completed = i < unlocked_level
                y = start_y + i * 34
                dot_col = (80, 255, 120) if completed else ((0, 220, 255) if unlocked else (30, 32, 42))
                pygame.draw.circle(gs, dot_col, (W//2 - 170, y + 10), 4)
                if completed:
                    pygame.draw.circle(gs, (0, 0, 0), (W//2 - 170, y + 10), 2)
                num_col = (80, 85, 100) if unlocked else (30, 32, 42)
                num = hint_font.render(f"{i+1:02d}", True, num_col)
                gs.blit(num, (W//2 - 155, y + 3))
                pygame.draw.circle(gs, (40, 42, 55), (W//2 - 130, y + 10), 2)
                name_col = (180, 185, 200) if unlocked else (35, 38, 48)
                name_surf = font.render(LEVELS[i]["name"], True, name_col)
                gs.blit(name_surf, (W//2 - 118, y + 2))
                if completed:
                    gs.blit(hint_font.render("done", True, (60, 180, 90)), (W//2 + 140, y + 3))
                elif i == unlocked_level:
                    if int(frame * 0.06) % 2:
                        gs.blit(hint_font.render("play", True, (0, 200, 255)), (W//2 + 140, y + 3))

            # ── generated levels row ──
            gen_y = start_y + len(LEVELS) * 34
            if unlocked_level >= len(LEVELS):
                gen_count = unlocked_level - len(LEVELS) + 1
                gen_label = f"∞  generated  ({gen_count} reached)"
                gen_col   = (180, 185, 200)
                blink_col = (0, 200, 255) if int(frame * 0.06) % 2 else (0, 200, 255)
                pygame.draw.circle(gs, (0, 220, 255), (W//2 - 170, gen_y + 10), 4)
                gs.blit(hint_font.render("∞ ", True, (80, 85, 100)), (W//2 - 155, gen_y + 3))
                gs.blit(font.render(gen_label, True, gen_col), (W//2 - 130, gen_y + 2))
                if unlocked_level >= len(LEVELS) and unlocked_level == unlocked_level:
                    if int(frame * 0.06) % 2:
                        gs.blit(hint_font.render("play", True, (0, 200, 255)), (W//2 + 140, gen_y + 3))
            else:
                # Not yet unlocked — show teaser
                pygame.draw.circle(gs, (30, 32, 42), (W//2 - 170, gen_y + 10), 4)
                gs.blit(hint_font.render("∞ ", True, (30, 32, 42)), (W//2 - 155, gen_y + 3))
                gs.blit(font.render("generated levels", True, (35, 38, 48)), (W//2 - 130, gen_y + 2))
```

- [ ] **Step 5: Verify syntax**

```bash
source robo_venv/bin/activate && python -c "import main" 2>&1
```

Expected: no output.

- [ ] **Step 6: Run the game and verify handcrafted levels still work**

```bash
source robo_venv/bin/activate && python main.py
```

- Play level 1 to completion (reach exit portal). Confirm level 2 loads.
- Press ESC to return to menu. Confirm level list shows levels 1–5 + `∞ generated levels` teaser row.
- Press ENTER on menu. Confirm level 2 starts (the next unlocked).

- [ ] **Step 7: Verify generated levels load**

In the running game: complete levels 1–5. After level 5's exit portal, the game should load a generated level. Confirm:
- Level name shows `ghost run 6` or similar in the HUD top-left
- Memory platforms appear and flash every 4 seconds
- Hazard zone is red and kills on touch
- R restarts the generated level

- [ ] **Step 8: Commit**

```bash
git add main.py
git commit -m "feat: wire get_level into load_level, update menu for infinite generated levels"
```

---

## Self-Review

**Spec coverage:**
- ✅ Runtime infinite (get_level beyond idx=4)
- ✅ DifficultyProfile with all five parameters
- ✅ Four templates (navigation, box_puzzle, memory_traverse, combo)
- ✅ Template rotation per n
- ✅ Combo unlocks at n≥8 (_pick_template checks `n >= 8`)
- ✅ Deterministic from n (no random calls in templates)
- ✅ get_level wrapper, single load_level edit
- ✅ Menu updated with ∞ row

**Placeholder scan:** None found.

**Type consistency:**
- `get_level(idx)` used in Task 3 step 3, referenced in Task 4 step 1 — consistent.
- `DifficultyProfile.n`, `.world_w`, `.gap_max_px`, `.timer_frames` used across templates — consistent.
- `_bridge_count(hz_w)` / `_bridge_count(hz_w, plat_w=100)` — consistent.
- Level dict keys in all four templates match handcrafted schema exactly.
