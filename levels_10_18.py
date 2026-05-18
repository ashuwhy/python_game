from levels_1_9 import DifficultyProfile, _pick_template

GND = 490  # H - 50

# ── Level 10: boss fight ──────────────────────────────────────────

def tmpl_boss(p):
    world_w = 1800
    return {
        "name":  "system error",
        "hint":  "terminate the source. [f] to shoot.",
        "world_w": world_w,
        "robot": (60, GND - 36),
        "exit":  (world_w - 60, GND),
        "platforms": [
            (0,    GND, world_w, 70),
            (200,  GND - 120, 140, 14),
            (500,  GND - 200, 140, 14),
            (900,  GND - 260, 180, 14),
            (1350, GND - 180, 140, 14),
            (1600, GND - 120, 140, 14),
        ],
        "memory_platforms": [],
        "hazards":  [],
        "switches": [],
        "gates": [{"x": world_w - 90, "y": GND - 220, "w": 16, "h": 220, "id": 999}],
        "boxes":    [],
        "viruses":  [],
        "boss": {"x": 800, "y": GND - 300, "left": 100, "right": 1700},
    }

# ── Levels 11-18: enhanced templates with escalating complexity ──

def _make_level_11(p):
    """broken bridge — navigation with vertical hazard walls."""
    base = _pick_template(p.n)(p)
    base["name"] = "broken bridge"
    base["hint"] = "walls of light block your path."
    # Add extra vertical hazards
    mid = p.world_w // 2
    base["hazards"].append((mid, GND - 250, 16, 180))
    base["hazards"].append((mid + 200, GND - 200, 16, 130))
    # Add elevated platform between hazards
    base["platforms"].append((mid + 40, GND - 160, 120, 14))
    return base

def _make_level_12(p):
    """phantom cargo — double box puzzle with timed switches."""
    base = _pick_template(p.n)(p)
    base["name"] = "phantom cargo"
    base["hint"] = "two weights. two gates. one timer."
    # Add extra box and timed switch
    base["boxes"].append((p.world_w // 2, GND))
    base["switches"].append({"x": p.world_w // 2 + 100, "y": GND - 8, "w": 44, "h": 8,
                             "id": 3, "timed": 400, "type": "button"})
    base["gates"].append({"x": p.world_w // 2 - 50, "y": GND - 200, "w": 16, "h": 200, "id": 3})
    return base

def _make_level_13(p):
    """static noise — heavy virus gauntlet."""
    base = _pick_template(p.n)(p)
    base["name"] = "static noise"
    base["hint"] = "mechs everywhere. shoot first."
    # Add more viruses
    vl = base.get("viruses", [])
    safe = 280
    vl.append((safe + 50, GND - 40, safe + 10, safe + 200))
    vl.append((p.world_w // 2, GND - 40, p.world_w // 2 - 100, p.world_w // 2 + 100))
    if p.n >= 14:
        vl.append((p.world_w - safe - 100, GND - 40, p.world_w - safe - 150, p.world_w - safe))
    base["viruses"] = vl
    return base

def _make_level_14(p):
    """blind leap — memory platforms with no safe zones."""
    base = _pick_template(p.n)(p)
    base["name"] = "blind leap"
    base["hint"] = "no island. no rest. just jump."
    # Remove mid-section safe platforms (keep only start and end)
    base["platforms"] = [pl for pl in base["platforms"]
                         if pl[0] < 300 or pl[0] > p.world_w - 350]
    # Add more memory platforms
    count = len(base.get("memory_platforms", []))
    extra = max(2, 8 - count)
    import random as _r
    _r.seed(p.n * 777)
    for _ in range(extra):
        x = _r.randint(400, p.world_w - 400)
        y = GND - _r.randint(40, 130)
        base.setdefault("memory_platforms", []).append((x, y, 85, 14))
    _r.seed()
    return base

def _make_level_15(p):
    """corrupted path — vertical laser corridors."""
    base = _pick_template(p.n)(p)
    base["name"] = "corrupted path"
    base["hint"] = "weave through the corruption."
    # Add many vertical hazards
    step = p.world_w // 6
    for i in range(1, 6):
        x = step * i
        h = 100 + (i % 3) * 40
        base["hazards"].append((x, GND - 200, 14, h))
    # Add platforms between vertical walls
    for i in range(1, 5):
        base["platforms"].append((step * i + 30, GND - 140, 100, 14))
    return base

def _make_level_16(p):
    """voltage spike — combo puzzle with virus guards on platforms."""
    base = _pick_template(p.n)(p)
    base["name"] = "voltage spike"
    base["hint"] = "they guard the high ground."
    # Add elevated platforms with viruses on them
    elevations = [
        (p.world_w // 4, GND - 180, 150, 14),
        (p.world_w // 2, GND - 220, 150, 14),
        (3 * p.world_w // 4, GND - 160, 150, 14),
    ]
    base["platforms"] += elevations
    vl = base.get("viruses", [])
    for ex, ey, ew, _ in elevations:
        vl.append((ex + 20, ey - 40, ex + 5, ex + ew - 5))
    base["viruses"] = vl
    return base

def _make_level_17(p):
    """dark transit — long memory traverse with mid-boss virus."""
    base = _pick_template(p.n)(p)
    base["name"] = "dark transit"
    base["hint"] = "something big patrols the middle."
    # Add a big virus patrol zone in the center
    mid = p.world_w // 2
    base["platforms"].append((mid - 100, GND, 200, 70))
    vl = base.get("viruses", [])
    vl.append((mid - 60, GND - 40, mid - 90, mid + 90))
    vl.append((mid + 20, GND - 40, mid - 90, mid + 90))
    base["viruses"] = vl
    # Add vertical hazards flanking the center
    base["hazards"].append((mid - 110, GND - 200, 14, 130))
    base["hazards"].append((mid + 100, GND - 200, 14, 130))
    return base

def _make_level_18(p):
    """memory leak — ultimate combo, tight timers, max viruses."""
    base = _pick_template(p.n)(p)
    base["name"] = "memory leak"
    base["hint"] = "everything is falling apart."
    # Tighten all timers
    for s in base.get("switches", []):
        if s.get("timed", 0) > 0:
            s["timed"] = max(150, s["timed"] - 200)
    # Add max viruses
    vl = base.get("viruses", [])
    safe = 300
    step = (p.world_w - safe * 2) // 5
    for i in range(4):
        x = safe + step * (i + 1)
        vl.append((x, GND - 40, x - 50, x + 50))
    base["viruses"] = vl
    # Add double gate at end
    base["gates"].append({"x": p.world_w - safe - 80, "y": GND - 200, "w": 16, "h": 200, "id": 5})
    base["switches"].append({"x": p.world_w // 2, "y": GND - 8, "w": 44, "h": 8,
                             "id": 5, "timed": 200, "type": "button"})
    return base


def generate_level_10_18(n, p):
    """Generate level for n in 11-18 (1-based)."""
    makers = {
        11: _make_level_11,
        12: _make_level_12,
        13: _make_level_13,
        14: _make_level_14,
        15: _make_level_15,
        16: _make_level_16,
        17: _make_level_17,
        18: _make_level_18,
    }
    if n in makers:
        return makers[n](p)
    return _pick_template(n)(p)
