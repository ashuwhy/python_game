"""
Comprehensive Level Playability Validator for VOLITAL
Tests all 20 levels for physics feasibility, path connectivity, 
puzzle solvability, and data integrity.

Physics:
  jump_power=-9.5, gravity=0.48, speed=3.8
  Max jump height ≈ 94px, Max horizontal air ≈ 152px
  Robot: 24×36
"""

import sys, math
sys.path.insert(0, '.')

from levels_1_9 import LEVELS, DifficultyProfile, _pick_template
from levels_10_18 import tmpl_boss, generate_level_10_18
from levels_19_20 import tmpl_gauntlet, tmpl_final_boss

GND = 490
MAX_JUMP_H = 94
MAX_JUMP_X = 152
SAFE_JUMP_H = 80
SAFE_JUMP_X = 120
ROBOT_W, ROBOT_H = 24, 36

def get_level(idx):
    if idx < len(LEVELS):
        return LEVELS[idx]
    n = idx + 1
    if n == 10: return tmpl_boss(DifficultyProfile(n))
    if 11 <= n <= 18: return generate_level_10_18(n, DifficultyProfile(n))
    if n == 19: return tmpl_gauntlet(DifficultyProfile(n))
    if n == 20: return tmpl_final_boss(DifficultyProfile(n))
    return _pick_template(n)(DifficultyProfile(n))

# ── Data integrity checks ──

REQUIRED_KEYS = ["name", "hint", "world_w", "robot", "exit", "platforms",
                 "hazards", "switches", "gates", "boxes"]

def check_data_integrity(d, idx):
    issues = []
    for k in REQUIRED_KEYS:
        if k not in d:
            issues.append(f"Missing required key: '{k}'")
    # Robot and exit should be tuples of 2
    if "robot" in d and len(d["robot"]) != 2:
        issues.append(f"Robot position has {len(d['robot'])} values, expected 2")
    if "exit" in d and len(d["exit"]) != 2:
        issues.append(f"Exit position has {len(d['exit'])} values, expected 2")
    # Platforms should be tuples of 4
    for i, p in enumerate(d.get("platforms", [])):
        if len(p) != 4:
            issues.append(f"Platform {i} has {len(p)} values, expected 4 (x,y,w,h)")
    for i, p in enumerate(d.get("memory_platforms", [])):
        if len(p) != 4:
            issues.append(f"Memory platform {i} has {len(p)} values, expected 4")
    for i, h in enumerate(d.get("hazards", [])):
        if len(h) != 4:
            issues.append(f"Hazard {i} has {len(h)} values, expected 4")
    # Switches must have required fields
    for i, s in enumerate(d.get("switches", [])):
        for k in ["x", "y", "w", "h", "id", "timed", "type"]:
            if k not in s:
                issues.append(f"Switch {i} missing key '{k}'")
    # Gates must have required fields
    for i, g in enumerate(d.get("gates", [])):
        for k in ["x", "y", "w", "h", "id"]:
            if k not in g:
                issues.append(f"Gate {i} missing key '{k}'")
    # Viruses should be tuples of 4
    for i, v in enumerate(d.get("viruses", [])):
        if len(v) != 4:
            issues.append(f"Virus {i} has {len(v)} values, expected 4 (x,y,left,right)")
        else:
            vx, vy, vl, vr = v
            if vl >= vr:
                issues.append(f"Virus {i} has left({vl}) >= right({vr}) patrol bounds")
            if vx < vl or vx > vr:
                issues.append(f"Virus {i} starts at x={vx} outside patrol [{vl},{vr}]")
    # World bounds
    world_w = d.get("world_w", 640)
    rx, ry = d.get("robot", (0, 0))
    ex, ey = d.get("exit", (0, 0))
    if rx < 0 or rx > world_w:
        issues.append(f"Robot x={rx} outside world [0,{world_w}]")
    if ex < 0 or ex > world_w:
        issues.append(f"Exit x={ex} outside world [0,{world_w}]")
    return issues

# ── Surface / node graph for path analysis ──

def build_surfaces(d):
    """Build a list of walkable surface nodes from platforms + memory platforms."""
    surfaces = []
    for p in d.get("platforms", []):
        x, y, w, h = p
        surfaces.append({"x": x, "y": y, "w": w, "type": "solid", "id": len(surfaces)})
    for p in d.get("memory_platforms", []):
        x, y, w, h = p
        surfaces.append({"x": x, "y": y, "w": w, "type": "memory", "id": len(surfaces)})
    return surfaces

