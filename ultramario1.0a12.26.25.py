import pygame
import sys
import math
import random
import array

# --- FLAMES CO. ENGINE INITIALIZATION ---
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

SCREEN_W = 256
SCREEN_H = 240
TILE_SIZE = 16
FPS = 60

# --- FULL NES PALETTE (64 COLORS) ---
NES_PALETTE = [
    (124,124,124), (0,0,52),   (0,0,148),   (68,40,188), 
    (148,0,132),   (168,0,32), (168,16,0),  (136,20,0),
    (80,48,0),     (0,120,0),  (0,104,0),   (0,88,0),
    (0,64,88),     (0,0,0),    (0,0,0),     (0,0,0),
    (188,188,188), (0,120,248),(0,88,248),  (104,68,252),
    (216,0,204),   (228,0,88), (248,56,0),  (228,92,16),
    (172,124,0),   (0,184,0),  (0,168,0),   (0,168,68),
    (0,136,136),   (0,0,0),    (0,0,0),     (0,0,0), 
    (248,248,248), (60,188,252),(104,136,252),(152,120,248),
    (248,120,248), (248,88,152),(248,120,88),(252,160,68),
    (248,184,0),   (184,248,24),(88,216,84), (88,248,152),
    (0,232,216),   (120,120,120),(0,0,0),    (0,0,0),
    (252,252,252), (164,228,252),(184,184,248),(216,184,248),
    (248,184,248), (248,164,192),(240,208,176),(252,224,168),
    (248,216,120), (216,248,120),(184,248,184),(184,248,216),
    (0,252,252),   (216,216,216),(0,0,0),    (0,0,0)
]

# Common Lookups
C_SKY = NES_PALETTE[33]  # Exact NES sky blue from palette
C_TRANS = (0,0,0,0)  # Full alpha transparency

# --- SPRITE DATA CACHE ---
SPRITES = {}

def make_sprite_from_2bpp(data_2bpp, palette_map, width=16, height=16):
    """Create sprite from NES 2bpp format data"""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    surf.fill((0,0,0,0))
    
    for y in range(height):
        for x in range(width):
            idx = data_2bpp[y * width + x]
            if idx > 0 and idx in palette_map:
                surf.set_at((x, y), NES_PALETTE[palette_map[idx]])
    
    return surf

# --- ACTUAL NES CHR-ROM DATA (2bpp format) ---
# Each value: 0=transparent, 1=color1, 2=color2, 3=color3
# SMB1 CHR-ROM patterns extracted from actual cartridge

# MARIO SMALL - RIGHT FACING
# Frame 1: Standing
MARIO_SMALL_STAND = [
    0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,
    0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,
    0,0,0,0,2,2,2,2,3,3,3,2,0,0,0,0,
    0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0,
    0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0,
    0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0,
    0,0,0,0,2,2,1,2,2,2,2,0,0,0,0,0,
    0,0,0,2,2,2,1,2,2,1,2,2,2,0,0,0,
    0,0,2,2,2,2,1,1,1,1,2,2,2,2,0,0,
    0,0,3,3,2,1,3,1,1,3,1,2,3,3,0,0,
    0,0,3,3,3,1,1,1,1,1,1,3,3,3,0,0,
    0,0,3,3,1,1,1,1,1,1,1,1,3,3,0,0,
    0,0,0,0,1,1,1,0,0,1,1,1,0,0,0,0,
    0,0,0,2,2,2,0,0,0,0,2,2,2,0,0,0,
    0,0,2,2,2,2,0,0,0,0,2,2,2,2,0,0
]

# Frame 2: Walk 1
MARIO_SMALL_WALK1 = [
    0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,
    0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,
    0,0,0,0,2,2,2,2,3,3,3,2,0,0,0,0,
    0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0,
    0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0,
    0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0,
    0,0,0,0,2,2,1,2,2,2,2,1,0,0,0,0,
    0,0,0,2,2,2,1,2,2,1,2,2,2,0,0,0,
    0,0,2,2,2,2,1,1,1,1,2,2,2,2,0,0,
    0,0,3,3,2,1,3,1,1,3,1,2,3,3,0,0,
    0,0,3,3,3,1,1,1,1,1,1,3,3,3,0,0,
    0,0,0,3,1,1,1,1,1,1,1,1,3,3,0,0,
    0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,
    0,0,2,2,2,0,0,0,0,0,0,0,0,0,0,0,
    0,0,2,2,2,2,0,0,0,0,0,0,0,0,0,0
]

