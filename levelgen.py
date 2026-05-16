"""Procedural level generation — chunk-based with fBm terrain."""
import math
import random
import pygame

from textures import get_texture, draw_tiled, draw_gradient_pipe
from noise_terrain import (
    build_surface_heights,
    ceiling_strip_heights,
    fbm2d,
    make_generators,
    surface_y_at,
    terrain_seed,
)

W, H = 960, 540
CHUNK_W = 960
GROUND_H = 48
MAX_CHUNKS = 24

TERRAIN_STEP = 16
TERRAIN_MAX_SLOPE = 16
TERRAIN_HEIGHT_SNAP = 16
GROUND_VARIATION_AMP = 48.0
PIT_FLOOR_Y = H - 385
MAX_JUMP = 120

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

        body_rect = pygame.Rect(sx + 6, self.y + self.LIP_H, self.PIPE_W - 12, self.PIPE_H - self.LIP_H)
        lip_rect = pygame.Rect(sx, self.y, self.PIPE_W, self.LIP_H)
        draw_gradient_pipe(surface, body_rect, is_dim, False)
        draw_gradient_pipe(surface, lip_rect, is_dim, True)

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
    """Returns (blocks, coins, pipes, flag_x, world_width, breakable_ids)."""
    num_chunks = min(MAX_CHUNKS, 8 + level_num)
    world_w = num_chunks * CHUNK_W
    gt = H - GROUND_H

    seed = terrain_seed(dimension, level_num)
    rng = random.Random(seed)
    ground_gen, pit_gen, plat_gen, ceil_gen = make_generators(seed)

    heights, col_solid = build_surface_heights(
        world_w,
        TERRAIN_STEP,
        float(gt),
        GROUND_VARIATION_AMP,
        TERRAIN_MAX_SLOPE,
        CHUNK_W,
        float(PIT_FLOOR_Y),
        TERRAIN_HEIGHT_SNAP,
        ground_gen,
        pit_gen,
        level_num,
    )

    blocks = []
    breakable_ids: set[int] = set()
    for i, solid in enumerate(col_solid):
        if not solid:
            continue
        x = i * TERRAIN_STEP
        top = int(heights[i])
        blocks.append(pygame.Rect(x, top, TERRAIN_STEP, H - top))

    if dimension == "underworld":
        ceil_depths = ceiling_strip_heights(world_w, TERRAIN_STEP, ceil_gen)
        for i, ch in enumerate(ceil_depths):
            x = i * TERRAIN_STEP
            h = int(max(16, min(ch, 38)))
            blocks.append(pygame.Rect(x, 0, TERRAIN_STEP, h))

    coins = []
    pipes = []
    tp_spots = []

    for ci in range(num_chunks):
        x0 = ci * CHUNK_W

        def sy(px):
            return surface_y_at(
                float(px), heights, TERRAIN_STEP, world_w, float(gt), CHUNK_W)

        # --- Platforms (reachable; heights follow fBm) ---
        chunk_plats = []
        num_plats = rng.randint(2, 4)
        anchor = sy(x0 + CHUNK_W // 2)
        prev_y = anchor
        for j in range(num_plats):
            t = (j + 0.5) / (num_plats + 1)
            px = x0 + int(CHUNK_W * t)
            px += rng.randint(-55, 55)
            px = max(x0 + 20, min(px, x0 + CHUNK_W - 160))
            base_g = sy(float(px))
            ph = fbm2d(
                plat_gen,
                px * 0.0031,
                ci * 0.17 + j * 0.09,
                octaves=3,
                persistence=0.52,
                lacunarity=2.0,
            )
            span = int(62 + (ph + 1) * 0.5 * (MAX_JUMP - 64))
            span = max(58, min(span, MAX_JUMP))
            py = prev_y - span
            py = int(max(H - 415, min(py, base_g - 38)))
            pw = rng.randint(80, 160)
            plat = pygame.Rect(px, py, pw, 24)
            blocks.append(plat)
            breakable_ids.add(id(plat))
            chunk_plats.append(plat)
            if rng.random() < 0.5:
                prev_y = float(py)
            else:
                prev_y = sy(float(px))

        # --- Coins ---
        for plat in chunk_plats:
            if rng.random() < 0.58:
                cx = plat.x + plat.w // 2
                coins.append({"pos": [cx, plat.y - 40], "taken": False,
                              "dim": dimension})
        if rng.random() < 0.42:
            cx = x0 + rng.randint(80, CHUNK_W - 80)
            gy = sy(float(cx))
            coins.append({"pos": [cx, int(gy) - 50], "taken": False,
                          "dim": dimension})

        # --- Pipes ---
        if 1 < ci < num_chunks - 1:
            if ci % 3 == 1:
                px = x0 + rng.randint(100, CHUNK_W - 150)
                tp_spots.append((px, sy(float(px)) - Pipe.PIPE_H))
            if ci == num_chunks // 2:
                px = x0 + CHUNK_W // 2
                pipes.append(Pipe(px, sy(float(px)) - Pipe.PIPE_H,
                                  "dimension", dimension, 900 + level_num))

    rng.shuffle(tp_spots)
    pid = 0
    for i in range(0, len(tp_spots) - 1, 2):
        pipes.append(Pipe(tp_spots[i][0], tp_spots[i][1],
                          "teleport", dimension, pid))
        pipes.append(Pipe(tp_spots[i + 1][0], tp_spots[i + 1][1],
                          "teleport", dimension, pid))
        pid += 1

    flag_x = world_w - 120
    return blocks, coins, pipes, flag_x, world_w, breakable_ids
