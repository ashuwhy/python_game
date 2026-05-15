"""
Mini Mario — pygame platformer with procedural levels & animated Mario.
Arrows / A-D: move · Space / W / Up: jump · Down: pipe · R: restart · Esc: quit
"""

import sys
import math
import random

import pygame

from camera import Camera
from particles import Particle, spawn_dust, spawn_land_puff
from levelgen import generate_level
from mario_sprite import draw_mario, get_anim_state

# ─── constants ───────────────────────────────────────────────
W, H = 960, 540
FPS = 60
GRAVITY = 0.65
JUMP_V = -14
MOVE_SPEED = 7
FRICTION = 0.82
GROUND_H = 48
PLAYER_W, PLAYER_H = 38, 54

# ─── colors ──────────────────────────────────────────────────
SKY = (107, 140, 255)
GROUND_COL = (34, 139, 34)
GROUND_BORDER = (20, 100, 20)
BRICK = (180, 90, 40)
BRICK_DARK = (120, 55, 25)
COIN_GOLD = (255, 215, 0)
FLAG_POLE_COL = (90, 90, 90)

UW_SKY = (18, 10, 30)
UW_GROUND = (50, 30, 60)
UW_GROUND_BORDER = (30, 15, 35)
UW_BRICK = (70, 40, 90)
UW_BRICK_DARK = (45, 20, 55)
UW_COIN_GOLD = (180, 80, 255)