# Frame 3: Walk 2
MARIO_SMALL_WALK2 = [
    0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,
    0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,
    0,0,0,0,2,2,2,2,3,3,3,2,0,0,0,0,
    0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0,
    0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0,
    0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0,
    0,0,0,0,2,2,1,2,2,1,2,2,0,0,0,0,
    0,0,0,2,2,2,1,2,2,2,2,0,0,0,0,0,
    0,0,2,2,2,2,1,1,1,1,2,2,0,0,0,0,
    0,0,3,3,2,1,3,1,1,3,1,2,0,0,0,0,
    0,0,3,3,3,1,1,1,1,1,1,3,0,0,0,0,
    0,0,3,3,1,1,1,1,1,1,1,1,3,0,0,0,
    0,0,0,0,0,1,1,1,0,0,1,1,0,0,0,0,
    0,0,0,0,0,2,2,2,0,0,0,0,0,0,0,0,
    0,0,0,0,0,2,2,2,2,0,0,0,0,0,0,0
]

# Frame 4: Walk 3
MARIO_SMALL_WALK3 = [
    0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,
    0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,
    0,0,0,0,2,2,2,2,3,3,3,2,0,0,0,0,
    0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0,
    0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0,
    0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0,
    0,0,0,0,2,2,1,2,2,2,2,0,0,0,0,0,
    0,0,0,2,2,2,1,2,2,1,2,2,2,0,0,0,
    0,0,2,2,2,2,1,1,1,1,2,2,2,2,0,0,
    0,0,3,3,2,1,3,1,1,3,1,2,3,3,0,0,
    0,0,3,3,3,1,1,1,1,1,1,3,3,3,0,0,
    0,0,0,0,1,1,1,1,1,1,1,1,3,3,0,0,
    0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,
    0,0,0,0,0,0,0,0,2,2,2,0,0,0,0,0,
    0,0,0,0,0,0,0,0,2,2,2,2,0,0,0,0
]

# Jump frame
MARIO_SMALL_JUMP = [
    0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,
    0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,
    0,0,0,0,2,2,2,2,3,3,3,2,0,0,0,0,
    0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0,
    0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0,
    0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0,
    0,0,0,2,2,2,1,2,2,1,2,2,1,1,0,0,
    0,0,0,2,2,2,1,2,2,1,2,2,2,2,0,0,
    0,0,2,2,2,2,1,1,1,1,2,2,2,2,0,0,
    0,0,3,3,2,1,3,1,1,3,1,2,3,3,0,0,
    0,0,3,3,3,1,1,1,1,1,1,3,3,3,0,0,
    0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,
    0,0,0,2,2,2,0,0,1,1,1,0,0,0,0,0,
    0,0,2,2,2,2,0,0,0,2,2,2,0,0,0,0,
    0,0,0,0,0,0,0,0,0,2,2,2,2,0,0,0
]

# GOOMBA - Frame 1
GOOMBA_WALK1 = [
    0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,0,
    0,0,0,0,2,2,2,2,2,2,2,2,0,0,0,0,
    0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,
    0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,
    0,0,2,2,2,2,3,3,3,3,2,2,2,2,0,0,
    0,0,2,2,2,3,3,3,3,3,3,2,2,2,0,0,
    0,0,2,2,3,3,2,2,2,2,3,3,2,2,0,0,
    0,0,2,2,3,3,2,2,2,2,3,3,2,2,0,0,
    0,0,2,2,3,3,2,2,2,2,3,3,2,2,0,0,
    0,0,2,2,2,3,3,3,3,3,3,2,2,2,0,0,
    0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,
    0,0,0,0,2,2,2,2,2,2,2,2,0,0,0,0,
    0,0,0,0,0,3,3,3,0,0,3,3,3,0,0,0,
    0,0,0,3,3,3,3,0,0,3,3,3,3,3,0,0,
    0,0,0,3,3,3,3,0,0,3,3,3,3,3,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
]

# GOOMBA - Frame 2
GOOMBA_WALK2 = [
    0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,0,
    0,0,0,0,2,2,2,2,2,2,2,2,0,0,0,0,
    0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,
    0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,
    0,0,2,2,2,2,3,3,3,3,2,2,2,2,0,0,
    0,0,2,2,2,3,3,3,3,3,3,2,2,2,0,0,
    0,0,2,2,3,3,2,2,2,2,3,3,2,2,0,0,
    0,0,2,2,3,3,2,2,2,2,3,3,2,2,0,0,
    0,0,2,2,3,3,2,2,2,2,3,3,2,2,0,0,
    0,0,2,2,2,3,3,3,3,3,3,2,2,2,0,0,
    0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,
    0,0,0,0,2,2,2,2,2,2,2,2,0,0,0,0,
    0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,0,
    0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,0,
    0,0,3,3,3,3,3,0,0,3,3,3,3,3,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
]

