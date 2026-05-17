
# pyrefly: ignore [missing-import]
import pygame
import sys
import random
import math

# ── Initialize ──────────────────────────────────────────────────
pygame.init()

INTERNAL_W, INTERNAL_H = 960, 540
FULLSCREEN = False
info = pygame.display.Info()
MONITOR_W, MONITOR_H = info.current_w, info.current_h

def create_display(fullscreen):
    if fullscreen:
        return pygame.display.set_mode((MONITOR_W, MONITOR_H), pygame.FULLSCREEN)
    else:
        return pygame.display.set_mode((INTERNAL_W, INTERNAL_H), pygame.RESIZABLE)

screen = create_display(FULLSCREEN)
pygame.display.set_caption("VOLT")
clock = pygame.time.Clock()
FPS = 60

game_surface = pygame.Surface((INTERNAL_W, INTERNAL_H))
W, H = INTERNAL_W, INTERNAL_H

# ── Color Palette ───────────────────────────────────────────────
BLACK       = (0, 0, 0)
SKY_TOP     = (18, 6, 8)
SKY_BOT     = (45, 15, 10)
BLD_FAR     = (25, 12, 12)
BLD_MID     = (20, 8, 8)
BLD_NEAR    = (12, 4, 4)
PLAT_FILL   = (22, 14, 18)
PLAT_EDGE   = (55, 30, 35)
PLAT_BOTTOM = (10, 5, 5)

# Darker Robot Colors
ROBO        = (32, 36, 50)
ROBO_DARK   = (20, 22, 35)
ROBO_HI     = (50, 56, 72)

EYE_COL     = (0, 210, 255)
EYE_GLOW_C  = (0, 70, 110)
SOLAR_COL   = (255, 255, 170)
DUST_COL    = (55, 50, 45)
SPARK_COL   = (0, 190, 235)
FOG_COL     = (22, 10, 6)
RAIN_COL    = (255, 120, 40)
WIN_DIM     = (60, 20, 0)
WIN_BRIGHT  = (255, 80, 0)

_particle_cache = {}

def _get_circle_surf(radius, color_rgba):
    key = (radius, color_rgba)
    if key not in _particle_cache:
        sz = radius * 2 + 2
        s = pygame.Surface((sz, sz), pygame.SRCALPHA)
        pygame.draw.circle(s, color_rgba, (radius + 1, radius + 1), radius)
        _particle_cache[key] = s
    return _particle_cache[key]

# ── Particles ───────────────────────────────────────────────────
class Particle:
    __slots__ = ('x','y','vx','vy','life','max_life','size','alpha','kind','color')
    def __init__(self, x, y, kind="dust"):
        self.x = x
        self.y = y
        self.kind = kind
        if kind == "dust":
            self.vx = random.uniform(-0.4, 0.4)
            self.vy = random.uniform(-0.9, -0.2)
            self.life = random.randint(35, 80)
            self.size = random.randint(2, 4)
            self.alpha = random.randint(25, 60)
            self.color = DUST_COL
        elif kind == "spark":
            a = random.uniform(0, math.pi * 2)
            sp = random.uniform(1.5, 4.5)
            self.vx = math.cos(a) * sp
            self.vy = math.sin(a) * sp - 2.5
            self.life = random.randint(12, 30)
            self.size = random.randint(1, 3)
            self.alpha = 255
            self.color = SPARK_COL
        elif kind == "ember":
            self.vx = random.uniform(-0.12, 0.12)
            self.vy = random.uniform(-1.0, -0.25)
            self.life = random.randint(70, 180)
            self.size = random.randint(1, 2)
            self.alpha = random.randint(50, 130)
            self.color = random.choice([(255,110,25),(255,70,8),(190,55,0)])
        elif kind == "rain":
            self.vx = random.uniform(-0.5, -0.2)
            self.vy = random.uniform(5, 9)
            self.life = random.randint(30, 60)
            self.size = 1
            self.alpha = random.randint(20, 50)
            self.color = RAIN_COL
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        t = self.life / self.max_life
        if self.kind == "dust":
            self.alpha = max(0, int(60 * t))
        elif self.kind == "spark":
            self.vy += 0.18
            self.alpha = max(0, int(255 * t))
        elif self.kind == "ember":
            self.vx += random.uniform(-0.02, 0.02)
            self.alpha = max(0, int(130 * t))
        elif self.kind == "rain":
            self.alpha = max(0, int(50 * t))
        return self.life > 0

    def draw(self, surface, ox=0):
        if self.alpha <= 0 or self.size <= 0:
            return
        rx = int(self.x - ox)
        if self.kind == "rain":
            end_y = int(self.y + self.vy * 0.5)
            line_col = (*self.color, self.alpha)
            rain_s = pygame.Surface((4, abs(end_y - int(self.y)) + 2), pygame.SRCALPHA)
            pygame.draw.line(rain_s, line_col, (2, 0), (2, abs(end_y - int(self.y))), 1)
            surface.blit(rain_s, (rx, int(self.y)))
        else:
            col = (*self.color, min(255, self.alpha))
            surf = _get_circle_surf(self.size, col)
            surface.blit(surf, (rx - self.size, int(self.y) - self.size))

# ── New Game Objects ────────────────────────────────────────────

