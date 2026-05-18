from levels_1_9 import DifficultyProfile, _pick_template

GND = 490  # H - 50

# ── Level 10: boss fight ──────────────────────────────────────────

def tmpl_boss(p):
    world_w = 1800
    return {
        "name":  "system error",
        "hint":  "terminate the source.",
        "world_w": world_w,
        "robot": (60, GND - 36),
        "exit":  (world_w - 60, GND),
        "platforms": [
            (0,    GND, world_w, 70),
            (350,  GND - 160, 180, 14),
            (900,  GND - 220, 180, 14),
            (1350, GND - 160, 180, 14),
        ],
        "memory_platforms": [],
        "hazards":  [],
        "switches": [],
        "gates": [{"x": world_w - 90, "y": GND - 220, "w": 16, "h": 220, "id": 999}],
        "boxes":    [],
        "viruses":  [],
        "boss": {"x": 800, "y": GND - 300, "left": 100, "right": 1700},
    }

# Levels 11-18 use the same rotation templates as 6-9 (tmpl_navigation,
# tmpl_box_puzzle, tmpl_memory_traverse, tmpl_combo) via _pick_template,
# scaled to higher DifficultyProfile values.