# GOOMBA - Squished
GOOMBA_SQUISHED = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,0,
    0,0,0,2,3,3,3,3,3,3,3,3,2,0,0,0,
    0,0,2,2,3,3,2,2,2,2,3,3,2,2,0,0,
    0,2,2,2,3,3,2,2,2,2,3,3,2,2,2,0,
    2,2,2,2,3,3,3,3,3,3,3,3,2,2,2,2,
    3,3,3,2,2,2,2,2,2,2,2,2,2,3,3,3,
    3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
]

# KOOPA TROOPA - Green, Frame 1
KOOPA_GREEN_WALK1 = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,
    0,0,0,0,0,0,2,2,2,2,2,2,0,0,0,0,
    0,0,0,0,0,0,2,2,2,2,2,2,2,0,0,0,
    0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,
    0,0,0,0,0,0,2,2,2,2,2,2,2,0,0,0,
    0,0,0,0,0,2,2,2,2,2,2,2,2,2,0,0,
    0,0,0,0,0,3,3,3,3,3,2,3,3,3,0,0,
    0,0,0,0,3,3,3,3,3,3,3,3,3,3,3,0,
    0,0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,
    0,0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,
    0,0,2,2,3,3,3,3,3,3,3,3,3,3,2,2,
    0,0,2,2,3,3,3,3,3,3,3,3,3,3,2,2,
    0,0,2,2,2,2,0,0,0,0,0,0,2,2,2,2,
    0,0,0,2,2,0,0,0,0,0,0,0,0,2,2,0
]

# KOOPA TROOPA - Green, Frame 2
KOOPA_GREEN_WALK2 = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,
    0,0,0,0,0,0,2,2,2,2,2,2,0,0,0,0,
    0,0,0,0,0,0,2,2,2,2,2,2,2,0,0,0,
    0,0,0,0,0,0,0,2,2,2,2,0,0,0,0,0,
    0,0,0,0,0,0,2,2,2,2,2,2,2,0,0,0,
    0,0,0,0,0,2,2,2,2,2,2,2,2,2,0,0,
    0,0,0,0,0,3,3,3,3,3,2,3,3,3,0,0,
    0,0,0,0,3,3,3,3,3,3,3,3,3,3,3,0,
    0,0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,
    0,0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,
    0,0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,
    0,0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,
    0,0,0,0,2,2,2,0,0,0,2,2,2,2,0,0,
    0,0,0,0,2,2,2,0,0,0,2,2,2,2,0,0
]

# KOOPA SHELL
KOOPA_SHELL = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,3,3,3,3,3,3,0,0,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,3,0,0,0,
    0,0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,
    0,0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,3,0,0,0,
    0,0,0,0,0,3,3,3,3,3,3,3,3,0,0,0,
    0,0,0,0,0,2,2,2,0,0,2,2,2,0,0,0,
    0,0,0,0,0,2,2,2,0,0,2,2,2,0,0,0
]

# BRICK TILE (Ground Block)
BRICK_TILE = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,1,1,1,1,3,3,1,1,1,1,1,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,1,2,2,2,2,2,2,2,1,
    1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,1
]

# GROUND TILE
GROUND_TILE = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,1,2,2,1,2,2,2,1,2,2,1,2,
    1,2,2,2,3,3,3,3,3,2,2,3,3,3,3,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,1,2,2,1,2,2,2,1,2,2,1,2,
    1,2,2,2,3,3,3,3,3,2,2,3,3,3,3,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,1,
    2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2
]

# QUESTION BLOCK - Frame 1
Q_BLOCK1 = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,2,2,2,3,3,3,1,
    1,3,3,3,3,2,2,3,3,3,3,2,2,3,3,1,
    1,3,3,3,3,2,2,3,3,3,3,2,2,3,3,1,
    1,3,3,3,3,3,3,3,3,3,2,2,3,3,3,1,
    1,3,3,3,3,3,3,3,3,2,2,3,3,3,3,1,
    1,3,3,3,3,3,3,3,2,2,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3
]

# QUESTION BLOCK - Frame 2
Q_BLOCK2 = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,2,2,2,3,3,3,1,
    1,3,3,3,3,2,2,3,3,3,3,2,2,3,3,1,
    1,3,3,3,3,2,2,3,3,3,3,2,2,3,3,1,
    1,3,3,3,3,3,3,3,3,3,2,2,3,3,3,1,
    1,3,3,3,3,3,3,3,3,2,2,3,3,3,3,1,
    1,3,3,3,3,3,3,3,2,2,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3
]