def surfaces_reachable(a, b):
    """Can the robot jump from surface a to surface b?"""
    # Horizontal gap between surfaces
    if a["x"] + a["w"] <= b["x"]:
        h_gap = b["x"] - (a["x"] + a["w"])
    elif b["x"] + b["w"] <= a["x"]:
        h_gap = a["x"] - (b["x"] + b["w"])
    else:
        h_gap = 0  # overlapping horizontally
    
    v_diff = a["y"] - b["y"]  # positive = b is higher than a
    
    if h_gap > MAX_JUMP_X:
        return False
    
    # Going up — must be within jump height
    if v_diff < 0:  # b is lower — dropping down, always possible
        return h_gap <= MAX_JUMP_X
    else:  # b is higher — must jump up
        return v_diff <= MAX_JUMP_H and h_gap <= MAX_JUMP_X
    
def check_path_connectivity(d):
    """Check if robot can reach exit via BFS over surface graph."""
    issues = []
    surfaces = build_surfaces(d)
    if not surfaces:
        issues.append("No surfaces at all!")
        return issues
    
    rx, ry = d["robot"]
    ex, ey = d["exit"]
    
    # Find start surface
    start_id = None
    for s in surfaces:
        if s["x"] - 20 <= rx <= s["x"] + s["w"] + 20:
            if abs(s["y"] - (ry + ROBOT_H)) <= 50 or (s["y"] >= GND - 5 and ry + ROBOT_H >= GND - 50):
                start_id = s["id"]
                break
    if start_id is None:
        issues.append(f"Robot at ({rx},{ry}) not on any surface")
        return issues
    
    # Find end surface
    end_id = None
    for s in surfaces:
        if s["x"] - 20 <= ex <= s["x"] + s["w"] + 20:
            if abs(s["y"] - ey) <= 50 or (s["y"] >= GND - 5 and ey >= GND - 5):
                end_id = s["id"]
                break
    if end_id is None:
        issues.append(f"Exit at ({ex},{ey}) not on any surface")
        return issues
    
    # Build adjacency
    n = len(surfaces)
    adj = {s["id"]: [] for s in surfaces}
    for i in range(n):
        for j in range(n):
            if i != j and surfaces_reachable(surfaces[i], surfaces[j]):
                adj[surfaces[i]["id"]].append(surfaces[j]["id"])
    
    # BFS
    visited = set()
    queue = [start_id]
    visited.add(start_id)
    while queue:
        cur = queue.pop(0)
        if cur == end_id:
            return issues  # path found
        for nxt in adj[cur]:
            if nxt not in visited:
                visited.add(nxt)
                queue.append(nxt)
    
    # Find which surfaces are unreachable
    reachable_names = []
    unreachable_names = []
    for s in surfaces:
        label = f"{s['type']}@x={s['x']},y={s['y']}"
        if s["id"] in visited:
            reachable_names.append(label)
        else:
            unreachable_names.append(label)
    
    issues.append(f"NO PATH from robot to exit! Reachable: {len(visited)}/{n} surfaces")
    if len(unreachable_names) <= 5:
        for name in unreachable_names:
            issues.append(f"  unreachable: {name}")
    return issues

# ── Hazard crossing checks ──

def check_hazard_crossing(d):
    issues = []
    warnings = []
    surfaces = build_surfaces(d)
    
    hazards = d.get("hazards", [])
    h_hazards = [(x, y, w, h) for x, y, w, h in hazards if w > h]
    v_hazards = [(x, y, w, h) for x, y, w, h in hazards if h >= w]
    
    for hx, hy, hw, hh in h_hazards:
        # Find all surfaces that help cross this hazard
        covering = [s for s in surfaces
                   if s["x"] + s["w"] > hx - 20 and s["x"] < hx + hw + 20 and s["y"] < hy]
        
        if not covering and hw > MAX_JUMP_X:
            issues.append(f"Floor hazard at x={hx} w={hw}: NO platforms to cross")
        elif covering:
            covering.sort(key=lambda s: s["x"])
            # Check consecutive gaps
            for i in range(len(covering) - 1):
                a, b = covering[i], covering[i+1]
                gap = b["x"] - (a["x"] + a["w"])
                if gap > MAX_JUMP_X:
                    issues.append(f"Floor hazard x={hx}: gap {gap}px between crossing platforms")
                elif gap > SAFE_JUMP_X:
                    warnings.append(f"Floor hazard x={hx}: tight gap {gap}px (challenging)")
    
    for vx, vy, vw, vh in v_hazards:
        # Check if passable — gap above or below the hazard
        top_gap = vy  # space above hazard from screen top
        bottom_gap = GND - (vy + vh)  # space below hazard
        if bottom_gap >= ROBOT_H + 10:
            continue  # can walk under
        if top_gap >= ROBOT_H + 10:
            # Need a platform to get over
            nearby_plats = [s for s in surfaces
                           if abs(s["x"] - vx) < MAX_JUMP_X * 2 and s["y"] < vy - 10]
            if not nearby_plats:
                warnings.append(f"Vertical hazard x={vx} y={vy} h={vh}: may need platform to pass")
            continue
        # Both gaps too small
        if bottom_gap < ROBOT_H and top_gap < ROBOT_H:
            issues.append(f"Vertical hazard x={vx}: blocks entire height ({vy} to {vy+vh})")
    
    return issues, warnings

