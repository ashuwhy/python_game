"""Fractional Brownian motion over OpenSimplex for procedural terrain."""
from __future__ import annotations

from opensimplex import OpenSimplex  # type: ignore[reportMissingImports]


def terrain_seed(dimension: str, level_num: int) -> int:
    dim = 0x5F356495 if dimension == "overworld" else 0xDCE1754A
    return (level_num * 195_709_347 + dim) & 0x7FFFFFFF


def make_generators(seed: int) -> tuple[OpenSimplex, OpenSimplex, OpenSimplex, OpenSimplex]:
    """Ground fBm, pit mask, platform detail, underworld ceiling."""
    return (
        OpenSimplex(seed),
        OpenSimplex(seed + 1_091),
        OpenSimplex(seed + 2_003),
        OpenSimplex(seed + 3_777),
    )


def fbm2d(
    gen: OpenSimplex,
    nx: float,
    ny: float,
    octaves: int = 5,
    persistence: float = 0.5,
    lacunarity: float = 2.0,
) -> float:
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    norm = 0.0
    for _ in range(octaves):
        value += amplitude * gen.noise2(nx * frequency, ny * frequency)
        norm += amplitude
        amplitude *= persistence
        frequency *= lacunarity
    return value / norm if norm else 0.0


def build_surface_heights(
    world_w: int,
    step: int,
    gt: float,
    ground_amp: float,
    max_step: int,
    edge_x: int,
    pit_floor: float,
    height_snap: int,
    gen: OpenSimplex,
    pit_gen: OpenSimplex,
    level_num: int,
) -> tuple[list[float], list[bool]]:
    """Per-column ground top Y and whether solid exists (False = pit air)."""
    n = world_w // step + 2
    heights: list[float] = []
    pit_thresh = -0.42 + min(level_num * 0.018, 0.38)

    for i in range(n):
        x = i * step
        if x < edge_x or x >= world_w - edge_x:
            heights.append(float(gt))
            continue
        nx = x * 0.00118
        ny = 0.29
        broad = fbm2d(gen, nx, ny, octaves=4, persistence=0.52, lacunarity=2.08)
        edge = fbm2d(gen, x * 0.0046, 8.75, octaves=2, persistence=0.45)
        v = broad * 0.82 + edge * 0.18
        h = gt + v * ground_amp
        h = max(pit_floor, min(h, gt + 22.0))
        heights.append(h)

    _slope_clamp(heights, max_step)
    _slope_clamp_backward(heights, max_step)

    if height_snap > 1:
        heights[:] = [_snap_height(h, height_snap, gt) for h in heights]
        _slope_clamp(heights, max_step)
        _slope_clamp_backward(heights, max_step)

    for i in range(n):
        x = i * step
        if x < edge_x or x >= world_w - edge_x:
            heights[i] = float(gt)

    _slope_clamp(heights, max_step)
    _slope_clamp_backward(heights, max_step)

    columns = [True] * (n - 1)
    for chunk_x in range(edge_x, max(edge_x, world_w - edge_x), edge_x):
        pv = pit_gen.noise2(chunk_x * 0.0011, 11.3)
        if pv >= pit_thresh:
            continue

        center_noise = pit_gen.noise2(chunk_x * 0.0025, 24.8)
        width_noise = pit_gen.noise2(chunk_x * 0.0034, 35.1)
        safe_pad = 220
        center_t = (center_noise + 1.0) * 0.5
        center = chunk_x + safe_pad + center_t * max(1, edge_x - safe_pad * 2)
        width = 88 + min(level_num * 7, 70) + (width_noise + 1.0) * 28
        gap_left = center - width * 0.5
        gap_right = center + width * 0.5

        for i in range(max(0, int(gap_left // step)),
                       min(len(columns), int(gap_right // step) + 1)):
            x = i * step
            if edge_x <= x < world_w - edge_x:
                columns[i] = False

    return heights, columns


def _slope_clamp(heights: list[float], max_step: int) -> None:
    for i in range(1, len(heights)):
        d = heights[i] - heights[i - 1]
        if d > max_step:
            heights[i] = heights[i - 1] + max_step
        elif d < -max_step:
            heights[i] = heights[i - 1] - max_step


def _slope_clamp_backward(heights: list[float], max_step: int) -> None:
    for i in range(len(heights) - 2, -1, -1):
        d = heights[i + 1] - heights[i]
        if d > max_step:
            heights[i] = heights[i + 1] - max_step
        elif d < -max_step:
            heights[i] = heights[i + 1] + max_step


def _snap_height(y: float, snap: int, origin: float) -> float:
    return origin + round((y - origin) / snap) * snap


def surface_y_at(
    x: float,
    heights: list[float],
    step: int,
    world_w: int,
    gt: float,
    edge_x: int,
) -> float:
    if x <= 0:
        return float(gt)
    if x >= world_w:
        return float(gt)
    if x < edge_x or x >= world_w - edge_x:
        return float(gt)
    fi = x / step
    i = int(fi)
    if i >= len(heights) - 1:
        return heights[-1]
    t = fi - i
    return heights[i] * (1.0 - t) + heights[i + 1] * t


def ceiling_strip_heights(
    world_w: int,
    step: int,
    gen: OpenSimplex,
    base_h: float = 21.0,
    vary: float = 9.0,
) -> list[float]:
    """Top trim depth per column (rect height from y=0)."""
    n = world_w // step + 1
    out: list[float] = []
    for i in range(n - 1):
        x = i * step
        v = fbm2d(gen, x * 0.00145, 0.61, octaves=3, persistence=0.55, lacunarity=2.0)
        out.append(base_h + v * vary)
    return out
