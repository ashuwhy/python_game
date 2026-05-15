"""Detailed animated Mario drawing — no sprite sheets, just pygame.draw."""
import math
import pygame

# Colors
MARIO_RED = (220, 40, 40)
MARIO_RED_DARK = (180, 30, 30)
MARIO_BLUE = (30, 60, 200)
MARIO_BLUE_DARK = (20, 40, 150)
SKIN = (255, 200, 150)
SKIN_DARK = (220, 170, 120)
SHOE_BROWN = (139, 69, 19)
SHOE_HIGHLIGHT = (170, 100, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MUSTACHE = (80, 40, 10)
BUTTON_YELLOW = (255, 220, 50)


def get_anim_state(vel_x, vel_y, on_ground, skid):
    if not on_ground:
        return "jump" if vel_y < 0 else "fall"
    if skid:
        return "skid"
    if abs(vel_x) > 1.0:
        return "walk"
    return "idle"


def draw_mario(surface, player, facing_right, state, frame):
    """Draw a detailed animated Mario at player rect position."""
    x, y = player.x, player.y
    w, h = player.w, player.h
    d = 1 if facing_right else -1
    cx = x + w // 2

    # --- smooth animation offsets (small and subtle) ---
    bob = 0
    walk_t = 0.0  # smooth 0-1 walk cycle

    if state == "idle":
        bob = round(math.sin(frame * 0.04) * 1.0)  # very gentle
    elif state == "walk":
        walk_t = (frame % 24) / 24.0  # one full cycle every 24 frames
    elif state == "jump":
        bob = -1
    elif state == "fall":
        bob = 1

    ay = y + bob

    # Smooth leg offset using sin wave instead of jerky phases
    leg_off = int(math.sin(walk_t * math.pi * 2) * 3) if state == "walk" else 0
    arm_off = int(math.sin(walk_t * math.pi * 2) * 2) if state == "walk" else 0

    # ===== SHOES =====
    sw, sh = 10, 6
    shoe_y = ay + h - sh

    if state == "jump":
        # Feet together, tucked
        lsx = cx - 7
        rsx = cx - 1
    elif state == "fall":
        lsx = cx - 9
        rsx = cx + 1
    else:
        lsx = cx - 10 + leg_off
        rsx = cx + 1 - leg_off

    pygame.draw.rect(surface, SHOE_BROWN, (lsx, shoe_y, sw, sh),
                     border_radius=2)
    pygame.draw.rect(surface, SHOE_BROWN, (rsx, shoe_y, sw, sh),
                     border_radius=2)
    pygame.draw.rect(surface, SHOE_HIGHLIGHT, (lsx + 2, shoe_y + 1, 4, 2))
    pygame.draw.rect(surface, SHOE_HIGHLIGHT, (rsx + 2, shoe_y + 1, 4, 2))

    # ===== LEGS =====
    lw, lh = 7, 12
    leg_y = shoe_y - lh + 3

    if state == "jump":
        llx = cx - 6
        rlx = cx
    else:
        llx = lsx + 1
        rlx = rsx + 1

    pygame.draw.rect(surface, MARIO_BLUE, (llx, leg_y, lw, lh))
    pygame.draw.rect(surface, MARIO_BLUE, (rlx, leg_y, lw, lh))

    # ===== BODY / OVERALLS =====
    body_top = ay + 18
    body_h = 16

    # Red shirt (visible at shoulders)
    pygame.draw.rect(surface, MARIO_RED,
                     (cx - 12, body_top - 2, 24, 8), border_radius=3)

    # Blue overalls
    overall_r = pygame.Rect(cx - 11, body_top + 3, 22, body_h)
    pygame.draw.rect(surface, MARIO_BLUE, overall_r, border_radius=2)
    pygame.draw.rect(surface, MARIO_BLUE_DARK, overall_r, 1, border_radius=2)

    # Straps
    pygame.draw.line(surface, MARIO_BLUE_DARK,
                     (cx - 5, body_top + 3), (cx - 5, body_top), 2)
    pygame.draw.line(surface, MARIO_BLUE_DARK,
                     (cx + 5, body_top + 3), (cx + 5, body_top), 2)

    # Buttons
    pygame.draw.circle(surface, BUTTON_YELLOW, (cx - 5, body_top + 5), 2)
    pygame.draw.circle(surface, BUTTON_YELLOW, (cx + 5, body_top + 5), 2)

    # ===== ARMS =====
    arm_y = body_top + 1
    if state == "jump":
        # Arms raised
        pygame.draw.rect(surface, SKIN,
                         (cx - 16, ay + 10, 6, 8), border_radius=2)
        pygame.draw.rect(surface, SKIN,
                         (cx + 10, ay + 10, 6, 8), border_radius=2)
    elif state == "fall":
        # Arms spread
        pygame.draw.rect(surface, SKIN,
                         (cx - 17, arm_y + 4, 7, 5), border_radius=2)
        pygame.draw.rect(surface, SKIN,
                         (cx + 10, arm_y + 4, 7, 5), border_radius=2)
    else:
        # Arms at sides with subtle swing
        pygame.draw.rect(surface, SKIN,
                         (cx - 15, arm_y + arm_off, 5, 11), border_radius=2)
        pygame.draw.rect(surface, SKIN,
                         (cx + 10, arm_y - arm_off, 5, 11), border_radius=2)

    # Sleeves
    pygame.draw.rect(surface, MARIO_RED, (cx - 14, arm_y, 4, 4),
                     border_radius=1)
    pygame.draw.rect(surface, MARIO_RED, (cx + 10, arm_y, 4, 4),
                     border_radius=1)

    # ===== HEAD =====
    head_cx = cx + d * 2
    head_cy = ay + 14
    head_r = 11
    pygame.draw.circle(surface, SKIN, (head_cx, head_cy), head_r)
    pygame.draw.circle(surface, SKIN_DARK, (head_cx, head_cy), head_r, 1)

    # Ear
    pygame.draw.circle(surface, SKIN, (head_cx - d * 9, head_cy), 3)

    # ===== EYE =====
    eye_x = head_cx + d * 4
    pygame.draw.circle(surface, WHITE, (eye_x, head_cy - 2), 3)
    # Blink every ~3 seconds
    blink = (frame % 180) < 5
    if not blink:
        pygame.draw.circle(surface, BLACK, (eye_x + d, head_cy - 2), 1)
    else:
        pygame.draw.line(surface, BLACK,
                         (eye_x - 2, head_cy - 2),
                         (eye_x + 2, head_cy - 2), 1)

    # ===== NOSE =====
    nose_x = head_cx + d * 7
    pygame.draw.circle(surface, SKIN_DARK, (nose_x, head_cy + 1), 3)

    # ===== MUSTACHE =====
    pygame.draw.ellipse(surface, MUSTACHE,
                        (head_cx + d * 1 - 4, head_cy + 4, 10, 4))

    # ===== CAP =====
    cap_y = ay + 1
    # Main cap dome
    pygame.draw.rect(surface, MARIO_RED,
                     (cx - 13, cap_y, 26, 10), border_radius=5)
    pygame.draw.rect(surface, MARIO_RED_DARK,
                     (cx - 13, cap_y, 26, 10), 1, border_radius=5)

    # Brim
    brim_x = cx + d * 5
    pygame.draw.rect(surface, MARIO_RED,
                     (brim_x - 8, cap_y + 7, 16, 4), border_radius=2)

    # "M" emblem
    em_x = cx + d * 1
    em_y = cap_y + 4
    pygame.draw.circle(surface, WHITE, (em_x, em_y), 3)
    # Tiny M lines
    pygame.draw.lines(surface, MARIO_RED, False, [
        (em_x - 2, em_y + 1), (em_x - 2, em_y - 1),
        (em_x, em_y), (em_x + 2, em_y - 1), (em_x + 2, em_y + 1)], 1)

    # ===== SKID LINES =====
    if state == "skid":
        for i in range(3):
            lx = cx - d * (18 + i * 6)
            ly = ay + 22 + i * 7
            pygame.draw.line(surface, (255, 255, 200),
                             (lx, ly), (lx - d * 10, ly), 1)