# ── Puzzle checks ──

def check_puzzles(d):
    issues = []
    warnings = []
    
    switches = d.get("switches", [])
    gates = d.get("gates", [])
    boxes = d.get("boxes", [])
    
    plates = [s for s in switches if s.get("type") == "plate"]
    buttons = [s for s in switches if s.get("type") == "button"]
    
    # Check gates have matching switches
    boss_gate_ids = {999, 998}
    for g in gates:
        gid = g.get("id")
        if gid in boss_gate_ids:
            continue
        matching = [s for s in switches if s.get("id") == gid]
        if not matching:
            issues.append(f"Gate id={gid} has no matching switch!")
    
    # Check plates have enough boxes
    if plates:
        if len(boxes) < len(plates):
            issues.append(f"Need {len(plates)} boxes for plates, only have {len(boxes)}")
    
    # Check boxes are on solid ground
    surfaces = build_surfaces(d)
    for bx, by in boxes:
        on_surface = False
        for s in surfaces:
            if s["type"] == "solid" and s["x"] <= bx <= s["x"] + s["w"]:
                if abs(s["y"] - by) <= 10:
                    on_surface = True
                    break
        if not on_surface:
            warnings.append(f"Box at ({bx},{by}) may not be on solid ground")
    
    return issues, warnings

# ── Memory platform coverage checks ──

def check_memory_coverage(d):
    """Check that hazardous gaps have memory platforms if needed."""
    issues = []
    
    mem_plats = d.get("memory_platforms", [])
    hazards = d.get("hazards", [])
    h_hazards = [(x, y, w, h) for x, y, w, h in hazards if w > h and w > MAX_JUMP_X]
    
    for hx, hy, hw, hh in h_hazards:
        # Wide floor hazards need stepping stones
        solid_plats = [p for p in d.get("platforms", [])
                      if p[0] + p[2] > hx and p[0] < hx + hw and p[1] < hy]
        mem_over = [m for m in mem_plats
                   if m[0] + m[2] > hx - 20 and m[0] < hx + hw + 20 and m[1] < hy]
        
        if not solid_plats and not mem_over:
            issues.append(f"Wide hazard x={hx} w={hw}: no memory or solid platforms to cross!")
    
    return issues

# ── Run all checks ──

def validate_level(idx):
    d = get_level(idx)
    name = d.get("name", f"level {idx+1}")
    all_issues = []
    all_warnings = []
    
    # 1. Data integrity
    all_issues += check_data_integrity(d, idx)
    
    # 2. Path connectivity
    all_issues += check_path_connectivity(d)
    
    # 3. Hazard crossing
    hi, hw = check_hazard_crossing(d)
    all_issues += hi
    all_warnings += hw
    
    # 4. Puzzle solvability
    pi, pw = check_puzzles(d)
    all_issues += pi
    all_warnings += pw
    
    # 5. Memory platform coverage
    all_issues += check_memory_coverage(d)
    
    return name, d, all_issues, all_warnings

# ── Main ──

print("=" * 70)
print("VOLITAL Comprehensive Level Validator")
print("=" * 70)
print()

total_issues = 0
total_warnings = 0
level_details = []

for i in range(20):
    name, d, issues, warnings = validate_level(i)
    status = "✅" if not issues else "❌"
    if warnings and not issues:
        status = "⚠️ "
    
    plats = len(d.get("platforms", []))
    mems = len(d.get("memory_platforms", []))
    haz = len(d.get("hazards", []))
    vir = len(d.get("viruses", []))
    sw = len(d.get("switches", []))
    gt = len(d.get("gates", []))
    bx = len(d.get("boxes", []))
    has_boss = "boss" in d or "boss2" in d
    
    print(f"Level {i+1:2d}: {name:22s} {status}  "
          f"[plats={plats} mem={mems} haz={haz} vir={vir} sw={sw} gt={gt} box={bx}"
          f"{' BOSS' if has_boss else ''}]")
    
    for issue in issues:
        print(f"  ❌ {issue}")
        total_issues += 1
    for warn in warnings:
        print(f"  ⚠️  {warn}")
        total_warnings += 1

print()
print("=" * 70)
print(f"Results: {total_issues} ISSUES, {total_warnings} warnings")
if total_issues == 0:
    print("🎮 ALL 20 LEVELS PASS comprehensive playability checks!")
else:
    print("🔧 Some levels need fixing!")
print("=" * 70)
