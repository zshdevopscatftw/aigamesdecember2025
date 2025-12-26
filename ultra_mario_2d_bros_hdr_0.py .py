#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS
By Flames Co. / Team Flames / Samsoft
600x400 @ 60 FPS - NES Speed Accurate
All Worlds: 1-1 to 8-4 + Minus World
"""

import pygame
import sys
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()
try:
    pygame.mixer.init()
    AUDIO_ENABLED = True
except:
    AUDIO_ENABLED = False

# Constants - NES Style
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
TILE_SIZE = 25
FPS = 60

# NES Accurate Physics
GRAVITY = 0.4
MARIO_WALK_SPEED = 2.5
MARIO_RUN_SPEED = 4.0
MARIO_JUMP_FORCE = -9.5
MARIO_MAX_FALL = 8.0
ENEMY_SPEED = 1.0

# Colors (NES Palette)
SKY_BLUE = (92, 148, 252)
UNDERGROUND_BG = (0, 0, 0)
CASTLE_BG = (0, 0, 0)
UNDERWATER_BG = (0, 80, 160)
NIGHT_SKY = (0, 0, 64)
BRICK_COLOR = (200, 76, 12)
BRICK_DARK = (136, 52, 8)
QUESTION_COLOR = (252, 152, 56)
QUESTION_DARK = (200, 100, 20)
GROUND_COLOR = (228, 92, 16)
GROUND_DARK = (136, 52, 8)
PIPE_GREEN = (0, 168, 0)
PIPE_DARK = (0, 120, 0)
MARIO_RED = (228, 0, 32)
MARIO_SKIN = (252, 188, 148)
MARIO_BROWN = (136, 52, 8)
GOOMBA_BROWN = (172, 100, 44)
KOOPA_GREEN = (0, 168, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COIN_GOLD = (252, 188, 60)
FLAG_GREEN = (0, 168, 0)
LAVA_RED = (252, 60, 0)
LAVA_ORANGE = (252, 152, 56)
CLOUD_WHITE = (252, 252, 252)
BUSH_GREEN = (0, 168, 68)

# Game States
class GameState(Enum):
    MAIN_MENU = 0
    WORLD_SELECT = 1
    PLAYING = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4
    PAUSED = 5

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ultra Mario 2D Bros - Flames Co.")
clock = pygame.time.Clock()

# Fonts
try:
    font_large = pygame.font.Font(None, 56)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 18)
except:
    font_large = pygame.font.SysFont('arial', 56)
    font_medium = pygame.font.SysFont('arial', 36)
    font_small = pygame.font.SysFont('arial', 24)
    font_tiny = pygame.font.SysFont('arial', 18)


class SoundManager:
    """Generates simple sound effects"""
    def __init__(self):
        self.enabled = AUDIO_ENABLED
        if not self.enabled:
            return
        try:
            self.jump_sound = self.generate_beep(440, 100)
            self.coin_sound = self.generate_beep(880, 50)
            self.stomp_sound = self.generate_beep(220, 80)
            self.powerup_sound = self.generate_beep(660, 150)
            self.death_sound = self.generate_beep(110, 500)
            self.flag_sound = self.generate_beep(550, 200)
        except:
            self.enabled = False
    
    def generate_beep(self, frequency, duration):
        sample_rate = 22050
        n_samples = int(sample_rate * duration / 1000)
        buf = bytes([int(128 + 127 * (((i * frequency) % sample_rate) < sample_rate // 2)) for i in range(n_samples)])
        return pygame.mixer.Sound(buffer=buf)
    
    def play(self, sound_name):
        if not self.enabled:
            return
        sounds = {
            'jump': self.jump_sound,
            'coin': self.coin_sound,
            'stomp': self.stomp_sound,
            'powerup': self.powerup_sound,
            'death': self.death_sound,
            'flag': self.flag_sound
        }
        if sound_name in sounds:
            sounds[sound_name].play()


class Mario(pygame.sprite.Sprite):
    """Player character with NES-accurate physics"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 20
        self.height = 24
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.running = False
        
        # State
        self.is_big = False
        self.has_fire = False
        self.invincible = 0
        self.star_power = 0
        self.lives = 3
        self.coins = 0
        self.score = 0
        
        # Animation
        self.anim_frame = 0
        self.anim_timer = 0
        
        self.draw_mario()
    
    def draw_mario(self):
        """Draw Mario sprite"""
        self.image.fill((0, 0, 0, 0))
        
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
        
        body_color = MARIO_RED
        if self.star_power > 0:
            colors = [MARIO_RED, (252, 188, 60), (0, 168, 0), (252, 252, 252)]
            body_color = colors[(self.star_power // 4) % 4]
        elif self.has_fire:
            body_color = WHITE
        
        # Head
        pygame.draw.rect(self.image, MARIO_SKIN, (5, 2, 10, 8))
        # Hair
        pygame.draw.rect(self.image, MARIO_BROWN, (5, 0, 10, 4))
        # Hat
        pygame.draw.rect(self.image, body_color, (3, 0, 14, 3))
        # Body
        pygame.draw.rect(self.image, body_color, (4, 10, 12, 8))
        # Overalls
        pygame.draw.rect(self.image, (0, 0, 200), (5, 14, 10, 6))
        # Legs
        if self.on_ground and abs(self.vel_x) > 0.5:
            offset = 2 if self.anim_frame % 2 == 0 else -2
            pygame.draw.rect(self.image, MARIO_BROWN, (4 + offset, 20, 5, 4))
            pygame.draw.rect(self.image, MARIO_BROWN, (11 - offset, 20, 5, 4))
        else:
            pygame.draw.rect(self.image, MARIO_BROWN, (4, 20, 5, 4))
            pygame.draw.rect(self.image, MARIO_BROWN, (11, 20, 5, 4))
    
    def update(self, keys, tiles, enemies, items):
        target_speed = MARIO_RUN_SPEED if self.running else MARIO_WALK_SPEED
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = max(self.vel_x - 0.15, -target_speed)
            self.facing_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = min(self.vel_x + 0.15, target_speed)
            self.facing_right = True
        else:
            if self.on_ground:
                self.vel_x *= 0.85
            else:
                self.vel_x *= 0.95
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0
        
        self.vel_y = min(self.vel_y + GRAVITY, MARIO_MAX_FALL)
        
        self.rect.x += int(self.vel_x)
        self.collide_horizontal(tiles)
        
        self.rect.y += int(self.vel_y)
        self.on_ground = False
        self.collide_vertical(tiles)
        
        self.anim_timer += 1
        if self.anim_timer > 6:
            self.anim_timer = 0
            self.anim_frame += 1
        
        if self.invincible > 0:
            self.invincible -= 1
        if self.star_power > 0:
            self.star_power -= 1
        
        self.draw_mario()
    
    def jump(self, sound_manager):
        if self.on_ground:
            self.vel_y = MARIO_JUMP_FORCE
            self.on_ground = False
            sound_manager.play('jump')
    
    def collide_horizontal(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel_x < 0:
                    self.rect.left = tile.rect.right
                self.vel_x = 0
    
    def collide_vertical(self, tiles):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                    self.vel_y = 0
                elif self.vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0
                    if hasattr(tile, 'hit'):
                        tile.hit()
    
    def take_damage(self, sound_manager):
        if self.invincible > 0 or self.star_power > 0:
            return False
        
        if self.has_fire:
            self.has_fire = False
            self.invincible = 120
            return False
        elif self.is_big:
            self.is_big = False
            self.invincible = 120
            return False
        else:
            self.lives -= 1
            sound_manager.play('death')
            return True


class Tile(pygame.sprite.Sprite):
    """Basic tile class"""
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tile_type = tile_type
        self.draw_tile()
    
    def draw_tile(self):
        if self.tile_type == 'ground':
            self.image.fill(GROUND_COLOR)
            pygame.draw.line(self.image, GROUND_DARK, (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 2)
            pygame.draw.line(self.image, GROUND_DARK, (TILE_SIZE//2, 0), (TILE_SIZE//2, TILE_SIZE//2), 2)
            pygame.draw.line(self.image, GROUND_DARK, (0, TILE_SIZE//2), (0, TILE_SIZE), 2)
            pygame.draw.line(self.image, GROUND_DARK, (TILE_SIZE-1, TILE_SIZE//2), (TILE_SIZE-1, TILE_SIZE), 2)
        elif self.tile_type == 'brick':
            self.image.fill(BRICK_COLOR)
            pygame.draw.rect(self.image, BRICK_DARK, (0, 0, TILE_SIZE, TILE_SIZE), 2)
            pygame.draw.line(self.image, BRICK_DARK, (0, TILE_SIZE//2), (TILE_SIZE, TILE_SIZE//2), 1)
            pygame.draw.line(self.image, BRICK_DARK, (TILE_SIZE//3, 0), (TILE_SIZE//3, TILE_SIZE//2), 1)
            pygame.draw.line(self.image, BRICK_DARK, (2*TILE_SIZE//3, TILE_SIZE//2), (2*TILE_SIZE//3, TILE_SIZE), 1)
        elif self.tile_type == 'stone':
            self.image.fill((128, 128, 128))
            pygame.draw.rect(self.image, (80, 80, 80), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        elif self.tile_type == 'castle_brick':
            self.image.fill((80, 80, 80))
            pygame.draw.rect(self.image, (60, 60, 60), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        elif self.tile_type == 'ice':
            self.image.fill((180, 220, 255))
            pygame.draw.rect(self.image, (140, 180, 220), (0, 0, TILE_SIZE, TILE_SIZE), 2)
        elif self.tile_type == 'snow_ground':
            self.image.fill((240, 240, 255))
            pygame.draw.rect(self.image, (200, 200, 220), (0, 0, TILE_SIZE, TILE_SIZE), 2)


class QuestionBlock(Tile):
    """? Block with items"""
    def __init__(self, x, y, contents='coin'):
        self.contents = contents
        self.is_empty = False
        self.anim_offset = random.randint(0, 20)
        super().__init__(x, y, 'question')
    
    def draw_tile(self):
        if self.is_empty:
            self.image.fill((128, 80, 40))
        else:
            self.image.fill(QUESTION_COLOR)
            pygame.draw.rect(self.image, QUESTION_DARK, (0, 0, TILE_SIZE, TILE_SIZE), 3)
            pygame.draw.rect(self.image, WHITE, (9, 6, 7, 3))
            pygame.draw.rect(self.image, WHITE, (13, 9, 3, 5))
            pygame.draw.rect(self.image, WHITE, (9, 12, 7, 3))
            pygame.draw.rect(self.image, WHITE, (9, 12, 3, 3))
            pygame.draw.rect(self.image, WHITE, (11, 18, 3, 3))
    
    def hit(self):
        if not self.is_empty:
            self.is_empty = True
            self.draw_tile()
            return self.contents
        return None


class Pipe(pygame.sprite.Sprite):
    """Warp pipe"""
    def __init__(self, x, y, height=2, warp_to=None):
        super().__init__()
        self.width = TILE_SIZE * 2
        self.height = TILE_SIZE * height
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.warp_to = warp_to
        self.draw_pipe()
    
    def draw_pipe(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, PIPE_GREEN, (4, TILE_SIZE//2, self.width-8, self.height-TILE_SIZE//2))
        pygame.draw.rect(self.image, PIPE_DARK, (4, TILE_SIZE//2, 6, self.height-TILE_SIZE//2))
        pygame.draw.rect(self.image, PIPE_GREEN, (0, 0, self.width, TILE_SIZE//2+4))
        pygame.draw.rect(self.image, PIPE_DARK, (0, 0, 6, TILE_SIZE//2+4))


class Enemy(pygame.sprite.Sprite):
    """Base enemy class"""
    def __init__(self, x, y, enemy_type='goomba'):
        super().__init__()
        self.width = 24
        self.height = 24
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.enemy_type = enemy_type
        self.vel_x = -ENEMY_SPEED
        self.vel_y = 0
        self.alive = True
        self.squish_timer = 0
        self.anim_frame = 0
        self.draw_enemy()
    
    def draw_enemy(self):
        self.image.fill((0, 0, 0, 0))
        
        if not self.alive:
            if self.enemy_type == 'goomba':
                pygame.draw.ellipse(self.image, GOOMBA_BROWN, (2, 16, 20, 8))
            return
        
        if self.enemy_type == 'goomba':
            pygame.draw.ellipse(self.image, GOOMBA_BROWN, (2, 8, 20, 14))
            offset = 2 if self.anim_frame % 2 == 0 else -2
            pygame.draw.ellipse(self.image, BLACK, (2 + offset, 18, 8, 6))
            pygame.draw.ellipse(self.image, BLACK, (14 - offset, 18, 8, 6))
            pygame.draw.ellipse(self.image, BLACK, (4, 10, 5, 5))
            pygame.draw.ellipse(self.image, BLACK, (15, 10, 5, 5))
            pygame.draw.line(self.image, BLACK, (4, 8), (9, 10), 2)
            pygame.draw.line(self.image, BLACK, (15, 10), (20, 8), 2)
        
        elif self.enemy_type == 'koopa':
            pygame.draw.ellipse(self.image, KOOPA_GREEN, (4, 8, 16, 14))
            pygame.draw.ellipse(self.image, (0, 200, 0), (6, 10, 12, 10))
            pygame.draw.ellipse(self.image, (252, 228, 160), (0, 4, 10, 10))
            pygame.draw.circle(self.image, BLACK, (4, 8), 2)
            pygame.draw.ellipse(self.image, (252, 228, 160), (4, 20, 6, 4))
            pygame.draw.ellipse(self.image, (252, 228, 160), (14, 20, 6, 4))
        
        elif self.enemy_type == 'buzzy':
            pygame.draw.ellipse(self.image, (40, 40, 80), (2, 6, 20, 16))
            pygame.draw.ellipse(self.image, (60, 60, 100), (4, 8, 16, 12))
            pygame.draw.ellipse(self.image, WHITE, (4, 10, 5, 5))
            pygame.draw.ellipse(self.image, WHITE, (15, 10, 5, 5))
        
        elif self.enemy_type == 'spiny':
            pygame.draw.ellipse(self.image, (200, 50, 50), (2, 10, 20, 12))
            for i in range(5):
                pygame.draw.polygon(self.image, (200, 50, 50), [
                    (4 + i*4, 10), (6 + i*4, 2), (8 + i*4, 10)
                ])
    
    def update(self, tiles):
        if not self.alive:
            self.squish_timer -= 1
            if self.squish_timer <= 0:
                self.kill()
            return
        
        self.vel_y = min(self.vel_y + GRAVITY, MARIO_MAX_FALL)
        
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0
                elif self.vel_x > 0:
                    self.rect.right = tile.rect.left
                    self.vel_x = -ENEMY_SPEED
                elif self.vel_x < 0:
                    self.rect.left = tile.rect.right
                    self.vel_x = ENEMY_SPEED
        
        self.anim_frame += 1
        if self.anim_frame > 10:
            self.anim_frame = 0
            self.draw_enemy()
    
    def stomp(self):
        if self.enemy_type == 'spiny':
            return -1
        self.alive = False
        self.squish_timer = 30
        self.draw_enemy()
        return 100


class Coin(pygame.sprite.Sprite):
    """Collectible coin"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.anim_frame = 0
        self.draw_coin()
    
    def draw_coin(self):
        self.image.fill((0, 0, 0, 0))
        widths = [14, 10, 4, 10, 14, 10, 4, 10]
        w = widths[self.anim_frame % 8]
        x_offset = (16 - w) // 2
        pygame.draw.ellipse(self.image, COIN_GOLD, (x_offset, 2, w, 12))
        if w > 6:
            pygame.draw.ellipse(self.image, (200, 140, 40), (x_offset + 2, 4, w - 4, 8))
    
    def update(self):
        self.anim_frame += 1
        if self.anim_frame % 6 == 0:
            self.draw_coin()


class FlagPole(pygame.sprite.Sprite):
    """End-of-level flag"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, TILE_SIZE * 8), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.flag_y = 10
        self.reached = False
        self.draw_flag()
    
    def draw_flag(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, (100, 100, 100), (8, 0, 4, TILE_SIZE * 8))
        pygame.draw.circle(self.image, (0, 200, 0), (10, 6), 6)
        pygame.draw.polygon(self.image, FLAG_GREEN, [
            (12, self.flag_y),
            (12, self.flag_y + 20),
            (0, self.flag_y + 10)
        ])
    
    def lower_flag(self):
        if self.flag_y < TILE_SIZE * 6:
            self.flag_y += 2
            self.draw_flag()
            return False
        return True


class Castle(pygame.sprite.Sprite):
    """End castle"""
    def __init__(self, x, y):
        super().__init__()
        self.width = TILE_SIZE * 5
        self.height = TILE_SIZE * 4
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw_castle()
    
    def draw_castle(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, (128, 128, 128), (0, TILE_SIZE, self.width, self.height - TILE_SIZE))
        pygame.draw.rect(self.image, BLACK, (self.width//2 - 12, self.height - 30, 24, 30))
        for i in range(5):
            pygame.draw.rect(self.image, (128, 128, 128), (i * TILE_SIZE + 2, 0, TILE_SIZE - 4, TILE_SIZE))
        pygame.draw.rect(self.image, BLACK, (self.width//2 - 8, TILE_SIZE + 10, 16, 16))


class Cloud(pygame.sprite.Sprite):
    """Background cloud"""
    def __init__(self, x, y, size=1):
        super().__init__()
        self.width = 40 * size
        self.height = 20 * size
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.draw_cloud(size)
    
    def draw_cloud(self, size):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.ellipse(self.image, CLOUD_WHITE, (0, 5*size, 20*size, 15*size))
        pygame.draw.ellipse(self.image, CLOUD_WHITE, (10*size, 0, 20*size, 20*size))
        pygame.draw.ellipse(self.image, CLOUD_WHITE, (20*size, 5*size, 20*size, 15*size))


class Level:
    """Level class holding all level data and objects"""
    def __init__(self, level_data, bg_color=SKY_BLUE):
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.pipes = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.flag = None
        self.castle = None
        self.bg_color = bg_color
        self.width = 0
        self.mario_start = (50, 300)
        
        self.load_level(level_data)
        self.generate_clouds()
    
    def generate_clouds(self):
        if self.bg_color not in [SKY_BLUE, NIGHT_SKY]:
            return
        for i in range(self.width // 200):
            x = i * 200 + random.randint(0, 100)
            y = random.randint(30, 100)
            size = random.choice([1, 2])
            self.clouds.add(Cloud(x, y, size))
    
    def load_level(self, level_data):
        """Parse level string and create objects"""
        lines = level_data.strip().split('\n')
        self.width = len(lines[0]) * TILE_SIZE if lines else SCREEN_WIDTH
        
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                px = x * TILE_SIZE
                py = y * TILE_SIZE
                
                if char == '#':
                    self.tiles.add(Tile(px, py, 'ground'))
                elif char == 'B':
                    self.tiles.add(Tile(px, py, 'brick'))
                elif char == '?':
                    self.tiles.add(QuestionBlock(px, py, 'coin'))
                elif char == '!':
                    self.tiles.add(QuestionBlock(px, py, 'mushroom'))
                elif char == 'S':
                    self.tiles.add(Tile(px, py, 'stone'))
                elif char == 'I':
                    self.tiles.add(Tile(px, py, 'ice'))
                elif char == 'W':
                    self.tiles.add(Tile(px, py, 'snow_ground'))
                elif char == 'G':
                    self.enemies.add(Enemy(px, py, 'goomba'))
                elif char == 'K':
                    self.enemies.add(Enemy(px, py, 'koopa'))
                elif char == 'Z':
                    self.enemies.add(Enemy(px, py, 'buzzy'))
                elif char == 'Y':
                    self.enemies.add(Enemy(px, py, 'spiny'))
                elif char == 'C':
                    self.coins.add(Coin(px, py))
                elif char == 'P':
                    pipe = Pipe(px, py - TILE_SIZE, 2)
                    self.pipes.add(pipe)
                    self.tiles.add(Tile(px, py - TILE_SIZE, 'stone'))
                    self.tiles.add(Tile(px + TILE_SIZE, py - TILE_SIZE, 'stone'))
                    self.tiles.add(Tile(px, py, 'stone'))
                    self.tiles.add(Tile(px + TILE_SIZE, py, 'stone'))
                elif char == 'p':
                    pipe = Pipe(px, py - TILE_SIZE * 2, 3)
                    self.pipes.add(pipe)
                    for i in range(3):
                        self.tiles.add(Tile(px, py - TILE_SIZE * i, 'stone'))
                        self.tiles.add(Tile(px + TILE_SIZE, py - TILE_SIZE * i, 'stone'))
                elif char == 'F':
                    self.flag = FlagPole(px, py - TILE_SIZE * 7)
                elif char == 'c':
                    self.castle = Castle(px, py - TILE_SIZE * 3)
                elif char == 'M':
                    self.mario_start = (px, py - TILE_SIZE)
                elif char == 'L':
                    lava = Tile(px, py, 'ground')
                    lava.image.fill(LAVA_RED)
                    self.tiles.add(lava)
                elif char == 'X':
                    self.tiles.add(Tile(px, py, 'castle_brick'))


# ============================================================================
# LEVEL DATA - ALL WORLDS
# ============================================================================

LEVEL_1_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                    ?                                                                                                                                                                                          
                                                                                                                                                                                                              
          M                                                             C C C                                                      ?                                                                          
                    ?B!B?              BB                    SBBB     BBBS            S                       B?B                                                                                             
                          ?B?B?              BB                    SBBB     BBBS            S                       B?B?B                                 S S                                                 
                                                                   S            S          S S                                                           S   S                                                
            G               G    G        G       P    G  G    p   S              S    p   S   S       p       G           G   P        G    G    G      S     S       Fc                                      
##############################################  ##################################  ######################  #####################################  ##############################  ###########################
##############################################  ##################################  ######################  #####################################  ##############################  ###########################
"""

LEVEL_1_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
       C C C C             C C C C                  C                                                                                                                                          
       BBBBBBB             BBBBBBB            BBBBBBBBB              ?     ?                                                                                                                   
                                                                                        BBBBBBBB                  B  B  B  B                                                                  
   M           G       G            G   P    G           G   p      G           G   P                  G     P                  G    p                                                        
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_1_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                  C                                                                                                                                           
                            SSSS                SSSSS                                             SSSS                                                                                         
                                    C   C                      C                         C               C   C                                           ?                                     
       M          SSSS              SSS            SSSS         SS           SSSS         SSS              SSSS              SSSSS           SSSS                 Fc                           
                              G                         G              G          G              G                    G                           G                                           
SSSS                                                                                                                                                                              SSSSSSSSSSSS
SSSS                                                                                                                                                                              SSSSSSSSSSSS
"""

LEVEL_1_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                          XXX                              XXX                                                            XXX                                          X
X                  XXX              XXX                     XXX         XXX                   XXX         XXX                   XXX                            XXX              XX  XX  XX    X
X             G             G              G          G             G          G         G          G             G         G            G              G               G                    cX
XXXXXXXXXXXXXXXXXXXXXX   XXXXX  XXXXXXXXXXXX   XXXXXX   XXXXXXXXXXXXXXXXX   XXXX   XXXXXXX   XXXXXX   XXXXXXXX  XXXXXXXXX   XXXXX   XXXXXXXX   XXXXX   XXXXXX   XXXXX   XX    XXXXXXXXXXXXXXXX
LLLLLLLLLLLLLLLLLLLLLL   LLLLL  LLLLLLLLLLLL   LLLLLL   LLLLLLLLLLLLLLLLL   LLLL   LLLLLLL   LLLLLL   LLLLLLLL  LLLLLLLLL   LLLLL   LLLLLLLL   LLLLL   LLLLLL   LLLLL   LL    LLLLLLLLLLLLLLLL
"""

LEVEL_2_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                        ?                                    ?                                                                                                                                                 
                                                                                              BBB                                                                                                              
          M           B?B?B                                B?B?B              P        K                   ?                                        SS                                                         
                                     P         G     G                 G            G              G                  P          K    K       G          SS      Fc                                           
########################################  ########################################  #################################  ##############################  #################################  #####################
########################################  ########################################  #################################  ##############################  #################################  #####################
"""

LEVEL_2_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
       C C C                   C C C                        C C                                                                                                                                
       BBBBB                   BBBBB                        BBB                   ?  ?  ?                                                                                                      
                                                                                                    BBBB                   BBB                                                                 
   M             G         G              G     p       G              G    P            G                     G     P                G     p                                                  
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_2_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                           C                                        C                                                                                          
                                SSSS                    SSSSS                              SSSS                SSSS                                                                            
                     C C                                             C           C C                                    C                                                                      
       M        SSS                SSSS            SSS                   SSS              SSS             SSSS                SSSSS                Fc                                          
                            G               G                   G              K                   G                  G                      G                                                 
SSS                                                                                                                                                                                SSSSSSSSSS
SSS                                                                                                                                                                                SSSSSSSSSS
"""

LEVEL_2_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                                                                                                                                                                       X
X                         XXX                   XXX                        XXX                     XXX                      XXX                      XXX                                       X
X              XXX                    XXX                     XXX                     XXX                    XXX                      XXX                      XXX          XX   XX   XX      X
X         G          G           G          G           G          G            G          G            G           G           G           G           G                                    cX
XXXXXXXXXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXXXX   XXXXX   XX      XXXXXXXXXXXXXXXXXXXXXXXX
LLLLLLLLLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLLLL   LLLLL   LL      LLLLLLLLLLLLLLLLLLLLLLLL
"""

LEVEL_3_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                    ?                                                                                                                                                                          
                                                                                                                  BBB                                                                                          
          M                   B?B                              ?                        BBB                                    ?B?                                                                             
                    K                     P          G   K            G    p       K              G          P              K            G    P         K    K         Fc                                      
###############################################  #########################################  #################################  ##############################  ################################  #################
###############################################  #########################################  #################################  ##############################  ################################  #################
"""

LEVEL_3_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                              C C                                             C C                                                                                                              
                              BBB                                             BBB                          BBBB                                                                                
       C C C                               ?                                              ?                               C C                                                                  
       BBB                                                                                                                BBB                                                                  
   M            K         K             K      p         K           K   P           K            K     P             K           p                                                            
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_3_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                C                                           C                                                                                  
                                            SSSS             SSSSS                                SSSS                 SSSS                                                                    
                        SSSS       C C                                     C C                                                   C                                                             
                                   SSS                                     SSS                                                                      ?                                          
       M     SSSS                              SSSS               SSS                 SSSS                  SSSS              SSSSS             SSSS                Fc                         
                           K              K              K              K              K                K              K                   K                                                   
SS                                                                                                                                                                                 SSSSSSSSSSS
SS                                                                                                                                                                                 SSSSSSSSSSS
"""

LEVEL_3_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                                                                                                                                                                       X
X                              XXXX                       XXXX                         XXXX                        XXXX                         XXX                                           X
X              XXXX                       XXXX                        XXXX                        XXXX                        XXXX                        XXXX            XXX  XXX  XXX      X
X         K           K           Z            K           K              K            K              K           K              K            K               K                              cX
XXXXXXXXXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXXXXX   XXXXX   XX   XXXXXXXXXXXXXXXXXXXXXX
LLLLLLLLLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLLLLL   LLLLL   LL   LLLLLLLLLLLLLLLLLLLLLL
"""

LEVEL_4_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                              ?                                                           ?                                                                                                                    
                                                               BBB                                                   BBB                                                                                       
          M               B?B?B            P             K                    p      B?B?B          P                             p             K    K            Fc                                           
                    K                           G    K              G                          K              G    K              G         K                                                                  
#################################################  ##########################################  #####################################  ################################  #######################################
#################################################  ##########################################  #####################################  ################################  #######################################
"""

LEVEL_4_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                                   C C                                              C C                                                                                                        
                                   BBB                                              BBB                               BBBB                                                                     
       C C C C                                  ?                                                 ?                                   C C                                                      
       BBBBBBB                                                                                                                        BBB                                                      
   M              K       K              K    p          K           K    P           K              K    P               K              p                                                     
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_4_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                              C                                                                                
                                                SSSS                                            SSSS                  SSSS                                                                     
                                 C C C                       C             C C                                                       C                                                         
       M           SSSS                    SSS           SSS                     SSSS                   SSS                SSSS                SSSSS           Fc                              
                              K              K              K              K              K              K              K              K                                                        
SS                                                                                                                                                                                  SSSSSSSSS
SS                                                                                                                                                                                  SSSSSSSSS
"""

LEVEL_4_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                                                                                                                                                                       X
X                                XXXXX                        XXXXX                          XXXXX                         XXXXX                          XXX                                 X
X                XXXXX                         XXXXX                         XXXXX                         XXXXX                         XXXXX                        XXX  XXX  XXX  XXX     X
X           Z            Z            Z              Z            Z              Z            Z               Z            Z               Z             Z                                   cX
XXXXXXXXXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXXXXXXX   XXXX   XXX    XXXXXXXXXXXXXXXXXX
LLLLLLLLLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLLLLLLL   LLLL   LLL    LLLLLLLLLLLLLLLLLL
"""

LEVEL_5_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                 ?                                                            ?                                                                                                                
                                                                   BBB                                                    BBB                                                                                  
          M                B?B?B?B              P              K                  p        B?B?B           P                             p               K    K    K        Fc                                 
                    Z                                G    Z              G    K                      Z              G    Z              G    K       Z                                                         
#################################################  ###########################################  #####################################  #################################  ######################################
#################################################  ###########################################  #####################################  #################################  ######################################
"""

LEVEL_5_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                                       C C C                                                C C C                                                                                              
                                       BBBBB                                                BBBBB                            BBBBB                                                             
       C C C C C                                        ?                                                   ?                                      C C                                         
       BBBBBBBBB                                                                                                                                   BBB                                         
   M                  Z         Z                Z    p          Z             Z    P             Z               Z    P                Z              p                                       
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_5_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                        C                                                                      
                                                      SSSS                                             SSSS                     SSSS                                                           
                                       C C C                       C               C C                                                         C                                               
                           SSSS                   SSS           SSS                      SSSS                     SSS                   SSSS                 ?                                 
       M        SSSS                                                                                                                                  SSSS            Fc                       
                                Z                Z                Z                Z                Z                Z                Z                                                        
S                                                                                                                                                                                    SSSSSSSS
S                                                                                                                                                                                    SSSSSSSS
"""

LEVEL_5_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                                                                                                                                                                       X
X                                    XXXXXX                            XXXXXX                              XXXXXX                             XXXXXX                        XXX               X
X                    XXXXXX                            XXXXXX                              XXXXXX                              XXXXXX                              XXXX           XXX  XXX   X
X             Z               Z               Y               Z               Z               Y               Z               Z                  Y                                          cX
XXXXXXXXXXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXXXXXXXX   XXXX   XXXX    XXXXXXXXXXXXXXXX
LLLLLLLLLLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLLLLLLLL   LLLL   LLLL    LLLLLLLLLLLLLLLL
"""

LEVEL_6_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                   ?                                                              ?                                                                                                            
                                                                      BBB                                                       BBB                                                                            
          M                  B?B?B?B             P               Z                    p        B?B?B?B         P                              p                Z    Z    Z         Fc                          
                    Y                                G     Y               G    Z                        Y               G     Y               G     Z      Y                                                  
##################################################  ############################################  #######################################  ##################################  ##################################
##################################################  ############################################  #######################################  ##################################  ##################################
"""

LEVEL_6_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                                          C C C C                                                  C C C C                                                                                     
                                          BBBBBBB                                                  BBBBBBB                                   BBBBB                                             
       C C C C C C                                           ?                                                        ?                                        C C                             
       BBBBBBBBBBB                                                                                                                                              BBB                             
   M                    Z           Z                 Z    p            Z               Z    P               Z                 Z    P                  Z            p                          
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_6_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                              C                                                                
                                                          SSSS                                                SSSS                     SSSS                                                    
                                          C C C C                         C                 C C                                                           C                                    
                              SSSS                     SSS              SSS                       SSSS                       SSS                    SSSS                  ?                    
       M           SSSS                                                                                                                                            SSSS            Fc          
                                  Y                 Y                 Z                 Z                 Y                 Y                 Z                                               
                                                                                                                                                                                    SSSSSSSSSS
                                                                                                                                                                                    SSSSSSSSSS
"""

LEVEL_6_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                                                                                                                                                                       X
X                                        XXXXXXX                                XXXXXXX                                  XXXXXXX                               XXXXXXX               XXX      X
X                        XXXXXXX                                XXXXXXX                                 XXXXXXX                                 XXXXXXX                               XXX     X
X               Y                   Y                   Y                   Y                   Y                   Y                   Y                   Y                               cX
XXXXXXXXXXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXXXXXXXXX   XXXX   XXXXXXXXXXXXX
LLLLLLLLLLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLLLLLLLLL   LLLL   LLLLLLLLLLLLL
"""

LEVEL_7_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                     ?                                                                ?                                                                                                        
                                                                         BBB                                                          BBB                                                                      
          M                    B?B?B?B              P                Y                    p        B?B?B?B           P                               p                 Y    Y    Y        Fc                   
                    Y                                  G     Y                 G    Y                          Y                 G     Y                 G     Y      Y                                        
###################################################  #############################################  ########################################  ###################################  ###############################
###################################################  #############################################  ########################################  ###################################  ###############################
"""

LEVEL_7_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                                             C C C C C                                                    C C C C C                                                                            
                                             BBBBBBBBB                                                    BBBBBBBBB                                     BBBBBBB                                
       C C C C C C C                                              ?                                                           ?                                            C C C                
       BBBBBBBBBBBBB                                                                                                                                                       BBBBB                
   M                      Y             Y                   Y    p              Y                 Y    P                 Y                   Y    P                    Y          p             
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_7_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                    C                                                          
                                                               SSSS                                                 SSSS                      SSSS                                             
                                             C C C C                           C                   C C                                                              C                          
                                 SSSS                       SSS               SSS                        SSSS                        SSS                     SSSS                   ?          
       M              SSSS                                                                                                                                                    SSSS          Fc 
                                    Y                   Y                   Y                   Y                   Y                   Y                   Y                                  
                                                                                                                                                                                     SSSSSSSSS
                                                                                                                                                                                     SSSSSSSSS
"""

LEVEL_7_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                                                                                                                                                                       X
X                                            XXXXXXXX                                    XXXXXXXX                                      XXXXXXXX                                   XXX         X
X                            XXXXXXXX                                    XXXXXXXX                                     XXXXXXXX                                     XXXXXXXX              XXX  X
X                 Y                     Y                     Y                     Y                     Y                     Y                     Y                                      cX
XXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXXXXXXXXX   XXXXX   XXXXXXXXXXXXXXXXX
LLLLLLLLLLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLLLLLLLLL   LLLLL   LLLLLLLLLLLLLLLLL
"""

LEVEL_8_1 = """
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                                                                                                                                                                                              
                                       ?                                                                  ?                                                                                                    
                                                                             BBB                                                              BBB                                                              
          M                      B?B?B?B?B              P                 Y                    p        B?B?B?B?B           P                                  p                  Y    Y    Y    Y        Fc   
                    Y                                      G     Y                   G    Y                            Y                   G     Y                   G     Y      Y                            
####################################################  ##############################################  #########################################  ####################################  ############################
####################################################  ##############################################  #########################################  ####################################  ############################
"""

LEVEL_8_2 = """
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS                   
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                C C C C C C                                                        C C C C C C                                                                
                                                BBBBBBBBBBB                                                        BBBBBBBBBBB                                         BBBBBBB                 
       C C C C C C C C                                                  ?                                                              ?                                              C C C    
       BBBBBBBBBBBBBBB                                                                                                                                                                 BBBBB    
   M                        Y               Y                     Y    p                Y                   Y    P                   Y                     Y    P                  Y        p   
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS    SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
"""

LEVEL_8_3 = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                          C                                                    
                                                                  SSSS                                                     SSSS                       SSSS                                     
                                                C C C C C                             C                     C C                                                               C                 
                                     SSSS                        SSS                SSS                          SSSS                         SSS                      SSSS                    
       M                 SSSS                                                                                                                                                           ?   Fc 
                                       Y                     Y                     Y                     Y                     Y                     Y                     Y                   
                                                                                                                                                                                      SSSSSSS
                                                                                                                                                                                      SSSSSSS
"""

LEVEL_8_4 = """
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X                                                                                                                                                                                             X
X     M                                                                                                                                                                                       X
X                                                XXXXXXXXX                                         XXXXXXXXX                                           XXXXXXXXX                         XXX  X
X                                XXXXXXXXX                                         XXXXXXXXX                                          XXXXXXXXX                                          XXX  X
X                    Y                       Y                       Y                       Y                       Y                       Y                       Y                       cX
XXXXXXXXXXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXXXXXXXXXX   XXXXX   XXXXXXXXXXXXXX
LLLLLLLLLLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLLLLLLLLLL   LLLLL   LLLLLLLLLLLLLL
"""

LEVEL_MINUS = """
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                                                                                                                                                                                              
                    ?   ?   ?                                                                     ?   ?   ?                                                                                   
                                                                                                                                                                                              
          M                                                                   C C C                                                                                                            
                    BBB       BBB       BBB                            BBB           BBB                            BBB       BBB                                                              
                                                      P                                             P                                              P                                          
                  G       G         G         G              G                G           G                G              G         G         G               G                              
##############################################################################################################################################################################               
##############################################################################################################################################################################               
"""


class Game:
    """Main game class"""
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.sound = SoundManager()
        
        self.levels = {
            '1-1': (LEVEL_1_1, SKY_BLUE), '1-2': (LEVEL_1_2, UNDERGROUND_BG),
            '1-3': (LEVEL_1_3, SKY_BLUE), '1-4': (LEVEL_1_4, CASTLE_BG),
            '2-1': (LEVEL_2_1, SKY_BLUE), '2-2': (LEVEL_2_2, UNDERGROUND_BG),
            '2-3': (LEVEL_2_3, SKY_BLUE), '2-4': (LEVEL_2_4, CASTLE_BG),
            '3-1': (LEVEL_3_1, SKY_BLUE), '3-2': (LEVEL_3_2, UNDERGROUND_BG),
            '3-3': (LEVEL_3_3, SKY_BLUE), '3-4': (LEVEL_3_4, CASTLE_BG),
            '4-1': (LEVEL_4_1, SKY_BLUE), '4-2': (LEVEL_4_2, UNDERGROUND_BG),
            '4-3': (LEVEL_4_3, SKY_BLUE), '4-4': (LEVEL_4_4, CASTLE_BG),
            '5-1': (LEVEL_5_1, SKY_BLUE), '5-2': (LEVEL_5_2, UNDERGROUND_BG),
            '5-3': (LEVEL_5_3, SKY_BLUE), '5-4': (LEVEL_5_4, CASTLE_BG),
            '6-1': (LEVEL_6_1, SKY_BLUE), '6-2': (LEVEL_6_2, UNDERGROUND_BG),
            '6-3': (LEVEL_6_3, SKY_BLUE), '6-4': (LEVEL_6_4, CASTLE_BG),
            '7-1': (LEVEL_7_1, SKY_BLUE), '7-2': (LEVEL_7_2, UNDERGROUND_BG),
            '7-3': (LEVEL_7_3, SKY_BLUE), '7-4': (LEVEL_7_4, CASTLE_BG),
            '8-1': (LEVEL_8_1, SKY_BLUE), '8-2': (LEVEL_8_2, UNDERGROUND_BG),
            '8-3': (LEVEL_8_3, SKY_BLUE), '8-4': (LEVEL_8_4, CASTLE_BG),
            '-1': (LEVEL_MINUS, UNDERWATER_BG),
        }
        
        self.level_keys = ['1-1','1-2','1-3','1-4','2-1','2-2','2-3','2-4',
                           '3-1','3-2','3-3','3-4','4-1','4-2','4-3','4-4',
                           '5-1','5-2','5-3','5-4','6-1','6-2','6-3','6-4',
                           '7-1','7-2','7-3','7-4','8-1','8-2','8-3','8-4','-1']
        
        self.current_level_name = '1-1'
        self.level = None
        self.mario = None
        self.camera_x = 0
        
        self.menu_selection = 0
        self.world_selection = 0
        self.menu_options = ['START GAME', 'WORLD SELECT', 'CONTROLS']
        self.showing_controls = False
        
        self.time_left = 400
        self.time_tick = 0
        
        self.transition_timer = 0
        self.showing_level_complete = False
        
        self.menu_anim = 0
    
    def start_level(self, level_name):
        level_data, bg_color = self.levels[level_name]
        self.level = Level(level_data, bg_color)
        self.current_level_name = level_name
        
        mario_x, mario_y = self.level.mario_start
        self.mario = Mario(mario_x, mario_y)
        
        self.camera_x = 0
        self.time_left = 400
        self.time_tick = 0
        self.state = GameState.PLAYING
        self.showing_level_complete = False
    
    def update(self):
        self.menu_anim += 1
        
        if self.state == GameState.MAIN_MENU:
            pass
        elif self.state == GameState.WORLD_SELECT:
            pass
        elif self.state == GameState.PLAYING:
            self.update_game()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.update_level_complete()
        elif self.state == GameState.GAME_OVER:
            pass
    
    def update_game(self):
        keys = pygame.key.get_pressed()
        self.mario.running = keys[pygame.K_LSHIFT] or keys[pygame.K_z]
        
        self.mario.update(keys, self.level.tiles, self.level.enemies, None)
        
        for enemy in self.level.enemies:
            enemy.update(self.level.tiles)
        
        for coin in self.level.coins:
            coin.update()
        
        coin_hits = pygame.sprite.spritecollide(self.mario, self.level.coins, True)
        for coin in coin_hits:
            self.mario.coins += 1
            self.mario.score += 200
            self.sound.play('coin')
        
        for enemy in self.level.enemies:
            if not enemy.alive:
                continue
            if self.mario.rect.colliderect(enemy.rect):
                if self.mario.vel_y > 0 and self.mario.rect.bottom < enemy.rect.centery + 5:
                    points = enemy.stomp()
                    if points > 0:
                        self.mario.score += points
                        self.mario.vel_y = -6
                        self.sound.play('stomp')
                    else:
                        if self.mario.take_damage(self.sound):
                            self.state = GameState.GAME_OVER
                else:
                    if self.mario.take_damage(self.sound):
                        self.state = GameState.GAME_OVER
        
        if self.level.flag and self.mario.rect.colliderect(self.level.flag.rect):
            if not self.level.flag.reached:
                self.level.flag.reached = True
                self.sound.play('flag')
                self.mario.score += max(100, (400 - self.time_left) * 10)
        
        if self.level.flag and self.level.flag.reached:
            if self.level.flag.lower_flag():
                self.showing_level_complete = True
                self.transition_timer = 180
                self.state = GameState.LEVEL_COMPLETE
        
        target_cam = self.mario.rect.centerx - SCREEN_WIDTH // 3
        self.camera_x = max(0, min(target_cam, self.level.width - SCREEN_WIDTH))
        
        self.time_tick += 1
        if self.time_tick >= 24:
            self.time_tick = 0
            self.time_left -= 1
            if self.time_left <= 0:
                self.mario.lives -= 1
                if self.mario.lives <= 0:
                    self.state = GameState.GAME_OVER
                else:
                    self.start_level(self.current_level_name)
        
        if self.mario.rect.top > SCREEN_HEIGHT:
            self.mario.lives -= 1
            self.sound.play('death')
            if self.mario.lives <= 0:
                self.state = GameState.GAME_OVER
            else:
                self.start_level(self.current_level_name)
        
        if self.mario.rect.left < 0:
            self.mario.rect.left = 0
    
    def update_level_complete(self):
        self.transition_timer -= 1
        if self.transition_timer <= 0:
            current_idx = self.level_keys.index(self.current_level_name)
            if current_idx < len(self.level_keys) - 1:
                self.start_level(self.level_keys[current_idx + 1])
            else:
                self.state = GameState.MAIN_MENU
    
    def draw(self):
        if self.state == GameState.MAIN_MENU:
            self.draw_menu()
        elif self.state == GameState.WORLD_SELECT:
            self.draw_world_select()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_game()
            self.draw_level_complete()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        for y in range(SCREEN_HEIGHT):
            r = int(92 + (y / SCREEN_HEIGHT) * 50)
            g = int(148 - (y / SCREEN_HEIGHT) * 50)
            b = 252
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        for i in range(5):
            x = (i * 150 + self.menu_anim // 3) % (SCREEN_WIDTH + 100) - 50
            y = 50 + i * 20
            pygame.draw.ellipse(screen, CLOUD_WHITE, (x, y, 60, 30))
            pygame.draw.ellipse(screen, CLOUD_WHITE, (x + 20, y - 10, 50, 40))
            pygame.draw.ellipse(screen, CLOUD_WHITE, (x + 40, y, 60, 30))
        
        title = font_large.render("ULTRA MARIO 2D BROS", True, WHITE)
        title_shadow = font_large.render("ULTRA MARIO 2D BROS", True, (50, 50, 50))
        tx = SCREEN_WIDTH//2 - title.get_width()//2
        screen.blit(title_shadow, (tx + 3, 48))
        screen.blit(title, (tx, 45))
        
        subtitle = font_small.render("Flames Co. / Team Flames / Samsoft", True, COIN_GOLD)
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 100))
        
        if self.showing_controls:
            controls = [
                "CONTROLS",
                "",
                "ARROWS / WASD - Move",
                "SPACE / W / UP - Jump",
                "SHIFT / Z - Run",
                "ESC - Pause / Menu",
                "",
                "Press ENTER to go back"
            ]
            for i, line in enumerate(controls):
                color = COIN_GOLD if i == 0 else WHITE
                text = font_small.render(line, True, color)
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150 + i * 28))
        else:
            for i, option in enumerate(self.menu_options):
                color = COIN_GOLD if i == self.menu_selection else WHITE
                text = font_medium.render(option, True, color)
                y_pos = 160 + i * 50
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
                
                if i == self.menu_selection:
                    bob = int(math.sin(self.menu_anim * 0.1) * 3)
                    pygame.draw.polygon(screen, MARIO_RED, [
                        (SCREEN_WIDTH//2 - text.get_width()//2 - 35, y_pos + 12 + bob),
                        (SCREEN_WIDTH//2 - text.get_width()//2 - 15, y_pos + 20 + bob),
                        (SCREEN_WIDTH//2 - text.get_width()//2 - 35, y_pos + 28 + bob)
                    ])
            
            ver = font_tiny.render("v1.0 - 33 Levels", True, WHITE)
            screen.blit(ver, (SCREEN_WIDTH//2 - ver.get_width()//2, SCREEN_HEIGHT - 30))
    
    def draw_world_select(self):
        screen.fill(SKY_BLUE)
        
        title = font_medium.render("SELECT WORLD", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        worlds = ['1', '2', '3', '4', '5', '6', '7', '8', '-']
        for i, world in enumerate(worlds):
            col = i % 3
            row = i // 3
            x = 150 + col * 120
            y = 100 + row * 80
            
            color = COIN_GOLD if i == self.world_selection else WHITE
            pygame.draw.rect(screen, color, (x, y, 80, 50), 3 if i != self.world_selection else 0)
            
            if i == self.world_selection:
                text_color = BLACK
            else:
                text_color = color
            
            world_text = "MINUS" if world == '-' else f"WORLD {world}"
            text = font_small.render(world_text, True, text_color)
            screen.blit(text, (x + 40 - text.get_width()//2, y + 15))
        
        inst = font_small.render("ARROWS: Select   ENTER: Play   ESC: Back", True, WHITE)
        screen.blit(inst, (SCREEN_WIDTH//2 - inst.get_width()//2, SCREEN_HEIGHT - 40))
    
    def draw_game(self):
        screen.fill(self.level.bg_color)
        
        for cloud in self.level.clouds:
            screen.blit(cloud.image, (cloud.rect.x - self.camera_x * 0.3, cloud.rect.y))
        
        for tile in self.level.tiles:
            screen.blit(tile.image, (tile.rect.x - self.camera_x, tile.rect.y))
        
        for pipe in self.level.pipes:
            screen.blit(pipe.image, (pipe.rect.x - self.camera_x, pipe.rect.y))
        
        for coin in self.level.coins:
            screen.blit(coin.image, (coin.rect.x - self.camera_x, coin.rect.y))
        
        for enemy in self.level.enemies:
            screen.blit(enemy.image, (enemy.rect.x - self.camera_x, enemy.rect.y))
        
        if self.level.flag:
            screen.blit(self.level.flag.image, (self.level.flag.rect.x - self.camera_x, self.level.flag.rect.y))
        
        if self.level.castle:
            screen.blit(self.level.castle.image, (self.level.castle.rect.x - self.camera_x, self.level.castle.rect.y))
        
        screen.blit(self.mario.image, (self.mario.rect.x - self.camera_x, self.mario.rect.y))
        
        self.draw_hud()
    
    def draw_hud(self):
        pygame.draw.rect(screen, (0, 0, 0, 128), (0, 0, SCREEN_WIDTH, 32))
        
        score_text = font_small.render(f"SCORE {self.mario.score:06d}", True, WHITE)
        screen.blit(score_text, (10, 8))
        
        coin_text = font_small.render(f"x{self.mario.coins:02d}", True, COIN_GOLD)
        pygame.draw.circle(screen, COIN_GOLD, (195, 16), 8)
        pygame.draw.circle(screen, (200, 140, 40), (195, 16), 5)
        screen.blit(coin_text, (210, 8))
        
        world_text = font_small.render(f"WORLD {self.current_level_name}", True, WHITE)
        screen.blit(world_text, (300, 8))
        
        time_text = font_small.render(f"TIME {self.time_left:03d}", True, WHITE)
        screen.blit(time_text, (450, 8))
        
        lives_text = font_small.render(f"x{self.mario.lives}", True, WHITE)
        pygame.draw.rect(screen, MARIO_RED, (550, 8, 12, 16))
        screen.blit(lives_text, (565, 8))
    
    def draw_level_complete(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(150)
        screen.blit(overlay, (0, 0))
        
        complete = font_large.render("COURSE CLEAR!", True, COIN_GOLD)
        screen.blit(complete, (SCREEN_WIDTH//2 - complete.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        score = font_medium.render(f"SCORE: {self.mario.score}", True, WHITE)
        screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, SCREEN_HEIGHT//2 + 10))
        
        next_text = font_small.render("Next level loading...", True, WHITE)
        screen.blit(next_text, (SCREEN_WIDTH//2 - next_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
    
    def draw_game_over(self):
        screen.fill(BLACK)
        
        text = font_large.render("GAME OVER", True, MARIO_RED)
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        score = font_medium.render(f"FINAL SCORE: {self.mario.score if self.mario else 0}", True, WHITE)
        screen.blit(score, (SCREEN_WIDTH//2 - score.get_width()//2, SCREEN_HEIGHT//2 + 10))
        
        inst = font_small.render("Press ENTER to return to menu", True, WHITE)
        screen.blit(inst, (SCREEN_WIDTH//2 - inst.get_width()//2, SCREEN_HEIGHT//2 + 70))
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MAIN_MENU:
                if self.showing_controls:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                        self.showing_controls = False
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selection == 0:
                            self.start_level('1-1')
                        elif self.menu_selection == 1:
                            self.state = GameState.WORLD_SELECT
                        elif self.menu_selection == 2:
                            self.showing_controls = True
            
            elif self.state == GameState.WORLD_SELECT:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.world_selection = (self.world_selection - 1) % 9
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.world_selection = (self.world_selection + 1) % 9
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.world_selection = (self.world_selection - 3) % 9
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.world_selection = (self.world_selection + 3) % 9
                elif event.key == pygame.K_RETURN:
                    worlds = ['1-1', '2-1', '3-1', '4-1', '5-1', '6-1', '7-1', '8-1', '-1']
                    self.start_level(worlds[self.world_selection])
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MAIN_MENU
            
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.mario.jump(self.sound)
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MAIN_MENU
            
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_RETURN:
                    self.state = GameState.MAIN_MENU
                    self.mario = None


def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        
        game.update()
        game.draw()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