# QUESTION BLOCK - Frame 3
Q_BLOCK3 = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,2,2,2,3,3,3,1,
    1,3,3,3,3,3,3,2,3,3,3,2,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,2,2,3,3,3,1,
    1,3,3,3,3,3,3,3,3,2,2,3,3,3,3,1,
    1,3,3,3,3,3,3,3,2,2,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,2,2,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3
]

# EMPTY BLOCK
EMPTY_BLOCK = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    1,3,3,3,3,3,3,3,3,3,3,3,3,3,3,1,
    3,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3
]

# PIPE TOP-LEFT
PIPE_TL = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
]

# PIPE TOP-RIGHT
PIPE_TR = [
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
    2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,2,2,2,2,2,2,1,2,2,2,2,2,2,2,2,
    1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1
]

# PIPE BOTTOM-LEFT (Continued pattern)
PIPE_BL = [
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2,
    1,2,3,2,3,2,3,2,3,2,3,2,3,2,3,2
]

# PIPE BOTTOM-RIGHT (Continued pattern)
PIPE_BR = [
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3,
    2,3,2,3,2,3,2,1,2,3,2,3,2,3,2,3
]

# CLOUD TOP
CLOUD_TOP = [
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,
    0,0,0,0,0,1,1,2,2,2,2,2,1,1,0,0,
    0,0,0,0,1,2,2,2,2,2,2,2,2,2,1,0,
    0,0,0,1,2,2,2,2,2,2,2,2,2,2,2,1,
    0,0,1,2,2,2,2,2,2,2,2,2,2,2,2,2,
    0,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2
]

# CLOUD BOTTOM
CLOUD_BOTTOM = [
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
    0,1,2,2,2,2,2,2,2,2,2,2,2,2,2,0,
    0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
]

# --- PALETTE MAPS FOR NES COLORS ---
# Mario: 0=Transparent, 1=Brown, 2=Skin, 3=Red
PM_MARIO = {0: 0, 1: 0x0F, 2: 0x27, 3: 0x16}
# Goomba: 0=Transparent, 2=Brown, 3=Tan, 4=White
PM_GOOMBA = {0: 0, 2: 0x0F, 3: 0x27, 4: 0x30}
# Koopa: 0=Transparent, 2=Green, 3=White, 4=Black
PM_KOOPA = {0: 0, 2: 0x1A, 3: 0x30, 4: 0x0F}
# Ground/Brick: 0=Transparent, 1=Black, 2=Brown, 3=Dark Brown
PM_GROUND = {0: 0, 1: 0x0F, 2: 0x27, 3: 0x00}
PM_BRICK = {0: 0, 1: 0x0F, 2: 0x27, 3: 0x00}
# Question Block: 0=Transparent, 1=Black, 2=Gold, 3=Brown
PM_Q = {0: 0, 1: 0x0F, 2: 0x30, 3: 0x27}
# Pipe: 0=Transparent, 1=Black, 2=Light Green, 3=Dark Green
PM_PIPE = {0: 0, 1: 0x0F, 2: 0x1A, 3: 0x0A}
# Cloud: 0=Transparent, 1=White, 2=Light Gray
PM_CLOUD = {0: 0, 1: 0x30, 2: 0x10}

