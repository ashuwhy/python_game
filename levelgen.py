"""Procedural level generation — chunk-based."""
import math
import random
import pygame

W, H = 960, 540
CHUNK_W = 960
GROUND_H = 48

# Pipe colors (duplicated here to avoid circular import)
PIPE_GREEN = (34, 177, 76)
PIPE_GREEN_DARK = (18, 130, 50)
PIPE_GREEN_LIP = (50, 210, 100)
PIPE_PURPLE = (130, 50, 180)
PIPE_PURPLE_DARK = (80, 25, 120)
PIPE_PURPLE_LIP = (170, 90, 220)


class Pipe:
    """A warp pipe. kind is 'teleport' or 'dimension'."""
    PIPE_W = 56
    PIPE_H = 64
    LIP_H = 16

    def __init__(self, x, y, kind, dimension, pair_id):
        self.x = x
        self.y = y
        self.kind = kind
        self.dimension = dimension
        self.pair_id = pair_id
        self.rect = pygame.Rect(x, y, self.PIPE_W, self.PIPE_H)
        self.entry_zone = pygame.Rect(x, y, self.PIPE_W, self.PIPE_H)

    def draw(self, surface, frame, cam_x):
        sx = self.x - int(cam_x)
        if sx < -self.PIPE_W - 20 or sx > W + 20:
            return
        is_dim = self.kind == "dimension"
        base = PIPE_PURPLE if is_dim else PIPE_GREEN
        dark = PIPE_PURPLE_DARK if is_dim else PIPE_GREEN_DARK
        lip = PIPE_PURPLE_LIP if is_dim else PIPE_GREEN_LIP

        # body
        body = pygame.Rect(sx + 6, self.y + self.LIP_H,
                           self.PIPE_W - 12, self.PIPE_H - self.LIP_H)
        pygame.draw.rect(surface, base, body)
        pygame.draw.rect(surface, dark, body, 2)
        stripe = pygame.Rect(sx + 12, self.y + self.LIP_H + 2,
                             6, self.PIPE_H - self.LIP_H - 4)
        pygame.draw.rect(surface, lip, stripe)

        # lip
        lip_rect = pygame.Rect(sx, self.y, self.PIPE_W, self.LIP_H)
        pygame.draw.rect(surface, base, lip_rect, border_radius=4)
        pygame.draw.rect(surface, dark, lip_rect, 2, border_radius=4)
        pygame.draw.rect(surface, lip,
                         pygame.Rect(sx + 4, self.y + 3, 8, self.LIP_H - 6))

        # glow for dimension pipes
        if is_dim:
            ga = int(80 + 50 * math.sin(frame * 0.08))
            gs = pygame.Surface((self.PIPE_W + 12, self.PIPE_H + 12),
                                pygame.SRCALPHA)
            pygame.draw.rect(gs, (170, 80, 255, ga), gs.get_rect(),
                             border_radius=8)
            surface.blit(gs, (sx - 6, self.y - 6))

        # arrow
        arrow_y = self.y - 14 + int(3 * math.sin(frame * 0.1))
        mid_x = sx + self.PIPE_W // 2
        ac = (200, 140, 255) if is_dim else (255, 255, 100)
        pygame.draw.polygon(surface, ac, [
            (mid_x, arrow_y + 8), (mid_x - 6, arrow_y), (mid_x + 6, arrow_y)])


def generate_level(dimension, level_num):
    """Returns (blocks, coins, pipes, flag_x, world_width)."""
    num_chunks = 8 + level_num
    world_w = num_chunks * CHUNK_W
    gt = H - GROUND_H  # ground top

    blocks = []
    coins = []
    pipes = []

    # Collect teleport pipe spots to pair them up later
    tp_spots = []

    for ci in range(num_chunks):
        x0 = ci * CHUNK_W

        # --- Ground (with occasional pits) ---
        if ci == 0 or ci >= num_chunks - 1:
            blocks.append(pygame.Rect(x0, gt, CHUNK_W, GROUND_H))
        else:
            pit_chance = min(0.3 + level_num * 0.03, 0.5)
            if random.random() < pit_chance:
                gs = random.randint(200, CHUNK_W - 280)
                gw = random.randint(80, min(100 + level_num * 8, 180))
                if gs > 0:
                    blocks.append(pygame.Rect(x0, gt, gs, GROUND_H))
                ax = x0 + gs + gw
                aw = CHUNK_W - gs - gw
                if aw > 0:
                    blocks.append(pygame.Rect(ax, gt, aw, GROUND_H))
            else:
                blocks.append(pygame.Rect(x0, gt, CHUNK_W, GROUND_H))

        # --- Platforms (reachable staircase) ---
        # Max jump height is ~150px, so each platform must be within
        # ~120px vertically of the ground or another platform.
        MAX_JUMP = 120
        chunk_plats = []
        num_plats = random.randint(2, 4)
        # Start from ground level and step upward
        prev_y = gt  # ground top
        for j in range(num_plats):
            px = x0 + int(CHUNK_W * (j + 0.5) / (num_plats + 1))
            px += random.randint(-60, 60)
            px = max(x0 + 20, min(px, x0 + CHUNK_W - 160))
            # Step up from previous surface, but keep it reachable
            step = random.randint(60, MAX_JUMP)
            py = prev_y - step
            py = max(H - 420, min(py, gt - 60))  # clamp
            pw = random.randint(80, 160)
            plat = pygame.Rect(px, py, pw, 24)
            blocks.append(plat)
            chunk_plats.append(plat)
            # Next platform can step from this one or reset to ground
            if random.random() < 0.5:
                prev_y = py  # build higher
            else:
                prev_y = gt  # reset to ground level

        # --- Coins (placed above platforms so they're reachable) ---
        for plat in chunk_plats:
            if random.random() < 0.6:
                cx = plat.x + plat.w // 2
                cy = plat.y - 40
                coins.append({"pos": [cx, cy], "taken": False,
                              "dim": dimension})
        # Extra ground-level coins
        if random.random() < 0.4:
            cx = x0 + random.randint(80, CHUNK_W - 80)
            coins.append({"pos": [cx, gt - 50], "taken": False,
                          "dim": dimension})

        # --- Underworld ceiling ---
        if dimension == "underworld":
            blocks.append(pygame.Rect(x0, 0, CHUNK_W, 24))

        # --- Pipes ---
        if 1 < ci < num_chunks - 1:
            if ci % 3 == 1:
                px = x0 + random.randint(100, CHUNK_W - 150)
                tp_spots.append((px, gt - 64))
            if ci == num_chunks // 2:
                px = x0 + CHUNK_W // 2
                pipes.append(Pipe(px, gt - 64, "dimension", dimension,
                                  900 + level_num))

    # Pair up teleport spots
    random.shuffle(tp_spots)
    pid = 0
    for i in range(0, len(tp_spots) - 1, 2):
        pipes.append(Pipe(tp_spots[i][0], tp_spots[i][1],
                          "teleport", dimension, pid))
        pipes.append(Pipe(tp_spots[i + 1][0], tp_spots[i + 1][1],
                          "teleport", dimension, pid))
        pid += 1

    flag_x = world_w - 120
    return blocks, coins, pipes, flag_x, world_w
