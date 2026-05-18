GND = 490  # H - 50; ground surface y-coordinate

# ── Handcrafted levels 1-5 ──────────────────────────────────────

LEVELS = [
    {
        "name": "the basics",
        "hint": "[e] pick up box in front of you. get it to the plate.",
        "world_w": 1400,
        "robot": (60, GND - 36),
        "exit": (1340, GND),
        "platforms": [
            (0,    GND, 400, 70),
            (490,  GND - 65, 120, 14),
            (700,  GND, 700, 70),
        ],
        "memory_platforms": [],
        "hazards": [],
        "switches": [
            {"x": 750, "y": GND - 8, "w": 44, "h": 8, "id": 1, "timed": 0, "type": "plate"}
        ],
        "gates": [
            {"x": 900, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [(180, GND)],
    },
    {
        "name": "the unseen path",
        "hint": "the world glitches. remember what you see.",
        "world_w": 1600,
        "robot": (60, GND - 36),
        "exit": (1530, GND),
        "platforms": [
            (0,    GND, 300, 70),
            (1200, GND, 400, 70),
        ],
        "memory_platforms": [
            (380, GND - 40,  100, 14),
            (580, GND - 80,  100, 14),
            (780, GND - 120, 100, 14),
            (980, GND - 60,  100, 14),
        ],
        "hazards": [(300, GND - 20, 900, 20)],
        "switches": [],
        "gates": [],
        "boxes": [],
    },
    {
        "name": "laser grid",
        "hint": "red is death. don't touch it.",
        "world_w": 2000,
        "robot": (60, GND - 36),
        "exit": (1940, GND),
        "platforms": [
            (0,    GND, 200, 70),
            (300,  GND - 65,  100, 14),
            (500,  GND - 130, 100, 14),
            (800,  GND, 300, 70),
            (1200, GND - 65,  120, 14),
            (1500, GND, 500, 70),
        ],
        "memory_platforms": [(680, GND - 60, 80, 14)],
        "hazards": [
            (200,  GND - 20,  600, 20),
            (1100, GND - 20,  400, 20),
            (650,  GND - 180,  20, 100),
        ],
        "switches": [
            {"x": 850, "y": GND - 8, "w": 44, "h": 8, "id": 1, "timed": 0, "type": "plate"},
        ],
        "gates": [
            {"x": 1400, "y": GND - 200, "w": 16, "h": 200, "id": 1},
        ],
        "boxes": [(100, GND)],
    },
    {
        "name": "mental acrobatics",
        "hint": "carry the box across the unseen. hurry.",
        "world_w": 2400,
        "robot": (60, GND - 36),
        "exit": (2340, GND),
        "platforms": [
            (0,    GND, 350, 70),
            (2000, GND, 400, 70),
        ],
        "memory_platforms": [
            (450,  GND - 40,  100, 14),
            (700,  GND - 80,  100, 14),
            (950,  GND - 120, 100, 14),
            (1200, GND - 80,  100, 14),
            (1450, GND - 40,  100, 14),
            (1700, GND,       100, 14),
        ],
        "hazards": [(350, GND - 20, 1650, 20)],
        "switches": [
            {"x": 100, "y": GND - 73, "w": 40, "h": 10, "id": 1, "timed": 600, "type": "button"}
        ],
        "gates": [
            {"x": 2100, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [(200, GND)],
    },
    {
        "name": "the grand illusion",
        "hint": "good luck.",
        "world_w": 3600,
        "robot": (60, GND - 36),
        "exit": (3540, GND),
        "platforms": [
            (0,    GND, 400, 70),
            (1000, GND - 100, 200, 14),
            (2200, GND, 300, 70),
            (3200, GND, 400, 70),
        ],
        "memory_platforms": [
            (450,  GND - 40,  80, 14),
            (600,  GND - 80,  80, 14),
            (750,  GND - 120, 80, 14),
            (1300, GND - 120, 80, 14),
            (1500, GND - 80,  80, 14),
            (1700, GND - 40,  80, 14),
            (1900, GND,       80, 14),
            (2600, GND - 60,  80, 14),
            (2800, GND - 120, 80, 14),
            (3000, GND - 60,  80, 14),
        ],
        "hazards": [
            (400,  GND - 20,  1800, 20),
            (2500, GND - 20,   700, 20),
            (850,  GND - 200,   20, 150),
            (1250, GND - 200,   20, 80),
            (1600, GND - 200,   20, 120),
            (2900, GND - 200,   20, 80),
        ],
        "switches": [
            {"x": 1050, "y": GND - 108, "w": 44, "h": 8, "id": 1, "timed": 0, "type": "plate"},
            {"x": 2350, "y": GND - 8,   "w": 44, "h": 8, "id": 2, "timed": 0, "type": "plate"},
        ],
        "gates": [
            {"x": 2050, "y": GND - 200, "w": 16, "h": 200, "id": 1},
            {"x": 3300, "y": GND - 200, "w": 16, "h": 200, "id": 2},
        ],
        "boxes": [(200, GND), (2250, GND)],
    },
]

# ── Generated levels 6-9: difficulty profile + 4 templates ───────

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
        self.n              = n
        self.world_w        = min(max(1400 + n * 220, 1400), 6000)
        self.mem_plat_count = min(max(n // 2, 4), 14)
        self.gap_max_px     = min(max(80 + n * 6, 80), 115)
        self.timer_frames   = min(max(600 - n * 20, 180), 600)


def _bridge_count(hazard_w, plat_w=90, max_gap=110):
    return max(4, int(hazard_w / (plat_w + max_gap)) + 2)


def tmpl_navigation(p):
    """Ghost run — memory platforms over hazards with elevated sections and MechaViruses."""
    safe_w  = 280
    hz_x    = safe_w
    hz_w    = p.world_w - safe_w * 2
    count   = max(4, int(hz_w / (p.gap_max_px + 45)) + 1)
    spacing = hz_w / (count + 1)
    heights = [GND - 40, GND - 80, GND - 120, GND - 80]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 45, heights[i % 4], 90, 14)
        for i in range(count)
    ]
    # Add an elevated mid-section platform
    mid_x = p.world_w // 2 - 80
    plats = [
        (0,              GND, safe_w, 70),
        (mid_x,          GND - 180, 160, 14),  # elevated lookout
        (p.world_w - safe_w, GND, safe_w, 70),
    ]
    # Vertical hazard walls creating corridors
    vert_hazards = []
    if p.n >= 7:
        vert_hazards.append((mid_x + 160, GND - 220, 16, 170))
    hazards = [(hz_x, GND - 20, hz_w, 20)] + vert_hazards
    # MechaViruses on safe zones
    virus_count = min(p.n - 4, 3)
    virus_list = []
    if virus_count >= 1:
        virus_list.append((p.world_w - safe_w + 30, GND - 40, p.world_w - safe_w + 10, p.world_w - 20))
    if virus_count >= 2:
        virus_list.append((mid_x + 20, GND - 180 - 40, mid_x, mid_x + 160))
    return {
        "name":  f"ghost run {p.n}",
        "hint":  _HINTS_NAV[p.n % len(_HINTS_NAV)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": plats,
        "memory_platforms": mem_plats,
        "hazards": hazards,
        "switches": [],
        "gates":   [],
        "boxes":   [],
        "viruses": virus_list,
    }


def tmpl_box_puzzle(p):
    """Cargo — multi-gate box puzzles with vertical laser walls and MechaVirus guards."""
    gap     = p.gap_max_px
    left_w  = p.world_w // 4
    mid_x   = left_w + gap
    mid_w   = p.world_w // 3
    right_x = mid_x + mid_w + gap
    right_w = p.world_w - right_x
    # Elevated platform for second box
    plats = [
        (0,       GND, left_w,  70),
        (mid_x,   GND, mid_w,   70),
        (mid_x + 60, GND - 120, 100, 14),  # elevated shelf
        (right_x, GND, right_w, 70),
    ]
    hazards = [
        (left_w, GND - 20, gap, 20),
        (mid_x + mid_w, GND - 20, gap, 20),
    ]
    # Vertical laser between gates
    if p.n >= 7:
        hazards.append((right_x + right_w // 2, GND - 200, 16, 150))
    # Two-gate puzzle: need 2 boxes on 2 plates
    switches = [
        {"x": mid_x + 80, "y": GND - 8, "w": 44, "h": 8,
         "id": 1, "timed": 0, "type": "plate"},
        {"x": p.world_w - 200, "y": GND - 8, "w": 44, "h": 8,
         "id": 2, "timed": 0, "type": "plate"},
    ]
    gates = [
        {"x": mid_x + mid_w - 20, "y": GND - 200, "w": 16, "h": 200, "id": 1},
        {"x": p.world_w - 130, "y": GND - 200, "w": 16, "h": 200, "id": 2},
    ]
    virus_list = [(right_x + 40, GND - 40, right_x + 10, p.world_w - 140)] if p.n >= 7 else []
    return {
        "name":  f"cargo {p.n}",
        "hint":  _HINTS_BOX[p.n % len(_HINTS_BOX)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 70, GND),
        "platforms": plats,
        "memory_platforms": [],
        "hazards": hazards,
        "switches": switches,
        "gates": gates,
        "boxes": [(100, GND), (mid_x + 20, GND)],
        "viruses": virus_list,
    }


def tmpl_memory_traverse(p):
    """Flash run — timed memory traverse with mid-section island, vertical hazards, and MechaVirus."""
    safe_w  = 300
    hz_x    = safe_w
    hz_w    = (p.world_w - safe_w * 2 - 160) // 2  # split into two sections
    # Mid-section safe island
    island_x = safe_w + hz_w
    island_w = 160
    hz2_x    = island_x + island_w
    hz2_w    = p.world_w - safe_w - hz2_x
    # Memory platforms for first half
    count1  = max(3, int(hz_w / (p.gap_max_px + 45)) + 1)
    spacing1 = hz_w / (count1 + 1)
    heights = [GND - 50, GND - 90, GND - 130, GND - 90]
    mem1 = [
        (int(hz_x + spacing1 * (i + 1)) - 45, heights[i % 4], 90, 14)
        for i in range(count1)
    ]
    # Memory platforms for second half
    count2  = max(3, int(hz2_w / (p.gap_max_px + 45)) + 1)
    spacing2 = hz2_w / (count2 + 1)
    mem2 = [
        (int(hz2_x + spacing2 * (i + 1)) - 45, heights[(i + 2) % 4], 90, 14)
        for i in range(count2)
    ]
    plats = [
        (0,                  GND, safe_w, 70),
        (island_x,           GND, island_w, 70),
        (island_x + 30,      GND - 130, 100, 14),  # elevated on island
        (p.world_w - safe_w, GND, safe_w, 70),
    ]
    hazards = [
        (hz_x, GND - 20, hz_w, 20),
        (hz2_x, GND - 20, hz2_w, 20),
    ]
    # Vertical hazard on island
    if p.n >= 8:
        hazards.append((island_x + island_w - 10, GND - 200, 12, 120))
    virus_list = [(island_x + 20, GND - 40, island_x + 10, island_x + island_w - 10)] if p.n >= 8 else []
    return {
        "name":  f"flash run {p.n}",
        "hint":  _HINTS_MEM[p.n % len(_HINTS_MEM)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": plats,
        "memory_platforms": mem1 + mem2,
        "hazards": hazards,
        "switches": [
            {"x": 100, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": p.timer_frames, "type": "button"}
        ],
        "gates": [
            {"x": p.world_w - safe_w - 20, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes":   [],
        "viruses": virus_list,
    }


def tmpl_combo(p):
    """Overload — box + memory + timer + multi-height platforms + MechaViruses."""
    safe_w  = 300
    hz_x    = safe_w
    hz_w    = p.world_w - safe_w * 2
    count   = max(4, int(hz_w / (p.gap_max_px + 50)) + 1)
    spacing = hz_w / (count + 1)
    heights = [GND - 50, GND - 90, GND - 130, GND - 90]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 50, heights[i % 4], 100, 14)
        for i in range(count)
    ]
    # Multi-height elevated platforms
    plats = [
        (0,                  GND, safe_w, 70),
        (safe_w + 100,       GND - 160, 120, 14),  # high perch
        (p.world_w // 2 - 60, GND - 200, 120, 14), # center high
        (p.world_w - safe_w - 150, GND - 140, 120, 14),  # pre-exit high
        (p.world_w - safe_w, GND, safe_w, 70),
    ]
    hazards = [(hz_x, GND - 20, hz_w, 20)]
    # Vertical hazards creating corridors
    if p.n >= 8:
        hazards.append((p.world_w // 2 - 8, GND - 250, 16, 140))
    if p.n >= 9:
        hazards.append((p.world_w - safe_w - 160, GND - 200, 16, 100))
    # More MechaViruses at higher levels
    virus_list = []
    if p.n >= 8:
        virus_list.append((p.world_w - safe_w + 40, GND - 40, p.world_w - safe_w + 10, p.world_w - 70))
    if p.n >= 9:
        virus_list.append((safe_w + 110, GND - 160 - 40, safe_w + 100, safe_w + 220))
    return {
        "name":  f"overload {p.n}",
        "hint":  _HINTS_COMBO[p.n % len(_HINTS_COMBO)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": plats,
        "memory_platforms": mem_plats,
        "hazards": hazards,
        "switches": [
            {"x": 80, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": p.timer_frames, "type": "button"}
        ],
        "gates": [
            {"x": p.world_w - safe_w - 20, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes":   [(220, GND)],
        "viruses": virus_list,
    }


def _pick_template(n):
    r = n % 4
    if r == 2: return tmpl_navigation
    if r == 3: return tmpl_box_puzzle
    if r == 0: return tmpl_memory_traverse
    return tmpl_combo if n >= 8 else tmpl_navigation  # r == 1