# ─── bitmap font ─────────────────────────────────────────────
_BITMAP = {
    " ": ["...", "...", "...", "...", "..."],
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", "###", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", "..#", "..#", "..#"],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    "A": [".#.", "#.#", "###", "#.#", "#.#"],
    "B": ["##.", "#.#", "##.", "#.#", "###"],
    "C": ["###", "#..", "#..", "#..", "###"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "F": ["###", "#..", "##.", "#..", "#.."],
    "G": ["###", "#..", "#.#", "#.#", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "J": ["..#", "..#", "..#", "#.#", "###"],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#.#", "###", "###", "#.#", "#.#"],
    "N": ["##.", "#.#", "#.#", "#.#", "#.#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"],
    "P": ["###", "#.#", "###", "#..", "#.."],
    "Q": ["###", "#.#", "#.#", "###", ".##"],
    "R": ["###", "#.#", "##.", "#.#", "#.#"],
    "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "V": ["#.#", "#.#", "#.#", ".#.", ".#."],
    "W": ["#.#", "#.#", "#.#", "###", "#.#"],
    "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    "Z": ["###", "..#", ".#.", "#..", "###"],
    "!": [".#.", ".#.", ".#.", "...", ".#."],
    "(": ["..#", ".#.", ".#.", ".#.", "..#"],
    ")": ["#..", ".#.", ".#.", ".#.", "#.."],
    ":": ["...", ".#.", "...", ".#.", "..."],
    "-": ["...", "...", "###", "...", "..."],
    "*": ["...", "#.#", ".#.", "#.#", "..."],
    ".": ["...", "...", "...", "...", ".#."],
}


def draw_bitmap_text(surface, text, x, y, color, scale=3, spacing=1):
    cx = x
    for ch in text:
        g = _BITMAP.get(ch.upper()) or _BITMAP[" "]
        for row, line in enumerate(g):
            for col, pixel in enumerate(line):
                if pixel == "#":
                    pygame.draw.rect(surface, color,
                                     (cx + col * scale, y + row * scale,
                                      scale, scale))
        cx += (len(g[0]) + spacing) * scale


def bitmap_text_width(text, scale=3, spacing=1):
    total = 0
    for ch in text:
        g = _BITMAP.get(ch.upper()) or _BITMAP[" "]
        total += (len(g[0]) + spacing) * scale
    return total


# ─── draw helpers ────────────────────────────────────────────

def draw_brick(surface, rect, dimension, cam):
    sr = cam.screen_rect(rect)
    if sr.right < -10 or sr.left > W + 10:
        return
    if dimension == "overworld":
        col, col_d = BRICK, BRICK_DARK
    else:
        col, col_d = UW_BRICK, UW_BRICK_DARK
    pygame.draw.rect(surface, col, sr)
    pygame.draw.rect(surface, col_d, sr, 2)
    seg = 24
    for cx in range(sr.x + seg, sr.x + sr.w, seg):
        pygame.draw.line(surface, col_d, (cx, sr.y), (cx, sr.y + sr.h), 1)


def draw_ground(surface, rect, dimension, cam):
    sr = cam.screen_rect(rect)
    if sr.right < -10 or sr.left > W + 10:
        return
    if dimension == "overworld":
        col, bord = GROUND_COL, GROUND_BORDER
    else:
        col, bord = UW_GROUND, UW_GROUND_BORDER
    pygame.draw.rect(surface, col, sr)
    pygame.draw.rect(surface, bord, sr, 3)
    # Grass tufts on top
    if dimension == "overworld" and rect.y >= H - 60:
        for gx in range(sr.x, sr.x + sr.w, 18):
            pygame.draw.arc(surface, (50, 180, 50),
                            (gx, sr.y - 4, 14, 8), 0, math.pi, 2)


def draw_coin(surface, pos, t, dimension, cam):
    sx = cam.wx(pos[0])
    if sx < -20 or sx > W + 20:
        return
    phase = (t // 4) % 4
    rx = 10 if phase in (0, 2) else 4
    if dimension == "overworld":
        gold, dark = COIN_GOLD, (200, 170, 0)
    else:
        gold, dark = UW_COIN_GOLD, (120, 50, 180)
    cy = pos[1]
    # Floating bob
    cy += int(math.sin(t * 0.05 + pos[0] * 0.01) * 3)
    pygame.draw.ellipse(surface, gold,
                        pygame.Rect(sx - rx, cy - 12, rx * 2, 24))
    pygame.draw.ellipse(surface, dark,
                        pygame.Rect(sx - rx, cy - 12, rx * 2, 24), 2)
    # Sparkle
    if t % 30 < 5:
        pygame.draw.circle(surface, (255, 255, 255), (sx + 5, cy - 8), 2)


def draw_bg_particles(surface, frame, dimension):
    if dimension == "underworld":
        for i in range(20):
            px = (i * 137 + frame) % W
            py = (i * 97 + frame // 2) % (H - 80)
            alpha = int(60 + 40 * math.sin(frame * 0.03 + i))
            sz = 2 + (i % 3)
            ps = pygame.Surface((sz, sz), pygame.SRCALPHA)
            ps.fill((160, 80, 255, alpha))
            surface.blit(ps, (px, py))
    else:
        for i in range(8):
            px = (i * 193 + frame // 3) % W
            py = 30 + (i * 53) % 120
            alpha = int(40 + 20 * math.sin(frame * 0.02 + i))
            ps = pygame.Surface((12, 6), pygame.SRCALPHA)
            ps.fill((255, 255, 255, alpha))
            surface.blit(ps, (px, py))


def draw_flag(surface, flag_x, cam):
    sx = cam.wx(flag_x)
    if sx < -60 or sx > W + 60:
        return
    flag_y = H - 400
    # Pole
    pygame.draw.rect(surface, FLAG_POLE_COL, (sx, flag_y, 8, H - flag_y - 48))
    # Ball on top
    pygame.draw.circle(surface, (255, 215, 0), (sx + 4, flag_y - 4), 6)
    # Flag
    pygame.draw.polygon(surface, (0, 180, 0), [
        (sx + 8, flag_y + 10),
        (sx + 8, flag_y + 45),
        (sx + 52, flag_y + 27),
    ])
    # Flag border
    pygame.draw.polygon(surface, (0, 120, 0), [
        (sx + 8, flag_y + 10),
        (sx + 8, flag_y + 45),
        (sx + 52, flag_y + 27),
    ], 2)


# ─── transitions ─────────────────────────────────────────────

def play_warp_transition(screen, clock, dimension_entering):
    for i in range(30):
        t = i / 29.0
        if dimension_entering == "underworld":
            r = int(107 * (1 - t) + 18 * t)
            g = int(140 * (1 - t) + 10 * t)
            b = int(255 * (1 - t) + 30 * t)
        else:
            r = int(18 * (1 - t) + 107 * t)
            g = int(10 * (1 - t) + 140 * t)
            b = int(30 * (1 - t) + 255 * t)
        screen.fill((r, g, b))
        radius = int((1 - t) * 400)
        if radius > 0:
            pygame.draw.circle(screen, (0, 0, 0), (W // 2, H // 2), radius + 4)
            pygame.draw.circle(screen, (r, g, b), (W // 2, H // 2), radius)
        msg = ("WARPING..." if dimension_entering == "underworld"
               else "RETURNING...")
        ox = max(8, (W - bitmap_text_width(msg, scale=4)) // 2)
        draw_bitmap_text(screen, msg, ox, H // 2 - 10, (255, 255, 255),
                         scale=4)
        pygame.display.flip()
        clock.tick(30)
    screen.fill((255, 255, 255))
    pygame.display.flip()
    pygame.time.delay(80)


def play_teleport_flash(screen, clock):
    for i in range(10):
        t = i / 9.0
        alpha = int(200 * (1 - t))
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((100, 255, 100, alpha))
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(40)


def play_level_intro(screen, clock, level_num):
    """Show level number before starting."""
    for i in range(60):
        t = i / 59.0
        screen.fill((0, 0, 0))
        msg = f"LEVEL {level_num}"
        ox = max(8, (W - bitmap_text_width(msg, scale=5)) // 2)
        alpha_t = min(t * 3, 1.0) if t < 0.5 else max(0.0, 1.0 - (t - 0.7) * 4)
        v = max(0, min(255, int(255 * alpha_t)))
        col = (v, v, v)
        draw_bitmap_text(screen, msg, ox, H // 2 - 20, col, scale=5)
        sub = "GET READY!"
        sox = max(8, (W - bitmap_text_width(sub, scale=3)) // 2)
        draw_bitmap_text(screen, sub, sox, H // 2 + 30, col, scale=3)
        pygame.display.flip()
        clock.tick(30)


# ─── main ────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Mini Mario — Procedural Levels")
    clock = pygame.time.Clock()

    cam = Camera()
    particles = []
    level_num = 1
    dimension = "overworld"

    def new_level():
        nonlocal blocks, coins, pipes, flag_x, world_w
        blocks, coins, pipes, flag_x, world_w = generate_level(
            dimension, level_num)
        # Also pre-generate underworld coins
        _, uw_coins, _, _, _ = generate_level("underworld", level_num)
        coins.extend(uw_coins)

    blocks, coins, pipes, flag_x, world_w = [], [], [], 0, W
    new_level()

    player = pygame.Rect(80, H - 200, PLAYER_W, PLAYER_H)
    vel_x, vel_y = 0.0, 0.0
    on_ground = False
    was_on_ground = False
    facing_right = True
    score = 0
    won = False
    frame = 0
    warp_cooldown = 0
    death_timer = 0
    anim_state = "idle"

    play_level_intro(screen, clock, level_num)

    while True:
        frame += 1
        if warp_cooldown > 0:
            warp_cooldown -= 1

        # ---- events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)
                if event.key == pygame.K_r:
                    level_num = 1
                    dimension = "overworld"
                    new_level()
                    player.topleft = (80, H - 200)
                    vel_x = vel_y = 0
                    score = 0
                    won = False
                    death_timer = 0
                    warp_cooldown = 0
                    cam.x = 0
                    particles.clear()
                    play_level_intro(screen, clock, level_num)

        # ---- death (fell off screen) ----
        if player.top > H + 50:
            death_timer += 1
            if death_timer > 30:
                player.topleft = (80, H - 200)
                vel_x = vel_y = 0
                cam.x = 0
                death_timer = 0
                warp_cooldown = 0
                particles.clear()
            # Still draw the death fade
            screen.fill((0, 0, 0))
            msg = "OOPS!"
            ox = max(8, (W - bitmap_text_width(msg, scale=4)) // 2)
            draw_bitmap_text(screen, msg, ox, H // 2 - 10, (255, 80, 80),
                             scale=4)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        # ---- win: advance level ----
        if won:
            won = False
            level_num += 1
            dimension = "overworld"
            new_level()
            player.topleft = (80, H - 200)
            vel_x = vel_y = 0
            cam.x = 0
            particles.clear()
            play_level_intro(screen, clock, level_num)
            continue

        # ---- input ----
        keys = pygame.key.get_pressed()
        ax = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= 1
            facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += 1
            facing_right = True

        # Detect skidding (moving one way, pressing the other)
        skidding = (on_ground and
                    ((vel_x > 2 and ax < 0) or (vel_x < -2 and ax > 0)))

        vel_x += ax * 0.9
        vel_x *= FRICTION
        if abs(vel_x) < 0.05:
            vel_x = 0
        vel_x = max(-MOVE_SPEED, min(MOVE_SPEED, vel_x))

        jump_pressed = (keys[pygame.K_SPACE] or keys[pygame.K_w]
                        or keys[pygame.K_UP])
        if jump_pressed and on_ground:
            vel_y = JUMP_V
            on_ground = False
            spawn_dust(particles, player.centerx, player.bottom,
                       count=5, color=(180, 160, 130))

        vel_y += GRAVITY

        # ---- horizontal collision ----
        player.x += int(vel_x)
        for b in blocks:
            if player.colliderect(b):
                if vel_x > 0:
                    player.right = b.left
                elif vel_x < 0:
                    player.left = b.right
                vel_x = 0

        # ---- vertical collision ----
        was_on_ground = on_ground
        player.y += int(vel_y)
        on_ground = False
        for b in blocks:
            if player.colliderect(b):
                if vel_y > 0:
                    player.bottom = b.top
                    if not was_on_ground and vel_y > 4:
                        spawn_land_puff(particles, player.centerx,
                                        player.bottom, count=8)
                    vel_y = 0
                    on_ground = True
                elif vel_y < 0:
                    player.top = b.bottom
                    vel_y = 0

        # ---- walking dust ----
        if on_ground and abs(vel_x) > 3 and frame % 8 == 0:
            spawn_dust(particles, player.centerx, player.bottom,
                       count=2, color=(160, 140, 110))

        # ---- animation state ----
        anim_state = get_anim_state(vel_x, vel_y, on_ground, skidding)

        # ---- pipe warp ----
        down_pressed = keys[pygame.K_DOWN] or keys[pygame.K_s]
        if down_pressed and on_ground and warp_cooldown == 0:
            for pipe in pipes:
                if pipe.dimension != dimension:
                    continue
                if player.colliderect(pipe.entry_zone):
                    if pipe.kind == "teleport":
                        partners = [p for p in pipes
                                    if p.pair_id == pipe.pair_id
                                    and p is not pipe
                                    and p.dimension == dimension]
                        if partners:
                            dest = partners[0]
                            play_teleport_flash(screen, clock)
                            player.midbottom = (
                                dest.x + dest.PIPE_W // 2, dest.y)
                            vel_x = vel_y = 0
                            warp_cooldown = 40
                            break
                    elif pipe.kind == "dimension":
                        new_dim = ("underworld" if dimension == "overworld"
                                   else "overworld")
                        play_warp_transition(screen, clock, new_dim)
                        dimension = new_dim
                        # Regenerate level for new dimension
                        blocks_new, coins_new, pipes_new, fx, ww = \
                            generate_level(new_dim, level_num)
                        blocks = blocks_new
                        # Merge coins (keep taken status for current dim)
                        old_coins = [c for c in coins if c["dim"] != new_dim]
                        coins = old_coins + coins_new
                        pipes = pipes_new
                        # Also need pipes from the original dimension for
                        # when we come back, but generate_level handles that
                        world_w = ww
                        flag_x = fx
                        dim_pipes = [p for p in pipes
                                     if p.dimension == new_dim
                                     and p.kind == "dimension"]
                        if dim_pipes:
                            dest = dim_pipes[0]
                            player.midbottom = (
                                dest.x + dest.PIPE_W // 2, dest.y)
                        else:
                            player.topleft = (80, H - 200)
                        vel_x = vel_y = 0
                        warp_cooldown = 40
                        cam.x = max(0, player.centerx - W // 3)
                        break

        # ---- coins ----
        for c in coins:
            if c["taken"] or c["dim"] != dimension:
                continue
            cx, cy = c["pos"]
            coin_rect = pygame.Rect(cx - 12, cy - 12, 24, 24)
            if player.colliderect(coin_rect):
                c["taken"] = True
                score += 100
                # Coin collect sparkle
                for _ in range(6):
                    particles.append(Particle(
                        cx, cy,
                        random.uniform(-3, 3), random.uniform(-4, -1),
                        (255, 215, 0), random.randint(10, 20)))

        # ---- flag ----
        if dimension == "overworld":
            pole_rect = pygame.Rect(flag_x, H - 400, 16, H - (H - 400) - 48)
            if player.colliderect(pole_rect):
                won = True

        # ---- keep in bounds ----
        if player.left < 0:
            player.left = 0
        if player.right > world_w:
            player.right = world_w

        # ---- camera ----
        cam.update(player, world_w)

        # ---- update particles ----
        particles[:] = [p for p in particles if p.update()]

        # ============= DRAW =============
        sky = SKY if dimension == "overworld" else UW_SKY
        screen.fill(sky)

        draw_bg_particles(screen, frame, dimension)

        # blocks
        for b in blocks:
            if not cam.visible(b):
                continue
            is_ground = b.y >= H - 60
            is_ceiling = b.y <= 1
            if is_ground or is_ceiling:
                draw_ground(screen, b, dimension, cam)
            else:
                draw_brick(screen, b, dimension, cam)

        # pipes
        for pipe in pipes:
            if pipe.dimension == dimension:
                pipe.draw(screen, frame, cam.x)

        # flag
        if dimension == "overworld":
            draw_flag(screen, flag_x, cam)

        # coins
        for c in coins:
            if not c["taken"] and c["dim"] == dimension:
                draw_coin(screen, c["pos"], frame, dimension, cam)

        # mario (drawn in screen coords)
        mario_screen = cam.screen_rect(player)
        draw_mario(screen, mario_screen, facing_right, anim_state, frame)

        # particles
        for p in particles:
            p.draw(screen, cam.x)

        # ---- HUD ----
        # Semi-transparent HUD background
        hud_bg = pygame.Surface((W, 36), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 80))
        screen.blit(hud_bg, (0, 0))

        draw_bitmap_text(screen, f"COINS: {score}", 16, 12,
                         (255, 255, 255), scale=3)

        lvl_text = f"LEVEL {level_num}"
        lw = bitmap_text_width(lvl_text, scale=3)
        draw_bitmap_text(screen, lvl_text, W // 2 - lw // 2, 12,
                         (255, 255, 100), scale=3)

        dim_label = "OVERWORLD" if dimension == "overworld" else "UNDERWORLD"
        dim_color = ((200, 220, 255) if dimension == "overworld"
                     else (180, 120, 255))
        dim_w = bitmap_text_width(dim_label, scale=2)
        draw_bitmap_text(screen, dim_label, W - dim_w - 16, 14,
                         dim_color, scale=2)

        # Controls hint at bottom
        hint_bg = pygame.Surface((W, 28), pygame.SRCALPHA)
        hint_bg.fill((0, 0, 0, 60))
        screen.blit(hint_bg, (0, H - 28))
        draw_bitmap_text(
            screen,
            "ARROWS MOVE * SPACE JUMP * DOWN PIPE * R RESTART",
            16, H - 24, (200, 200, 200), scale=2)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
