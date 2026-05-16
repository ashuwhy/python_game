import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Top-Down Block Game")

# Colors
GROUND_COLOR = (85, 170, 85)  # Grass-like green
CHAR_COLOR = (50, 50, 200)   # Blue block

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Character setup
char_size = 40
char_rect = pygame.Rect(WIDTH // 2 - char_size // 2, HEIGHT // 2 - char_size // 2, char_size, char_size)
char_speed = 5

def main():
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Movement handling
        keys = pygame.key.get_pressed()
        
        # Calculate movement vector
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= char_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += char_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= char_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += char_speed

        # Normalize diagonal movement speed (so you don't move faster diagonally)
        if dx != 0 and dy != 0:
            dx = dx * 0.707
            dy = dy * 0.707

        # Apply movement
        char_rect.x += int(dx)
        char_rect.y += int(dy)

        # Boundary checking to keep character on screen
        char_rect.clamp_ip(screen.get_rect())

        # Drawing
        screen.fill(GROUND_COLOR)  # Draw grass ground
        pygame.draw.rect(screen, CHAR_COLOR, char_rect)  # Draw block character

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
