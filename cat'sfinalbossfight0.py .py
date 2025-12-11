#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS: BOSS FIGHT REDUX
A retro-styled boss rush platformer inspired by classic Nintendo games
Features: 5 Boss Fights, Power-up Corridors, Galaxy-style HUD
By Team Flames / Samsoft

Controls:
- Arrow Keys / WASD: Move
- Space/Z: Jump
- X: Attack/Fireball
- Enter: Start/Confirm
- P: Pause
"""

import pygame
import math
import random
import sys
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# ============================================================================
# CONSTANTS
# ============================================================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 32

# Colors (Yoshi's Island / SMW inspired palette)
COLORS = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'red': (228, 52, 52),
    'blue': (52, 100, 228),
    'green': (52, 228, 92),
    'yellow': (255, 220, 50),
    'orange': (255, 160, 50),
    'purple': (160, 80, 200),
    'pink': (255, 150, 200),
    'brown': (139, 90, 43),
    'sky_blue': (135, 206, 235),
    'dark_blue': (25, 25, 112),
    'gold': (255, 215, 0),
    'cyan': (0, 255, 255),
    'mario_red': (228, 52, 52),
    'mario_blue': (52, 100, 228),
    'skin': (255, 200, 150),
    'yoshi_green': (80, 200, 80),
    'galaxy_purple': (60, 20, 100),
    'galaxy_blue': (30, 60, 150),
    'star_yellow': (255, 255, 100),
}

# Game States
class GameState(Enum):
    TITLE = auto()
    CORRIDOR = auto()
    BOSS_INTRO = auto()
    BOSS_FIGHT = auto()
    BOSS_DEFEATED = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    PAUSED = auto()

# Power-up Types
class PowerUp(Enum):
    NONE = auto()
    MUSHROOM = auto()
    FIRE_FLOWER = auto()
    STAR = auto()
    CAPE = auto()

# ============================================================================
# SPRITE GENERATOR - Creates retro-styled pixel art sprites
# ============================================================================
class SpriteGenerator:
    """Generates pixel art sprites in the style of classic Nintendo games"""
    
    @staticmethod
    def create_mario_sprite(size: int = 32, power_state: PowerUp = PowerUp.MUSHROOM, frame: int = 0) -> pygame.Surface:
        """Create SMB3-styled Mario sprite"""
        surf = pygame.Surface((size, size * 2 if power_state != PowerUp.NONE else size), pygame.SRCALPHA)
        
        is_big = power_state != PowerUp.NONE
        h = size * 2 if is_big else size
        
        # Colors based on power state
        if power_state == PowerUp.FIRE_FLOWER:
            hat_color = COLORS['white']
            shirt_color = COLORS['red']
        elif power_state == PowerUp.STAR:
            # Rainbow effect
            colors = [COLORS['red'], COLORS['yellow'], COLORS['green'], COLORS['cyan']]
            hat_color = colors[(frame // 4) % len(colors)]
            shirt_color = colors[(frame // 4 + 2) % len(colors)]
        else:
            hat_color = COLORS['mario_red']
            shirt_color = COLORS['mario_red']
        
        # Draw Mario (SMB3 style)
        pixel = size // 16
        
        if is_big:
            # Big Mario
            # Hat
            pygame.draw.rect(surf, hat_color, (4*pixel, 0, 8*pixel, 4*pixel))
            # Face
            pygame.draw.rect(surf, COLORS['skin'], (3*pixel, 4*pixel, 10*pixel, 6*pixel))
            # Hair/Sideburns
            pygame.draw.rect(surf, COLORS['brown'], (3*pixel, 4*pixel, 2*pixel, 4*pixel))
            pygame.draw.rect(surf, COLORS['brown'], (11*pixel, 4*pixel, 2*pixel, 4*pixel))
            # Eyes
            pygame.draw.rect(surf, COLORS['black'], (5*pixel, 5*pixel, 2*pixel, 2*pixel))
            pygame.draw.rect(surf, COLORS['black'], (9*pixel, 5*pixel, 2*pixel, 2*pixel))
            # Mustache
            pygame.draw.rect(surf, COLORS['brown'], (4*pixel, 8*pixel, 8*pixel, 2*pixel))
            # Body/Shirt
            pygame.draw.rect(surf, shirt_color, (2*pixel, 10*pixel, 12*pixel, 10*pixel))
            # Overalls
            pygame.draw.rect(surf, COLORS['mario_blue'], (3*pixel, 14*pixel, 10*pixel, 10*pixel))
            # Overall straps
            pygame.draw.rect(surf, COLORS['mario_blue'], (4*pixel, 10*pixel, 2*pixel, 4*pixel))
            pygame.draw.rect(surf, COLORS['mario_blue'], (10*pixel, 10*pixel, 2*pixel, 4*pixel))
            # Buttons
            pygame.draw.rect(surf, COLORS['yellow'], (5*pixel, 15*pixel, 2*pixel, 2*pixel))
            pygame.draw.rect(surf, COLORS['yellow'], (9*pixel, 15*pixel, 2*pixel, 2*pixel))
            # Hands
            pygame.draw.rect(surf, COLORS['skin'], (0, 14*pixel, 3*pixel, 4*pixel))
            pygame.draw.rect(surf, COLORS['skin'], (13*pixel, 14*pixel, 3*pixel, 4*pixel))
            # Shoes
            pygame.draw.rect(surf, COLORS['brown'], (2*pixel, 28*pixel, 5*pixel, 4*pixel))
            pygame.draw.rect(surf, COLORS['brown'], (9*pixel, 28*pixel, 5*pixel, 4*pixel))
        else:
            # Small Mario
            pygame.draw.rect(surf, hat_color, (4*pixel, 0, 8*pixel, 3*pixel))
            pygame.draw.rect(surf, COLORS['skin'], (4*pixel, 3*pixel, 8*pixel, 5*pixel))
            pygame.draw.rect(surf, COLORS['brown'], (4*pixel, 3*pixel, 2*pixel, 3*pixel))
            pygame.draw.rect(surf, COLORS['black'], (6*pixel, 4*pixel, 2*pixel, 2*pixel))
            pygame.draw.rect(surf, COLORS['brown'], (5*pixel, 6*pixel, 6*pixel, 2*pixel))
            pygame.draw.rect(surf, shirt_color, (3*pixel, 8*pixel, 10*pixel, 4*pixel))
            pygame.draw.rect(surf, COLORS['mario_blue'], (4*pixel, 10*pixel, 8*pixel, 4*pixel))
            pygame.draw.rect(surf, COLORS['brown'], (3*pixel, 14*pixel, 4*pixel, 2*pixel))
            pygame.draw.rect(surf, COLORS['brown'], (9*pixel, 14*pixel, 4*pixel, 2*pixel))
        
        return surf
    
    @staticmethod
    def create_goomboss_sprite(size: int = 96, frame: int = 0, angry: bool = False) -> pygame.Surface:
        """Create Goomboss sprite - giant angry Goomba king"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Body color (darker when angry)
        body_color = (160, 100, 60) if not angry else (180, 60, 40)
        
        # Main body (big round shape)
        pygame.draw.ellipse(surf, body_color, (4, size//4, size-8, size*3//4))
        
        # Crown
        crown_color = COLORS['gold']
        pygame.draw.rect(surf, crown_color, (size//4, 4, size//2, size//6))
        # Crown points
        for i in range(5):
            x = size//4 + i * (size//10)
            pygame.draw.polygon(surf, crown_color, [(x, 4), (x + size//20, 0), (x + size//10, 4)])
        # Crown jewels
        pygame.draw.circle(surf, COLORS['red'], (size//2, size//8), size//16)
        
        # Angry eyebrows
        brow_y = size//3 + (4 if angry else 0)
        pygame.draw.polygon(surf, COLORS['black'], 
                          [(size//4, brow_y), (size//2 - 4, brow_y - 8), (size//2 - 4, brow_y)])
        pygame.draw.polygon(surf, COLORS['black'],
                          [(size*3//4, brow_y), (size//2 + 4, brow_y - 8), (size//2 + 4, brow_y)])
        
        # Eyes
        eye_y = size//3 + 8
        pygame.draw.ellipse(surf, COLORS['white'], (size//4, eye_y, size//5, size//4))
        pygame.draw.ellipse(surf, COLORS['white'], (size*11//20, eye_y, size//5, size//4))
        # Pupils
        pupil_offset = math.sin(frame * 0.1) * 4
        pygame.draw.circle(surf, COLORS['black'], (int(size//4 + size//10 + pupil_offset), eye_y + size//8), size//12)
        pygame.draw.circle(surf, COLORS['black'], (int(size*11//20 + size//10 + pupil_offset), eye_y + size//8), size//12)
        
        # Fangs
        fang_y = size*2//3
        pygame.draw.polygon(surf, COLORS['white'], 
                          [(size//3, fang_y), (size//3 + 8, fang_y + 16), (size//3 + 16, fang_y)])
        pygame.draw.polygon(surf, COLORS['white'],
                          [(size*2//3 - 16, fang_y), (size*2//3 - 8, fang_y + 16), (size*2//3, fang_y)])
        
        # Feet
        pygame.draw.ellipse(surf, COLORS['black'], (size//6, size - 20, size//4, 20))
        pygame.draw.ellipse(surf, COLORS['black'], (size*7//12, size - 20, size//4, 20))
        
        return surf
    
    @staticmethod
    def create_yoob_sprite(size: int = 128, frame: int = 0, phase: int = 1) -> pygame.Surface:
        """Create Yoob sprite - giant corrupted Yoshi creature"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Phase affects color (gets more purple/corrupted)
        if phase == 1:
            body_color = (100, 180, 100)  # Sickly green
        else:
            body_color = (140, 100, 180)  # Corrupted purple
        
        # Body (large dinosaur shape)
        pygame.draw.ellipse(surf, body_color, (size//8, size//4, size*3//4, size*3//4))
        
        # Belly
        belly_color = (min(body_color[0] + 60, 255), min(body_color[1] + 60, 255), min(body_color[2] + 60, 255))
        pygame.draw.ellipse(surf, belly_color, (size//4, size*3//8, size//2, size//2))
        
        # Spots (corrupted style)
        spot_color = (body_color[0] - 40, body_color[1] - 40, body_color[2] - 40)
        for i in range(5):
            sx = size//4 + random.Random(i).randint(0, size//2)
            sy = size//3 + random.Random(i+10).randint(0, size//3)
            pygame.draw.circle(surf, spot_color, (sx, sy), size//16)
        
        # Head/snout
        pygame.draw.ellipse(surf, body_color, (size*5//8, size//8, size*3//8, size//3))
        # Nose
        pygame.draw.ellipse(surf, (body_color[0] - 20, body_color[1] - 20, body_color[2] - 20),
                          (size*7//8, size//6, size//10, size//8))
        
        # Evil eyes
        eye_glow = abs(math.sin(frame * 0.15)) * 50
        eye_color = (255, int(50 + eye_glow), int(50 + eye_glow))
        pygame.draw.ellipse(surf, COLORS['white'], (size*11//16, size//6, size//8, size//6))
        pygame.draw.circle(surf, eye_color, (size*11//16 + size//16, size//6 + size//12), size//20)
        
        # Spikes on back
        for i in range(4):
            spike_x = size//4 + i * size//6
            spike_y = size//4
            pygame.draw.polygon(surf, COLORS['red'], [
                (spike_x, spike_y),
                (spike_x + size//16, spike_y - size//8),
                (spike_x + size//8, spike_y)
            ])
        
        # Legs
        pygame.draw.ellipse(surf, body_color, (size//4, size*3//4, size//5, size//4))
        pygame.draw.ellipse(surf, body_color, (size//2, size*3//4, size//5, size//4))
        
        # Tail
        pygame.draw.arc(surf, body_color, (0, size//2, size//3, size//2), 0, math.pi, size//10)
        
        return surf
    
    @staticmethod
    def create_kamek_sprite(size: int = 64, frame: int = 0, casting: bool = False) -> pygame.Surface:
        """Create Kamek sprite - Magikoopa boss from Yoshi's Island"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Robe
        robe_color = COLORS['blue'] if not casting else (100, 50, 200)
        pygame.draw.polygon(surf, robe_color, [
            (size//4, size//3),
            (size*3//4, size//3),
            (size*7//8, size),
            (size//8, size)
        ])
        
        # White trim
        pygame.draw.line(surf, COLORS['white'], (size//4, size//3), (size*3//4, size//3), 3)
        
        # Head (rounder for Yoshi's Island style)
        pygame.draw.circle(surf, COLORS['yellow'], (size//2, size//4), size//5)
        
        # Glasses (round, iconic)
        glass_color = COLORS['white']
        pygame.draw.circle(surf, glass_color, (size*3//8, size//4), size//10)
        pygame.draw.circle(surf, glass_color, (size*5//8, size//4), size//10)
        pygame.draw.circle(surf, COLORS['black'], (size*3//8, size//4), size//16)
        pygame.draw.circle(surf, COLORS['black'], (size*5//8, size//4), size//16)
        # Glass frames
        pygame.draw.line(surf, COLORS['black'], (size*3//8 - size//10, size//4), 
                        (size*5//8 + size//10, size//4), 2)
        
        # Hat (wizard style)
        hat_color = COLORS['blue'] if not casting else (100, 50, 200)
        pygame.draw.polygon(surf, hat_color, [
            (size//4, size//4),
            (size//2, 0),
            (size*3//4, size//4)
        ])
        # Hat brim
        pygame.draw.ellipse(surf, hat_color, (size//6, size//5, size*2//3, size//8))
        
        # Wand
        wand_glow = abs(math.sin(frame * 0.2)) * 100 if casting else 0
        pygame.draw.line(surf, COLORS['brown'], (size*3//4, size//2), (size, size//4), 4)
        # Wand gem
        gem_color = (255, int(100 + wand_glow), int(wand_glow))
        pygame.draw.circle(surf, gem_color, (size, size//4), size//12)
        
        # Magic sparkles when casting
        if casting:
            for i in range(6):
                angle = frame * 0.1 + i * math.pi / 3
                dist = size//4 + math.sin(frame * 0.3) * 8
                sx = int(size + math.cos(angle) * dist)
                sy = int(size//4 + math.sin(angle) * dist)
                pygame.draw.circle(surf, COLORS['star_yellow'], (sx, sy), 3)
        
        return surf
    
    @staticmethod
    def create_petey_piranha_sprite(size: int = 96, frame: int = 0, mouth_open: bool = False) -> pygame.Surface:
        """Create Petey Piranha sprite - Giant piranha plant boss"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Body
        body_color = (100, 160, 80)
        pygame.draw.ellipse(surf, body_color, (size//6, size//3, size*2//3, size*2//3))
        
        # Belly dots
        pygame.draw.circle(surf, COLORS['yellow'], (size//3, size//2), size//12)
        pygame.draw.circle(surf, COLORS['yellow'], (size//2, size*5//8), size//12)
        pygame.draw.circle(surf, COLORS['yellow'], (size*2//3, size//2), size//12)
        
        # Head (large piranha head)
        head_color = (200, 60, 80)
        pygame.draw.ellipse(surf, head_color, (size//8, 0, size*3//4, size//2))
        
        # Lips
        lip_color = COLORS['white']
        pygame.draw.ellipse(surf, lip_color, (size//6, size//8, size*2//3, size//4))
        
        # Mouth
        if mouth_open:
            pygame.draw.ellipse(surf, COLORS['black'], (size//4, size//6, size//2, size//4))
            # Teeth
            for i in range(5):
                tx = size//4 + 8 + i * (size//10)
                pygame.draw.polygon(surf, COLORS['white'], [
                    (tx, size//6), (tx + size//20, size//4), (tx + size//10, size//6)
                ])
        
        # Spots on head
        pygame.draw.circle(surf, COLORS['white'], (size//3, size//10), size//14)
        pygame.draw.circle(surf, COLORS['white'], (size*2//3, size//10), size//14)
        
        # Leaves (like collar)
        leaf_color = (80, 180, 80)
        for i in range(6):
            angle = i * math.pi / 3 + math.sin(frame * 0.1) * 0.2
            lx = size//2 + math.cos(angle) * size//3
            ly = size//3 + math.sin(angle) * size//6
            pygame.draw.ellipse(surf, leaf_color, (lx - size//8, ly - size//16, size//4, size//8))
        
        # Arms/vines
        arm_swing = math.sin(frame * 0.15) * 10
        pygame.draw.arc(surf, body_color, (0, size//3 + arm_swing, size//3, size//2), 
                       math.pi/2, math.pi*3/2, 8)
        pygame.draw.arc(surf, body_color, (size*2//3, size//3 - arm_swing, size//3, size//2),
                       -math.pi/2, math.pi/2, 8)
        
        return surf
    
    @staticmethod
    def create_king_boo_sprite(size: int = 80, frame: int = 0, attacking: bool = False) -> pygame.Surface:
        """Create King Boo sprite - Ghost king boss"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Ghost body (translucent effect through multiple layers)
        float_offset = math.sin(frame * 0.1) * 5
        
        # Outer glow
        glow_alpha = 100 + int(math.sin(frame * 0.15) * 30)
        glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (200, 200, 255, glow_alpha), 
                          (0, 8 + float_offset, size, size - 16))
        surf.blit(glow_surf, (0, 0))
        
        # Main body
        pygame.draw.ellipse(surf, COLORS['white'], (4, 12 + float_offset, size - 8, size - 20))
        
        # Crown
        crown_y = 4 + float_offset
        pygame.draw.polygon(surf, COLORS['gold'], [
            (size//4, crown_y + 16),
            (size//3, crown_y),
            (size//2, crown_y + 12),
            (size*2//3, crown_y),
            (size*3//4, crown_y + 16)
        ])
        # Crown gem
        pygame.draw.circle(surf, COLORS['purple'], (size//2, crown_y + 8), size//16)
        
        # Eyes
        eye_y = size//3 + float_offset
        if attacking:
            # Angry eyes
            pygame.draw.ellipse(surf, COLORS['black'], (size//4, eye_y, size//5, size//6))
            pygame.draw.ellipse(surf, COLORS['black'], (size*11//20, eye_y, size//5, size//6))
            # Red glow
            pygame.draw.circle(surf, COLORS['red'], (size//4 + size//10, eye_y + size//12), size//16)
            pygame.draw.circle(surf, COLORS['red'], (size*11//20 + size//10, eye_y + size//12), size//16)
        else:
            pygame.draw.ellipse(surf, COLORS['black'], (size//4, eye_y, size//5, size//5))
            pygame.draw.ellipse(surf, COLORS['black'], (size*11//20, eye_y, size//5, size//5))
        
        # Tongue (when attacking)
        if attacking:
            tongue_ext = abs(math.sin(frame * 0.2)) * size//4
            pygame.draw.ellipse(surf, COLORS['pink'], 
                              (size//3, size*2//3 + float_offset, size//3, size//8 + tongue_ext))
        
        # Wavy bottom
        for i in range(4):
            wave_x = size//6 + i * size//5
            wave_y = size - 8 + math.sin(frame * 0.2 + i) * 4 + float_offset
            pygame.draw.circle(surf, COLORS['white'], (wave_x, int(wave_y)), size//10)
        
        return surf
    
    @staticmethod
    def create_powerup_sprite(power_type: PowerUp, size: int = 24, frame: int = 0) -> pygame.Surface:
        """Create power-up sprites"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if power_type == PowerUp.MUSHROOM:
            # Super Mushroom
            pygame.draw.ellipse(surf, COLORS['red'], (2, 0, size - 4, size//2 + 4))
            pygame.draw.rect(surf, COLORS['skin'], (size//4, size//2, size//2, size//2))
            # Spots
            pygame.draw.circle(surf, COLORS['white'], (size//3, size//4), size//8)
            pygame.draw.circle(surf, COLORS['white'], (size*2//3, size//4), size//8)
            # Eyes
            pygame.draw.circle(surf, COLORS['black'], (size//3, size*5//8), 2)
            pygame.draw.circle(surf, COLORS['black'], (size*2//3, size*5//8), 2)
            
        elif power_type == PowerUp.FIRE_FLOWER:
            # Fire Flower
            stem_color = COLORS['green']
            pygame.draw.rect(surf, stem_color, (size//2 - 2, size//2, 4, size//2))
            # Petals
            petal_colors = [COLORS['red'], COLORS['orange'], COLORS['yellow'], COLORS['white']]
            for i in range(4):
                angle = i * math.pi/2 + frame * 0.1
                px = size//2 + math.cos(angle) * size//4
                py = size//3 + math.sin(angle) * size//4
                pygame.draw.circle(surf, petal_colors[i], (int(px), int(py)), size//6)
            # Center
            pygame.draw.circle(surf, COLORS['orange'], (size//2, size//3), size//8)
            # Eyes
            pygame.draw.circle(surf, COLORS['black'], (size//2 - 2, size//3), 2)
            pygame.draw.circle(surf, COLORS['black'], (size//2 + 2, size//3), 2)
            
        elif power_type == PowerUp.STAR:
            # Super Star
            bounce = abs(math.sin(frame * 0.2)) * 4
            color_shift = (frame // 4) % 4
            colors = [COLORS['yellow'], COLORS['gold'], COLORS['white'], COLORS['gold']]
            star_color = colors[color_shift]
            
            # Draw 5-pointed star
            points = []
            for i in range(10):
                angle = i * math.pi / 5 - math.pi/2
                radius = size//2 - 2 if i % 2 == 0 else size//4
                px = size//2 + math.cos(angle) * radius
                py = size//2 - bounce + math.sin(angle) * radius
                points.append((px, py))
            pygame.draw.polygon(surf, star_color, points)
            pygame.draw.polygon(surf, COLORS['black'], points, 2)
            # Eyes
            pygame.draw.circle(surf, COLORS['black'], (size//2 - 4, int(size//2 - bounce - 2)), 2)
            pygame.draw.circle(surf, COLORS['black'], (size//2 + 4, int(size//2 - bounce - 2)), 2)
            
        elif power_type == PowerUp.CAPE:
            # Cape Feather (SMW style)
            pygame.draw.ellipse(surf, COLORS['yellow'], (4, 4, size - 8, size - 8))
            # Feather detail lines
            pygame.draw.arc(surf, COLORS['orange'], (6, 6, size - 12, size - 12), 0, math.pi, 2)
            pygame.draw.line(surf, COLORS['red'], (size//2, 4), (size//2, size - 4), 2)
        
        return surf
    
    @staticmethod
    def create_fireball_sprite(size: int = 12, frame: int = 0) -> pygame.Surface:
        """Create Mario's fireball"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        colors = [COLORS['orange'], COLORS['red'], COLORS['yellow']]
        color = colors[(frame // 2) % 3]
        
        pygame.draw.circle(surf, color, (size//2, size//2), size//2)
        pygame.draw.circle(surf, COLORS['yellow'], (size//2, size//2), size//4)
        
        return surf
    
    @staticmethod
    def create_block_sprite(block_type: str, size: int = 32, frame: int = 0) -> pygame.Surface:
        """Create various block sprites"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        if block_type == "brick":
            pygame.draw.rect(surf, COLORS['brown'], (0, 0, size, size))
            # Brick pattern
            pygame.draw.line(surf, COLORS['black'], (0, size//2), (size, size//2), 2)
            pygame.draw.line(surf, COLORS['black'], (size//2, 0), (size//2, size//2), 2)
            pygame.draw.line(surf, COLORS['black'], (size//4, size//2), (size//4, size), 2)
            pygame.draw.line(surf, COLORS['black'], (size*3//4, size//2), (size*3//4, size), 2)
            pygame.draw.rect(surf, COLORS['black'], (0, 0, size, size), 2)
            
        elif block_type == "question":
            # Animated question block
            shine = abs(math.sin(frame * 0.15)) * 30
            base_color = (200 + int(shine), 150 + int(shine), 0)
            pygame.draw.rect(surf, base_color, (0, 0, size, size))
            pygame.draw.rect(surf, COLORS['black'], (0, 0, size, size), 2)
            # Question mark
            pygame.draw.arc(surf, COLORS['black'], (size//4, size//6, size//2, size//2), 0, math.pi*1.5, 3)
            pygame.draw.rect(surf, COLORS['black'], (size//2 - 2, size//2, 4, size//6))
            pygame.draw.rect(surf, COLORS['black'], (size//2 - 2, size*3//4, 4, 4))
            
        elif block_type == "ground":
            pygame.draw.rect(surf, COLORS['brown'], (0, 0, size, size))
            pygame.draw.rect(surf, (100, 60, 30), (2, 2, size-4, size//3))
            pygame.draw.rect(surf, COLORS['black'], (0, 0, size, size), 1)
            
        elif block_type == "platform":
            pygame.draw.rect(surf, (180, 180, 180), (0, 0, size, size))
            pygame.draw.rect(surf, (220, 220, 220), (2, 2, size-4, size//3))
            pygame.draw.rect(surf, (100, 100, 100), (0, 0, size, size), 2)
        
        return surf


# ============================================================================
# HUD SYSTEM - Galaxy-inspired heads-up display
# ============================================================================
class GalaxyHUD:
    """Galaxy-styled HUD system"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Star counter animation
        self.star_rotation = 0
        self.coin_spin = 0
        
    def draw(self, player_health: int, max_health: int, lives: int, 
             coins: int, score: int, boss_health: int = 0, boss_max_health: int = 0,
             boss_name: str = "", frame: int = 0):
        """Draw the complete HUD"""
        self.star_rotation = frame * 2
        self.coin_spin = frame
        
        # Top bar background (Galaxy style gradient)
        gradient_surf = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
        for y in range(60):
            alpha = 200 - y * 2
            pygame.draw.line(gradient_surf, (*COLORS['galaxy_purple'][:3], alpha), 
                           (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(gradient_surf, (0, 0))
        
        # Mario icon and lives
        mario_icon = SpriteGenerator.create_mario_sprite(16, PowerUp.MUSHROOM)
        self.screen.blit(pygame.transform.scale(mario_icon, (32, 64)), (10, -10))
        lives_text = self.font_medium.render(f"x {lives}", True, COLORS['white'])
        self.screen.blit(lives_text, (50, 15))
        
        # Health meter (like Galaxy's health wheel)
        self._draw_health_wheel(150, 30, player_health, max_health)
        
        # Coin counter with spinning coin
        self._draw_coin_counter(SCREEN_WIDTH - 200, 10, coins)
        
        # Score with star
        self._draw_score(SCREEN_WIDTH - 200, 35, score)
        
        # Boss health bar (if in boss fight)
        if boss_max_health > 0:
            self._draw_boss_health(boss_name, boss_health, boss_max_health)
    
    def _draw_health_wheel(self, x: int, y: int, health: int, max_health: int):
        """Draw Galaxy-style health meter"""
        radius = 20
        
        # Background circle
        pygame.draw.circle(self.screen, COLORS['dark_blue'], (x, y), radius + 2)
        
        # Health segments
        for i in range(max_health):
            angle_start = -90 + (i * 360 / max_health)
            angle_end = -90 + ((i + 1) * 360 / max_health)
            
            color = COLORS['green'] if i < health else COLORS['dark_blue']
            if i < health:
                # Glowing effect for filled segments
                glow_color = (100, 255, 100)
                pygame.draw.arc(self.screen, glow_color, 
                              (x - radius - 2, y - radius - 2, radius * 2 + 4, radius * 2 + 4),
                              math.radians(angle_start), math.radians(angle_end), 4)
            
            pygame.draw.arc(self.screen, color,
                          (x - radius, y - radius, radius * 2, radius * 2),
                          math.radians(angle_start), math.radians(angle_end), 6)
        
        # Center
        pygame.draw.circle(self.screen, COLORS['white'], (x, y), radius - 8)
        
        # Health number
        health_text = self.font_small.render(str(health), True, COLORS['black'])
        text_rect = health_text.get_rect(center=(x, y))
        self.screen.blit(health_text, text_rect)
    
    def _draw_coin_counter(self, x: int, y: int, coins: int):
        """Draw coin counter with spinning coin animation"""
        # Spinning coin (simple scale effect)
        coin_scale = abs(math.sin(self.coin_spin * 0.1))
        coin_width = int(16 * max(0.2, coin_scale))
        
        pygame.draw.ellipse(self.screen, COLORS['gold'], 
                          (x, y + 4, coin_width, 16))
        pygame.draw.ellipse(self.screen, COLORS['yellow'],
                          (x + 2, y + 6, max(1, coin_width - 4), 12))
        
        # Coin count
        coin_text = self.font_medium.render(f"x {coins}", True, COLORS['white'])
        self.screen.blit(coin_text, (x + 24, y))
    
    def _draw_score(self, x: int, y: int, score: int):
        """Draw score with star icon"""
        # Rotating star
        star_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        points = []
        for i in range(10):
            angle = math.radians(self.star_rotation + i * 36 - 90)
            r = 8 if i % 2 == 0 else 4
            px = 10 + math.cos(angle) * r
            py = 10 + math.sin(angle) * r
            points.append((px, py))
        pygame.draw.polygon(star_surf, COLORS['star_yellow'], points)
        self.screen.blit(star_surf, (x, y))
        
        # Score text
        score_text = self.font_small.render(f"{score:08d}", True, COLORS['white'])
        self.screen.blit(score_text, (x + 24, y + 2))
    
    def _draw_boss_health(self, name: str, health: int, max_health: int):
        """Draw boss health bar at bottom of screen"""
        bar_width = 400
        bar_height = 20
        x = (SCREEN_WIDTH - bar_width) // 2
        y = SCREEN_HEIGHT - 50
        
        # Boss name
        name_text = self.font_medium.render(name, True, COLORS['white'])
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, y - 20))
        
        # Name shadow
        shadow_text = self.font_medium.render(name, True, COLORS['black'])
        self.screen.blit(shadow_text, (name_rect.x + 2, name_rect.y + 2))
        self.screen.blit(name_text, name_rect)
        
        # Health bar background
        pygame.draw.rect(self.screen, COLORS['dark_blue'], (x - 2, y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, COLORS['black'], (x, y, bar_width, bar_height))
        
        # Health bar fill
        health_width = int((health / max_health) * bar_width)
        if health_width > 0:
            # Gradient effect
            for i in range(health_width):
                progress = i / bar_width
                r = int(255 * (1 - progress * 0.3))
                g = int(50 + 100 * progress)
                b = 50
                pygame.draw.line(self.screen, (r, g, b), (x + i, y), (x + i, y + bar_height))
        
        # Health bar border
        pygame.draw.rect(self.screen, COLORS['white'], (x, y, bar_width, bar_height), 2)
        
        # Health text
        health_text = self.font_small.render(f"{health}/{max_health}", True, COLORS['white'])
        text_rect = health_text.get_rect(center=(SCREEN_WIDTH // 2, y + bar_height // 2))
        self.screen.blit(health_text, text_rect)


# ============================================================================
# ENTITY CLASSES
# ============================================================================
@dataclass
class Vector2:
    x: float = 0
    y: float = 0
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self):
        l = self.length()
        if l > 0:
            return Vector2(self.x / l, self.y / l)
        return Vector2(0, 0)


class Entity:
    """Base entity class"""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.width = width
        self.height = height
        self.active = True
        self.frame = 0
        
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.width, self.height)
    
    def update(self, dt: float):
        self.frame += 1
        self.pos.x += self.vel.x * dt * 60
        self.pos.y += self.vel.y * dt * 60
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        pass


class Player(Entity):
    """Mario player class with SMB3-style physics"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24, 32)
        
        # Physics constants (SMB3 style)
        self.gravity = 0.6
        self.max_fall_speed = 12
        self.run_speed = 5
        self.max_run_speed = 7
        self.jump_power = 12
        self.air_control = 0.7
        
        # State
        self.on_ground = False
        self.facing_right = True
        self.jumping = False
        self.running = False
        self.invincible_timer = 0
        self.star_timer = 0
        
        # Stats
        self.power_state = PowerUp.MUSHROOM
        self.health = 3
        self.max_health = 3
        self.lives = 3
        self.coins = 0
        self.score = 0
        
        # Attack
        self.attack_cooldown = 0
        self.fireballs: List[Fireball] = []
        
        # Animation
        self.anim_frame = 0
        self.walk_timer = 0
        
    def update(self, dt: float, keys: dict, platforms: List[pygame.Rect]):
        self.frame += 1
        self.walk_timer += 1
        
        # Update timers
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.star_timer > 0:
            self.star_timer -= 1
            if self.star_timer == 0 and self.power_state == PowerUp.STAR:
                self.power_state = PowerUp.MUSHROOM
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        # Horizontal movement
        move_speed = self.max_run_speed if self.running else self.run_speed
        accel = 0.5 if self.on_ground else 0.3
        
        if keys.get('left'):
            self.vel.x = max(self.vel.x - accel, -move_speed)
            self.facing_right = False
        elif keys.get('right'):
            self.vel.x = min(self.vel.x + accel, move_speed)
            self.facing_right = True
        else:
            # Friction
            friction = 0.85 if self.on_ground else 0.95
            self.vel.x *= friction
            if abs(self.vel.x) < 0.1:
                self.vel.x = 0
        
        # Jumping
        if keys.get('jump') and self.on_ground and not self.jumping:
            self.vel.y = -self.jump_power
            self.jumping = True
            self.on_ground = False
        
        # Variable jump height
        if not keys.get('jump') and self.vel.y < -4:
            self.vel.y = -4
        
        # Gravity
        if not self.on_ground:
            self.vel.y = min(self.vel.y + self.gravity, self.max_fall_speed)
        
        # Apply velocity
        self.pos.x += self.vel.x * dt * 60
        self.pos.y += self.vel.y * dt * 60
        
        # Platform collision
        self.on_ground = False
        player_rect = self.rect
        
        for plat in platforms:
            if player_rect.colliderect(plat):
                # Vertical collision
                if self.vel.y > 0 and player_rect.bottom > plat.top and player_rect.top < plat.top:
                    self.pos.y = plat.top - self.height
                    self.vel.y = 0
                    self.on_ground = True
                    self.jumping = False
                elif self.vel.y < 0 and player_rect.top < plat.bottom and player_rect.bottom > plat.bottom:
                    self.pos.y = plat.bottom
                    self.vel.y = 0
                
                # Update rect after vertical correction
                player_rect = self.rect
                
                # Horizontal collision
                if player_rect.colliderect(plat):
                    if self.vel.x > 0:
                        self.pos.x = plat.left - self.width
                    elif self.vel.x < 0:
                        self.pos.x = plat.right
                    self.vel.x = 0
        
        # Screen bounds
        self.pos.x = max(0, min(self.pos.x, SCREEN_WIDTH - self.width))
        if self.pos.y > SCREEN_HEIGHT:
            self.take_damage(self.health)  # Fall death
        
        # Update fireballs
        for fb in self.fireballs[:]:
            fb.update(dt)
            if not fb.active:
                self.fireballs.remove(fb)
        
        # Animation
        if abs(self.vel.x) > 0.5:
            if self.walk_timer > 6:
                self.anim_frame = (self.anim_frame + 1) % 4
                self.walk_timer = 0
        else:
            self.anim_frame = 0
    
    def attack(self):
        """Fire attack based on power state"""
        if self.attack_cooldown > 0:
            return None
        
        if self.power_state == PowerUp.FIRE_FLOWER:
            self.attack_cooldown = 15
            direction = 1 if self.facing_right else -1
            fb = Fireball(self.pos.x + self.width//2, self.pos.y + self.height//2, direction)
            self.fireballs.append(fb)
            return fb
        elif self.power_state == PowerUp.STAR:
            # Star power does contact damage, no projectile needed
            pass
        return None
    
    def take_damage(self, amount: int = 1):
        """Handle taking damage"""
        if self.invincible_timer > 0 or self.star_timer > 0:
            return
        
        self.health -= amount
        self.invincible_timer = 120  # 2 seconds at 60fps
        
        # Downgrade power state
        if self.power_state == PowerUp.FIRE_FLOWER:
            self.power_state = PowerUp.MUSHROOM
        elif self.power_state == PowerUp.MUSHROOM and self.health <= 0:
            self.power_state = PowerUp.NONE
        
        if self.health <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.respawn()
    
    def respawn(self):
        """Respawn after death"""
        self.health = self.max_health
        self.power_state = PowerUp.MUSHROOM
        self.invincible_timer = 180
        self.pos = Vector2(100, 300)
        self.vel = Vector2(0, 0)
    
    def collect_powerup(self, power_type: PowerUp):
        """Collect a power-up"""
        if power_type == PowerUp.MUSHROOM:
            if self.power_state == PowerUp.NONE:
                self.power_state = PowerUp.MUSHROOM
            else:
                self.health = min(self.health + 1, self.max_health)
        elif power_type == PowerUp.FIRE_FLOWER:
            self.power_state = PowerUp.FIRE_FLOWER
            self.health = min(self.health + 1, self.max_health)
        elif power_type == PowerUp.STAR:
            self.power_state = PowerUp.STAR
            self.star_timer = 600  # 10 seconds
        elif power_type == PowerUp.CAPE:
            self.power_state = PowerUp.CAPE
        
        self.score += 1000
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        # Blinking when invincible
        if self.invincible_timer > 0 and (self.frame // 4) % 2 == 0:
            return
        
        sprite = SpriteGenerator.create_mario_sprite(24, self.power_state, self.frame)
        
        # Flip if facing left
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        
        draw_x = self.pos.x - camera_offset.x
        draw_y = self.pos.y - camera_offset.y - (sprite.get_height() - self.height)
        
        screen.blit(sprite, (draw_x, draw_y))
        
        # Draw fireballs
        for fb in self.fireballs:
            fb.draw(screen, camera_offset)


class Fireball(Entity):
    """Mario's fireball projectile"""
    
    def __init__(self, x: float, y: float, direction: int):
        super().__init__(x, y, 12, 12)
        self.vel = Vector2(direction * 8, 0)
        self.gravity = 0.4
        self.bounce_power = -6
        self.damage = 1
        self.lifetime = 180
        
    def update(self, dt: float):
        super().update(dt)
        
        # Gravity and bouncing
        self.vel.y += self.gravity
        
        # Ground bounce (simple)
        if self.pos.y > SCREEN_HEIGHT - 100:
            self.pos.y = SCREEN_HEIGHT - 100
            self.vel.y = self.bounce_power
        
        # Lifetime
        self.lifetime -= 1
        if self.lifetime <= 0 or self.pos.x < 0 or self.pos.x > SCREEN_WIDTH:
            self.active = False
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        sprite = SpriteGenerator.create_fireball_sprite(12, self.frame)
        screen.blit(sprite, (self.pos.x - camera_offset.x, self.pos.y - camera_offset.y))


class PowerUpItem(Entity):
    """Collectible power-up"""
    
    def __init__(self, x: float, y: float, power_type: PowerUp):
        super().__init__(x, y, 24, 24)
        self.power_type = power_type
        self.float_offset = 0
        self.collected = False
        
    def update(self, dt: float):
        super().update(dt)
        self.float_offset = math.sin(self.frame * 0.1) * 4
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        if self.collected:
            return
        
        sprite = SpriteGenerator.create_powerup_sprite(self.power_type, 24, self.frame)
        draw_y = self.pos.y + self.float_offset - camera_offset.y
        screen.blit(sprite, (self.pos.x - camera_offset.x, draw_y))


# ============================================================================
# BOSS CLASSES
# ============================================================================
class Boss(Entity):
    """Base boss class"""
    
    def __init__(self, x: float, y: float, width: int, height: int, 
                 name: str, max_health: int):
        super().__init__(x, y, width, height)
        self.name = name
        self.health = max_health
        self.max_health = max_health
        self.phase = 1
        self.attack_timer = 0
        self.state = "idle"
        self.defeated = False
        self.intro_timer = 180
        self.death_timer = 0
        self.vulnerable = True
        self.damage_flash = 0
        
    def take_damage(self, amount: int = 1):
        if not self.vulnerable or self.damage_flash > 0:
            return False
        
        self.health -= amount
        self.damage_flash = 30
        
        if self.health <= 0:
            self.defeated = True
            self.death_timer = 120
        elif self.health <= self.max_health // 2 and self.phase == 1:
            self.phase = 2
            self.on_phase_change()
        
        return True
    
    def on_phase_change(self):
        """Override in subclasses for phase transition behavior"""
        pass
    
    def update(self, dt: float, player: Player):
        super().update(dt)
        
        if self.damage_flash > 0:
            self.damage_flash -= 1
        
        if self.intro_timer > 0:
            self.intro_timer -= 1
            return
        
        if self.defeated:
            self.death_timer -= 1
            return
        
        self.attack_timer += 1
        self._update_ai(dt, player)
    
    def _update_ai(self, dt: float, player: Player):
        """Override in subclasses"""
        pass
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        pass


class Goomboss(Boss):
    """First boss - Giant Goomba King"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 96, 96, "GOOMBOSS", 8)
        self.charge_speed = 6
        self.stomp_cooldown = 0
        self.angry = False
        self.jump_timer = 0
        self.minions: List[Entity] = []
        
    def on_phase_change(self):
        self.angry = True
        self.charge_speed = 8
        
    def _update_ai(self, dt: float, player: Player):
        # Basic AI: Move toward player, occasionally jump
        dx = player.pos.x - self.pos.x
        
        if abs(dx) > 20:
            self.vel.x = self.charge_speed if dx > 0 else -self.charge_speed
        else:
            self.vel.x = 0
        
        # Jump attack
        self.jump_timer += 1
        if self.jump_timer > 120 and self.vel.y == 0:
            self.vel.y = -15
            self.jump_timer = 0
        
        # Gravity
        self.vel.y = min(self.vel.y + 0.8, 12)
        
        # Ground check
        if self.pos.y > SCREEN_HEIGHT - 150 - self.height:
            self.pos.y = SCREEN_HEIGHT - 150 - self.height
            self.vel.y = 0
        
        # Summon minions in phase 2
        if self.phase == 2 and self.attack_timer % 180 == 0:
            self._summon_minion()
    
    def _summon_minion(self):
        # Create a small goomba minion (simplified)
        pass
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        # Flash when damaged
        if self.damage_flash > 0 and (self.frame // 4) % 2 == 0:
            return
        
        sprite = SpriteGenerator.create_goomboss_sprite(96, self.frame, self.angry)
        
        draw_x = self.pos.x - camera_offset.x
        draw_y = self.pos.y - camera_offset.y
        
        # Shake when angry
        if self.angry and self.attack_timer % 4 < 2:
            draw_x += random.randint(-2, 2)
        
        screen.blit(sprite, (draw_x, draw_y))


class Yoob(Boss):
    """Second boss - Corrupted giant Yoshi creature from Partners in Time"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 128, 128, "YOOB", 12)
        self.tongue_attack = False
        self.tongue_extend = 0
        self.egg_timer = 0
        self.eggs: List[Entity] = []
        
    def on_phase_change(self):
        # Get faster and more aggressive
        pass
    
    def _update_ai(self, dt: float, player: Player):
        dx = player.pos.x - self.pos.x
        
        # Slow movement toward player
        move_speed = 2 if self.phase == 1 else 3
        if abs(dx) > 50:
            self.vel.x = move_speed if dx > 0 else -move_speed
        else:
            self.vel.x = 0
        
        # Ground
        if self.pos.y < SCREEN_HEIGHT - 180 - self.height:
            self.vel.y = min(self.vel.y + 0.5, 8)
        else:
            self.pos.y = SCREEN_HEIGHT - 180 - self.height
            self.vel.y = 0
        
        # Tongue attack pattern
        if self.attack_timer % 150 == 0:
            self.tongue_attack = True
            self.tongue_extend = 0
        
        if self.tongue_attack:
            self.tongue_extend = min(self.tongue_extend + 10, 200)
            if self.tongue_extend >= 200:
                self.tongue_attack = False
        else:
            self.tongue_extend = max(0, self.tongue_extend - 15)
        
        # Egg attack in phase 2
        if self.phase == 2:
            self.egg_timer += 1
            if self.egg_timer > 90:
                self.egg_timer = 0
                # Spawn egg projectile
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        if self.damage_flash > 0 and (self.frame // 4) % 2 == 0:
            return
        
        sprite = SpriteGenerator.create_yoob_sprite(128, self.frame, self.phase)
        
        draw_x = self.pos.x - camera_offset.x
        draw_y = self.pos.y - camera_offset.y
        
        screen.blit(sprite, (draw_x, draw_y))
        
        # Draw tongue
        if self.tongue_extend > 0:
            tongue_color = (200, 100, 150)
            tongue_start = (draw_x + 120, draw_y + 30)
            tongue_end = (tongue_start[0] + self.tongue_extend, tongue_start[1])
            pygame.draw.line(screen, tongue_color, tongue_start, tongue_end, 12)
            pygame.draw.circle(screen, tongue_color, (int(tongue_end[0]), int(tongue_end[1])), 15)


class PeteyPiranha(Boss):
    """Third boss - Petey Piranha"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 96, 96, "PETEY PIRANHA", 10)
        self.flying = False
        self.fly_height = 0
        self.mouth_open = False
        self.goop_timer = 0
        
    def _update_ai(self, dt: float, player: Player):
        dx = player.pos.x - self.pos.x
        
        # Flying pattern
        if self.attack_timer % 240 < 120:
            self.flying = True
            target_y = 150
        else:
            self.flying = False
            target_y = SCREEN_HEIGHT - 180 - self.height
        
        # Move toward target height
        dy = target_y - self.pos.y
        self.vel.y = max(-4, min(4, dy * 0.1))
        
        # Move toward player
        move_speed = 3 if not self.flying else 5
        if abs(dx) > 30:
            self.vel.x = move_speed if dx > 0 else -move_speed
        else:
            self.vel.x = 0
        
        # Mouth attack pattern
        if self.attack_timer % 60 < 20:
            self.mouth_open = True
        else:
            self.mouth_open = False
        
        # Screen bounds
        self.pos.x = max(50, min(self.pos.x, SCREEN_WIDTH - 150))
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        if self.damage_flash > 0 and (self.frame // 4) % 2 == 0:
            return
        
        sprite = SpriteGenerator.create_petey_piranha_sprite(96, self.frame, self.mouth_open)
        screen.blit(sprite, (self.pos.x - camera_offset.x, self.pos.y - camera_offset.y))


class KingBoo(Boss):
    """Fourth boss - King Boo"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 80, 80, "KING BOO", 10)
        self.visible = True
        self.fade_timer = 0
        self.attacking = False
        self.orbit_angle = 0
        self.minions: List = []
        
    def _update_ai(self, dt: float, player: Player):
        # Orbit around arena center
        self.orbit_angle += 0.02 if self.phase == 1 else 0.03
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2 - 50
        orbit_radius = 200 if self.phase == 1 else 150
        
        target_x = center_x + math.cos(self.orbit_angle) * orbit_radius
        target_y = center_y + math.sin(self.orbit_angle) * orbit_radius * 0.5
        
        self.pos.x += (target_x - self.pos.x) * 0.05
        self.pos.y += (target_y - self.pos.y) * 0.05
        
        # Visibility cycling
        self.fade_timer += 1
        if self.fade_timer > 180:
            self.visible = not self.visible
            self.fade_timer = 0
        
        # Attack pattern
        if self.attack_timer % 90 < 30:
            self.attacking = True
        else:
            self.attacking = False
        
        # Only vulnerable when visible
        self.vulnerable = self.visible
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        if not self.visible and self.fade_timer > 30:
            return
        
        if self.damage_flash > 0 and (self.frame // 4) % 2 == 0:
            return
        
        sprite = SpriteGenerator.create_king_boo_sprite(80, self.frame, self.attacking)
        
        # Fade effect
        if not self.visible or self.fade_timer < 30:
            alpha = 255 if self.visible else max(0, 255 - self.fade_timer * 8)
            sprite.set_alpha(alpha)
        
        screen.blit(sprite, (self.pos.x - camera_offset.x, self.pos.y - camera_offset.y))


class Kamek(Boss):
    """Final boss - Kamek the Magikoopa"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 64, 64, "KAMEK", 15)
        self.casting = False
        self.teleport_timer = 0
        self.magic_projectiles: List = []
        self.pattern = 0
        
    def on_phase_change(self):
        self.pattern = 1
        
    def _update_ai(self, dt: float, player: Player):
        # Teleport pattern
        self.teleport_timer += 1
        if self.teleport_timer > 120:
            self.teleport_timer = 0
            # Teleport to random position
            self.pos.x = random.randint(100, SCREEN_WIDTH - 164)
            self.pos.y = random.randint(100, 300)
        
        # Casting animation
        if self.attack_timer % 60 < 30:
            self.casting = True
        else:
            self.casting = False
        
        # Float in place with slight movement
        self.pos.y += math.sin(self.frame * 0.05) * 0.5
        
        # Magic attack pattern
        if self.casting and self.attack_timer % 30 == 0:
            self._cast_magic(player)
    
    def _cast_magic(self, player: Player):
        # Create magic projectile aimed at player
        pass
    
    def draw(self, screen: pygame.Surface, camera_offset: Vector2 = None):
        if camera_offset is None:
            camera_offset = Vector2(0, 0)
        
        if self.damage_flash > 0 and (self.frame // 4) % 2 == 0:
            return
        
        sprite = SpriteGenerator.create_kamek_sprite(64, self.frame, self.casting)
        
        # Magic aura when casting
        if self.casting:
            aura_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            aura_alpha = int(100 + math.sin(self.frame * 0.2) * 50)
            pygame.draw.circle(aura_surf, (*COLORS['purple'][:3], aura_alpha), (40, 40), 35)
            screen.blit(aura_surf, (self.pos.x - 8 - camera_offset.x, self.pos.y - 8 - camera_offset.y))
        
        screen.blit(sprite, (self.pos.x - camera_offset.x, self.pos.y - camera_offset.y))


# ============================================================================
# GAME SCENES
# ============================================================================
class Scene:
    """Base scene class"""
    
    def __init__(self, game):
        self.game = game
        
    def update(self, dt: float, events: List):
        pass
    
    def draw(self, screen: pygame.Surface):
        pass


class TitleScene(Scene):
    """Title screen"""
    
    def __init__(self, game):
        super().__init__(game)
        self.timer = 0
        self.font_title = pygame.font.Font(None, 72)
        self.font_sub = pygame.font.Font(None, 36)
        self.font_prompt = pygame.font.Font(None, 28)
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), 
                      random.random() * 2 + 0.5) for _ in range(100)]
        
    def update(self, dt: float, events: List):
        self.timer += 1
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    self.game.change_state(GameState.CORRIDOR)
    
    def draw(self, screen: pygame.Surface):
        # Starfield background (Galaxy style)
        screen.fill(COLORS['galaxy_purple'])
        
        for i, (x, y, speed) in enumerate(self.stars):
            brightness = int(150 + math.sin(self.timer * 0.05 + i) * 100)
            color = (brightness, brightness, min(255, brightness + 50))
            size = 1 if speed < 1 else 2
            pygame.draw.circle(screen, color, (int(x), int(y)), size)
            
            # Animate stars
            self.stars[i] = ((x + speed * 0.5) % SCREEN_WIDTH, y, speed)
        
        # Title with glow effect
        title_text = "ULTRA MARIO 2D BROS"
        subtitle_text = "BOSS FIGHT REDUX"
        
        # Glow
        glow_offset = math.sin(self.timer * 0.05) * 3
        glow_color = (255, 200, 100)
        glow_surf = self.font_title.render(title_text, True, glow_color)
        glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2, 150 + glow_offset))
        
        # Shadow
        shadow_surf = self.font_title.render(title_text, True, COLORS['black'])
        screen.blit(shadow_surf, (glow_rect.x + 4, glow_rect.y + 4))
        
        # Main title
        title_surf = self.font_title.render(title_text, True, COLORS['gold'])
        screen.blit(title_surf, glow_rect)
        
        # Subtitle
        sub_surf = self.font_sub.render(subtitle_text, True, COLORS['red'])
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH//2, 210))
        screen.blit(sub_surf, sub_rect)
        
        # Mario sprite
        mario = SpriteGenerator.create_mario_sprite(32, PowerUp.FIRE_FLOWER, self.timer)
        screen.blit(pygame.transform.scale(mario, (64, 128)), (SCREEN_WIDTH//2 - 32, 280))
        
        # Boss preview icons
        boss_y = 450
        boss_sprites = [
            SpriteGenerator.create_goomboss_sprite(48, self.timer),
            SpriteGenerator.create_yoob_sprite(48, self.timer),
            SpriteGenerator.create_petey_piranha_sprite(48, self.timer),
            SpriteGenerator.create_king_boo_sprite(48, self.timer),
            SpriteGenerator.create_kamek_sprite(48, self.timer)
        ]
        
        start_x = SCREEN_WIDTH//2 - len(boss_sprites) * 35
        for i, sprite in enumerate(boss_sprites):
            screen.blit(pygame.transform.scale(sprite, (48, 48)), (start_x + i * 70, boss_y))
        
        # Press start prompt
        if (self.timer // 30) % 2 == 0:
            prompt_surf = self.font_prompt.render("PRESS ENTER TO START", True, COLORS['white'])
            prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH//2, 550))
            screen.blit(prompt_surf, prompt_rect)
        
        # Credits
        credit_surf = self.font_prompt.render("By Team Flames / Samsoft", True, COLORS['cyan'])
        credit_rect = credit_surf.get_rect(center=(SCREEN_WIDTH//2, 580))
        screen.blit(credit_surf, credit_rect)


class CorridorScene(Scene):
    """Power-up corridor between boss fights"""
    
    def __init__(self, game, boss_index: int = 0):
        super().__init__(game)
        self.boss_index = boss_index
        self.player = game.player
        self.timer = 0
        
        # Create platforms
        self.platforms = [
            pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Ground
        ]
        
        # Add floating platforms
        for i in range(3):
            self.platforms.append(
                pygame.Rect(150 + i * 200, 400 - i * 50, 100, 20)
            )
        
        # Power-ups based on boss index
        self.powerups = []
        if boss_index == 0:
            self.powerups.append(PowerUpItem(200, 350, PowerUp.MUSHROOM))
        elif boss_index == 1:
            self.powerups.append(PowerUpItem(200, 350, PowerUp.FIRE_FLOWER))
        elif boss_index == 2:
            self.powerups.append(PowerUpItem(200, 350, PowerUp.FIRE_FLOWER))
            self.powerups.append(PowerUpItem(400, 280, PowerUp.MUSHROOM))
        elif boss_index >= 3:
            self.powerups.append(PowerUpItem(200, 350, PowerUp.STAR))
            self.powerups.append(PowerUpItem(400, 280, PowerUp.FIRE_FLOWER))
        
        # Question blocks
        self.question_blocks = [
            {"rect": pygame.Rect(300, 300, 32, 32), "hit": False, "item": PowerUp.MUSHROOM},
            {"rect": pygame.Rect(500, 250, 32, 32), "hit": False, "item": PowerUp.FIRE_FLOWER},
        ]
        
        # Door to boss
        self.door_rect = pygame.Rect(SCREEN_WIDTH - 80, SCREEN_HEIGHT - 150, 60, 100)
        self.door_open = False
        
        self.font = pygame.font.Font(None, 36)
        
        # Reset player position
        self.player.pos = Vector2(100, SCREEN_HEIGHT - 150)
        self.player.vel = Vector2(0, 0)
        
    def update(self, dt: float, events: List):
        self.timer += 1
        
        # Get input
        keys = pygame.key.get_pressed()
        key_state = {
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
            'jump': keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP] or keys[pygame.K_w],
            'run': keys[pygame.K_LSHIFT],
            'attack': keys[pygame.K_x]
        }
        
        # Attack input handling
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    self.player.attack()
        
        # Update player
        self.player.update(dt, key_state, self.platforms + 
                          [b["rect"] for b in self.question_blocks if not b["hit"]])
        
        # Check power-up collection
        for powerup in self.powerups[:]:
            if not powerup.collected and self.player.rect.colliderect(powerup.rect):
                self.player.collect_powerup(powerup.power_type)
                powerup.collected = True
        
        # Check question block hits
        for block in self.question_blocks:
            if not block["hit"]:
                player_rect = self.player.rect
                if (player_rect.top <= block["rect"].bottom and 
                    player_rect.top >= block["rect"].bottom - 10 and
                    player_rect.right > block["rect"].left and
                    player_rect.left < block["rect"].right and
                    self.player.vel.y < 0):
                    block["hit"] = True
                    # Spawn item
                    item = PowerUpItem(block["rect"].x, block["rect"].y - 30, block["item"])
                    self.powerups.append(item)
        
        # Update powerups
        for powerup in self.powerups:
            powerup.update(dt)
        
        # Check door collision
        if self.player.rect.colliderect(self.door_rect):
            self.door_open = True
            # Enter boss fight
            self.game.start_boss_fight(self.boss_index)
    
    def draw(self, screen: pygame.Surface):
        # Background gradient (SMW style)
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(135 * (1 - progress) + 100 * progress)
            g = int(206 * (1 - progress) + 150 * progress)
            b = int(235 * (1 - progress) + 200 * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw platforms
        for plat in self.platforms:
            sprite = SpriteGenerator.create_block_sprite("ground" if plat.height > 30 else "platform", 32)
            for x in range(plat.x, plat.x + plat.width, 32):
                screen.blit(sprite, (x, plat.y))
        
        # Draw question blocks
        for block in self.question_blocks:
            block_type = "question" if not block["hit"] else "brick"
            sprite = SpriteGenerator.create_block_sprite(block_type, 32, self.timer)
            screen.blit(sprite, block["rect"])
        
        # Draw door
        door_color = COLORS['brown'] if not self.door_open else COLORS['gold']
        pygame.draw.rect(screen, door_color, self.door_rect)
        pygame.draw.rect(screen, COLORS['black'], self.door_rect, 3)
        # Door handle
        pygame.draw.circle(screen, COLORS['gold'], 
                          (self.door_rect.right - 15, self.door_rect.centery), 5)
        
        # Boss number above door
        boss_names = ["GOOMBOSS", "YOOB", "PETEY PIRANHA", "KING BOO", "KAMEK"]
        if self.boss_index < len(boss_names):
            name_surf = self.font.render(f"BOSS {self.boss_index + 1}: {boss_names[self.boss_index]}", 
                                        True, COLORS['white'])
            name_rect = name_surf.get_rect(center=(self.door_rect.centerx, self.door_rect.top - 20))
            # Shadow
            shadow = self.font.render(f"BOSS {self.boss_index + 1}: {boss_names[self.boss_index]}", 
                                     True, COLORS['black'])
            screen.blit(shadow, (name_rect.x + 2, name_rect.y + 2))
            screen.blit(name_surf, name_rect)
        
        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(screen)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw HUD
        self.game.hud.draw(
            self.player.health, self.player.max_health,
            self.player.lives, self.player.coins,
            self.player.score, frame=self.timer
        )
        
        # Instructions
        if self.timer < 180:
            inst_font = pygame.font.Font(None, 24)
            instructions = [
                "Arrow Keys: Move  |  Space: Jump  |  X: Attack",
                "Enter the door to face the boss!"
            ]
            for i, text in enumerate(instructions):
                surf = inst_font.render(text, True, COLORS['white'])
                rect = surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100 + i * 25))
                screen.blit(surf, rect)


class BossArena(Scene):
    """Boss fight arena"""
    
    def __init__(self, game, boss_index: int):
        super().__init__(game)
        self.boss_index = boss_index
        self.player = game.player
        self.timer = 0
        
        # Create arena platforms
        self.platforms = [
            pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50),  # Ground
            pygame.Rect(100, SCREEN_HEIGHT - 180, 150, 20),  # Left platform
            pygame.Rect(SCREEN_WIDTH - 250, SCREEN_HEIGHT - 180, 150, 20),  # Right platform
            pygame.Rect(SCREEN_WIDTH//2 - 75, SCREEN_HEIGHT - 280, 150, 20),  # Center platform
        ]
        
        # Create boss
        self.boss = self._create_boss(boss_index)
        
        # State
        self.intro_complete = False
        self.victory = False
        self.victory_timer = 0
        
        # Reset player position
        self.player.pos = Vector2(100, SCREEN_HEIGHT - 150)
        self.player.vel = Vector2(0, 0)
        
        self.font = pygame.font.Font(None, 48)
        
    def _create_boss(self, index: int) -> Boss:
        """Create boss based on index"""
        boss_x = SCREEN_WIDTH - 200
        boss_y = SCREEN_HEIGHT - 250
        
        if index == 0:
            return Goomboss(boss_x, boss_y)
        elif index == 1:
            return Yoob(boss_x - 50, boss_y - 50)
        elif index == 2:
            return PeteyPiranha(boss_x, boss_y)
        elif index == 3:
            return KingBoo(SCREEN_WIDTH//2, 200)
        else:
            return Kamek(SCREEN_WIDTH//2, 150)
    
    def update(self, dt: float, events: List):
        self.timer += 1
        
        # Boss intro
        if self.boss.intro_timer > 0:
            self.boss.intro_timer -= 1
            return
        
        if not self.intro_complete:
            self.intro_complete = True
        
        # Victory check
        if self.boss.defeated:
            self.victory_timer += 1
            if self.victory_timer > 180:
                self.player.score += 5000 * (self.boss_index + 1)
                if self.boss_index < 4:
                    self.game.change_state(GameState.CORRIDOR)
                else:
                    self.game.change_state(GameState.VICTORY)
            return
        
        # Get input
        keys = pygame.key.get_pressed()
        key_state = {
            'left': keys[pygame.K_LEFT] or keys[pygame.K_a],
            'right': keys[pygame.K_RIGHT] or keys[pygame.K_d],
            'jump': keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP] or keys[pygame.K_w],
            'run': keys[pygame.K_LSHIFT],
            'attack': keys[pygame.K_x]
        }
        
        # Attack input handling
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    self.player.attack()
        
        # Update player
        self.player.update(dt, key_state, self.platforms)
        
        # Update boss
        self.boss.update(dt, self.player)
        
        # Check player-boss collision
        if self.player.rect.colliderect(self.boss.rect):
            # Check if player is jumping on boss
            if (self.player.vel.y > 0 and 
                self.player.pos.y + self.player.height < self.boss.pos.y + 30):
                # Stomp damage
                if self.boss.take_damage(1):
                    self.player.vel.y = -10
                    self.player.score += 100
            else:
                # Player takes damage
                if self.player.star_timer > 0:
                    # Star power damages boss
                    self.boss.take_damage(1)
                else:
                    self.player.take_damage()
        
        # Check fireball hits
        for fb in self.player.fireballs[:]:
            if fb.rect.colliderect(self.boss.rect):
                if self.boss.take_damage(fb.damage):
                    self.player.score += 50
                fb.active = False
        
        # Check Yoob tongue attack
        if isinstance(self.boss, Yoob) and self.boss.tongue_extend > 50:
            tongue_rect = pygame.Rect(
                self.boss.pos.x + 120,
                self.boss.pos.y + 20,
                self.boss.tongue_extend,
                30
            )
            if self.player.rect.colliderect(tongue_rect):
                self.player.take_damage()
        
        # Game over check
        if self.player.lives <= 0:
            self.game.change_state(GameState.GAME_OVER)
    
    def draw(self, screen: pygame.Surface):
        # Arena background
        self._draw_background(screen)
        
        # Draw platforms
        for plat in self.platforms:
            if plat.height > 30:
                sprite = SpriteGenerator.create_block_sprite("ground", 32)
            else:
                sprite = SpriteGenerator.create_block_sprite("platform", 32)
            for x in range(plat.x, plat.x + plat.width, 32):
                screen.blit(sprite, (x, plat.y))
        
        # Draw boss
        self.boss.draw(screen)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw HUD
        self.game.hud.draw(
            self.player.health, self.player.max_health,
            self.player.lives, self.player.coins,
            self.player.score, self.boss.health, self.boss.max_health,
            self.boss.name, self.timer
        )
        
        # Boss intro text
        if self.boss.intro_timer > 60:
            alpha = min(255, (self.boss.intro_timer - 60) * 4)
            intro_surf = self.font.render(f"VS {self.boss.name}", True, COLORS['white'])
            intro_surf.set_alpha(alpha)
            intro_rect = intro_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            # Background box
            box_rect = intro_rect.inflate(40, 20)
            box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surf.fill((*COLORS['black'][:3], int(alpha * 0.7)))
            screen.blit(box_surf, box_rect)
            screen.blit(intro_surf, intro_rect)
        
        # Victory text
        if self.victory_timer > 0:
            victory_surf = self.font.render(f"{self.boss.name} DEFEATED!", True, COLORS['gold'])
            victory_rect = victory_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            # Animate
            scale = 1 + math.sin(self.victory_timer * 0.1) * 0.1
            scaled = pygame.transform.scale(victory_surf, 
                (int(victory_rect.width * scale), int(victory_rect.height * scale)))
            scaled_rect = scaled.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(scaled, scaled_rect)
    
    def _draw_background(self, screen: pygame.Surface):
        """Draw boss-specific arena background"""
        if self.boss_index == 0:
            # Goomboss - Brown castle
            screen.fill((80, 60, 40))
            for y in range(0, SCREEN_HEIGHT, 64):
                for x in range(0, SCREEN_WIDTH, 64):
                    pygame.draw.rect(screen, (100, 75, 50), (x, y, 62, 62))
                    pygame.draw.rect(screen, (60, 45, 30), (x, y, 64, 64), 2)
        elif self.boss_index == 1:
            # Yoob - Yoshi's Island colorful
            for y in range(SCREEN_HEIGHT):
                progress = y / SCREEN_HEIGHT
                r = int(150 + 50 * progress)
                g = int(220 - 70 * progress)
                b = int(150 + 50 * progress)
                pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        elif self.boss_index == 2:
            # Petey - Jungle
            screen.fill((50, 100, 50))
            for i in range(20):
                x = (i * 100 + self.timer) % (SCREEN_WIDTH + 200) - 100
                pygame.draw.ellipse(screen, (30, 80, 30), (x, 0, 150, 300))
        elif self.boss_index == 3:
            # King Boo - Haunted mansion
            screen.fill((40, 30, 60))
            # Ghost particles
            for i in range(15):
                x = (i * 60 + self.timer * 0.5) % SCREEN_WIDTH
                y = 100 + math.sin(self.timer * 0.02 + i) * 50
                pygame.draw.circle(screen, (60, 50, 80), (int(x), int(y)), 20)
        else:
            # Kamek - Magic sky
            for y in range(SCREEN_HEIGHT):
                progress = y / SCREEN_HEIGHT
                r = int(30 + 40 * progress)
                g = int(20 + 30 * progress)
                b = int(80 + 40 * progress)
                pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
            # Stars
            for i in range(30):
                x = (i * 30 + self.timer * 0.3) % SCREEN_WIDTH
                y = (i * 25) % (SCREEN_HEIGHT - 100)
                brightness = int(150 + math.sin(self.timer * 0.1 + i) * 100)
                pygame.draw.circle(screen, (brightness, brightness, min(255, brightness + 50)), 
                                 (int(x), int(y)), 2)


class GameOverScene(Scene):
    """Game over screen"""
    
    def __init__(self, game):
        super().__init__(game)
        self.timer = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        
    def update(self, dt: float, events: List):
        self.timer += 1
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.reset()
                    self.game.change_state(GameState.TITLE)
    
    def draw(self, screen: pygame.Surface):
        screen.fill(COLORS['black'])
        
        # Game Over text
        text = self.font_large.render("GAME OVER", True, COLORS['red'])
        rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(text, rect)
        
        # Score
        score_text = self.font_medium.render(f"Final Score: {self.game.player.score}", True, COLORS['white'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        screen.blit(score_text, score_rect)
        
        # Prompt
        if (self.timer // 30) % 2 == 0:
            prompt = self.font_medium.render("Press ENTER to try again", True, COLORS['white'])
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
            screen.blit(prompt, prompt_rect)


class VictoryScene(Scene):
    """Victory screen after defeating all bosses"""
    
    def __init__(self, game):
        super().__init__(game)
        self.timer = 0
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) 
                     for _ in range(50)]
        
    def update(self, dt: float, events: List):
        self.timer += 1
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.reset()
                    self.game.change_state(GameState.TITLE)
    
    def draw(self, screen: pygame.Surface):
        # Rainbow gradient background
        for y in range(SCREEN_HEIGHT):
            hue = (y / SCREEN_HEIGHT + self.timer * 0.002) % 1.0
            color = pygame.Color(0)
            color.hsva = (hue * 360, 70, 90, 100)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Animated stars
        for i, (x, y) in enumerate(self.stars):
            size = 2 + math.sin(self.timer * 0.1 + i) * 2
            pygame.draw.circle(screen, COLORS['star_yellow'], (x, int(y)), int(size))
        
        # Victory text
        text = self.font_large.render("VICTORY!", True, COLORS['gold'])
        rect = text.get_rect(center=(SCREEN_WIDTH//2, 150))
        # Glow effect
        for offset in range(3, 0, -1):
            glow = self.font_large.render("VICTORY!", True, COLORS['yellow'])
            glow.set_alpha(50)
            screen.blit(glow, (rect.x + offset, rect.y + offset))
        screen.blit(text, rect)
        
        # All bosses defeated
        subtitle = self.font_medium.render("All Bosses Defeated!", True, COLORS['white'])
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH//2, 220))
        screen.blit(subtitle, sub_rect)
        
        # Final score
        score_text = self.font_medium.render(f"Final Score: {self.game.player.score}", True, COLORS['white'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        screen.blit(score_text, score_rect)
        
        # Mario celebration
        mario = SpriteGenerator.create_mario_sprite(32, PowerUp.STAR, self.timer)
        mario_scaled = pygame.transform.scale(mario, (64, 128))
        screen.blit(mario_scaled, (SCREEN_WIDTH//2 - 32, 350))
        
        # Credits
        credits = [
            "ULTRA MARIO 2D BROS: BOSS FIGHT REDUX",
            "",
            "Created with Pygame",
            "By Team Flames / Samsoft",
            "",
            "Thanks for playing!"
        ]
        
        for i, line in enumerate(credits):
            credit_surf = self.font_medium.render(line, True, COLORS['white'])
            credit_rect = credit_surf.get_rect(center=(SCREEN_WIDTH//2, 480 + i * 25))
            screen.blit(credit_surf, credit_rect)
        
        # Prompt
        if (self.timer // 30) % 2 == 0:
            prompt = self.font_medium.render("Press ENTER to play again", True, COLORS['white'])
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40))
            screen.blit(prompt, prompt_rect)


# ============================================================================
# MAIN GAME CLASS
# ============================================================================
class Game:
    """Main game controller"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultra Mario 2D Bros: Boss Fight Redux")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize systems
        self.hud = GalaxyHUD(self.screen)
        self.player = Player(100, 300)
        
        # Game state
        self.state = GameState.TITLE
        self.current_boss_index = 0
        self.scene = TitleScene(self)
        self.paused = False
        
        # Pause menu
        self.pause_font = pygame.font.Font(None, 48)
        
    def reset(self):
        """Reset game to initial state"""
        self.player = Player(100, 300)
        self.current_boss_index = 0
        
    def change_state(self, new_state: GameState):
        """Change game state and create appropriate scene"""
        self.state = new_state
        
        if new_state == GameState.TITLE:
            self.scene = TitleScene(self)
        elif new_state == GameState.CORRIDOR:
            self.scene = CorridorScene(self, self.current_boss_index)
        elif new_state == GameState.BOSS_FIGHT:
            self.scene = BossArena(self, self.current_boss_index)
        elif new_state == GameState.GAME_OVER:
            self.scene = GameOverScene(self)
        elif new_state == GameState.VICTORY:
            self.scene = VictoryScene(self)
    
    def start_boss_fight(self, boss_index: int):
        """Start a boss fight"""
        self.current_boss_index = boss_index
        self.change_state(GameState.BOSS_FIGHT)
    
    def advance_to_next_boss(self):
        """Move to next boss or victory"""
        self.current_boss_index += 1
        if self.current_boss_index >= 5:
            self.change_state(GameState.VICTORY)
        else:
            self.change_state(GameState.CORRIDOR)
    
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused
            
            # Update
            if not self.paused:
                self.scene.update(dt, events)
            
            # Draw
            self.scene.draw(self.screen)
            
            # Pause overlay
            if self.paused:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                self.screen.blit(overlay, (0, 0))
                
                pause_text = self.pause_font.render("PAUSED", True, COLORS['white'])
                pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(pause_text, pause_rect)
                
                resume_text = pygame.font.Font(None, 32).render("Press P to resume", True, COLORS['white'])
                resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
                self.screen.blit(resume_text, resume_rect)
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


# ============================================================================
# ENTRY POINT
# ============================================================================
def main():
    """Main entry point"""
    print("=" * 60)
    print("ULTRA MARIO 2D BROS: BOSS FIGHT REDUX")
    print("=" * 60)
    print("\nControls:")
    print("  Arrow Keys / WASD - Move")
    print("  Space / Z / Up / W - Jump")
    print("  X - Attack (with Fire Flower)")
    print("  P - Pause")
    print("  ESC - Quit")
    print("\nBosses:")
    print("  1. Goomboss - Jump on his head!")
    print("  2. Yoob - Avoid the tongue attack!")
    print("  3. Petey Piranha - Attack when mouth is open!")
    print("  4. King Boo - Only vulnerable when visible!")
    print("  5. Kamek - Final battle against the Magikoopa!")
    print("\n" + "=" * 60)
    print("Starting game...")
    print("=" * 60 + "\n")
    
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
