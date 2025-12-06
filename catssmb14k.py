#!/usr/bin/env python3
import pygame, sys
# ---------- basics ----------
WIDTH, HEIGHT = 600, 400
TILE = 16
FPS = 60
# tile types: 0 = empty, 1 = solid ground, 2 = question block, 3 = pipe, 4 = brick block
# for simplicity, all solid for collision; add behavior later
LEVELS = {
    'original': [
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,],
    ],
    'smb3_world1_1': [  # Simplified SMB3 World 1-1 (approx 176 wide, 15 high; truncated to 50 for brevity)
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  # sky
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # ground
    ],
    # Add more SMB3 levels here, e.g., 'smb3_world1_2': [[...]],
    # For full list, extract from ROM using tools like https://github.com/mchlnix/SMB3-Foundry
}
# Default level
current_level = 'original'
LEVEL = LEVELS[current_level]
LEVEL_W = len(LEVEL[0]) * TILE
LEVEL_H = len(LEVEL) * TILE
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# ---------- colors for tiles ----------
TILE_COLORS = {
    0: (110,160,255),  # sky
    1: (80,70,60),  # ground
    2: (255,255,0),  # question block
    3: (0,255,0),  # pipe
    4: (150,75,0),  # brick
}
# ---------- helpers ----------
def solids_rects():
    r = []
    for y,row in enumerate(LEVEL):
        for x,t in enumerate(row):
            if t > 0:  # all non-empty are solid for now
                r.append(pygame.Rect(x*TILE, y*TILE, TILE, TILE))
    return r
SOLIDS = solids_rects()
def aabb_sweep(rect, dx, dy, blocks):
    # move X
    rect.x += dx
    for b in blocks:
        if rect.colliderect(b):
            if dx > 0: rect.right = b.left
            elif dx < 0: rect.left = b.right
    # move Y
    rect.y += dy
    on_ground = False
    for b in blocks:
        if rect.colliderect(b):
            if dy > 0: rect.bottom = b.top; on_ground = True
            elif dy < 0: rect.top = b.bottom
    return on_ground
# ---------- sprites ----------
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((12, 14)).convert_alpha()
        self.image.fill((240,80,80))
        self.rect = self.image.get_rect(topleft=pos)
        self.vel = pygame.Vector2(0,0)
        self.speed = 2.2
        self.jump = -6.0
        self.gravity = 0.35
        self.on_ground = False
    def update(self, keys):
        ax = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.vel.x = ax
        if keys[pygame.K_z] and self.on_ground:
            self.vel.y = self.jump
        self.vel.y = min(self.vel.y + self.gravity, 7.5)
        self.on_ground = aabb_sweep(self.rect, self.vel.x, self.vel.y, SOLIDS)
player = Player((40, 0))
all_sprites = pygame.sprite.Group(player)
# ---------- camera ----------
cam = pygame.Vector2(0,0)
def update_camera(focus_rect):
    cam.x = focus_rect.centerx - WIDTH//2
    cam.y = focus_rect.centery - HEIGHT//2
    cam.x = max(0, min(cam.x, LEVEL_W - WIDTH))
    cam.y = max(0, min(cam.y, LEVEL_H - HEIGHT))
# ---------- main loop ----------
accum = 0.0
dt = 1.0 / FPS
running = True
while running:
    ms = clock.tick(FPS)
    accum += ms / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_2, ... , pygame.K_8):  # load worlds
                world = event.key - pygame.K_1 + 1
                current_level = f'smb3_world{world}_1'  # example; add more keys
                if current_level in LEVELS:
                    LEVEL = LEVELS[current_level]
                    LEVEL_W = len(LEVEL[0]) * TILE
                    LEVEL_H = len(LEVEL) * TILE
                    SOLIDS = solids_rects()
                    player.rect.topleft = (40, 0)  # reset player
    while accum >= dt:
        keys = pygame.key.get_pressed()
        all_sprites.update(keys)
        update_camera(player.rect)
        accum -= dt
    # draw
    screen.fill((110,160,255))
    # draw tiles
    start_x = int(cam.x // TILE)
    end_x = int((cam.x + WIDTH) // TILE) + 1
    start_y = int(cam.y // TILE)
    end_y = int((cam.y + HEIGHT) // TILE) + 1
    for y in range(start_y, min(end_y, len(LEVEL))):
        for x in range(start_x, min(end_x, len(LEVEL[0]))):
            t = LEVEL[y][x]
            if t > 0:
                color = TILE_COLORS.get(t, (80,70,60))
                pygame.draw.rect(screen, color, pygame.Rect(x*TILE - cam.x, y*TILE - cam.y, TILE, TILE))
    # draw sprites
    for spr in all_sprites:
        screen.blit(spr.image, (spr.rect.x - cam.x, spr.rect.y - cam.y))
    pygame.display.set_caption(f"Pygame Platformer | {clock.get_fps():.1f} FPS | frame {clock.get_time()} ms")
    pygame.display.flip()
pygame.quit(); sys.exit()