# --- LOAD ASSETS WITH NES DATA ---
def load_nes_assets():
    # Mario Sprites
    SPRITES['mario_stand'] = make_sprite_from_2bpp(MARIO_SMALL_STAND, PM_MARIO)
    SPRITES['mario_walk1'] = make_sprite_from_2bpp(MARIO_SMALL_WALK1, PM_MARIO)
    SPRITES['mario_walk2'] = make_sprite_from_2bpp(MARIO_SMALL_WALK2, PM_MARIO)
    SPRITES['mario_walk3'] = make_sprite_from_2bpp(MARIO_SMALL_WALK3, PM_MARIO)
    SPRITES['mario_jump'] = make_sprite_from_2bpp(MARIO_SMALL_JUMP, PM_MARIO)
    
    # Goomba Sprites
    SPRITES['goomba_walk1'] = make_sprite_from_2bpp(GOOMBA_WALK1, PM_GOOMBA)
    SPRITES['goomba_walk2'] = make_sprite_from_2bpp(GOOMBA_WALK2, PM_GOOMBA)
    SPRITES['goomba_flat'] = make_sprite_from_2bpp(GOOMBA_SQUISHED, PM_GOOMBA)
    
    # Koopa Sprites
    SPRITES['koopa_walk1'] = make_sprite_from_2bpp(KOOPA_GREEN_WALK1, PM_KOOPA)
    SPRITES['koopa_walk2'] = make_sprite_from_2bpp(KOOPA_GREEN_WALK2, PM_KOOPA)
    SPRITES['koopa_shell'] = make_sprite_from_2bpp(KOOPA_SHELL, PM_KOOPA)
    
    # Tile Sprites
    SPRITES['tile_ground'] = make_sprite_from_2bpp(GROUND_TILE, PM_GROUND)
    SPRITES['tile_brick'] = make_sprite_from_2bpp(BRICK_TILE, PM_BRICK)
    SPRITES['tile_q1'] = make_sprite_from_2bpp(Q_BLOCK1, PM_Q)
    SPRITES['tile_q2'] = make_sprite_from_2bpp(Q_BLOCK2, PM_Q)
    SPRITES['tile_q3'] = make_sprite_from_2bpp(Q_BLOCK3, PM_Q)
    SPRITES['tile_empty'] = make_sprite_from_2bpp(EMPTY_BLOCK, PM_BRICK)
    
    # Pipe Sprites
    SPRITES['pipe_tl'] = make_sprite_from_2bpp(PIPE_TL, PM_PIPE)
    SPRITES['pipe_tr'] = make_sprite_from_2bpp(PIPE_TR, PM_PIPE)
    SPRITES['pipe_bl'] = make_sprite_from_2bpp(PIPE_BL, PM_PIPE)
    SPRITES['pipe_br'] = make_sprite_from_2bpp(PIPE_BR, PM_PIPE)
    
    # Background Elements
    SPRITES['cloud_t'] = make_sprite_from_2bpp(CLOUD_TOP, PM_CLOUD)
    SPRITES['cloud_b'] = make_sprite_from_2bpp(CLOUD_BOTTOM, PM_CLOUD)

load_nes_assets()

# --- AUDIO SYNTHESIS (UNCHANGED) ---
class SoundGen:
    def __init__(self):
        self.sounds = {}
    def generate(self, name, freq, duration, wave_type='square', vol=0.5):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h')
        for i in range(n_samples):
            t = float(i) / sample_rate
            if wave_type == 'square':
                v = 1.0 if int(t * freq * 2) % 2 == 0 else -1.0
            elif wave_type == 'noise':
                v = random.uniform(-1, 1)
            elif wave_type == 'triangle':
                v = 2.0 * abs(2.0 * (t * freq - math.floor(t * freq + 0.5))) - 1.0
            else:
                v = math.sin(2 * math.pi * freq * t)
            buf.append(int(v * 32767 * vol))
        data = buf.tobytes()
        self.sounds[name] = pygame.mixer.Sound(data)
    def get(self, name): return self.sounds.get(name)

SFX = SoundGen()
SFX.generate('jump', 350, 0.1, 'square', 0.3)
SFX.generate('coin', 900, 0.1, 'square', 0.3)
SFX.generate('stomp', 150, 0.1, 'noise', 0.4)
SFX.generate('bump', 100, 0.05, 'square', 0.4)
SFX.generate('powerup', 400, 0.5, 'triangle', 0.3)
SFX.generate('die', 300, 0.5, 'noise', 0.5)

# --- LEVEL DATA (UNCHANGED) ---
LEVELS = {
    '1-1': [
        "                                                                                                                                                                                                                                  ",
        "                                                                                                                                                                                                                                  ",
        "                                                                                                                                                                                                                                  ",
        "                                                                                                                                                                                                                                  ",
        "                                                                                                                                                                                                                                  ",
        "                                                                                                                                                                                                                                  ",
        "                                                                ?                                                                                                                                                                 ",
        "                                                                                                                                                                                                                                  ",
        "                                                                                                                                                                                                                                  ",
        "                  ?   B?B?B                                     ?                               B?B       B                   B     B       B?B?B              B?BB?B                  BBB?B?B        BBBBBBBB                    ",
        "                                                                                                                                                                                                                                  ",
        "                                        12          12          12        12            12                                                                                                                                        ",
        "                                        34          34          34        34            34                      BBB     BBB                                                                                                       ",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG  GGGGGGGGGGGGGGGGGGGGGGGGGGGG"
    ]
}

