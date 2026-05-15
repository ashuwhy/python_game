"""Simple particle system for dust/landing effects."""
import random
# pyrefly: ignore [missing-import]
import pygame

W, H = 960, 540


class Particle:
    def __init__(self, x, y, vx, vy, color, life):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1
        return self.life > 0

    def draw(self, surface, cam_x):
        alpha = int(255 * self.life / self.max_life)
        sz = max(1, int(3 * self.life / self.max_life))
        sx, sy = int(self.x - cam_x), int(self.y)
        if 0 <= sx <= W and 0 <= sy <= H:
            ps = pygame.Surface((sz, sz), pygame.SRCALPHA)
            ps.fill((*self.color[:3], alpha))
            surface.blit(ps, (sx, sy))


def spawn_dust(particles, x, y, count=6, color=(180, 160, 130)):
    for _ in range(count):
        vx = random.uniform(-2, 2)
        vy = random.uniform(-3, -0.5)
        life = random.randint(10, 25)
        particles.append(Particle(x, y, vx, vy, color, life))


def spawn_land_puff(particles, x, y, count=8, color=(200, 180, 150)):
    for _ in range(count):
        vx = random.uniform(-3, 3)
        vy = random.uniform(-2, 0)
        life = random.randint(8, 18)
        particles.append(Particle(x, y, vx, vy, color, life))
