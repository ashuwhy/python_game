"""Camera system for side-scrolling."""
import pygame

W, H = 960, 540


class Camera:
    def __init__(self):
        self.x = 0.0

    def update(self, player, world_w):
        target = player.centerx - W // 3
        target = max(0, min(target, world_w - W))
        self.x += (target - self.x) * 0.12
        if abs(self.x - target) < 0.5:
            self.x = target

    def wx(self, world_x):
        """World x → screen x."""
        return world_x - int(self.x)

    def screen_rect(self, r):
        return pygame.Rect(r.x - int(self.x), r.y, r.w, r.h)

    def visible(self, r):
        """Is rect potentially on screen?"""
        sx = r.x - int(self.x)
        return -r.w < sx < W + r.w