class Switch:
    def __init__(self, x, y, w, h, switch_id, timed, stype):
        self.rect = pygame.Rect(x, y, w, h)
        self.switch_id = switch_id
        self.timed = timed
        self.active = False
        self.timer = 0
        self.type = stype # "button" or "plate"

    def update(self, player, boxes):
        is_pressed = False
        if self.rect.colliderect(player.rect):
            is_pressed = True
        for b in boxes:
            if self.rect.colliderect(b.rect):
                is_pressed = True
                
        if is_pressed:
            self.active = True
            if self.timed > 0:
                self.timer = self.timed
        else:
            if self.timer > 0:
                self.timer -= 1
                if self.timer <= 0:
                    self.active = False
            else:
                self.active = False

    def draw(self, surface):
        color = (0, 220, 255) if self.type == "button" else (255, 160, 30)
        dim = tuple(c // 3 for c in color)
        # Base
        base_h = 6 if self.active else 12
        base_y = self.rect.bottom - base_h
        pygame.draw.rect(surface, dim, (self.rect.x - 2, base_y, self.rect.w + 4, base_h))
        # Lit top
        top_col = color if self.active else dim
        pygame.draw.rect(surface, top_col, (self.rect.x, base_y, self.rect.w, 3))
        # Glow when active
        if self.active:
            gs = pygame.Surface((self.rect.w + 20, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(gs, (*color, 60), gs.get_rect())
            surface.blit(gs, (self.rect.x - 10, base_y - 8))
        # Timer bar
        if self.timed > 0 and self.active and self.timer > 0:
            ratio = self.timer / self.timed
            bar_w = int(self.rect.w * ratio)
            pygame.draw.rect(surface, (255, 255, 80), (self.rect.x, base_y - 6, bar_w, 3))

class Gate:
    def __init__(self, x, y, w, h, switch_id, inverted=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.switch_id = switch_id
        self.is_open = False
        self.inverted = inverted

    def update(self, switches):
        for s in switches:
            if s.switch_id == self.switch_id:
                self.is_open = not s.active if self.inverted else s.active

    def draw(self, surface, frame=0):
        if not self.is_open:
            # Dark border
            pygame.draw.rect(surface, (80, 15, 15), self.rect)
            # Animated energy lines
            for i in range(0, self.rect.h, 8):
                a = int(120 + 80 * math.sin((i + frame * 3) * 0.15))
                line_col = (min(255, a + 80), 40, 40)
                pygame.draw.line(surface, line_col, (self.rect.x + 1, self.rect.y + i), (self.rect.right - 1, self.rect.y + i), 2)
            # Side glow
            glow = pygame.Surface((self.rect.w + 12, self.rect.h + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 50, 50, 25), glow.get_rect(), border_radius=4)
            surface.blit(glow, (self.rect.x - 6, self.rect.y - 4))

class ExitPortal:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y - 60, 40, 60)
        self.frame = 0

    def draw(self, surface):
        self.frame += 1
        # Outer glow
        pulse = (math.sin(self.frame * 0.08) + 1) / 2
        glow_s = pygame.Surface((self.rect.w + 30, self.rect.h + 30), pygame.SRCALPHA)
        glow_a = int(30 + 40 * pulse)
        pygame.draw.ellipse(glow_s, (40, 255, 120, glow_a), glow_s.get_rect())
        surface.blit(glow_s, (self.rect.x - 15, self.rect.y - 15))
        # Inner fill
        inner_a = int(60 + 60 * pulse)
        inner = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        inner.fill((40, 255, 100, inner_a))
        surface.blit(inner, self.rect)
        # Border
        pygame.draw.rect(surface, (80, 255, 140), self.rect, 2)
        # Arrow hint
        cx = self.rect.centerx
        ay = self.rect.y + 10 + int(4 * math.sin(self.frame * 0.12))
        pygame.draw.polygon(surface, (200, 255, 220), [(cx, ay), (cx - 8, ay + 12), (cx + 8, ay + 12)])

class Box:
    def __init__(self, x, y):
        self.w = 30
        self.h = 30
        self.x = float(x)
        self.y = float(y - self.h)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def draw(self, surface):
        pygame.draw.rect(surface, (50, 50, 60), self.rect)
        pygame.draw.rect(surface, (90, 90, 100), self.rect, 2)
        pygame.draw.line(surface, (90, 90, 100), (self.rect.left, self.rect.top), (self.rect.right, self.rect.bottom), 2)
        pygame.draw.line(surface, (90, 90, 100), (self.rect.right, self.rect.top), (self.rect.left, self.rect.bottom), 2)

    def update(self, platforms, gates):
        self.vy += 0.48
        self.y += self.vy
        self.on_ground = False
        
        r = self.rect
        for p in platforms:
            if r.colliderect(p.rect):
                if self.vy > 0:
                    r.bottom = p.rect.top
                    self.y = float(r.y)
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    r.top = p.rect.bottom
                    self.y = float(r.y)
                    self.vy = 0
        for g in gates:
            if not g.is_open and r.colliderect(g.rect):
                if self.vy > 0:
                    r.bottom = g.rect.top
                    self.y = float(r.y)
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    r.top = g.rect.bottom
                    self.y = float(r.y)
                    self.vy = 0


# ── Robot ───────────────────────────────────────────────────────
class Robot:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.w = 24
        self.h = 36
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 3.8
        self.jump_power = -9.5
        self.gravity = 0.48
        self.on_ground = False
        self.facing_right = True
        self.awake = False
        self.eye_brightness = 0.0
        self.walk_timer = 0.0
        self.head_bob = 0.0
        self.idle_timer = 0.0
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.was_on_ground = False
        self.carried = None  # currently held box

    def try_pickup(self, boxes):
        """Toggle carrying the nearest box. Called on E keydown."""
        if self.carried is not None:
            # Drop it — release just in front
            self.carried.vy = 0
            self.carried.vx = 0
            self.carried = None
        else:
            best = None
            best_dist = 60
            for b in boxes:
                cx = self.x + self.w / 2
                if self.facing_right and b.rect.centerx < cx: continue
                if not self.facing_right and b.rect.centerx > cx: continue
                
                dx = abs(b.rect.centerx - cx)
                dy = abs(b.rect.centery - self.rect.centery)
                d = dx + dy
                if d < best_dist:
                    best_dist = d
                    best = b
            if best:
                self.carried = best

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def move_x(self, dx, platforms, boxes, gates):
        self.x += dx
        r = self.rect
        for p in platforms:
            if r.colliderect(p.rect):
                if dx > 0: r.right = p.rect.left
                elif dx < 0: r.left = p.rect.right
                self.x = float(r.x)
                self.vx = 0
                
        for g in gates:
            if not g.is_open and r.colliderect(g.rect):
                if dx > 0: r.right = g.rect.left
                elif dx < 0: r.left = g.rect.right
                self.x = float(r.x)
                self.vx = 0

        for b in boxes:
            if r.colliderect(b.rect):
                if dx > 0:
                    b.x += dx
                    b_r = b.rect
                    b_r.left = r.right
                    b.x = float(b_r.x)
                    for p in platforms:
                        if b.rect.colliderect(p.rect):
                            b_r.right = p.rect.left
                            b.x = float(b_r.x)
                            r.right = b_r.left
                            self.x = float(r.x)
                            self.vx = 0
                    for g in gates:
                        if not g.is_open and b.rect.colliderect(g.rect):
                            b_r.right = g.rect.left
                            b.x = float(b_r.x)
                            r.right = b_r.left
                            self.x = float(r.x)
                            self.vx = 0
                elif dx < 0:
                    b.x += dx
                    b_r = b.rect
                    b_r.right = r.left
                    b.x = float(b_r.x)
                    for p in platforms:
                        if b.rect.colliderect(p.rect):
                            b_r.left = p.rect.right
                            b.x = float(b_r.x)
                            r.left = b_r.right
                            self.x = float(r.x)
                            self.vx = 0
                    for g in gates:
                        if not g.is_open and b.rect.colliderect(g.rect):
                            b_r.left = g.rect.right
                            b.x = float(b_r.x)
                            r.left = b_r.right
                            self.x = float(r.x)
                            self.vx = 0

    def move_y(self, dy, platforms, boxes, gates, particles, shake):
        self.was_on_ground = self.on_ground
        self.y += dy
        self.on_ground = False
        r = self.rect
        
        def handle_landing():
            if not self.was_on_ground and self.vy > 2:
                impact = min(self.vy / 10, 1.0)
                self.scale_x = 1.0 + 0.3 * impact
                self.scale_y = 1.0 - 0.25 * impact
                shake[0] = int(1.5 * impact)
                for _ in range(int(6 * impact)):
                    particles.append(Particle(self.x + self.w // 2 + random.uniform(-10,10), self.y + self.h, "dust"))
            self.vy = 0
            self.on_ground = True

        for p in platforms:
            if r.colliderect(p.rect):
                if dy > 0:
                    r.bottom = p.rect.top
                    self.y = float(r.y)
                    handle_landing()
                elif dy < 0:
                    r.top = p.rect.bottom
                    self.y = float(r.y)
                    self.vy = 0
                    
        for g in gates:
            if not g.is_open and r.colliderect(g.rect):
                if dy > 0:
                    r.bottom = g.rect.top
                    self.y = float(r.y)
                    handle_landing()
                elif dy < 0:
                    r.top = g.rect.bottom
                    self.y = float(r.y)
                    self.vy = 0
                    
        for b in boxes:
            if r.colliderect(b.rect):
                if dy > 0:
                    r.bottom = b.rect.top
                    self.y = float(r.y)
                    handle_landing()
                elif dy < 0:
                    r.top = b.rect.bottom
                    self.y = float(r.y)
                    self.vy = 0

    def update(self, platforms, particles, shake, boxes, gates, world_w=None):
        if not self.awake: return shake
        if world_w is None: world_w = W

        keys = pygame.key.get_pressed()
        target = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target = self.speed
            self.facing_right = True

        self.vx += (target - self.vx) * 0.22

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = self.jump_power
            self.scale_x = 0.8
            self.scale_y = 1.3
            for _ in range(8):
                particles.append(Particle(self.x + self.w // 2 + random.uniform(-6,6), self.y + self.h, "dust"))

        self.vy += self.gravity

        # Don't collide with carried box
        active_boxes = [b for b in boxes if b is not self.carried]
        self.move_x(self.vx, platforms, active_boxes, gates)
        self.move_y(self.vy, platforms, active_boxes, gates, particles, shake)

        # Clamp to world
        self.x = max(0, min(self.x, world_w - self.w))

        # Keep carried box glued above head
        if self.carried is not None:
            self.carried.x = self.x + self.w / 2 - self.carried.w / 2
            self.carried.y = self.y - self.carried.h - 2
            self.carried.vy = 0
            self.carried.vx = 0

        self.scale_x += (1.0 - self.scale_x) * 0.15
        self.scale_y += (1.0 - self.scale_y) * 0.15

        if abs(self.vx) > 0.5 and self.on_ground:
            self.walk_timer += 0.18
            self.head_bob = math.sin(self.walk_timer * 3) * 1.8
        else:
            self.walk_timer *= 0.9
            self.head_bob *= 0.85

        if abs(self.vx) < 0.3 and self.on_ground:
            self.idle_timer += 0.04
        else:
            self.idle_timer = 0

        return shake

    def draw(self, surface, ox=0):
        # ox = camera x offset
        rx_world = self.x - ox  # screen x
        cx = rx_world + self.w / 2
        bot = self.y + self.h
        draw_w = int(self.w * self.scale_x)
        draw_h = int(self.h * self.scale_y)
        rx = int(cx - draw_w / 2)
        ry = int(bot - draw_h + self.head_bob)

        breathe = math.sin(self.idle_timer) * 1.2 if self.idle_timer > 0 else 0
        sx = draw_w / self.w
        sy = draw_h / self.h

        shadow_w = int(20 * self.scale_x)
        shadow_surf = pygame.Surface((shadow_w * 2, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 35), (0, 0, shadow_w * 2, 6))
        surface.blit(shadow_surf, (int(cx - shadow_w), int(bot)))

        # Draw carried box above head
        if self.carried is not None:
            bx = int(cx - self.carried.w / 2)
            by = ry - self.carried.h - 4
            pygame.draw.rect(surface, (55, 58, 72), (bx, by, self.carried.w, self.carried.h))
            pygame.draw.rect(surface, (100, 105, 125), (bx, by, self.carried.w, self.carried.h), 2)
            pygame.draw.line(surface, (100, 105, 125), (bx, by), (bx + self.carried.w, by + self.carried.h), 1)
            pygame.draw.line(surface, (100, 105, 125), (bx + self.carried.w, by), (bx, by + self.carried.h), 1)
            # Arms stretch up
            pygame.draw.rect(surface, ROBO_DARK, (rx + int(-2*sx), ry + int((12+breathe)*sy), int(5*sx), int(20*sy)))
            pygame.draw.rect(surface, ROBO_DARK, (rx + int(21*sx), ry + int((12+breathe)*sy), int(5*sx), int(20*sy)))
            # Tiny hands gripping the box
            pygame.draw.rect(surface, ROBO_HI, (rx + int(-4*sx), ry - 6, int(8*sx), int(8*sy)))
            pygame.draw.rect(surface, ROBO_HI, (rx + int(20*sx), ry - 6, int(8*sx), int(8*sy)))
        else:
            arm_swing = math.sin(self.walk_timer * 3) * 3 if abs(self.vx) > 0.5 else 0
            la = pygame.Rect(rx + int(-2*sx), ry + int((14 - arm_swing + breathe)*sy), int(5*sx), int(14*sy))
            ra = pygame.Rect(rx + int(21*sx), ry + int((14 + arm_swing + breathe)*sy), int(5*sx), int(14*sy))
            pygame.draw.rect(surface, ROBO_DARK, la)
            pygame.draw.rect(surface, ROBO_DARK, ra)
            pygame.draw.rect(surface, ROBO_HI, la, 1)
            pygame.draw.rect(surface, ROBO_HI, ra, 1)

        leg_anim = math.sin(self.walk_timer * 3) * 4 if abs(self.vx) > 0.5 else 0
        lleg = pygame.Rect(rx + int(4*sx), ry + int((28+breathe)*sy), int(6*sx), int((10 + leg_anim)*sy))
        rleg = pygame.Rect(rx + int(14*sx), ry + int((28+breathe)*sy), int(6*sx), int((10 - leg_anim)*sy))
        pygame.draw.rect(surface, ROBO_DARK, lleg)
        pygame.draw.rect(surface, ROBO_DARK, rleg)

        body = pygame.Rect(rx + int(2*sx), ry + int((12+breathe)*sy), int(20*sx), int(18*sy))
        pygame.draw.rect(surface, ROBO, body)
        pygame.draw.rect(surface, ROBO_HI, body, 1)
        chest_y = ry + int((18+breathe)*sy)
        pygame.draw.line(surface, ROBO_DARK, (rx + int(5*sx), chest_y), (rx + int(19*sx), chest_y), 1)

        head = pygame.Rect(rx + int(3*sx), ry + int(breathe*sy), int(18*sx), int(13*sy))
        pygame.draw.rect(surface, ROBO, head)
        pygame.draw.rect(surface, ROBO_HI, head, 1)
        pygame.draw.line(surface, ROBO_DARK, (rx + int(5*sx), ry + int((11+breathe)*sy)), (rx + int(19*sx), ry + int((11+breathe)*sy)), 1)

        ant_base = (rx + int(12*sx), ry + int(breathe*sy))
        ant_tip = (rx + int(12*sx), ry + int(breathe*sy) - int(9*sy))
        pygame.draw.line(surface, ROBO_HI, ant_base, ant_tip, 2)
        if self.awake and self.eye_brightness > 0.3:
            ga = int(90 * self.eye_brightness)
            ds = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(ds, (*EYE_COL, ga), (4, 4), 4)
            surface.blit(ds, (ant_tip[0] - 4, ant_tip[1] - 4))

        if self.awake and self.eye_brightness > 0:
            ex = rx + int(14*sx) if self.facing_right else rx + int(5*sx)
            ey = ry + int((4+breathe)*sy)
            gs_r = int(14 * self.eye_brightness)
            if gs_r > 0:
                gsurf = pygame.Surface((gs_r*2, gs_r*2), pygame.SRCALPHA)
                pygame.draw.circle(gsurf, (*EYE_GLOW_C, int(35*self.eye_brightness)), (gs_r, gs_r), gs_r)
                surface.blit(gsurf, (ex - gs_r + 3, ey - gs_r + 2))
            ea = int(255 * self.eye_brightness)
            esurf = pygame.Surface((5, 4), pygame.SRCALPHA)
            esurf.fill((*EYE_COL, ea))
            surface.blit(esurf, (ex, ey))

class Platform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.surf = pygame.Surface((w, h), pygame.SRCALPHA)
        self.surf.fill(PLAT_FILL)
        pygame.draw.line(self.surf, PLAT_EDGE, (0, 0), (w, 0), 1)
        pygame.draw.line(self.surf, PLAT_BOTTOM, (0, h-1), (w, h-1), 1)
        for i in range(0, w, random.randint(15,30)):
            lh = random.randint(2, max(2, h-2))
            pygame.draw.line(self.surf, (PLAT_FILL[0]+3, PLAT_FILL[1]+3, PLAT_FILL[2]+5), (i, 2), (i, lh), 1)

    def draw(self, surface):
        surface.blit(self.surf, self.rect.topleft)

class MemoryPlatform:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.w = w
        self.h = h

    def draw(self, surface, flashback_active, frame, cam_x=0):
        if flashback_active:
            rx = self.rect.x - cam_x
            r = pygame.Rect(rx, self.rect.y, self.rect.w, self.rect.h)
            # Draw glitchy / cyan outline
            pygame.draw.rect(surface, (0, 255, 255, 60), r)
            pygame.draw.rect(surface, (0, 255, 255, 180), r, 2)
            # Scanlines inside
            for i in range(0, self.w, 15):
                offset = int(5 * math.sin(frame * 0.1 + i))
                pygame.draw.line(surface, (0, 255, 255, 100), (rx + i, self.rect.y + offset), (rx + i, self.rect.bottom), 1)

class Hazard:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.w = w
        self.h = h
        
    def draw(self, surface, frame, cam_x=0):
        rx = self.rect.x - cam_x
        r = pygame.Rect(rx, self.rect.y, self.rect.w, self.rect.h)
        pygame.draw.rect(surface, (50, 5, 5), r)
        pygame.draw.rect(surface, (150, 20, 20), r, 1)
        # Laser beams going up
        for i in range(0, self.w, 12):
            h_line = 6 + 8 * math.sin(frame * 0.2 + i)
            pygame.draw.line(surface, (255, 40, 40), (rx + i, self.rect.y), (rx + i, self.rect.y - h_line), 2)
            # Floating particles above hazard
            if random.random() < 0.1:
                py = self.rect.y - random.randint(5, 20)
                pygame.draw.rect(surface, (255, 100, 100), (rx + i, py, 2, 2))

# ── City Background ─────────────────────────────
def build_city_surface(width):
    surf = pygame.Surface((width, H), pygame.SRCALPHA)
    layers = [
        (BLD_FAR,  -20, 60, 160, 220, 480, 5, 25,  WIN_DIM,   0.25),
        (BLD_MID,  -10, 50, 130, 160, 380, 10, 45,  WIN_DIM,   0.20),
        (BLD_NEAR,   0, 40, 110, 100, 270, 25, 70,  WIN_BRIGHT,0.15),
    ]
    for color, start_x, min_w, max_w, min_h, max_h, min_gap, max_gap, win_col, win_chance in layers:
        x = start_x
        while x < width + 50:
            bw = random.randint(min_w, max_w)
            bh = random.randint(min_h, max_h)
            by = H - bh
            pygame.draw.rect(surf, color, (x, by, bw, bh))
            pygame.draw.rect(surf, (color[0]+4, color[1]+4, color[2]+6), (x, by, bw, 3))
            cols = max(1, bw // 22)
            rows = max(1, (bh - 30) // 28)
            for c in range(cols):
                for r in range(rows):
                    if random.random() < win_chance:
                        wx = x + 8 + c * 22
                        wy = by + 18 + r * 28
                        pygame.draw.rect(surf, win_col, (wx, wy, 6, 10))
            x += bw + random.randint(min_gap, max_gap)
    return surf

def build_sky_surface():
    surf = pygame.Surface((W, H))
    for y in range(H):
        t = y / H
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (W, y))
    return surf

def build_fog_surface(intensity):
    fog = pygame.Surface((W, H), pygame.SRCALPHA)
    for i in range(10):
        y = H - 80 - i * 18
        a = max(0, intensity - i * (intensity // 10))
        pygame.draw.rect(fog, (*FOG_COL, a), (0, y, W, 22))
    return fog

def build_scanline_overlay():
    s = pygame.Surface((W, H), pygame.SRCALPHA)
    for y in range(0, H, 3):
        pygame.draw.line(s, (0, 0, 0, 8), (0, y), (W, y))
    return s

# ── Levels ──────────────────────────────────────────────────────
# Jump physics: jump_power=-9.5, gravity=0.48, speed=3.8
# Max jump height ≈ 94px, safe target ≈ 80px rise per step
# Max horizontal air travel ≈ 152px, safe gap ≈ 120px
# Ground top is at H-50 (y=490). Robot spawns standing on ground.

GND = H - 50  # y of ground surface

# Physics reference: jump_power=-9.5, gravity=0.48, speed=3.8
# Max height ~94px (safe: 75px). Max air reach ~152px (safe: 115px).
# [E] = pick up / drop box   [SPACE/W] = jump   [ARROWS/WASD] = move

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
        "boxes": [
            (180, GND)
        ]
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
            (380, GND - 40, 100, 14),
            (580, GND - 80, 100, 14),
            (780, GND - 120, 100, 14),
            (980, GND - 60, 100, 14),
        ],
        "hazards": [
            (300, GND - 20, 900, 20)
        ],
        "switches": [],
        "gates": [],
        "boxes": []
    },
    {
        "name": "laser grid",
        "hint": "red is death. don't touch it.",
        "world_w": 2000,
        "robot": (60, GND - 36),
        "exit": (1940, GND),
        "platforms": [
            (0,    GND, 200, 70),
            (300,  GND - 65, 100, 14),
            (500,  GND - 130, 100, 14),
            (800,  GND, 300, 70),
            (1200, GND - 65, 120, 14),
            (1500, GND, 500, 70),
        ],
        "memory_platforms": [
            (680, GND - 60, 80, 14)
        ],
        "hazards": [
            (200, GND - 20, 600, 20),
            (1100, GND - 20, 400, 20),
            (650, GND - 180, 20, 100)
        ],
        "switches": [
            {"x": 850, "y": GND - 8, "w": 44, "h": 8, "id": 1, "timed": 0, "type": "plate"},
        ],
        "gates": [
            {"x": 1400, "y": GND - 200, "w": 16, "h": 200, "id": 1},
        ],
        "boxes": [
            (100, GND)
        ]
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
            (450, GND - 40, 100, 14),
            (700, GND - 80, 100, 14),
            (950, GND - 120, 100, 14),
            (1200, GND - 80, 100, 14),
            (1450, GND - 40, 100, 14),
            (1700, GND, 100, 14),
        ],
        "hazards": [
            (350, GND - 20, 1650, 20)
        ],
        "switches": [
            {"x": 100, "y": GND - 73, "w": 40, "h": 10, "id": 1, "timed": 600, "type": "button"}
        ],
        "gates": [
            {"x": 2100, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [
            (200, GND)
        ]
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
            (450, GND - 40, 80, 14),
            (600, GND - 80, 80, 14),
            (750, GND - 120, 80, 14),
            (1300, GND - 120, 80, 14),
            (1500, GND - 80, 80, 14),
            (1700, GND - 40, 80, 14),
            (1900, GND, 80, 14),
            (2600, GND - 60, 80, 14),
            (2800, GND - 120, 80, 14),
            (3000, GND - 60, 80, 14),
        ],
        "hazards": [
            (400, GND - 20, 1800, 20),
            (2500, GND - 20, 700, 20),
            (850, GND - 200, 20, 150),
            (1250, GND - 200, 20, 80),
            (1600, GND - 200, 20, 120),
            (2900, GND - 200, 20, 80),
        ],
        "switches": [
            {"x": 1050, "y": GND - 108, "w": 44, "h": 8, "id": 1, "timed": 0, "type": "plate"},
            {"x": 2350, "y": GND - 8, "w": 44, "h": 8, "id": 2, "timed": 0, "type": "plate"},
        ],
        "gates": [
            {"x": 2050, "y": GND - 200, "w": 16, "h": 200, "id": 1},
            {"x": 3300, "y": GND - 200, "w": 16, "h": 200, "id": 2},
        ],
        "boxes": [
            (200, GND),
            (2250, GND)
        ]
    }
]

# ── Level Generator ─────────────────────────────────────────────

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
        self.n             = n
        self.world_w       = min(max(1400 + n * 220, 1400), 6000)
        self.mem_plat_count = min(max(n // 2, 4), 14)
        self.gap_max_px    = min(max(80 + n * 6, 80), 115)
        self.timer_frames  = min(max(600 - n * 20, 180), 600)


def _bridge_count(hazard_w, plat_w=90, max_gap=110):
    """Minimum memory platforms needed so no gap exceeds max_gap."""
    return max(4, int(hazard_w / (plat_w + max_gap)) + 2)


def tmpl_navigation(p):
    safe_w = 280
    hz_x   = safe_w
    hz_w   = p.world_w - safe_w * 2
    count  = max(4, int(hz_w / (p.gap_max_px + 45)) + 1)
    spacing = hz_w / (count + 1)
    heights = [GND - 40, GND - 80, GND - 120, GND - 80]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 45, heights[i % 4], 90, 14)
        for i in range(count)
    ]
    return {
        "name":  f"ghost run {p.n}",
        "hint":  _HINTS_NAV[p.n % len(_HINTS_NAV)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": [
            (0,              GND, safe_w, 70),
            (p.world_w - safe_w, GND, safe_w, 70),
        ],
        "memory_platforms": mem_plats,
        "hazards": [(hz_x, GND - 20, hz_w, 20)],
        "switches": [],
        "gates":   [],
        "boxes":   [],
    }


def tmpl_box_puzzle(p):
    gap     = p.gap_max_px
    left_w  = p.world_w // 3
    right_x = left_w + gap
    right_w = p.world_w - right_x
    return {
        "name":  f"cargo {p.n}",
        "hint":  _HINTS_BOX[p.n % len(_HINTS_BOX)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 70, GND),
        "platforms": [
            (0,       GND, left_w,  70),
            (right_x, GND, right_w, 70),
        ],
        "memory_platforms": [],
        "hazards": [(left_w, GND - 20, gap, 20)],
        "switches": [
            {"x": p.world_w - 200, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": 0, "type": "plate"}
        ],
        "gates": [
            {"x": p.world_w - 130, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [(160, GND)],
    }


def tmpl_memory_traverse(p):
    safe_w  = 300
    hz_x    = safe_w
    hz_w    = p.world_w - safe_w * 2
    count   = max(4, int(hz_w / (p.gap_max_px + 45)) + 1)
    spacing = hz_w / (count + 1)
    heights = [GND - 50, GND - 90, GND - 130, GND - 90]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 45, heights[i % 4], 90, 14)
        for i in range(count)
    ]
    return {
        "name":  f"flash run {p.n}",
        "hint":  _HINTS_MEM[p.n % len(_HINTS_MEM)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": [
            (0,                  GND, safe_w, 70),
            (p.world_w - safe_w, GND, safe_w, 70),
        ],
        "memory_platforms": mem_plats,
        "hazards": [(hz_x, GND - 20, hz_w, 20)],
        "switches": [
            {"x": 100, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": p.timer_frames, "type": "button"}
        ],
        "gates": [
            {"x": p.world_w - safe_w - 20, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [],
    }


def tmpl_combo(p):
    safe_w  = 300
    hz_x    = safe_w
    hz_w    = p.world_w - safe_w * 2
    count   = max(4, int(hz_w / (p.gap_max_px + 50)) + 1)  # wider plats (100px), so +50
    spacing = hz_w / (count + 1)
    heights = [GND - 50, GND - 90, GND - 130, GND - 90]
    mem_plats = [
        (int(hz_x + spacing * (i + 1)) - 50, heights[i % 4], 100, 14)
        for i in range(count)
    ]
    return {
        "name":  f"overload {p.n}",
        "hint":  _HINTS_COMBO[p.n % len(_HINTS_COMBO)],
        "world_w": p.world_w,
        "robot": (60, GND - 36),
        "exit":  (p.world_w - 60, GND),
        "platforms": [
            (0,                  GND, safe_w, 70),
            (p.world_w - safe_w, GND, safe_w, 70),
        ],
        "memory_platforms": mem_plats,
        "hazards": [(hz_x, GND - 20, hz_w, 20)],
        "switches": [
            {"x": 80, "y": GND - 8, "w": 44, "h": 8,
             "id": 1, "timed": p.timer_frames, "type": "button"}
        ],
        "gates": [
            {"x": p.world_w - safe_w - 20, "y": GND - 200, "w": 16, "h": 200, "id": 1}
        ],
        "boxes": [(220, GND)],
    }


def _pick_template(n):
    r = n % 4
    if r == 2: return tmpl_navigation
    if r == 3: return tmpl_box_puzzle
    if r == 0: return tmpl_memory_traverse
    return tmpl_combo if n >= 8 else tmpl_navigation  # r == 1


def generate_level(n):
    """Return a level dict for 1-based level index n (call with n >= 6)."""
    return _pick_template(n)(DifficultyProfile(n))


def get_level(idx):
    """0-based index. Returns handcrafted level for idx < len(LEVELS), generated for idx >= len(LEVELS)."""
    if idx < len(LEVELS):
        return LEVELS[idx]
    return generate_level(idx + 1)


# ── Main ────────────────────────────────────────────────────────
def main():
    global screen, FULLSCREEN

    font = pygame.font.SysFont("Courier", 20)
    title_font = pygame.font.SysFont("Courier", 52)
    hint_font = pygame.font.SysFont("Courier", 16)

    sky_surf = build_sky_surface()
    city_surf = build_city_surface(W)
    fog_low = build_fog_surface(45)
    fog_top = build_fog_surface(20)
    scanlines = build_scanline_overlay()

    shake = [0]
    particles = []
    
    ST_MENU    = 0
    ST_PLAY    = 1
    ST_TRANS   = 2
    ST_INTRO   = 3

    state = ST_MENU
    frame = 0
    
    current_level = 0
    unlocked_level = 0
    intro_done = False
    
    platforms = []
    memory_platforms = []
    hazards = []
    switches = []
    gates = []
    boxes = []
    robot = None
    exit_portal = None
    
    cam_x = 0
    current_world_w = W

    def load_level(idx):
        nonlocal platforms, memory_platforms, hazards, switches, gates, boxes, robot, exit_portal, cam_x, current_world_w
        data = LEVELS[idx]
        robot = Robot(*data["robot"])
        robot.awake = True
        robot.eye_brightness = 1.0
        exit_portal = ExitPortal(*data["exit"])
        platforms = [Platform(*p) for p in data["platforms"]]
        memory_platforms = [MemoryPlatform(*p) for p in data.get("memory_platforms", [])]
        hazards = [Hazard(*h) for h in data.get("hazards", [])]
        switches = [Switch(s["x"], s["y"], s["w"], s["h"], s["id"], s["timed"], s["type"]) for s in data["switches"]]
        gates = [Gate(g["x"], g["y"], g["w"], g["h"], g["id"]) for g in data["gates"]]
        boxes = [Box(*b) for b in data["boxes"]]
        current_world_w = data.get("world_w", W)
        city_surf = build_city_surface(int(current_world_w * 0.5) + W)
        cam_x = 0
        particles.clear()
        
    overlay = pygame.Surface((W, H))
    overlay.fill(BLACK)
    overlay_alpha = 0.0

    running = True
    while running:
        clock.tick(FPS)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == ST_PLAY or state == ST_INTRO:
                        state = ST_MENU
                    else:
                        running = False
                elif event.key == pygame.K_F11:
                    FULLSCREEN = not FULLSCREEN
                    screen = create_display(FULLSCREEN)
                elif event.key == pygame.K_r and state == ST_PLAY:
                    load_level(current_level)
                elif event.key == pygame.K_e and state == ST_PLAY and robot:
                    robot.try_pickup(boxes)
                elif state == ST_MENU:
                    if pygame.K_1 <= event.key <= pygame.K_6:
                        lvl = event.key - pygame.K_1
                        if lvl <= unlocked_level and lvl < len(LEVELS):
                            current_level = lvl
                            state = ST_TRANS
                            overlay_alpha = 255.0
                    elif event.key == pygame.K_RETURN:
                        current_level = min(unlocked_level, len(LEVELS) - 1)
                        state = ST_TRANS
                        overlay_alpha = 255.0

        if state == ST_TRANS:
            overlay_alpha -= 5
            if overlay_alpha <= 0:
                overlay_alpha = 0
                load_level(current_level)
                if current_level == 0 and not intro_done:
                    state = ST_INTRO
                    frame = 0
                    robot.awake = False
                    robot.eye_brightness = 0.0
                else:
                    state = ST_PLAY
                    intro_done = True

        elif state == ST_INTRO:
            if frame < 60:
                pass
            elif frame < 120:
                robot.awake = True
                p = (frame - 60) / 60
                robot.eye_brightness = p
            else:
                robot.eye_brightness = 1.0
                state = ST_PLAY
                intro_done = True

        flashback_active = False
        if state == ST_PLAY:
            if frame % 240 < 15: # Glitch for 15 frames every 4 seconds
                flashback_active = True
                
            all_platforms = platforms + memory_platforms
            for b in boxes:
                if b is not robot.carried:
                    b.update(all_platforms, gates)
            active_boxes = [b for b in boxes if b is not robot.carried]
            for s in switches:
                s.update(robot, active_boxes)
            for g in gates:
                g.update(switches)
            shake = robot.update(all_platforms, particles, shake, boxes, gates, current_world_w)
            
            # Camera follows robot
            cam_x = max(0, min(int(robot.x - W // 2 + robot.w // 2), current_world_w - W))
            
            player_rect = robot.rect
            for h in hazards:
                if player_rect.colliderect(h.rect):
                    # DEATH
                    load_level(current_level)
                    break

            #check if any box is on a hazard
            for b in boxes :
                for h in hazards :
                    if b.rect.colliderect(h.rect):
                        # to spawn a cool spark explotion where the box died
                        for _ in range(10) :
                            particles.append(Particle(b.rect.centerx, b.rect.centery,"spark"))

                        # teleport the box back to the sky at the start of the
                        b.x = 120
                        b.y = -50
                        b.vy = 0 



            if exit_portal and robot.rect.colliderect(exit_portal.rect):
                unlocked_level = max(unlocked_level, current_level + 1)
                if current_level + 1 < len(LEVELS):
                    current_level += 1
                    state = ST_TRANS
                    overlay_alpha = 255.0
                else:
                    state = ST_MENU

        if state >= ST_INTRO:
            if frame % 14 == 0:
                particles.append(Particle(random.uniform(0, current_world_w), H - 50, "ember"))
            if frame % 3 == 0:
                particles.append(Particle(random.uniform(0, current_world_w), random.uniform(-20, 0), "rain"))

        if shake[0] > 0:
            shake[0] = max(0, shake[0] - 0.6)
        particles = [p for p in particles if p.update()]

        # ── DRAW ──
        gs = game_surface
        gs.blit(sky_surf, (0, 0))
        if city_surf:
            gs.blit(city_surf, (-int(cam_x * 0.5), 0))
        gs.blit(fog_low, (0, 0))

        if state == ST_MENU:
            # ── nothing-inspired title ──
            pulse = (math.sin(frame * 0.04) + 1) / 2
            # Dot grid decoration
            for dx in range(-4, 5):
                for dy in range(-1, 2):
                    dot_a = int(15 + 10 * pulse)
                    dot_x = W//2 + dx * 28
                    dot_y = H//6 + dy * 20
                    pygame.draw.circle(gs, (255, 255, 255, dot_a) if (dx+dy)%3==0 else (40, 42, 55), (dot_x, dot_y), 2)

            title = title_font.render("volt.", True, (230, 235, 245))
            gs.blit(title, (W//2 - title.get_width()//2, H//5 + 10))
            # Thin separator line
            line_y = H//5 + 60
            pygame.draw.line(gs, (40, 42, 55), (W//2 - 100, line_y), (W//2 + 100, line_y), 1)
            sub = hint_font.render("a puzzle platformer", True, (70, 75, 90))
            gs.blit(sub, (W//2 - sub.get_width()//2, line_y + 8))

            # ── level list ──
            start_y = H//2 - 20
            for i in range(len(LEVELS)):
                unlocked = i <= unlocked_level
                completed = i < unlocked_level
                y = start_y + i * 34
                # Dot indicator
                dot_col = (0, 220, 255) if unlocked else (30, 32, 42)
                if completed:
                    dot_col = (80, 255, 120)
                pygame.draw.circle(gs, dot_col, (W//2 - 170, y + 10), 4)
                if completed:
                    pygame.draw.circle(gs, (0, 0, 0), (W//2 - 170, y + 10), 2)
                # Number
                num_col = (80, 85, 100) if unlocked else (30, 32, 42)
                num = hint_font.render(f"{i+1:02d}", True, num_col)
                gs.blit(num, (W//2 - 155, y + 3))
                # Separator dot
                pygame.draw.circle(gs, (40, 42, 55), (W//2 - 130, y + 10), 2)
                # Name
                name_col = (180, 185, 200) if unlocked else (35, 38, 48)
                name = font.render(LEVELS[i]["name"], True, name_col)
                gs.blit(name, (W//2 - 118, y + 2))
                # Status text
                if completed:
                    st = hint_font.render("done", True, (60, 180, 90))
                    gs.blit(st, (W//2 + 140, y + 3))
                elif i == unlocked_level:
                    blink = int(frame * 0.06) % 2
                    if blink:
                        st = hint_font.render("play", True, (0, 200, 255))
                        gs.blit(st, (W//2 + 140, y + 3))

            # Bottom controls
            ctrl = hint_font.render("1-6 select  //  enter continue  //  esc quit", True, (50, 52, 65))
            gs.blit(ctrl, (W//2 - ctrl.get_width()//2, H - 40))
            
        elif exit_portal is not None:
            # ── Draw game objects with camera offset ──
            def ox(obj_x): return int(obj_x - cam_x)

            # Exit portal
            ep = exit_portal
            ep_s = pygame.Surface((ep.rect.w + 30, ep.rect.h + 30), pygame.SRCALPHA)
            pulse = (math.sin(ep.frame * 0.08) + 1) / 2
            ep.frame += 1
            pygame.draw.ellipse(ep_s, (40, 255, 120, int(30 + 40 * pulse)), ep_s.get_rect())
            gs.blit(ep_s, (ox(ep.rect.x) - 15, ep.rect.y - 15))
            inner_a = int(60 + 60 * pulse)
            ep_inner = pygame.Surface((ep.rect.w, ep.rect.h), pygame.SRCALPHA)
            ep_inner.fill((40, 255, 100, inner_a))
            gs.blit(ep_inner, (ox(ep.rect.x), ep.rect.y))
            pygame.draw.rect(gs, (80, 255, 140), (ox(ep.rect.x), ep.rect.y, ep.rect.w, ep.rect.h), 2)
            ecx = ox(ep.rect.centerx)
            eay = ep.rect.y + 10 + int(4 * math.sin(ep.frame * 0.12))
            pygame.draw.polygon(gs, (200, 255, 220), [(ecx, eay), (ecx - 8, eay + 12), (ecx + 8, eay + 12)])

            for s in switches:
                color = (0, 220, 255) if s.type == "button" else (255, 160, 30)
                dim = tuple(c // 3 for c in color)
                base_h = 6 if s.active else 12
                base_y = s.rect.bottom - base_h
                pygame.draw.rect(gs, dim, (ox(s.rect.x) - 2, base_y, s.rect.w + 4, base_h))
                top_col = color if s.active else dim
                pygame.draw.rect(gs, top_col, (ox(s.rect.x), base_y, s.rect.w, 3))
                if s.active:
                    g_sw = pygame.Surface((s.rect.w + 20, 20), pygame.SRCALPHA)
                    pygame.draw.ellipse(g_sw, (*color, 60), g_sw.get_rect())
                    gs.blit(g_sw, (ox(s.rect.x) - 10, base_y - 8))
                if s.timed > 0 and s.active and s.timer > 0:
                    pygame.draw.rect(gs, (255, 255, 80), (ox(s.rect.x), base_y - 6, int(s.rect.w * s.timer / s.timed), 3))

            for g in gates:
                if not g.is_open:
                    pygame.draw.rect(gs, (80, 15, 15), (ox(g.rect.x), g.rect.y, g.rect.w, g.rect.h))
                    for i in range(0, g.rect.h, 8):
                        a = int(120 + 80 * math.sin((i + frame * 3) * 0.15))
                        pygame.draw.line(gs, (min(255, a + 80), 40, 40),
                                         (ox(g.rect.x) + 1, g.rect.y + i), (ox(g.rect.x) + g.rect.w - 1, g.rect.y + i), 2)

            for b in boxes:
                if b is not robot.carried:
                    bx = ox(b.rect.x)
                    pygame.draw.rect(gs, (50, 52, 65), (bx, b.rect.y, b.w, b.h))
                    pygame.draw.rect(gs, (90, 95, 110), (bx, b.rect.y, b.w, b.h), 2)
                    pygame.draw.line(gs, (90, 95, 110), (bx, b.rect.y), (bx + b.w, b.rect.y + b.h), 1)
                    pygame.draw.line(gs, (90, 95, 110), (bx + b.w, b.rect.y), (bx, b.rect.y + b.h), 1)

            for p in platforms:
                gs.blit(p.surf, (ox(p.rect.x), p.rect.y))
                
            for h in hazards:
                h.draw(gs, frame, cam_x)
                
            for p in memory_platforms:
                p.draw(gs, flashback_active, frame, cam_x)

            robot.draw(gs, cam_x)

            if state == ST_INTRO and frame < 60:
                beam = pygame.Surface((W, H), pygame.SRCALPHA)
                cx = robot.x + robot.w // 2
                pulse = (math.sin(frame * 0.2) + 1) / 2
                ba = int(22 + 28 * pulse)
                pts = [(cx - 55, 0), (cx + 55, 0), (cx + 10, robot.y), (cx - 10, robot.y)]
                pygame.draw.polygon(beam, (*SOLAR_COL, ba), pts)
                gs.blit(beam, (0, 0))

            for p in particles:
                p.draw(gs, ox=cam_x)

            # ── nothing-style HUD ──
            if state == ST_PLAY:
                # Level tag
                tag = f"{current_level+1:02d} // {LEVELS[current_level]['name']}"
                lvl_text = font.render(tag, True, (140, 145, 160))
                gs.blit(lvl_text, (16, 12))
                # Hint
                hint_text = hint_font.render(LEVELS[current_level].get("hint", ""), True, (70, 75, 90))
                gs.blit(hint_text, (16, 32))
                # Controls
                ctrl = hint_font.render("r restart  //  esc menu", True, (40, 42, 55))
                gs.blit(ctrl, (W - ctrl.get_width() - 12, 12))

        gs.blit(fog_top, (0, 0))
        gs.blit(scanlines, (0, 0))

        if overlay_alpha > 0:
            overlay.set_alpha(int(overlay_alpha))
            gs.blit(overlay, (0, 0))

        sw, sh = screen.get_size()
        scale = min(sw / W, sh / H)
        scaled_w = int(W * scale)
        scaled_h = int(H * scale)
        offset_x = (sw - scaled_w) // 2
        offset_y = (sh - scaled_h) // 2

        screen.fill(BLACK)
        sx_off = int(random.uniform(-shake[0], shake[0])) if shake[0] > 0 else 0
        sy_off = int(random.uniform(-shake[0], shake[0])) if shake[0] > 0 else 0
        scaled = pygame.transform.scale(gs, (scaled_w, scaled_h))
        screen.blit(scaled, (offset_x + sx_off, offset_y + sy_off))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
