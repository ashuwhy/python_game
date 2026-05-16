import math
import pygame
import os

_mario_frames = None

def _load_mario_frames():
    global _mario_frames
    if _mario_frames is not None:
        return

    sheet_path = os.path.join(os.path.dirname(__file__), "mario_bros.bmp")
    try:
        sheet = pygame.image.load(sheet_path).convert()
    except pygame.error:
        # Fallback if image is missing
        sheet = pygame.Surface((400, 400))
        sheet.fill((255, 0, 255))
        
    def get_image(x, y, w, h):
        image = pygame.Surface((w, h))
        image.blit(sheet, (0, 0), (x, y, w, h))
        image.set_colorkey((255, 0, 255))
        return image

    right_frames = {
        "idle": get_image(178, 32, 12, 16),
        "walk1": get_image(80, 32, 15, 16),
        "walk2": get_image(96, 32, 16, 16),
        "walk3": get_image(112, 32, 16, 16),
        "jump": get_image(144, 32, 16, 16),
        "skid": get_image(130, 32, 14, 16),
    }

    _mario_frames = {"right": right_frames, "left": {}}
    for k, v in right_frames.items():
        _mario_frames["left"][k] = pygame.transform.flip(v, True, False)


def get_anim_state(vel_x, vel_y, on_ground, skid):
    if not on_ground:
        return "jump" if vel_y < 0 else "fall"
    if skid:
        return "skid"
    if abs(vel_x) > 1.0:
        return "walk"
    return "idle"


def draw_mario(surface, player, facing_right, state, frame):
    """Draw a real animated Mario at player rect position."""
    if _mario_frames is None:
        _load_mario_frames()

    direction = "right" if facing_right else "left"
    frames = _mario_frames[direction]

    if state == "idle":
        img = frames["idle"]
    elif state == "walk":
        walk_cycle = (frame // 4) % 3
        if walk_cycle == 0:
            img = frames["walk1"]
        elif walk_cycle == 1:
            img = frames["walk2"]
        else:
            img = frames["walk3"]
    elif state in ("jump", "fall"):
        img = frames["jump"]
    elif state == "skid":
        img = frames["skid"]
    else:
        img = frames["idle"]

    # Original sprite is 16px high
    scale = player.h / 16.0
    scaled_w = int(img.get_width() * scale)
    scaled_h = int(img.get_height() * scale)
    
    # Scale image (using scale function which keeps colorkey transparency)
    scaled_img = pygame.transform.scale(img, (scaled_w, scaled_h))

    # Center horizontally, align to bottom
    x = player.centerx - scaled_w // 2
    y = player.bottom - scaled_h

    surface.blit(scaled_img, (x, y))
