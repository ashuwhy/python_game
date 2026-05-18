from levels_1_9 import DifficultyProfile

GND = 490  # H - 50

# ── Level 19: gauntlet (virus swarm) ─────────────────────────────

def tmpl_gauntlet(p):
    world_w = 3000
    plats = [
        (0,    GND,          280, 70),
        (380,  GND - 130,    180, 14),
        (660,  GND,          280, 70),
        (1040, GND - 160,    180, 14),
        (1320, GND,          280, 70),
        (1700, GND - 110,    180, 14),
        (1980, GND,          280, 70),
        (2360, GND - 140,    180, 14),
        (2640, GND,          360, 70),
    ]
    hazards = [
        (280,  GND - 20, 100, 20),
        (940,  GND - 20, 100, 20),
        (1600, GND - 20, 100, 20),
        (2260, GND - 20, 100, 20),
    ]
    virus_list = [
        (50,   GND - 20,          10,   260),
        (420,  GND - 130 - 20,   380,   560),
        (700,  GND - 20,         660,   940),
        (1080, GND - 160 - 20,  1040,  1220),
        (1360, GND - 20,        1320,  1600),
        (1730, GND - 110 - 20,  1700,  1880),
        (2020, GND - 20,        1980,  2260),
        (2400, GND - 140 - 20,  2360,  2540),
        (2700, GND - 20,        2640,  2990),
    ]
    return {
        "name":  "the gauntlet",
        "hint":  "clear the path. no shortcuts.",
        "world_w": world_w,
        "robot":  (60, GND - 36),
        "exit":   (world_w - 60, GND),
        "platforms":        plats,
        "memory_platforms": [],
        "hazards":          hazards,
        "switches":         [],
        "gates":            [],
        "boxes":            [],
        "viruses":          virus_list,
    }


# ── Level 20: final boss ──────────────────────────────────────────

def tmpl_final_boss(p):
    world_w = 2400
    return {
        "name":  "kernel panic",
        "hint":  "no escape. finish it.",
        "world_w": world_w,
        "robot":  (60, GND - 36),
        "exit":   (world_w - 60, GND),
        "platforms": [
            (0,    GND, world_w, 70),
            (280,  GND - 190, 200, 14),
            (850,  GND - 260, 200, 14),
            (1450, GND - 210, 200, 14),
            (2000, GND - 170, 200, 14),
        ],
        "memory_platforms": [],
        "hazards":  [],
        "switches": [],
        "gates": [{"x": world_w - 90, "y": GND - 230, "w": 16, "h": 230, "id": 998}],
        "boxes":    [],
        "viruses":  [],
        "boss2": {"x": 1100, "y": GND - 420, "left": 60, "right": 2340},
    }
