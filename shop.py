"""Upgrade shop catalog and stat derivation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame


@dataclass
class Stats:
    jump_v: float = -14.0
    move_speed: float = 7.0
    can_break_bricks: bool = False
    coin_magnet_px: int = 0


@dataclass(frozen=True)
class Upgrade:
    id: str
    name: str
    desc: str
    base_cost: int
    cost_growth: float
    max_level: int
    apply_level: Callable[[Stats], None]

    def current_cost(self, owned_level: int) -> int:
        return int(self.base_cost * (self.cost_growth**owned_level))


def _high_jump(s: Stats) -> None:
    s.jump_v -= 1.5


def _swift_feet(s: Stats) -> None:
    s.move_speed += 1.0


def _wall_break(s: Stats) -> None:
    s.can_break_bricks = True


def _mag_1(s: Stats) -> None:
    s.coin_magnet_px = 60


def _mag_2(s: Stats) -> None:
    s.coin_magnet_px = 120


CATALOG: list[Upgrade] = [
    Upgrade(
        "high_jump",
        "HIGH JUMP",
        "Jump higher each level.",
        10,
        2.5,
        3,
        _high_jump,
    ),
    Upgrade(
        "swift_feet",
        "SWIFT FEET",
        "Move faster.",
        15,
        2.67,
        2,
        _swift_feet,
    ),
    Upgrade(
        "wall_break",
        "WALL BREAK",
        "Break brick platforms from below.",
        40,
        1.0,
        1,
        _wall_break,
    ),
    Upgrade(
        "coin_magnet",
        "COIN MAGNET",
        "Pull nearby coins (lv1: 60px, lv2: 120px).",
        20,
        2.5,
        2,
        _mag_1,
    ),
]


def derive_stats(upgrades_owned: dict[str, int]) -> Stats:
    s = Stats()
    owned = {str(k): int(v) for k, v in upgrades_owned.items() if int(v) > 0}
    for u in CATALOG:
        lvl = owned.get(u.id, 0)
        for i in range(lvl):
            if u.id == "coin_magnet" and i == 1:
                _mag_2(s)
            else:
                u.apply_level(s)
    return s


def run_shop(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    save_state: dict,
    draw_bitmap_text,
    bitmap_text_width,
    present_fn,
    w: int,
    h: int,
    fps: int,
    save_fn,
) -> None:
    """Modal shop: Up/Down select, Enter buy, Esc/B close."""
    selection = 0
    dirty = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if dirty:
                    save_fn()
                pygame.quit()
                raise SystemExit(0)
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_b):
                    if dirty:
                        save_fn()
                    return
                if event.key == pygame.K_UP:
                    selection = (selection - 1) % len(CATALOG)
                if event.key == pygame.K_DOWN:
                    selection = (selection + 1) % len(CATALOG)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    u = CATALOG[selection]
                    owned = int(save_state["upgrades"].get(u.id, 0))
                    if owned >= u.max_level:
                        continue
                    cost = u.current_cost(owned)
                    if save_state["coins"] < cost:
                        continue
                    save_state["coins"] -= cost
                    save_state["upgrades"][u.id] = owned + 1
                    dirty = True
                    save_fn()

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        title = "UPGRADE SHOP"
        tx = max(8, (w - bitmap_text_width(title, scale=4)) // 2)
        draw_bitmap_text(screen, title, tx, 40, (255, 220, 100), scale=4)

        bal = f"COINS: {save_state['coins']}"
        draw_bitmap_text(screen, bal, 24, 100, (255, 255, 255), scale=3)

        y = 150
        for i, u in enumerate(CATALOG):
            owned = int(save_state["upgrades"].get(u.id, 0))
            if i == selection:
                pygame.draw.rect(screen, (60, 60, 120), (10, y - 4, w - 20, 52))
            if owned >= u.max_level:
                cost_s = "MAX"
                row = f"> {u.name}  LVL {owned}/{u.max_level}  {cost_s}"
                col = (140, 200, 140)
            else:
                c = u.current_cost(owned)
                row = f"> {u.name}  LVL {owned}/{u.max_level}  COST {c}"
                col = (
                    (255, 255, 120)
                    if save_state["coins"] >= c
                    else (200, 100, 100)
                )
            draw_bitmap_text(screen, row, 24, y, col, scale=2)
            y += 54

        foot = "UP/DOWN  ENTER BUY   B/ESC CLOSE"
        fw = bitmap_text_width(foot, scale=2)
        draw_bitmap_text(screen, foot, max(8, (w - fw) // 2), h - 44,
                         (200, 200, 200), scale=2)

        present_fn()
        clock.tick(fps)