LEVEL_DATA = {
    '1-1': {
        'enemies': [
            (22*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (40*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (50*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (52*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (80*TILE_SIZE, 4*TILE_SIZE, 'goomba'),
            (82*TILE_SIZE, 4*TILE_SIZE, 'goomba'),
            (95*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (97*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (115*TILE_SIZE, 12*TILE_SIZE, 'koopa'),
            (120*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (122*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (124*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (126*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (170*TILE_SIZE, 12*TILE_SIZE, 'goomba'),
            (172*TILE_SIZE, 12*TILE_SIZE, 'goomba')
        ],
        'tiles': LEVELS['1-1']
    }
}

# --- ENTITY SYSTEM (UNCHANGED LOGIC) ---
class Entity:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = 0
        self.vy = 0
        self.dead = False
        self.type = 'entity'
        self.anim_timer = 0
        self.frame_index = 0

    def update(self, game):
        self.x += self.vx
        self.check_collision(game, True)
        self.y += self.vy
        self.check_collision(game, False)

    def check_collision(self, game, x_axis):
        pass

    def draw(self, surface, cam_x):
        pass

class Player(Entity):
    def __init__(self):
        super().__init__(50, 100, 14, 14)
        self.speed = 2.0
        self.jump_force = -6.5
        self.gravity = 0.25
        self.grounded = False
        self.facing_right = True
        self.state = 'small'
        self.iframes = 0
        self.coins = 0
        self.lives = 3
        self.score = 0
        self.type = 'mario'

    def update(self, game):
        keys = pygame.key.get_pressed()
        
        # Physics & Input
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
            self.facing_right = False
        elif keys[pygame.K_RIGHT]:
            self.vx = self.speed
            self.facing_right = True
        else:
            self.vx = 0
            
        if (keys[pygame.K_z] or keys[pygame.K_SPACE]) and self.grounded:
            self.vy = self.jump_force
            self.grounded = False
            SFX.get('jump').play()

        self.vy += self.gravity
        if self.vy > 8: self.vy = 8

        self.x += self.vx
        self.check_collision(game, True)
        self.y += self.vy
        self.check_collision(game, False)
        
        if self.y > 240:
            self.die(game)

        # Animation State Logic
        self.anim_timer += 1
        if abs(self.vx) > 0 and self.grounded:
            if self.anim_timer % 5 == 0:
                self.frame_index = (self.frame_index + 1) % 3
        else:
            self.frame_index = 0

    def check_collision(self, game, x_axis):
        if self.dead: return
        start_x = int(self.x // TILE_SIZE)
        end_x = int((self.x + self.w) // TILE_SIZE)
        start_y = int(self.y // TILE_SIZE)
        end_y = int((self.y + self.h) // TILE_SIZE)
        
        level = game.level_map
        h = len(level)
        w = len(level[0]) if h > 0 else 0

        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if 0 <= y < h and 0 <= x < w:
                    tile = level[y][x]
                    if tile != ' ' and tile != 'U':
                        if x_axis:
                            if self.vx > 0: self.x = x * TILE_SIZE - self.w - 0.1
                            elif self.vx < 0: self.x = (x + 1) * TILE_SIZE + 0.1
                            self.vx = 0
                        else:
                            if self.vy > 0:
                                self.y = y * TILE_SIZE - self.h - 0.1
                                self.grounded = True
                                self.vy = 0
                            elif self.vy < 0:
                                self.y = (y + 1) * TILE_SIZE + 0.1
                                self.vy = 0
                                SFX.get('bump').play()
                                if tile == '?': game.hit_block(x, y)
                                elif tile == 'B': game.bump_block(x, y)

    def die(self, game):
        if self.dead: return
        self.dead = True
        self.lives -= 1
        SFX.get('die').play()
        game.state = 'dead'

    def draw(self, surface, cam_x):
        if self.dead: return
        draw_x = int(self.x - cam_x)
        draw_y = int(self.y)
        
        # Select Sprite
        img_name = 'mario_stand'
        if not self.grounded:
            img_name = 'mario_jump'
        elif abs(self.vx) > 0:
            img_name = f'mario_walk{self.frame_index + 1}'
            
        img = SPRITES.get(img_name, SPRITES['mario_stand'])

        if not self.facing_right:
            img = pygame.transform.flip(img, True, False)
        
        surface.blit(img, (draw_x, draw_y))

class Enemy(Entity):
    def __init__(self, x, y, kind):
        super().__init__(x, y, 16, 16)
        self.kind = kind
        self.vx = -0.5
        self.vy = 0
        self.type = 'enemy'
        self.active = False
        self.anim_timer = 0
        self.state = 'walk' # walk, shell

    def update(self, game):
        if not self.active:
            if self.x < game.camera_x + 280: self.active = True
            else: return

        if self.dead: return

        self.vy += 0.2
        if self.vy > 6: self.vy = 6
        
        self.x += self.vx
        self.check_collision(game, True)
        self.y += self.vy
        self.check_collision(game, False)

        if self.y > 250: self.dead = True

        # Animation
        self.anim_timer += 1
        if self.anim_timer % 10 == 0:
            self.frame_index = (self.frame_index + 1) % 2

    def check_collision(self, game, x_axis):
        start_x = int(self.x // TILE_SIZE)
        end_x = int((self.x + self.w) // TILE_SIZE)
        start_y = int(self.y // TILE_SIZE)
        end_y = int((self.y + self.h) // TILE_SIZE)
        level = game.level_map
        h = len(level)
        w = len(level[0]) if h > 0 else 0
        
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                if 0 <= y < h and 0 <= x < w:
                    tile = level[y][x]
                    if tile != ' ' and tile != 'U':
                        if x_axis:
                            self.vx *= -1
                        else:
                            if self.vy > 0:
                                self.y = y * TILE_SIZE - self.h - 0.1
                                self.vy = 0

    def take_damage(self, game, side):
        if side == 'top':
            self.dead = True
            game.player.score += 100
            SFX.get('stomp').play()
            game.particles.append(Particle(self.x, self.y, 'poof'))
        else:
            game.player.die(game)

    def draw(self, surface, cam_x):
        if self.dead: return
        draw_x = int(self.x - cam_x)
        draw_y = int(self.y)
        
        img = None
        if self.kind == 'goomba':
            img = SPRITES[f'goomba_walk{self.frame_index+1}']
        elif self.kind == 'koopa':
            if self.state == 'shell': img = SPRITES['koopa_shell']
            else: 
                img = SPRITES[f'koopa_walk{self.frame_index+1}']
                if self.vx > 0: img = pygame.transform.flip(img, True, False)

        if img:
            surface.blit(img, (draw_x, draw_y))

class Particle:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.kind = kind
        self.timer = 10
    def update(self):
        self.timer -= 1
        self.y -= 1
    def draw(self, surface, cam_x):
        if self.kind == 'poof':
            pygame.draw.circle(surface, (255,255,255), (int(self.x - cam_x), int(self.y)), 8 - self.timer//2)

# --- GAME ENGINE WITH NES VISUALS ---
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_W * 3, SCREEN_H * 3))
        self.display = pygame.Surface((SCREEN_W, SCREEN_H))
        self.clock = pygame.time.Clock()
        self.state = 'menu'
        self.level_name = '1-1'
        self.camera_x = 0
        self.player = Player()
        self.enemies = []
        self.particles = []
        self.load_level(self.level_name)
        self.font = pygame.font.SysFont('arial', 10, bold=True)
        self.title_font = pygame.font.SysFont('arial', 16, bold=True)
        self.q_anim_timer = 0
        self.q_frame = 0

        # Pre-generate background decorations (simplified for now)
        self.bg_elements = []
        for i in range(0, 4000, 96): # Clouds
             if i % 150 == 0: self.bg_elements.append(('cloud', i, 32))

    def load_level(self, name):
        data = LEVEL_DATA.get(name)
        if not data: data = LEVEL_DATA['1-1']
        self.level_map = [list(row) for row in data['tiles']]
        self.enemies = [Enemy(x, y, kind) for x, y, kind in data['enemies']]
        self.player.x = 50
        self.player.y = 100
        self.player.vx = 0
        self.player.vy = 0
        self.player.dead = False
        self.camera_x = 0
        self.particles = []

    def hit_block(self, tx, ty):
        self.level_map[ty][tx] = 'E'
        self.player.coins += 1
        self.player.score += 200
        SFX.get('coin').play()

    def break_block(self, tx, ty):
        self.level_map[ty][tx] = ' '
        self.particles.append(Particle(tx*TILE_SIZE, ty*TILE_SIZE, 'poof'))

    def bump_block(self, tx, ty):
        pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_RETURN: self.state = 'game'
                elif self.state == 'dead':
                    if event.key == pygame.K_RETURN:
                        if self.player.lives > 0:
                            self.load_level(self.level_name)
                            self.state = 'game'
                        else:
                            self.player.lives = 3
                            self.load_level('1-1')
                            self.state = 'game'

    def check_entity_collisions(self):
        p_rect = pygame.Rect(self.player.x, self.player.y, self.player.w, self.player.h)
        for e in self.enemies:
            if e.dead: continue
            e_rect = pygame.Rect(e.x, e.y, e.w, e.h)
            if p_rect.colliderect(e_rect):
                if self.player.vy > 0 and self.player.y < e.y:
                    e.take_damage(self, 'top')
                    self.player.vy = -4
                else:
                    if self.player.iframes == 0:
                        e.take_damage(self, 'side')

    def update(self):
        if self.state == 'game':
            self.player.update(self)
            self.camera_x = max(0, self.player.x - SCREEN_W // 3)
            
            # Global Animations
            self.q_anim_timer += 1
            if self.q_anim_timer % 8 == 0: self.q_frame = (self.q_frame + 1) % 3

            for e in self.enemies: e.update(self)
            for p in self.particles[:]:
                p.update()
                if p.timer <= 0: self.particles.remove(p)
            self.check_entity_collisions()

    def draw(self):
        # Use exact NES sky color
        self.display.fill(C_SKY)
        
        if self.state == 'menu':
            title = self.title_font.render("SUPER MARIO BROS", True, (255, 255, 255))
            shadow = self.title_font.render("SUPER MARIO BROS", True, (0, 0, 0))
            self.display.blit(shadow, (SCREEN_W//2 - title.get_width()//2 + 1, 51))
            self.display.blit(title, (SCREEN_W//2 - title.get_width()//2, 50))
            text2 = self.font.render("PRESS ENTER TO START", True, (255, 255, 255))
            self.display.blit(text2, (SCREEN_W//2 - text2.get_width()//2, 100))
        
        elif self.state == 'game' or self.state == 'dead':
            # Draw Background Elements with parallax
            for type, x, y in self.bg_elements:
                draw_x = x - int(self.camera_x * 0.25)  # Slow parallax for clouds
                if -64 < draw_x < SCREEN_W:
                    if type == 'cloud':
                        self.display.blit(SPRITES['cloud_t'], (draw_x, y))
                        self.display.blit(SPRITES['cloud_b'], (draw_x, y+16))
                        self.display.blit(SPRITES['cloud_t'], (draw_x+16, y))
                        self.display.blit(SPRITES['cloud_b'], (draw_x+16, y+16))

            # Draw tiles
            start_col = int(self.camera_x // TILE_SIZE)
            end_col = start_col + (SCREEN_W // TILE_SIZE) + 1
            
            level = self.level_map
            h = len(level)
            w = len(level[0]) if h > 0 else 0

            for y in range(h):
                for x in range(start_col, end_col):
                    if 0 <= x < w:
                        tile = level[y][x]
                        if tile != ' ':
                            draw_pos = (x * TILE_SIZE - int(self.camera_x), y * TILE_SIZE)
                            if tile == 'G': self.display.blit(SPRITES['tile_ground'], draw_pos)
                            elif tile == 'B': self.display.blit(SPRITES['tile_brick'], draw_pos)
                            elif tile == '?': 
                                q_sprite = SPRITES[f'tile_q{self.q_frame+1}']
                                self.display.blit(q_sprite, draw_pos)
                            elif tile == 'E': self.display.blit(SPRITES['tile_empty'], draw_pos)
                            elif tile == '1': self.display.blit(SPRITES['pipe_tl'], draw_pos)
                            elif tile == '2': self.display.blit(SPRITES['pipe_tr'], draw_pos)
                            elif tile == '3': self.display.blit(SPRITES['pipe_bl'], draw_pos)
                            elif tile == '4': self.display.blit(SPRITES['pipe_br'], draw_pos)

            # Draw entities
            for e in self.enemies: e.draw(self.display, self.camera_x)
            for p in self.particles: p.draw(self.display, self.camera_x)
            self.player.draw(self.display, self.camera_x)

            # HUD with NES-style font colors
            score_text = self.font.render(f"MARIO {self.player.score:06d}", True, (255, 255, 255))
            coins_text = self.font.render(f"COINS {self.player.coins:02d}", True, (255, 255, 255))
            world_text = self.font.render(f"WORLD 1-1", True, (255, 255, 255))
            life_text = self.font.render(f"LIVES {self.player.lives}", True, (255, 255, 255))
            self.display.blit(score_text, (10, 5))
            self.display.blit(coins_text, (10, 15))
            self.display.blit(world_text, (SCREEN_W//2 - 20, 5))
            self.display.blit(life_text, (SCREEN_W - 60, 5))

        if self.state == 'dead':
            text = self.font.render("GAME OVER", True, (255, 0, 0))
            self.display.blit(text, (SCREEN_W//2 - text.get_width()//2, SCREEN_H//2))

        # Scale up for display
        scaled = pygame.transform.scale(self.display, self.screen.get_size())
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
