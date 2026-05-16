import pygame
import random

_textures = None

def create_gradient_surface(w, h, color1, color2, vertical=True):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    r1, g1, b1 = color1[:3]
    r2, g2, b2 = color2[:3]
    if vertical:
        for y in range(h):
            t = y / max(1, h - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))
    else:
        for x in range(w):
            t = x / max(1, w - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            pygame.draw.line(surf, (r, g, b), (x, 0), (x, h))
    return surf

def gen_grass_block(w=32, h=32):
    surf = pygame.Surface((w, h))
    # Dirt base
    surf.fill((100, 60, 25))
    random.seed(42) # fixed seed for consistency
    for _ in range(15):
        x, y = random.randint(0, w-1), random.randint(8, h-1)
        c = random.choice([(70, 40, 15), (130, 80, 40)])
        surf.set_at((x, y), c)
    # Grass top
    pygame.draw.rect(surf, (40, 180, 40), (0, 0, w, 10))
    pygame.draw.rect(surf, (100, 240, 80), (0, 0, w, 2))
    pygame.draw.rect(surf, (20, 120, 20), (0, 8, w, 2))
    return surf

def gen_uw_ground(w=32, h=32):
    surf = pygame.Surface((w, h))
    surf.fill((45, 25, 55))
    random.seed(43)
    for _ in range(15):
        x, y = random.randint(0, w-1), random.randint(8, h-1)
        c = random.choice([(30, 15, 40), (60, 35, 75)])
        surf.set_at((x, y), c)
    pygame.draw.rect(surf, (80, 40, 100), (0, 0, w, 10))
    pygame.draw.rect(surf, (120, 70, 150), (0, 0, w, 2))
    pygame.draw.rect(surf, (50, 20, 70), (0, 8, w, 2))
    return surf

def gen_brick_block(w=32, h=32, is_uw=False):
    surf = pygame.Surface((w, h))
    mortar = (30, 15, 15) if not is_uw else (20, 10, 30)
    surf.fill(mortar)
    
    base_col = (180, 50, 30) if not is_uw else (80, 40, 100)
    light_col = (240, 100, 80) if not is_uw else (130, 70, 160)
    dark_col = (100, 20, 10) if not is_uw else (40, 15, 60)
    
    # Draw two rows of bricks
    bricks = [
        (1, 1, w-2, h//2-2),
        (1, h//2+1, w//2-2, h//2-2),
        (w//2+1, h//2+1, w//2-2, h//2-2)
    ]
    for bx, by, bw, bh in bricks:
        pygame.draw.rect(surf, base_col, (bx, by, bw, bh))
        pygame.draw.line(surf, light_col, (bx, by), (bx+bw-1, by))
        pygame.draw.line(surf, light_col, (bx, by), (bx, by+bh-1))
        pygame.draw.line(surf, dark_col, (bx, by+bh-1), (bx+bw-1, by+bh-1))
        pygame.draw.line(surf, dark_col, (bx+bw-1, by), (bx+bw-1, by+bh-1))
    return surf

def gen_coin(phase=0):
    surf = pygame.Surface((24, 32), pygame.SRCALPHA)
    w = 20 if phase in (0, 2) else 8
    x = (24 - w) // 2
    
    pygame.draw.ellipse(surf, (200, 140, 0), (x, 2, w, 28))
    pygame.draw.ellipse(surf, (255, 210, 0), (x+1, 3, w-2, 26))
    if w > 10:
        pygame.draw.ellipse(surf, (255, 255, 100), (x+4, 6, w-8, 20))
    return surf

def gen_flag_pole(w=16, h=32):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (150, 150, 160), (4, 0, 8, h))
    pygame.draw.line(surf, (220, 220, 230), (5, 0), (5, h))
    pygame.draw.line(surf, (80, 80, 90), (10, 0), (10, h))
    return surf

def gen_flag_top(w=32, h=32):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.circle(surf, (200, 180, 40), (w//2, h//2), 12)
    pygame.draw.circle(surf, (255, 255, 100), (w//2 - 3, h//2 - 3), 4)
    pygame.draw.circle(surf, (0, 0, 0), (w//2, h//2), 12, 2)
    return surf

def gen_flag(w=48, h=32):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (40, 200, 50), [(0, 0), (0, h), (w, h//2)])
    pygame.draw.polygon(surf, (20, 100, 30), [(0, 0), (0, h), (w, h//2)], 2)
    return surf

def _load_textures():
    global _textures
    _textures = {
        "overworld_ground": gen_grass_block(),
        "underworld_ground": gen_uw_ground(),
        "overworld_brick": gen_brick_block(is_uw=False),
        "underworld_brick": gen_brick_block(is_uw=True),
        "coin_1": gen_coin(0),
        "coin_2": gen_coin(1),
        "coin_3": gen_coin(2),
        "flag_pole": gen_flag_pole(),
        "flag_top": gen_flag_top(),
        "flag": gen_flag(),
    }

def get_texture(name):
    if _textures is None:
        _load_textures()
    return _textures.get(name)

def draw_tiled(surface, img, rect):
    if img is None:
        return
    iw, ih = img.get_size()
    surface.set_clip(rect)
    for y in range(rect.y, rect.bottom, ih):
        for x in range(rect.x, rect.right, iw):
            surface.blit(img, (x, y))
    surface.set_clip(None)

def draw_gradient_pipe(surface, rect, is_dim, is_lip):
    base_color1 = (20, 100, 30) if not is_dim else (60, 20, 90)
    base_color2 = (60, 220, 90) if not is_dim else (140, 70, 220)
    base_color3 = (10, 60, 15) if not is_dim else (30, 10, 50)
    
    # Create horizontal gradient cylinder
    # Dark edges, bright center
    w, h = rect.w, rect.h
    for x in range(w):
        t = x / max(1, w - 1)
        if t < 0.5:
            # 0 to 0.5: color1 -> color2
            f = t * 2
            r = int(base_color1[0] + (base_color2[0] - base_color1[0]) * f)
            g = int(base_color1[1] + (base_color2[1] - base_color1[1]) * f)
            b = int(base_color1[2] + (base_color2[2] - base_color1[2]) * f)
        else:
            # 0.5 to 1.0: color2 -> color3
            f = (t - 0.5) * 2
            r = int(base_color2[0] + (base_color3[0] - base_color2[0]) * f)
            g = int(base_color2[1] + (base_color3[1] - base_color2[1]) * f)
            b = int(base_color2[2] + (base_color3[2] - base_color2[2]) * f)
        
        pygame.draw.line(surface, (r, g, b), (rect.x + x, rect.y), (rect.x + x, rect.bottom - 1))
        
    if is_lip:
        pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=4)
        # bright rim
        pygame.draw.line(surface, (200, 255, 200) if not is_dim else (220, 180, 255), 
                         (rect.x + 4, rect.y + 2), (rect.x + w - 4, rect.y + 2))
    else:
        pygame.draw.rect(surface, (0, 0, 0), rect, 2)
