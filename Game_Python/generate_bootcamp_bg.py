"""Generate a procedural Boot Camp background for SI3LN."""
import os
import pygame

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.Surface((WIDTH, HEIGHT))

# Colors
DARK_BG = (5, 8, 18)
PANEL_BG = (15, 22, 38)
HOLO_CYAN = (0, 220, 255)
HOLO_BLUE = (80, 150, 220)
GRID_FADE = (0, 220, 255, 30)
WHITE_FAINT = (200, 210, 230, 40)

# Fill background
screen.fill(DARK_BG)

# Draw distant stars / particles
import random
random.seed(42)
for _ in range(150):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT // 2)
    brightness = random.randint(30, 120)
    pygame.draw.circle(screen, (brightness, brightness, brightness + 20), (x, y), random.choice([1, 1, 2]))

# Draw ceiling panels
for y in range(0, HEIGHT // 2, 80):
    alpha = int(10 + (y / HEIGHT) * 30)
    panel = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
    panel.fill((*PANEL_BG, alpha))
    screen.blit(panel, (0, y))
    # Horizontal neon line
    pygame.draw.line(screen, HOLO_CYAN, (0, y), (WIDTH, y), 1)

# Draw side walls
for x in [0, WIDTH - 120]:
    wall = pygame.Surface((120, HEIGHT), pygame.SRCALPHA)
    wall.fill((*PANEL_BG, 40))
    screen.blit(wall, (x, 0))
    pygame.draw.line(screen, HOLO_CYAN, (x + 60, 0), (x + 60, HEIGHT), 1)

# Draw floor perspective grid
floor_y = HEIGHT // 2 + 50
grid_surf = pygame.Surface((WIDTH, HEIGHT - floor_y), pygame.SRCALPHA)
# Vertical perspective lines
for i in range(-10, 11):
    x_top = WIDTH // 2 + i * 30
    x_bottom = WIDTH // 2 + i * 180
    pygame.draw.line(grid_surf, GRID_FADE, (x_top, 0), (x_bottom, HEIGHT - floor_y), 1)
# Horizontal lines
for j in range(0, HEIGHT - floor_y, 40):
    alpha = int(60 * (1 - j / (HEIGHT - floor_y)))
    pygame.draw.line(grid_surf, (*HOLO_CYAN[:3], alpha), (0, j), (WIDTH, j), 1)
screen.blit(grid_surf, (0, floor_y))

# Draw a glowing Boot Camp emblem / target rings in the center background
emblem_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
center = (WIDTH // 2, HEIGHT // 2 - 30)
for radius, alpha in [(200, 20), (160, 35), (120, 50), (80, 70)]:
    pygame.draw.circle(emblem_surf, (*HOLO_CYAN[:3], alpha), center, radius, 2)
pygame.draw.circle(emblem_surf, (*HOLO_CYAN[:3], 90), center, 40, 3)
pygame.draw.line(emblem_surf, (*HOLO_CYAN[:3], 60), (center[0] - 60, center[1]), (center[0] + 60, center[1]), 2)
pygame.draw.line(emblem_surf, (*HOLO_CYAN[:3], 60), (center[0], center[1] - 60), (center[0], center[1] + 60), 2)
screen.blit(emblem_surf, (0, 0))

# Draw bottom holographic HUD strip
hud_surf = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
hud_surf.fill((*PANEL_BG, 60))
pygame.draw.line(hud_surf, HOLO_CYAN, (0, 0), (WIDTH, 0), 2)
for x in range(0, WIDTH, 80):
    pygame.draw.rect(hud_surf, (*HOLO_CYAN[:3], 30), (x + 10, 20, 60, 20), border_radius=2)
screen.blit(hud_surf, (0, HEIGHT - 80))

# Add scanline overlay
scanlines = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 4):
    pygame.draw.line(scanlines, (0, 0, 0, 25), (0, y), (WIDTH, y), 1)
screen.blit(scanlines, (0, 0))

# Vignette
vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for i in range(200):
    alpha = int(180 * (i / 200))
    pygame.draw.rect(vignette, (0, 0, 0, alpha),
                     (i, i, WIDTH - 2 * i, HEIGHT - 2 * i), 1)
screen.blit(vignette, (0, 0))

# Save
output_path = os.path.join("assets", "worlds", "background_bootcamp.jpg")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
pygame.image.save(screen, output_path)
print(f"Saved {output_path}")
pygame.quit()
