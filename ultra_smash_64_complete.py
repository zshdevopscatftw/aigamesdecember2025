#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           U L T R A ! S M A S H   6 4                         ║
║                          [by catsan and co] [C] 1999-2025                     ║
║                                                                               ║
║                    Complete Super Smash Bros 64 Recreation                    ║
║                         All 12 Characters + 9 Stages                          ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import pygame
import math
import random
import sys
import json
from enum import Enum, auto

# =============================================================================
# INITIALIZATION
# =============================================================================
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ULTRA!SMASH 64 - [by catsan and co] [C] 1999-2025")
clock = pygame.time.Clock()

# =============================================================================
# N64 COLOR PALETTE
# =============================================================================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (150, 30, 30)
BLUE = (40, 80, 200)
DARK_BLUE = (20, 20, 80)
GREEN = (40, 180, 40)
DARK_GREEN = (20, 100, 20)
YELLOW = (255, 220, 0)
PURPLE = (140, 40, 180)
ORANGE = (255, 140, 0)
CYAN = (0, 200, 220)
PINK = (255, 100, 150)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
GOLD = (255, 200, 50)
BROWN = (139, 90, 43)
LIGHT_BLUE = (100, 150, 255)
SKY_BLUE = (135, 206, 235)
CREAM = (255, 253, 208)
NAVY = (0, 0, 80)

# =============================================================================
# SOUND SYSTEM
# =============================================================================
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_enabled = True
        self.sfx_enabled = True
        self._generate_sounds()
    
    def _create_sound(self, frequency, duration, volume=0.3, wave_type='square', decay=True):
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = []
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == 'square':
                val = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == 'sine':
                val = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'noise':
                val = random.uniform(-1, 1)
            elif wave_type == 'saw':
                val = 2 * (t * frequency - math.floor(t * frequency + 0.5))
            elif wave_type == 'triangle':
                val = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1
            else:
                val = math.sin(2 * math.pi * frequency * t)
            
            if decay:
                fade = 1 - (i / n_samples) ** 0.5
            else:
                fade = 1
            sample = int(val * volume * 32767 * fade)
            sample = max(-32767, min(32767, sample))
            buf.append(sample)
            buf.append(sample)
        
        return pygame.mixer.Sound(buffer=bytes([
            b for s in buf for b in [s & 0xFF, (s >> 8) & 0xFF]
        ]))
    
    def _generate_sounds(self):
        try:
            self.sounds['menu_move'] = self._create_sound(500, 0.05, 0.2, 'sine')
            self.sounds['menu_select'] = self._create_sound(600, 0.08, 0.25, 'square')
            self.sounds['menu_confirm'] = self._create_sound(800, 0.1, 0.3, 'square')
            self.sounds['menu_back'] = self._create_sound(300, 0.1, 0.2, 'square')
            
            self.sounds['jump'] = self._create_sound(400, 0.1, 0.2, 'sine')
            self.sounds['double_jump'] = self._create_sound(500, 0.12, 0.25, 'sine')
            self.sounds['land'] = self._create_sound(100, 0.05, 0.15, 'noise')
            
            self.sounds['jab'] = self._create_sound(300, 0.08, 0.25, 'noise')
            self.sounds['strong'] = self._create_sound(200, 0.12, 0.35, 'noise')
            self.sounds['smash'] = self._create_sound(150, 0.2, 0.45, 'noise')
            self.sounds['aerial'] = self._create_sound(350, 0.1, 0.3, 'noise')
            
            self.sounds['hit_weak'] = self._create_sound(400, 0.1, 0.3, 'noise')
            self.sounds['hit_medium'] = self._create_sound(300, 0.15, 0.4, 'noise')
            self.sounds['hit_strong'] = self._create_sound(200, 0.2, 0.5, 'noise')
            self.sounds['hit_smash'] = self._create_sound(100, 0.3, 0.6, 'noise')
            
            self.sounds['shield'] = self._create_sound(250, 0.1, 0.2, 'sine')
            self.sounds['shield_break'] = self._create_sound(80, 0.5, 0.5, 'noise')
            self.sounds['parry'] = self._create_sound(600, 0.1, 0.3, 'square')
            
            self.sounds['ko_blast'] = self._create_sound(60, 0.4, 0.5, 'square')
            self.sounds['star_ko'] = self._create_sound(800, 0.8, 0.3, 'sine')
            self.sounds['respawn'] = self._create_sound(440, 0.3, 0.25, 'sine')
            
            self.sounds['fireball'] = self._create_sound(350, 0.15, 0.3, 'saw')
            self.sounds['thunder'] = self._create_sound(100, 0.4, 0.5, 'noise')
            self.sounds['pk_fire'] = self._create_sound(450, 0.2, 0.35, 'square')
            self.sounds['charge_shot'] = self._create_sound(200, 0.3, 0.4, 'saw')
            self.sounds['falcon_punch'] = self._create_sound(80, 0.5, 0.6, 'square')
            self.sounds['blaster'] = self._create_sound(600, 0.08, 0.25, 'square')
            self.sounds['spin_attack'] = self._create_sound(300, 0.3, 0.35, 'triangle')
            self.sounds['inhale'] = self._create_sound(150, 0.4, 0.3, 'noise')
            
            self.sounds['crowd_cheer'] = self._create_sound(200, 0.5, 0.2, 'noise')
            self.sounds['game_set'] = self._create_sound(440, 0.5, 0.4, 'sine')
            self.sounds['announcer'] = self._create_sound(300, 0.3, 0.35, 'square')
            
            self.sounds['item_appear'] = self._create_sound(700, 0.15, 0.3, 'sine')
            self.sounds['item_pickup'] = self._create_sound(550, 0.1, 0.25, 'square')
            self.sounds['bat_swing'] = self._create_sound(250, 0.15, 0.35, 'noise')
            self.sounds['beam_sword'] = self._create_sound(400, 0.2, 0.3, 'saw')
            
        except Exception as e:
            print(f"Sound generation error: {e}")
    
    def play(self, sound_name):
        if self.sfx_enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass

sound_manager = SoundManager()

# =============================================================================
# FONTS
# =============================================================================
def get_font(size):
    try:
        return pygame.font.Font(None, size)
    except:
        return pygame.font.SysFont('arial', size)

FONT_TITLE = get_font(80)
FONT_HUGE = get_font(64)
FONT_LARGE = get_font(48)
FONT_MEDIUM = get_font(32)
FONT_SMALL = get_font(24)
FONT_TINY = get_font(18)
FONT_MICRO = get_font(14)

# =============================================================================
# GAME ENUMS
# =============================================================================
class GameState(Enum):
    INTRO = auto()
    TITLE = auto()
    MAIN_MENU = auto()
    MODE_SELECT = auto()
    CHAR_SELECT = auto()
    STAGE_SELECT = auto()
    VS_OPTIONS = auto()
    BATTLE = auto()
    PAUSE = auto()
    RESULTS = auto()
    CONTINUE = auto()
    GAME_OVER = auto()
    CREDITS = auto()
    OPTIONS = auto()
    DATA = auto()
    HOW_TO_PLAY = auto()
    TRAINING_OPTIONS = auto()
    BONUS_SELECT = auto()
    BREAK_TARGETS = auto()
    BOARD_PLATFORMS = auto()

class AttackType(Enum):
    NONE = auto()
    JAB1 = auto()
    JAB2 = auto()
    JAB3 = auto()
    RAPID_JAB = auto()
    DASH_ATTACK = auto()
    FTILT = auto()
    UTILT = auto()
    DTILT = auto()
    FSMASH = auto()
    USMASH = auto()
    DSMASH = auto()
    NAIR = auto()
    FAIR = auto()
    BAIR = auto()
    UAIR = auto()
    DAIR = auto()
    NEUTRAL_B = auto()
    SIDE_B = auto()
    UP_B = auto()
    DOWN_B = auto()
    GRAB = auto()
    PUMMEL = auto()
    FTHROW = auto()
    BTHROW = auto()
    UTHROW = auto()
    DTHROW = auto()
    GETUP_ATTACK = auto()
    LEDGE_ATTACK = auto()

class FighterState(Enum):
    IDLE = auto()
    WALK = auto()
    RUN = auto()
    DASH = auto()
    JUMPSQUAT = auto()
    AIRBORNE = auto()
    LANDING = auto()
    ATTACK = auto()
    HITSTUN = auto()
    TUMBLE = auto()
    SHIELD = auto()
    SHIELD_STUN = auto()
    GRAB = auto()
    GRABBED = auto()
    THROW = auto()
    LEDGE_HANG = auto()
    LEDGE_CLIMB = auto()
    CROUCH = auto()
    PRONE = auto()
    TECH = auto()
    DEAD = auto()
    RESPAWN = auto()
    SPECIAL = auto()

# =============================================================================
# ALL 12 ORIGINAL CHARACTERS
# =============================================================================
CHARACTERS = {
    'MARIO': {
        'name': 'Mario',
        'series': 'Super Mario',
        'color': RED,
        'color2': BLUE,
        'color3': BROWN,
        'weight': 100,
        'walk_speed': 3.5,
        'run_speed': 5.5,
        'air_speed': 3.8,
        'fall_speed': 5.2,
        'fast_fall': 8.5,
        'jump_power': 14,
        'double_jump': 13,
        'air_jumps': 1,
        'special_neutral': 'Fireball',
        'special_side': 'Cape',
        'special_up': 'Super Jump Punch',
        'special_down': 'Mario Tornado',
        'tier': 'A',
        'unlock': False
    },
    'DONKEY KONG': {
        'name': 'Donkey Kong',
        'series': 'Donkey Kong',
        'color': BROWN,
        'color2': (220, 180, 120),
        'color3': RED,
        'weight': 140,
        'walk_speed': 3.0,
        'run_speed': 5.0,
        'air_speed': 3.5,
        'fall_speed': 6.5,
        'fast_fall': 10.0,
        'jump_power': 13,
        'double_jump': 12,
        'air_jumps': 1,
        'special_neutral': 'Giant Punch',
        'special_side': 'Headbutt',
        'special_up': 'Spinning Kong',
        'special_down': 'Hand Slap',
        'tier': 'B',
        'unlock': False
    },
    'LINK': {
        'name': 'Link',
        'series': 'Legend of Zelda',
        'color': GREEN,
        'color2': BROWN,
        'color3': (220, 200, 150),
        'weight': 104,
        'walk_speed': 3.2,
        'run_speed': 5.2,
        'air_speed': 3.5,
        'fall_speed': 6.0,
        'fast_fall': 9.5,
        'jump_power': 12,
        'double_jump': 11,
        'air_jumps': 1,
        'special_neutral': 'Boomerang',
        'special_side': 'Boomerang',
        'special_up': 'Spin Attack',
        'special_down': 'Bomb',
        'tier': 'B',
        'unlock': False
    },
    'SAMUS': {
        'name': 'Samus',
        'series': 'Metroid',
        'color': ORANGE,
        'color2': (200, 100, 0),
        'color3': GREEN,
        'weight': 110,
        'walk_speed': 3.0,
        'run_speed': 5.0,
        'air_speed': 3.8,
        'fall_speed': 5.5,
        'fast_fall': 9.0,
        'jump_power': 13,
        'double_jump': 12,
        'air_jumps': 1,
        'special_neutral': 'Charge Shot',
        'special_side': 'Missile',
        'special_up': 'Screw Attack',
        'special_down': 'Bomb',
        'tier': 'B',
        'unlock': False
    },
    'YOSHI': {
        'name': 'Yoshi',
        'series': 'Super Mario',
        'color': GREEN,
        'color2': WHITE,
        'color3': ORANGE,
        'weight': 108,
        'walk_speed': 3.5,
        'run_speed': 5.8,
        'air_speed': 4.0,
        'fall_speed': 5.0,
        'fast_fall': 8.0,
        'jump_power': 12,
        'double_jump': 18,
        'air_jumps': 1,
        'special_neutral': 'Egg Lay',
        'special_side': 'Egg Roll',
        'special_up': 'Egg Throw',
        'special_down': 'Yoshi Bomb',
        'tier': 'B',
        'unlock': False
    },
    'KIRBY': {
        'name': 'Kirby',
        'series': 'Kirby',
        'color': PINK,
        'color2': (255, 150, 180),
        'color3': RED,
        'weight': 70,
        'walk_speed': 3.0,
        'run_speed': 5.0,
        'air_speed': 3.5,
        'fall_speed': 4.0,
        'fast_fall': 7.0,
        'jump_power': 11,
        'double_jump': 10,
        'air_jumps': 5,
        'special_neutral': 'Inhale',
        'special_side': 'Hammer',
        'special_up': 'Final Cutter',
        'special_down': 'Stone',
        'tier': 'A',
        'unlock': False
    },
    'FOX': {
        'name': 'Fox',
        'series': 'Star Fox',
        'color': (200, 150, 100),
        'color2': WHITE,
        'color3': (100, 80, 60),
        'weight': 75,
        'walk_speed': 4.0,
        'run_speed': 7.0,
        'air_speed': 4.5,
        'fall_speed': 6.8,
        'fast_fall': 11.0,
        'jump_power': 14,
        'double_jump': 13,
        'air_jumps': 1,
        'special_neutral': 'Blaster',
        'special_side': 'Fox Illusion',
        'special_up': 'Fire Fox',
        'special_down': 'Reflector',
        'tier': 'S',
        'unlock': False
    },
    'PIKACHU': {
        'name': 'Pikachu',
        'series': 'Pokemon',
        'color': YELLOW,
        'color2': (255, 200, 0),
        'color3': RED,
        'weight': 80,
        'walk_speed': 3.8,
        'run_speed': 6.2,
        'air_speed': 4.2,
        'fall_speed': 5.5,
        'fast_fall': 9.0,
        'jump_power': 14,
        'double_jump': 13,
        'air_jumps': 1,
        'special_neutral': 'Thunder Jolt',
        'special_side': 'Skull Bash',
        'special_up': 'Quick Attack',
        'special_down': 'Thunder',
        'tier': 'S',
        'unlock': False
    },
    'LUIGI': {
        'name': 'Luigi',
        'series': 'Super Mario',
        'color': GREEN,
        'color2': BLUE,
        'color3': BROWN,
        'weight': 98,
        'walk_speed': 3.2,
        'run_speed': 5.0,
        'air_speed': 3.2,
        'fall_speed': 4.5,
        'fast_fall': 7.5,
        'jump_power': 15,
        'double_jump': 14,
        'air_jumps': 1,
        'special_neutral': 'Fireball',
        'special_side': 'Green Missile',
        'special_up': 'Super Jump Punch',
        'special_down': 'Luigi Cyclone',
        'tier': 'B',
        'unlock': True
    },
    'CAPTAIN FALCON': {
        'name': 'Captain Falcon',
        'series': 'F-Zero',
        'color': (0, 0, 150),
        'color2': GOLD,
        'color3': RED,
        'weight': 104,
        'walk_speed': 3.5,
        'run_speed': 7.5,
        'air_speed': 4.8,
        'fall_speed': 6.8,
        'fast_fall': 11.0,
        'jump_power': 14,
        'double_jump': 13,
        'air_jumps': 1,
        'special_neutral': 'Falcon Punch',
        'special_side': 'Raptor Boost',
        'special_up': 'Falcon Dive',
        'special_down': 'Falcon Kick',
        'tier': 'A',
        'unlock': True
    },
    'NESS': {
        'name': 'Ness',
        'series': 'EarthBound',
        'color': (100, 50, 150),
        'color2': YELLOW,
        'color3': BLUE,
        'weight': 94,
        'walk_speed': 3.2,
        'run_speed': 5.2,
        'air_speed': 3.8,
        'fall_speed': 5.0,
        'fast_fall': 8.5,
        'jump_power': 13,
        'double_jump': 15,
        'air_jumps': 1,
        'special_neutral': 'PK Flash',
        'special_side': 'PK Fire',
        'special_up': 'PK Thunder',
        'special_down': 'PSI Magnet',
        'tier': 'B',
        'unlock': True
    },
    'JIGGLYPUFF': {
        'name': 'Jigglypuff',
        'series': 'Pokemon',
        'color': (255, 180, 200),
        'color2': CYAN,
        'color3': GREEN,
        'weight': 60,
        'walk_speed': 3.0,
        'run_speed': 4.5,
        'air_speed': 5.5,
        'fall_speed': 3.5,
        'fast_fall': 6.0,
        'jump_power': 10,
        'double_jump': 9,
        'air_jumps': 5,
        'special_neutral': 'Rollout',
        'special_side': 'Pound',
        'special_up': 'Sing',
        'special_down': 'Rest',
        'tier': 'A',
        'unlock': True
    }
}

# =============================================================================
# ALL 9 ORIGINAL STAGES
# =============================================================================
STAGES = {
    'PEACH\'S CASTLE': {
        'name': "Peach's Castle",
        'series': 'Super Mario',
        'bg_color': SKY_BLUE,
        'ground_color': (150, 100, 80),
        'platform_color': (200, 150, 100),
        'main_platform': (150, 420, 500, 30),
        'platforms': [
            (100, 300, 150, 15),
            (350, 250, 100, 15),
            (550, 300, 150, 15)
        ],
        'hazards': True,
        'moving': True,
        'blast_zones': (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 100)
    },
    'CONGO JUNGLE': {
        'name': 'Congo Jungle',
        'series': 'Donkey Kong',
        'bg_color': (40, 80, 40),
        'ground_color': (100, 70, 40),
        'platform_color': (80, 60, 30),
        'main_platform': (180, 420, 440, 25),
        'platforms': [
            (80, 300, 140, 15),
            (330, 260, 140, 15),
            (580, 300, 140, 15)
        ],
        'hazards': False,
        'moving': True,
        'blast_zones': (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 150)
    },
    'HYRULE CASTLE': {
        'name': 'Hyrule Castle',
        'series': 'Legend of Zelda',
        'bg_color': (100, 120, 80),
        'ground_color': (120, 100, 70),
        'platform_color': (100, 80, 50),
        'main_platform': (100, 430, 600, 30),
        'platforms': [
            (50, 320, 120, 15),
            (300, 250, 200, 15),
            (630, 320, 120, 15)
        ],
        'hazards': True,
        'moving': False,
        'blast_zones': (-200, SCREEN_WIDTH + 200, -250, SCREEN_HEIGHT + 100)
    },
    'PLANET ZEBES': {
        'name': 'Planet Zebes',
        'series': 'Metroid',
        'bg_color': (60, 20, 40),
        'ground_color': (80, 40, 60),
        'platform_color': (100, 60, 80),
        'main_platform': (200, 400, 400, 25),
        'platforms': [
            (120, 280, 130, 15),
            (350, 220, 100, 15),
            (550, 280, 130, 15)
        ],
        'hazards': True,
        'moving': False,
        'blast_zones': (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 100)
    },
    'YOSHI\'S ISLAND': {
        'name': "Yoshi's Island",
        'series': 'Super Mario',
        'bg_color': (150, 200, 255),
        'ground_color': (100, 180, 100),
        'platform_color': (80, 150, 80),
        'main_platform': (150, 420, 500, 25),
        'platforms': [
            (250, 320, 100, 15),
            (450, 320, 100, 15)
        ],
        'hazards': False,
        'moving': False,
        'blast_zones': (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 100)
    },
    'DREAM LAND': {
        'name': 'Dream Land',
        'series': 'Kirby',
        'bg_color': LIGHT_BLUE,
        'ground_color': (255, 200, 150),
        'platform_color': (255, 220, 180),
        'main_platform': (200, 400, 400, 20),
        'platforms': [
            (100, 280, 150, 15),
            (350, 200, 100, 15),
            (550, 280, 150, 15)
        ],
        'hazards': False,
        'moving': False,
        'blast_zones': (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 100)
    },
    'SECTOR Z': {
        'name': 'Sector Z',
        'series': 'Star Fox',
        'bg_color': (10, 10, 30),
        'ground_color': (60, 60, 80),
        'platform_color': (80, 80, 100),
        'main_platform': (50, 450, 700, 35),
        'platforms': [
            (200, 350, 200, 15),
            (450, 300, 150, 15)
        ],
        'hazards': True,
        'moving': False,
        'blast_zones': (-200, SCREEN_WIDTH + 200, -250, SCREEN_HEIGHT + 150)
    },
    'SAFFRON CITY': {
        'name': 'Saffron City',
        'series': 'Pokemon',
        'bg_color': (200, 180, 160),
        'ground_color': (150, 130, 110),
        'platform_color': (180, 160, 140),
        'main_platform': (200, 430, 400, 30),
        'platforms': [
            (50, 350, 120, 20),
            (300, 300, 200, 15),
            (630, 350, 120, 20)
        ],
        'hazards': True,
        'moving': False,
        'blast_zones': (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 100)
    },
    'MUSHROOM KINGDOM': {
        'name': 'Mushroom Kingdom',
        'series': 'Super Mario',
        'bg_color': (100, 150, 255),
        'ground_color': (200, 100, 50),
        'platform_color': (150, 80, 40),
        'main_platform': (100, 450, 600, 30),
        'platforms': [
            (150, 350, 100, 15),
            (350, 280, 100, 15),
            (550, 350, 100, 15)
        ],
        'hazards': True,
        'moving': True,
        'blast_zones': (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 100)
    }
}

# =============================================================================
# ITEMS
# =============================================================================
ITEMS = {
    'BEAM_SWORD': {'damage': 12, 'knockback': 8, 'duration': 600},
    'HOME_RUN_BAT': {'damage': 30, 'knockback': 25, 'duration': 600},
    'FAN': {'damage': 2, 'knockback': 1, 'duration': 600},
    'STAR_ROD': {'damage': 14, 'knockback': 9, 'duration': 600},
    'RAY_GUN': {'damage': 8, 'knockback': 5, 'ammo': 16},
    'FIRE_FLOWER': {'damage': 3, 'knockback': 1, 'ammo': 80},
    'HAMMER': {'damage': 22, 'knockback': 15, 'duration': 300},
    'MOTION_SENSOR_BOMB': {'damage': 25, 'knockback': 18},
    'BOB_OMB': {'damage': 28, 'knockback': 20},
    'BUMPER': {'knockback': 12},
    'GREEN_SHELL': {'damage': 10, 'knockback': 8},
    'RED_SHELL': {'damage': 10, 'knockback': 8},
    'POKEBALL': {},
    'MAXIM_TOMATO': {'heal': 50},
    'HEART_CONTAINER': {'heal': 100},
    'STAR': {'duration': 480, 'invincible': True}
}

# =============================================================================
# PROJECTILE CLASS
# =============================================================================
class Projectile:
    def __init__(self, x, y, vx, vy, proj_type, owner, damage, knockback, lifetime=120):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.proj_type = proj_type
        self.owner = owner
        self.damage = damage
        self.knockback = knockback
        self.lifetime = lifetime
        self.active = True
        self.width = 15
        self.height = 15
        
        if proj_type == 'fireball':
            self.color = ORANGE
            self.width = 12
            self.height = 12
        elif proj_type == 'thunder_jolt':
            self.color = YELLOW
            self.width = 10
            self.height = 10
        elif proj_type == 'boomerang':
            self.color = BROWN
            self.width = 20
            self.height = 8
            self.return_timer = 30
        elif proj_type == 'charge_shot':
            self.color = CYAN
            self.width = 25
            self.height = 25
        elif proj_type == 'pk_fire':
            self.color = (255, 100, 50)
            self.width = 15
            self.height = 10
        elif proj_type == 'blaster':
            self.color = (255, 50, 50)
            self.width = 8
            self.height = 4
        elif proj_type == 'missile':
            self.color = GREEN
            self.width = 18
            self.height = 8
        else:
            self.color = WHITE
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        if self.proj_type == 'fireball':
            self.vy += 0.3
        elif self.proj_type == 'thunder_jolt':
            pass
        elif self.proj_type == 'boomerang':
            self.return_timer -= 1
            if self.return_timer <= 0:
                self.vx *= -0.98
        
        if self.lifetime <= 0:
            self.active = False
        if self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.active = False
        if self.y < -100 or self.y > SCREEN_HEIGHT + 50:
            self.active = False
    
    def draw(self, surface):
        if self.proj_type == 'fireball':
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.width // 2)
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.width // 4)
        elif self.proj_type == 'charge_shot':
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.width // 2)
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.width // 4)
        else:
            pygame.draw.ellipse(surface, self.color, 
                              (self.x - self.width//2, self.y - self.height//2, 
                               self.width, self.height))
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)

# =============================================================================
# PARTICLE SYSTEM
# =============================================================================
class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=4, particle_type='normal'):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.particle_type = particle_type

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def spawn(self, x, y, color, count=10, speed=5, particle_type='normal'):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(speed * 0.5, speed * 1.5)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * spd,
                math.sin(angle) * spd,
                color,
                random.randint(15, 35),
                random.randint(2, 5),
                particle_type
            ))
    
    def spawn_hit(self, x, y, damage):
        if damage < 5:
            self.spawn(x, y, YELLOW, 5, 3)
        elif damage < 12:
            self.spawn(x, y, ORANGE, 10, 5)
        elif damage < 20:
            self.spawn(x, y, RED, 15, 7)
        else:
            self.spawn(x, y, WHITE, 20, 10)
            self.spawn(x, y, YELLOW, 10, 8)
    
    def spawn_ko(self, x, y, color):
        self.spawn(x, y, color, 30, 12)
        self.spawn(x, y, WHITE, 20, 10)
    
    def update(self):
        for p in self.particles[:]:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.15
            p.vx *= 0.98
            p.life -= 1
            if p.life <= 0:
                self.particles.remove(p)
    
    def draw(self, surface):
        for p in self.particles:
            alpha = p.life / p.max_life
            size = int(p.size * alpha) + 1
            pygame.draw.circle(surface, p.color, (int(p.x), int(p.y)), size)

particles = ParticleSystem()

# =============================================================================
# FIGHTER CLASS
# =============================================================================
class Fighter:
    def __init__(self, x, y, char_name, player_num, controls, is_cpu=False):
        self.x = x
        self.y = y
        self.char_name = char_name
        self.char_data = CHARACTERS[char_name]
        self.player_num = player_num
        self.controls = controls
        self.is_cpu = is_cpu
        
        self.vx = 0
        self.vy = 0
        self.width = 40
        self.height = 50
        
        self.state = FighterState.IDLE
        self.facing = 1 if player_num % 2 == 1 else -1
        self.on_ground = False
        self.jumps_left = self.char_data['air_jumps'] + 1
        
        self.damage = 0
        self.stocks = 4
        self.kos = 0
        self.falls = 0
        
        self.shield_health = 100
        self.shielding = False
        self.shield_stun = 0
        
        self.hitstun = 0
        self.hitlag = 0
        self.invincible = 0
        self.intangible = 0
        
        self.attack_type = AttackType.NONE
        self.attack_frame = 0
        self.attack_duration = 0
        self.can_cancel = False
        
        self.grab_target = None
        self.grabbed_by = None
        self.grab_timer = 0
        
        self.special_charge = 0
        self.special_active = False
        
        self.aerial_used = False
        self.fastfalling = False
        self.short_hop = False
        
        self.ledge_timer = 0
        self.ledge_invincible = 0
        
        self.combo_count = 0
        self.last_hit_by = None
        
        self.animation_frame = 0
        self.animation_timer = 0
        
        self.cpu_action_timer = 0
        self.cpu_target = None
        self.cpu_difficulty = 5
    
    def reset_position(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.state = FighterState.RESPAWN
        self.damage = 0
        self.jumps_left = self.char_data['air_jumps'] + 1
        self.shield_health = 100
        self.invincible = 120
        self.hitstun = 0
        self.attack_type = AttackType.NONE
        self.attack_frame = 0
        self.fastfalling = False
        self.aerial_used = False
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def handle_input(self, keys, events):
        if self.is_cpu:
            return
        
        if self.state in [FighterState.HITSTUN, FighterState.TUMBLE, 
                          FighterState.GRABBED, FighterState.DEAD]:
            return
        
        if self.hitlag > 0:
            return
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == self.controls.get('jump'):
                    self.do_jump()
                elif event.key == self.controls.get('attack'):
                    self.do_attack(keys)
                elif event.key == self.controls.get('special'):
                    self.do_special(keys)
                elif event.key == self.controls.get('grab'):
                    self.do_grab()
        
        if keys[self.controls.get('shield', pygame.K_UNKNOWN)]:
            if self.on_ground and self.state not in [FighterState.ATTACK, FighterState.SPECIAL]:
                self.shielding = True
                self.state = FighterState.SHIELD
        else:
            self.shielding = False
            if self.state == FighterState.SHIELD:
                self.state = FighterState.IDLE
        
        if self.state not in [FighterState.ATTACK, FighterState.SPECIAL, 
                              FighterState.SHIELD, FighterState.HITSTUN]:
            left = keys[self.controls.get('left', pygame.K_UNKNOWN)]
            right = keys[self.controls.get('right', pygame.K_UNKNOWN)]
            down = keys[self.controls.get('down', pygame.K_UNKNOWN)]
            
            if left:
                self.facing = -1
                if self.on_ground:
                    self.vx = -self.char_data['run_speed']
                    self.state = FighterState.RUN
                else:
                    self.vx = max(self.vx - 0.5, -self.char_data['air_speed'])
            elif right:
                self.facing = 1
                if self.on_ground:
                    self.vx = self.char_data['run_speed']
                    self.state = FighterState.RUN
                else:
                    self.vx = min(self.vx + 0.5, self.char_data['air_speed'])
            else:
                if self.on_ground:
                    self.vx *= 0.8
                    if abs(self.vx) < 0.5:
                        self.vx = 0
                        if self.state == FighterState.RUN:
                            self.state = FighterState.IDLE
            
            if down and not self.on_ground and not self.fastfalling:
                if self.vy > 0:
                    self.vy = self.char_data['fast_fall']
                    self.fastfalling = True
            
            if down and self.on_ground:
                self.state = FighterState.CROUCH
    
    def do_jump(self):
        if self.shielding:
            return
        
        if self.jumps_left > 0:
            if self.on_ground:
                self.vy = -self.char_data['jump_power']
                sound_manager.play('jump')
            else:
                self.vy = -self.char_data['double_jump']
                sound_manager.play('double_jump')
            
            self.jumps_left -= 1
            self.on_ground = False
            self.state = FighterState.AIRBORNE
            self.fastfalling = False
    
    def do_attack(self, keys):
        if self.attack_frame > 0:
            return
        
        up = keys[self.controls.get('up', pygame.K_UNKNOWN)]
        down = keys[self.controls.get('down', pygame.K_UNKNOWN)]
        left = keys[self.controls.get('left', pygame.K_UNKNOWN)]
        right = keys[self.controls.get('right', pygame.K_UNKNOWN)]
        
        if self.on_ground:
            if up:
                self.attack_type = AttackType.USMASH
                self.attack_duration = 35
                sound_manager.play('smash')
            elif down:
                self.attack_type = AttackType.DSMASH
                self.attack_duration = 30
                sound_manager.play('smash')
            elif left or right:
                self.attack_type = AttackType.FSMASH
                self.attack_duration = 40
                self.facing = 1 if right else -1
                sound_manager.play('smash')
            else:
                self.attack_type = AttackType.JAB1
                self.attack_duration = 15
                sound_manager.play('jab')
        else:
            if up:
                self.attack_type = AttackType.UAIR
                self.attack_duration = 20
            elif down:
                self.attack_type = AttackType.DAIR
                self.attack_duration = 25
            elif (left and self.facing == -1) or (right and self.facing == 1):
                self.attack_type = AttackType.FAIR
                self.attack_duration = 22
            elif (left and self.facing == 1) or (right and self.facing == -1):
                self.attack_type = AttackType.BAIR
                self.attack_duration = 22
            else:
                self.attack_type = AttackType.NAIR
                self.attack_duration = 18
            sound_manager.play('aerial')
        
        self.attack_frame = self.attack_duration
        self.state = FighterState.ATTACK
    
    def do_special(self, keys):
        if self.attack_frame > 0:
            return
        
        up = keys[self.controls.get('up', pygame.K_UNKNOWN)]
        down = keys[self.controls.get('down', pygame.K_UNKNOWN)]
        left = keys[self.controls.get('left', pygame.K_UNKNOWN)]
        right = keys[self.controls.get('right', pygame.K_UNKNOWN)]
        
        if up:
            self.attack_type = AttackType.UP_B
            self.attack_duration = 40
        elif down:
            self.attack_type = AttackType.DOWN_B
            self.attack_duration = 35
        elif left or right:
            self.attack_type = AttackType.SIDE_B
            self.attack_duration = 30
            self.facing = 1 if right else -1
        else:
            self.attack_type = AttackType.NEUTRAL_B
            self.attack_duration = 25
        
        self.attack_frame = self.attack_duration
        self.state = FighterState.SPECIAL
        self.special_active = True
    
    def do_grab(self):
        if self.attack_frame > 0 or not self.on_ground:
            return
        
        self.attack_type = AttackType.GRAB
        self.attack_duration = 25
        self.attack_frame = self.attack_duration
        self.state = FighterState.GRAB
    
    def get_hitbox(self):
        if self.attack_frame <= 0:
            return None
        
        startup_ratio = self.attack_frame / self.attack_duration
        
        if self.attack_type == AttackType.JAB1:
            if startup_ratio < 0.7:
                hx = self.x + (self.width if self.facing > 0 else -25)
                return {'rect': (hx, self.y + 15, 25, 18), 
                       'damage': 3, 'knockback': 2, 'angle': 45}
        
        elif self.attack_type == AttackType.FSMASH:
            if 0.3 < startup_ratio < 0.6:
                hx = self.x + (self.width if self.facing > 0 else -50)
                return {'rect': (hx, self.y + 5, 50, 35),
                       'damage': 18, 'knockback': 14, 'angle': 40}
        
        elif self.attack_type == AttackType.USMASH:
            if 0.3 < startup_ratio < 0.7:
                return {'rect': (self.x - 10, self.y - 40, self.width + 20, 45),
                       'damage': 16, 'knockback': 13, 'angle': 85}
        
        elif self.attack_type == AttackType.DSMASH:
            if 0.3 < startup_ratio < 0.6:
                return {'rect': (self.x - 30, self.y + self.height - 20, self.width + 60, 20),
                       'damage': 14, 'knockback': 10, 'angle': 30}
        
        elif self.attack_type == AttackType.NAIR:
            if 0.2 < startup_ratio < 0.8:
                return {'rect': (self.x - 15, self.y - 10, self.width + 30, self.height + 20),
                       'damage': 10, 'knockback': 6, 'angle': 50}
        
        elif self.attack_type == AttackType.FAIR:
            if 0.3 < startup_ratio < 0.6:
                hx = self.x + (self.width if self.facing > 0 else -35)
                return {'rect': (hx, self.y + 10, 35, 30),
                       'damage': 12, 'knockback': 8, 'angle': 45}
        
        elif self.attack_type == AttackType.BAIR:
            if 0.3 < startup_ratio < 0.6:
                hx = self.x + (-35 if self.facing > 0 else self.width)
                return {'rect': (hx, self.y + 10, 35, 30),
                       'damage': 14, 'knockback': 10, 'angle': 135}
        
        elif self.attack_type == AttackType.UAIR:
            if 0.2 < startup_ratio < 0.7:
                return {'rect': (self.x - 5, self.y - 35, self.width + 10, 40),
                       'damage': 11, 'knockback': 7, 'angle': 80}
        
        elif self.attack_type == AttackType.DAIR:
            if 0.3 < startup_ratio < 0.6:
                return {'rect': (self.x - 5, self.y + self.height, self.width + 10, 30),
                       'damage': 13, 'knockback': 9, 'angle': 270}
        
        elif self.attack_type == AttackType.NEUTRAL_B:
            if 0.4 < startup_ratio < 0.6:
                return {'rect': (self.x - 10, self.y - 10, self.width + 20, self.height + 20),
                       'damage': 8, 'knockback': 5, 'angle': 60}
        
        elif self.attack_type == AttackType.SIDE_B:
            if 0.3 < startup_ratio < 0.7:
                hx = self.x + (self.width if self.facing > 0 else -40)
                return {'rect': (hx, self.y + 10, 40, 30),
                       'damage': 10, 'knockback': 7, 'angle': 45}
        
        elif self.attack_type == AttackType.UP_B:
            if 0.2 < startup_ratio < 0.8:
                return {'rect': (self.x - 15, self.y - 30, self.width + 30, self.height + 40),
                       'damage': 12, 'knockback': 8, 'angle': 75}
        
        elif self.attack_type == AttackType.DOWN_B:
            if 0.3 < startup_ratio < 0.6:
                return {'rect': (self.x - 20, self.y, self.width + 40, self.height + 10),
                       'damage': 10, 'knockback': 6, 'angle': 60}
        
        return None
    
    def create_projectile(self, projectiles):
        if self.attack_type == AttackType.NEUTRAL_B:
            if self.char_name in ['MARIO', 'LUIGI']:
                proj = Projectile(
                    self.x + self.width//2 + self.facing * 20,
                    self.y + 25,
                    self.facing * 8, 2,
                    'fireball', self, 6, 3, 90
                )
                projectiles.append(proj)
                sound_manager.play('fireball')
            
            elif self.char_name == 'PIKACHU':
                proj = Projectile(
                    self.x + self.width//2 + self.facing * 20,
                    self.y + 25,
                    self.facing * 6, 0,
                    'thunder_jolt', self, 8, 4, 120
                )
                projectiles.append(proj)
                sound_manager.play('thunder')
            
            elif self.char_name == 'FOX':
                proj = Projectile(
                    self.x + self.width//2 + self.facing * 25,
                    self.y + 20,
                    self.facing * 15, 0,
                    'blaster', self, 3, 0, 60
                )
                projectiles.append(proj)
                sound_manager.play('blaster')
            
            elif self.char_name == 'SAMUS':
                power = min(self.special_charge / 100, 1.0)
                proj = Projectile(
                    self.x + self.width//2 + self.facing * 25,
                    self.y + 20,
                    self.facing * (8 + power * 7), 0,
                    'charge_shot', self, int(5 + power * 20), int(5 + power * 15), 120
                )
                proj.width = int(15 + power * 15)
                proj.height = int(15 + power * 15)
                projectiles.append(proj)
                sound_manager.play('charge_shot')
                self.special_charge = 0
            
            elif self.char_name == 'LINK':
                proj = Projectile(
                    self.x + self.width//2 + self.facing * 20,
                    self.y + 20,
                    self.facing * 10, 0,
                    'boomerang', self, 8, 4, 150
                )
                projectiles.append(proj)
            
            elif self.char_name == 'NESS':
                proj = Projectile(
                    self.x + self.width//2 + self.facing * 15,
                    self.y + 20,
                    self.facing * 7, -1,
                    'pk_fire', self, 6, 3, 90
                )
                projectiles.append(proj)
                sound_manager.play('pk_fire')
    
    def take_hit(self, damage, knockback, angle, attacker):
        if self.invincible > 0 or self.intangible > 0:
            return False
        
        if self.shielding and self.shield_health > 0:
            self.shield_health -= damage * 1.5
            self.shield_stun = int(damage * 0.5)
            if self.shield_health <= 0:
                self.shield_health = 0
                self.shielding = False
                self.hitstun = 120
                self.state = FighterState.HITSTUN
                sound_manager.play('shield_break')
            else:
                sound_manager.play('shield')
            return False
        
        self.damage += damage
        
        kb_multiplier = (self.damage / 100) * 0.7 + 0.8
        kb_multiplier *= (200 / (self.char_data['weight'] + 100))
        actual_kb = knockback * kb_multiplier
        
        angle_rad = math.radians(angle)
        self.vx = math.cos(angle_rad) * actual_kb * (attacker.facing if angle < 90 or angle > 270 else -attacker.facing)
        self.vy = -abs(math.sin(angle_rad) * actual_kb)
        
        self.hitstun = int(actual_kb * 2.5)
        self.hitlag = int(damage * 0.4) + 3
        attacker.hitlag = int(damage * 0.4) + 3
        
        self.state = FighterState.HITSTUN
        self.shielding = False
        self.attack_frame = 0
        self.attack_type = AttackType.NONE
        
        if actual_kb > 15:
            self.state = FighterState.TUMBLE
        
        self.last_hit_by = attacker
        self.combo_count = 0
        attacker.combo_count += 1
        
        if damage < 5:
            sound_manager.play('hit_weak')
        elif damage < 12:
            sound_manager.play('hit_medium')
        elif damage < 20:
            sound_manager.play('hit_strong')
        else:
            sound_manager.play('hit_smash')
        
        return True
    
    def check_death(self, blast_zones):
        left, right, top, bottom = blast_zones
        
        if self.x < left or self.x > right or self.y < top or self.y > bottom:
            return True
        return False
    
    def die(self):
        self.stocks -= 1
        self.falls += 1
        if self.last_hit_by:
            self.last_hit_by.kos += 1
        
        particles.spawn_ko(self.x + self.width//2, self.y + self.height//2, 
                          self.char_data['color'])
        sound_manager.play('ko_blast')
        
        self.state = FighterState.DEAD
    
    def respawn(self, spawn_x, spawn_y):
        self.reset_position(spawn_x, spawn_y)
        self.invincible = 180
        sound_manager.play('respawn')
    
    def update(self, platforms, blast_zones):
        if self.hitlag > 0:
            self.hitlag -= 1
            return
        
        if self.invincible > 0:
            self.invincible -= 1
        if self.intangible > 0:
            self.intangible -= 1
        
        if self.state == FighterState.DEAD:
            return
        
        if self.hitstun > 0:
            self.hitstun -= 1
            if self.hitstun == 0:
                self.state = FighterState.AIRBORNE if not self.on_ground else FighterState.IDLE
        
        if self.shield_stun > 0:
            self.shield_stun -= 1
        
        if self.attack_frame > 0:
            self.attack_frame -= 1
            if self.attack_frame == 0:
                self.attack_type = AttackType.NONE
                self.state = FighterState.AIRBORNE if not self.on_ground else FighterState.IDLE
                self.special_active = False
        
        if self.attack_type == AttackType.UP_B and self.attack_frame > 0:
            ratio = self.attack_frame / self.attack_duration
            if 0.3 < ratio < 0.8:
                self.vy = -self.char_data['jump_power'] * 0.8
        
        if self.state not in [FighterState.HITSTUN, FighterState.TUMBLE]:
            self.vy += 0.55
            if self.fastfalling:
                self.vy = min(self.vy, self.char_data['fast_fall'])
            else:
                self.vy = min(self.vy, self.char_data['fall_speed'])
        else:
            self.vy += 0.4
            self.vy = min(self.vy, 12)
        
        self.x += self.vx
        self.y += self.vy
        
        self.on_ground = False
        for plat in platforms:
            px, py, pw, ph = plat
            
            if (self.vy >= 0 and 
                self.x + self.width > px and self.x < px + pw and
                self.y + self.height >= py and self.y + self.height <= py + ph + 10):
                
                prev_y = self.y - self.vy
                if prev_y + self.height <= py + 5:
                    self.y = py - self.height
                    self.vy = 0
                    self.on_ground = True
                    self.jumps_left = self.char_data['air_jumps'] + 1
                    self.fastfalling = False
                    self.aerial_used = False
                    
                    if self.state == FighterState.AIRBORNE:
                        self.state = FighterState.IDLE
                    elif self.state == FighterState.TUMBLE:
                        self.state = FighterState.PRONE
                        self.hitstun = 30
        
        if self.shielding and self.on_ground:
            self.shield_health = max(0, self.shield_health - 0.15)
        elif self.shield_health < 100:
            self.shield_health = min(100, self.shield_health + 0.08)
        
        if self.check_death(blast_zones):
            self.die()
        
        self.animation_timer += 1
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def cpu_think(self, fighters, platforms, projectiles):
        if not self.is_cpu:
            return
        
        self.cpu_action_timer -= 1
        if self.cpu_action_timer > 0:
            return
        
        self.cpu_action_timer = random.randint(5, 15 - self.cpu_difficulty)
        
        if not self.cpu_target or self.cpu_target.stocks <= 0:
            valid_targets = [f for f in fighters if f != self and f.stocks > 0]
            if valid_targets:
                self.cpu_target = min(valid_targets, 
                                     key=lambda f: abs(f.x - self.x) + abs(f.y - self.y))
        
        if not self.cpu_target:
            return
        
        target = self.cpu_target
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if self.state in [FighterState.HITSTUN, FighterState.TUMBLE]:
            if random.random() < 0.1 * self.cpu_difficulty:
                self.do_jump()
            return
        
        if not self.on_ground and self.y > SCREEN_HEIGHT - 150:
            self.do_jump()
            if random.random() < 0.3:
                if dx > 0:
                    self.vx = min(self.vx + 1, self.char_data['air_speed'])
                else:
                    self.vx = max(self.vx - 1, -self.char_data['air_speed'])
            return
        
        move_chance = 0.3 + self.cpu_difficulty * 0.05
        
        if dist > 150:
            if random.random() < move_chance:
                if dx > 0:
                    self.facing = 1
                    self.vx = self.char_data['run_speed']
                else:
                    self.facing = -1
                    self.vx = -self.char_data['run_speed']
            
            if dy < -80 and random.random() < 0.15:
                self.do_jump()
        
        elif dist < 80:
            attack_chance = 0.1 + self.cpu_difficulty * 0.03
            if random.random() < attack_chance:
                if self.on_ground:
                    if random.random() < 0.4:
                        self.attack_type = AttackType.FSMASH
                        self.attack_duration = 40
                        self.attack_frame = self.attack_duration
                        self.state = FighterState.ATTACK
                    else:
                        self.attack_type = AttackType.JAB1
                        self.attack_duration = 15
                        self.attack_frame = self.attack_duration
                        self.state = FighterState.ATTACK
                else:
                    self.attack_type = AttackType.NAIR
                    self.attack_duration = 18
                    self.attack_frame = self.attack_duration
                    self.state = FighterState.ATTACK
        
        if target.attack_frame > 0 and dist < 100:
            if random.random() < 0.05 * self.cpu_difficulty:
                self.shielding = True
                self.state = FighterState.SHIELD
            elif random.random() < 0.03 * self.cpu_difficulty:
                self.do_jump()
        else:
            self.shielding = False
        
        for proj in projectiles:
            if proj.owner != self:
                pdist = math.sqrt((proj.x - self.x)**2 + (proj.y - self.y)**2)
                if pdist < 100:
                    if random.random() < 0.1 * self.cpu_difficulty:
                        self.do_jump()
                    elif random.random() < 0.05 * self.cpu_difficulty:
                        self.shielding = True
    
    def draw(self, surface):
        if self.state == FighterState.DEAD:
            return
        
        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return
        
        color = self.char_data['color']
        color2 = self.char_data['color2']
        color3 = self.char_data['color3']
        
        if self.shielding:
            shield_alpha = int(self.shield_health * 1.5)
            shield_size = int(35 * (self.shield_health / 100))
            pygame.draw.circle(surface, (100, 100, 255),
                             (int(self.x + self.width//2), int(self.y + self.height//2)),
                             shield_size, 4)
        
        body_rect = pygame.Rect(self.x + 5, self.y + 18, 30, 32)
        head_pos = (int(self.x + self.width//2), int(self.y + 12))
        
        if self.state in [FighterState.RUN, FighterState.WALK]:
            body_rect.x += math.sin(self.animation_frame * 0.8) * 2
        
        pygame.draw.ellipse(surface, color3, (self.x + 5, self.y + self.height - 12, 14, 12))
        pygame.draw.ellipse(surface, color3, (self.x + 21, self.y + self.height - 12, 14, 12))
        
        pygame.draw.ellipse(surface, color2, body_rect)
        
        pygame.draw.circle(surface, color, head_pos, 14)
        
        eye_x = head_pos[0] + self.facing * 5
        pygame.draw.circle(surface, WHITE, (eye_x, head_pos[1] - 2), 4)
        pygame.draw.circle(surface, BLACK, (eye_x + self.facing * 2, head_pos[1] - 2), 2)
        
        if self.hitstun > 0:
            pygame.draw.circle(surface, WHITE, (eye_x, head_pos[1] - 2), 3)
            for _ in range(3):
                sx = self.x + random.randint(0, self.width)
                sy = self.y + random.randint(0, self.height)
                pygame.draw.circle(surface, YELLOW, (int(sx), int(sy)), 2)
        
        if self.attack_frame > 0 and self.attack_type != AttackType.NONE:
            arm_len = 25
            arm_angle = 0
            
            if self.attack_type in [AttackType.JAB1, AttackType.FSMASH, AttackType.FAIR]:
                arm_angle = 0 if self.facing > 0 else 180
            elif self.attack_type in [AttackType.USMASH, AttackType.UAIR]:
                arm_angle = -90
            elif self.attack_type in [AttackType.DSMASH, AttackType.DAIR]:
                arm_angle = 90
            
            arm_x = self.x + self.width//2 + math.cos(math.radians(arm_angle)) * arm_len * self.facing
            arm_y = self.y + 25 + math.sin(math.radians(arm_angle)) * arm_len
            
            pygame.draw.line(surface, color3, 
                           (self.x + self.width//2, self.y + 25),
                           (arm_x, arm_y), 5)
            pygame.draw.circle(surface, color3, (int(arm_x), int(arm_y)), 6)
        
        if self.attack_frame > 0:
            hitbox = self.get_hitbox()
            if hitbox:
                rect = hitbox['rect']
                s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
                s.fill((255, 0, 0, 80))
                surface.blit(s, (rect[0], rect[1]))

# =============================================================================
# GAME CLASS
# =============================================================================
class UltraSmash64:
    def __init__(self):
        self.state = GameState.INTRO
        self.prev_state = None
        
        self.intro_timer = 0
        self.title_timer = 0
        
        self.menu_index = 0
        self.char_cursor = [0, 0, 0, 0]
        self.stage_cursor = 0
        
        self.game_mode = '1P GAME'
        self.num_players = 2
        self.stocks = 4
        self.time_limit = 0
        self.items_on = True
        self.cpu_level = 5
        
        self.player_chars = ['MARIO', 'FOX', 'PIKACHU', 'KIRBY']
        self.player_types = ['HUMAN', 'CPU', 'NONE', 'NONE']
        self.current_stage = 'DREAM LAND'
        
        self.fighters = []
        self.projectiles = []
        self.items = []
        self.platforms = []
        self.bg_color = DARK_BLUE
        self.blast_zones = (-150, SCREEN_WIDTH + 150, -200, SCREEN_HEIGHT + 100)
        
        self.game_timer = 0
        self.game_frame = 0
        self.paused = False
        self.winner = None
        
        self.unlocked_chars = {name: not data['unlock'] for name, data in CHARACTERS.items()}
        
        self.options = {
            'music_volume': 80,
            'sfx_volume': 100,
            'rumble': True,
            'deflicker': False
        }
        
        self.records = {char: {'plays': 0, 'wins': 0, 'kos': 0} for char in CHARACTERS}
        
        self.main_menu_items = [
            '1P GAME',
            'VS MODE', 
            'OPTIONS',
            'DATA'
        ]
        
        self.p1_controls = {
            'left': pygame.K_a, 'right': pygame.K_d,
            'up': pygame.K_w, 'down': pygame.K_s,
            'attack': pygame.K_f, 'special': pygame.K_g,
            'shield': pygame.K_h, 'grab': pygame.K_j,
            'jump': pygame.K_w
        }
        
        self.p2_controls = {
            'left': pygame.K_LEFT, 'right': pygame.K_RIGHT,
            'up': pygame.K_UP, 'down': pygame.K_DOWN,
            'attack': pygame.K_COMMA, 'special': pygame.K_PERIOD,
            'shield': pygame.K_SLASH, 'grab': pygame.K_SEMICOLON,
            'jump': pygame.K_UP
        }
    
    def transition_to(self, new_state):
        self.prev_state = self.state
        self.state = new_state
        self.menu_index = 0
    
    def handle_intro(self, events, keys):
        self.intro_timer += 1
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.transition_to(GameState.TITLE)
        
        if self.intro_timer > 180:
            self.transition_to(GameState.TITLE)
    
    def handle_title(self, events, keys):
        self.title_timer += 1
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_z]:
                    sound_manager.play('menu_confirm')
                    self.transition_to(GameState.MAIN_MENU)
    
    def handle_main_menu(self, events, keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(self.main_menu_items)
                    sound_manager.play('menu_move')
                elif event.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(self.main_menu_items)
                    sound_manager.play('menu_move')
                elif event.key in [pygame.K_RETURN, pygame.K_z]:
                    sound_manager.play('menu_confirm')
                    selected = self.main_menu_items[self.menu_index]
                    
                    if selected == '1P GAME':
                        self.game_mode = '1P GAME'
                        self.transition_to(GameState.MODE_SELECT)
                    elif selected == 'VS MODE':
                        self.game_mode = 'VS MODE'
                        self.transition_to(GameState.MODE_SELECT)
                    elif selected == 'OPTIONS':
                        self.transition_to(GameState.OPTIONS)
                    elif selected == 'DATA':
                        self.transition_to(GameState.DATA)
                
                elif event.key == pygame.K_ESCAPE:
                    self.transition_to(GameState.TITLE)
    
    def handle_mode_select(self, events, keys):
        if self.game_mode == '1P GAME':
            modes = ['CLASSIC', 'TRAINING', 'BONUS 1: BREAK THE TARGETS', 
                    'BONUS 2: BOARD THE PLATFORMS', 'BACK']
        else:
            modes = ['TIME MATCH', 'STOCK MATCH', 'TEAM BATTLE', 'FREE FOR ALL', 'BACK']
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(modes)
                    sound_manager.play('menu_move')
                elif event.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(modes)
                    sound_manager.play('menu_move')
                elif event.key in [pygame.K_RETURN, pygame.K_z]:
                    sound_manager.play('menu_confirm')
                    selected = modes[self.menu_index]
                    
                    if selected == 'BACK':
                        self.transition_to(GameState.MAIN_MENU)
                    elif selected == 'TRAINING':
                        self.game_mode = 'TRAINING'
                        self.transition_to(GameState.CHAR_SELECT)
                    elif selected.startswith('BONUS'):
                        self.game_mode = selected
                        self.transition_to(GameState.CHAR_SELECT)
                    else:
                        self.game_mode = selected
                        self.transition_to(GameState.CHAR_SELECT)
                
                elif event.key == pygame.K_ESCAPE:
                    sound_manager.play('menu_back')
                    self.transition_to(GameState.MAIN_MENU)
    
    def handle_char_select(self, events, keys):
        char_list = [name for name, data in CHARACTERS.items() 
                    if self.unlocked_chars.get(name, False) or not data['unlock']]
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.char_cursor[0] = (self.char_cursor[0] - 1) % len(char_list)
                    sound_manager.play('menu_move')
                elif event.key == pygame.K_RIGHT:
                    self.char_cursor[0] = (self.char_cursor[0] + 1) % len(char_list)
                    sound_manager.play('menu_move')
                elif event.key == pygame.K_UP:
                    self.char_cursor[0] = (self.char_cursor[0] - 4) % len(char_list)
                    sound_manager.play('menu_move')
                elif event.key == pygame.K_DOWN:
                    self.char_cursor[0] = (self.char_cursor[0] + 4) % len(char_list)
                    sound_manager.play('menu_move')
                elif event.key in [pygame.K_RETURN, pygame.K_z]:
                    sound_manager.play('menu_confirm')
                    self.player_chars[0] = char_list[self.char_cursor[0]]
                    
                    if self.game_mode in ['1P GAME', 'CLASSIC', 'TRAINING']:
                        self.player_chars[1] = random.choice(char_list)
                        self.player_types[1] = 'CPU'
                    
                    self.transition_to(GameState.STAGE_SELECT)
                
                elif event.key == pygame.K_ESCAPE:
                    sound_manager.play('menu_back')
                    self.transition_to(GameState.MODE_SELECT)
    
    def handle_stage_select(self, events, keys):
        stage_list = list(STAGES.keys())
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_LEFT, pygame.K_UP]:
                    self.stage_cursor = (self.stage_cursor - 1) % len(stage_list)
                    sound_manager.play('menu_move')
                elif event.key in [pygame.K_RIGHT, pygame.K_DOWN]:
                    self.stage_cursor = (self.stage_cursor + 1) % len(stage_list)
                    sound_manager.play('menu_move')
                elif event.key in [pygame.K_RETURN, pygame.K_z]:
                    sound_manager.play('menu_confirm')
                    self.current_stage = stage_list[self.stage_cursor]
                    self.start_battle()
                elif event.key == pygame.K_ESCAPE:
                    sound_manager.play('menu_back')
                    self.transition_to(GameState.CHAR_SELECT)
    
    def handle_options(self, events, keys):
        opt_items = ['MUSIC VOLUME', 'SFX VOLUME', 'SOUND TEST', 'BACK']
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(opt_items)
                    sound_manager.play('menu_move')
                elif event.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(opt_items)
                    sound_manager.play('menu_move')
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    if self.menu_index == 0:
                        delta = 10 if event.key == pygame.K_RIGHT else -10
                        self.options['music_volume'] = max(0, min(100, 
                            self.options['music_volume'] + delta))
                    elif self.menu_index == 1:
                        delta = 10 if event.key == pygame.K_RIGHT else -10
                        self.options['sfx_volume'] = max(0, min(100,
                            self.options['sfx_volume'] + delta))
                    sound_manager.play('menu_move')
                elif event.key in [pygame.K_RETURN, pygame.K_z]:
                    if self.menu_index == 2:
                        sound_manager.play('hit_smash')
                    elif self.menu_index == 3:
                        sound_manager.play('menu_confirm')
                        self.transition_to(GameState.MAIN_MENU)
                elif event.key == pygame.K_ESCAPE:
                    sound_manager.play('menu_back')
                    self.transition_to(GameState.MAIN_MENU)
    
    def handle_data(self, events, keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_z]:
                    sound_manager.play('menu_back')
                    self.transition_to(GameState.MAIN_MENU)
    
    def start_battle(self):
        self.transition_to(GameState.BATTLE)
        
        stage_data = STAGES[self.current_stage]
        self.bg_color = stage_data['bg_color']
        self.blast_zones = stage_data['blast_zones']
        
        self.platforms = [stage_data['main_platform']] + stage_data['platforms']
        
        self.fighters = []
        self.projectiles = []
        self.items = []
        particles.particles = []
        
        spawn_x = [200, 550, 350, 450]
        spawn_y = 200
        
        for i in range(2):
            is_cpu = (self.player_types[i] == 'CPU' or 
                     (i == 1 and self.game_mode in ['1P GAME', 'CLASSIC', 'TRAINING']))
            controls = self.p1_controls if i == 0 else self.p2_controls
            
            fighter = Fighter(
                spawn_x[i], spawn_y,
                self.player_chars[i],
                i + 1,
                controls,
                is_cpu
            )
            fighter.stocks = self.stocks
            fighter.cpu_difficulty = self.cpu_level
            self.fighters.append(fighter)
        
        self.game_timer = self.time_limit * 60 * 60 if self.time_limit > 0 else 0
        self.game_frame = 0
        self.winner = None
        self.paused = False
        
        sound_manager.play('announcer')
    
    def handle_battle(self, events, keys):
        if self.paused:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = False
                    elif event.key == pygame.K_q:
                        self.transition_to(GameState.MAIN_MENU)
            return
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = True
                    return
        
        for fighter in self.fighters:
            if not fighter.is_cpu:
                fighter.handle_input(keys, events)
            else:
                fighter.cpu_think(self.fighters, self.platforms, self.projectiles)
        
        for proj in self.projectiles[:]:
            proj.update()
            if not proj.active:
                self.projectiles.remove(proj)
                continue
            
            for fighter in self.fighters:
                if fighter != proj.owner and fighter.state != FighterState.DEAD:
                    if proj.get_rect().colliderect(fighter.get_rect()):
                        if fighter.take_hit(proj.damage, proj.knockback, 45, proj.owner):
                            particles.spawn_hit(fighter.x + fighter.width//2,
                                              fighter.y + fighter.height//2, proj.damage)
                        self.projectiles.remove(proj)
                        break
        
        for fighter in self.fighters:
            fighter.update(self.platforms, self.blast_zones)
            
            if fighter.attack_type == AttackType.NEUTRAL_B:
                if fighter.attack_frame == int(fighter.attack_duration * 0.5):
                    fighter.create_projectile(self.projectiles)
        
        for i, f1 in enumerate(self.fighters):
            hitbox = f1.get_hitbox()
            if hitbox:
                hit_rect = pygame.Rect(hitbox['rect'])
                for j, f2 in enumerate(self.fighters):
                    if i != j and f2.state != FighterState.DEAD:
                        if hit_rect.colliderect(f2.get_rect()):
                            if f2.take_hit(hitbox['damage'], hitbox['knockback'], 
                                          hitbox['angle'], f1):
                                particles.spawn_hit(
                                    f2.x + f2.width//2, f2.y + f2.height//2,
                                    hitbox['damage']
                                )
                                f1.attack_frame = 0
        
        for fighter in self.fighters:
            if fighter.state == FighterState.DEAD and fighter.stocks > 0:
                fighter.respawn(SCREEN_WIDTH // 2, 100)
        
        particles.update()
        
        if self.game_mode == 'TRAINING':
            for f in self.fighters:
                if f.player_num == 2:
                    f.damage = 0
                    f.stocks = 99
        
        alive = [f for f in self.fighters if f.stocks > 0]
        if len(alive) <= 1:
            self.winner = alive[0] if alive else None
            sound_manager.play('game_set')
            self.transition_to(GameState.RESULTS)
        
        self.game_frame += 1
    
    def handle_results(self, events, keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_z, pygame.K_ESCAPE]:
                    sound_manager.play('menu_confirm')
                    self.transition_to(GameState.MAIN_MENU)
    
    def draw_intro(self, surface):
        surface.fill(BLACK)
        
        alpha = min(255, self.intro_timer * 3)
        if self.intro_timer > 120:
            alpha = max(0, 255 - (self.intro_timer - 120) * 5)
        
        text1 = FONT_LARGE.render("catsan and co", True, GOLD)
        text2 = FONT_MEDIUM.render("presents", True, WHITE)
        
        surface.blit(text1, (SCREEN_WIDTH//2 - text1.get_width()//2, 250))
        surface.blit(text2, (SCREEN_WIDTH//2 - text2.get_width()//2, 310))
    
    def draw_title(self, surface):
        for y in range(SCREEN_HEIGHT):
            r = int(20 + y * 0.05)
            g = int(20 + y * 0.03)
            b = int(80 - y * 0.05)
            pygame.draw.line(surface, (max(0,r), max(0,g), max(0,b)), (0, y), (SCREEN_WIDTH, y))
        
        for _ in range(80):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            pygame.draw.circle(surface, WHITE, (x, y), 1)
        
        title = "ULTRA!SMASH 64"
        colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE]
        
        for i, char in enumerate(title):
            x = SCREEN_WIDTH // 2 - 280 + i * 40
            y = 100 + math.sin(pygame.time.get_ticks() / 200 + i * 0.5) * 8
            
            color = colors[i % len(colors)]
            
            shadow = FONT_TITLE.render(char, True, BLACK)
            surface.blit(shadow, (x + 4, y + 4))
            
            text = FONT_TITLE.render(char, True, color)
            surface.blit(text, (x, y))
        
        sub1 = FONT_SMALL.render("[by catsan and co]", True, GOLD)
        sub2 = FONT_SMALL.render("[C] 1999-2025", True, GRAY)
        surface.blit(sub1, (SCREEN_WIDTH//2 - sub1.get_width()//2, 200))
        surface.blit(sub2, (SCREEN_WIDTH//2 - sub2.get_width()//2, 230))
        
        if (self.title_timer // 30) % 2 == 0:
            press = FONT_MEDIUM.render("PRESS START", True, WHITE)
            surface.blit(press, (SCREEN_WIDTH//2 - press.get_width()//2, 450))
        
        chars_text = FONT_TINY.render("12 FIGHTERS - 9 STAGES - ALL MODES", True, LIGHT_GRAY)
        surface.blit(chars_text, (SCREEN_WIDTH//2 - chars_text.get_width()//2, 520))
    
    def draw_main_menu(self, surface):
        surface.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("ULTRA!SMASH 64", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 60))
        
        sub = FONT_TINY.render("[by catsan and co] [C] 1999-2025", True, GRAY)
        surface.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 110))
        
        for i, item in enumerate(self.main_menu_items):
            y = 200 + i * 60
            
            if i == self.menu_index:
                pygame.draw.rect(surface, (40, 40, 120), (200, y - 5, 400, 50), border_radius=10)
                pygame.draw.rect(surface, GOLD, (200, y - 5, 400, 50), 3, border_radius=10)
                color = GOLD
            else:
                color = WHITE
            
            text = FONT_LARGE.render(item, True, color)
            surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
        
        hint = FONT_TINY.render("UP/DOWN: Select   Z/ENTER: Confirm   ESC: Back", True, GRAY)
        surface.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 40))
    
    def draw_mode_select(self, surface):
        surface.fill((30, 30, 80))
        
        title = FONT_LARGE.render(self.game_mode, True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        if self.game_mode == '1P GAME':
            modes = ['CLASSIC', 'TRAINING', 'BONUS 1: BREAK THE TARGETS',
                    'BONUS 2: BOARD THE PLATFORMS', 'BACK']
        else:
            modes = ['TIME MATCH', 'STOCK MATCH', 'TEAM BATTLE', 'FREE FOR ALL', 'BACK']
        
        for i, mode in enumerate(modes):
            y = 150 + i * 55
            
            if i == self.menu_index:
                pygame.draw.rect(surface, (50, 50, 130), (150, y - 5, 500, 45), border_radius=8)
                color = GOLD
            else:
                color = WHITE
            
            text = FONT_MEDIUM.render(mode, True, color)
            surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
    
    def draw_char_select(self, surface):
        surface.fill((30, 30, 60))
        
        title = FONT_LARGE.render("SELECT YOUR FIGHTER", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 20))
        
        char_list = [name for name, data in CHARACTERS.items()
                    if self.unlocked_chars.get(name, False) or not data['unlock']]
        
        cols = 4
        cell_w = 100
        cell_h = 90
        start_x = (SCREEN_WIDTH - cols * cell_w) // 2
        start_y = 80
        
        for i, char in enumerate(char_list):
            row = i // cols
            col = i % cols
            x = start_x + col * cell_w
            y = start_y + row * cell_h
            
            char_data = CHARACTERS[char]
            is_selected = i == self.char_cursor[0]
            
            if is_selected:
                pygame.draw.rect(surface, GOLD, (x - 3, y - 3, cell_w - 4, cell_h - 4), 3, border_radius=8)
            
            pygame.draw.rect(surface, DARK_GRAY, (x, y, cell_w - 10, cell_h - 10), border_radius=6)
            
            pygame.draw.circle(surface, char_data['color'], (x + 45, y + 30), 20)
            pygame.draw.ellipse(surface, char_data['color2'], (x + 30, y + 45, 30, 18))
            
            name = FONT_TINY.render(char[:8], True, WHITE)
            surface.blit(name, (x + 45 - name.get_width()//2, y + 68))
        
        if char_list:
            current = char_list[self.char_cursor[0]]
            char_data = CHARACTERS[current]
            
            info_x = 50
            info_y = SCREEN_HEIGHT - 180
            
            pygame.draw.rect(surface, DARK_GRAY, (info_x, info_y, 300, 160), border_radius=10)
            pygame.draw.rect(surface, char_data['color'], (info_x, info_y, 300, 160), 2, border_radius=10)
            
            name = FONT_MEDIUM.render(char_data['name'], True, char_data['color'])
            surface.blit(name, (info_x + 10, info_y + 10))
            
            series = FONT_TINY.render(char_data['series'], True, GRAY)
            surface.blit(series, (info_x + 10, info_y + 45))
            
            stats = [
                f"Weight: {char_data['weight']}",
                f"Speed: {char_data['run_speed']:.1f}",
                f"Jump: {char_data['jump_power']}",
                f"Air Jumps: {char_data['air_jumps']}"
            ]
            for j, stat in enumerate(stats):
                t = FONT_TINY.render(stat, True, WHITE)
                surface.blit(t, (info_x + 10, info_y + 70 + j * 20))
            
            special = FONT_SMALL.render(f"B: {char_data['special_neutral']}", True, GOLD)
            surface.blit(special, (info_x + 160, info_y + 70))
    
    def draw_stage_select(self, surface):
        surface.fill((20, 30, 50))
        
        title = FONT_LARGE.render("SELECT STAGE", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 30))
        
        stage_list = list(STAGES.keys())
        cols = 3
        cell_w = 200
        cell_h = 150
        start_x = (SCREEN_WIDTH - cols * cell_w) // 2
        start_y = 100
        
        for i, stage in enumerate(stage_list):
            row = i // cols
            col = i % cols
            x = start_x + col * cell_w
            y = start_y + row * cell_h
            
            stage_data = STAGES[stage]
            is_selected = i == self.stage_cursor
            
            pygame.draw.rect(surface, stage_data['bg_color'], (x + 5, y + 5, cell_w - 20, cell_h - 40), border_radius=5)
            
            scale = 0.2
            main = stage_data['main_platform']
            mx = x + 10 + int(main[0] * scale)
            my = y + 10 + int(main[1] * scale * 0.5)
            mw = int(main[2] * scale)
            mh = max(3, int(main[3] * scale))
            pygame.draw.rect(surface, stage_data['ground_color'], (mx, my, mw, mh))
            
            for plat in stage_data['platforms']:
                px = x + 10 + int(plat[0] * scale)
                py = y + 10 + int(plat[1] * scale * 0.5)
                pw = int(plat[2] * scale)
                ph = max(2, int(plat[3] * scale))
                pygame.draw.rect(surface, stage_data['platform_color'], (px, py, pw, ph))
            
            if is_selected:
                pygame.draw.rect(surface, GOLD, (x + 3, y + 3, cell_w - 16, cell_h - 36), 3, border_radius=5)
            
            name = FONT_TINY.render(stage_data['name'], True, WHITE)
            surface.blit(name, (x + cell_w//2 - name.get_width()//2, y + cell_h - 30))
    
    def draw_options(self, surface):
        surface.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("OPTIONS", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        opt_items = [
            f"MUSIC VOLUME: {self.options['music_volume']}%",
            f"SFX VOLUME: {self.options['sfx_volume']}%",
            "SOUND TEST",
            "BACK"
        ]
        
        for i, item in enumerate(opt_items):
            y = 150 + i * 60
            color = GOLD if i == self.menu_index else WHITE
            
            if i == self.menu_index:
                pygame.draw.rect(surface, (40, 40, 100), (150, y - 5, 500, 50), border_radius=8)
            
            text = FONT_MEDIUM.render(item, True, color)
            surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
        
        hint = FONT_TINY.render("LEFT/RIGHT: Adjust   Z: Select   ESC: Back", True, GRAY)
        surface.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 50))
    
    def draw_data(self, surface):
        surface.fill(DARK_BLUE)
        
        title = FONT_LARGE.render("DATA", True, GOLD)
        surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        
        info = [
            f"Total Fighters: {len(CHARACTERS)}",
            f"Unlocked: {sum(self.unlocked_chars.values())}",
            f"Total Stages: {len(STAGES)}",
            "",
            "Press any key to return"
        ]
        
        for i, line in enumerate(info):
            color = GOLD if i == 0 else WHITE
            text = FONT_MEDIUM.render(line, True, color)
            surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150 + i * 50))
    
    def draw_battle(self, surface):
        surface.fill(self.bg_color)
        
        stage_data = STAGES[self.current_stage]
        
        for plat in self.platforms:
            if plat == self.platforms[0]:
                color = stage_data['ground_color']
            else:
                color = stage_data['platform_color']
            
            pygame.draw.rect(surface, color, plat)
            pygame.draw.rect(surface, tuple(max(0, c - 30) for c in color), 
                           (plat[0], plat[1], plat[2], 4))
        
        for proj in self.projectiles:
            proj.draw(surface)
        
        particles.draw(surface)
        
        for fighter in self.fighters:
            fighter.draw(surface)
        
        self.draw_hud(surface)
        
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            
            pause_text = FONT_HUGE.render("PAUSED", True, WHITE)
            surface.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 200))
            
            hint1 = FONT_MEDIUM.render("ESC - Resume", True, GRAY)
            hint2 = FONT_MEDIUM.render("Q - Quit", True, GRAY)
            surface.blit(hint1, (SCREEN_WIDTH//2 - hint1.get_width()//2, 300))
            surface.blit(hint2, (SCREEN_WIDTH//2 - hint2.get_width()//2, 350))
    
    def draw_hud(self, surface):
        for i, fighter in enumerate(self.fighters):
            x = 80 + i * 350
            y = SCREEN_HEIGHT - 90
            
            pygame.draw.rect(surface, (30, 30, 50), (x - 10, y - 5, 280, 80), border_radius=10)
            pygame.draw.rect(surface, fighter.char_data['color'], (x - 10, y - 5, 280, 80), 2, border_radius=10)
            
            pygame.draw.circle(surface, fighter.char_data['color'], (x + 30, y + 25), 22)
            pygame.draw.circle(surface, fighter.char_data['color2'], (x + 30, y + 20), 10)
            
            name = FONT_SMALL.render(fighter.char_data['name'][:10], True, WHITE)
            surface.blit(name, (x + 60, y + 5))
            
            p_text = FONT_TINY.render(f"P{fighter.player_num}", True, GOLD)
            surface.blit(p_text, (x + 220, y + 5))
            
            if fighter.damage < 50:
                dmg_color = WHITE
            elif fighter.damage < 100:
                dmg_color = YELLOW
            elif fighter.damage < 150:
                dmg_color = ORANGE
            else:
                dmg_color = RED
            
            dmg = FONT_LARGE.render(f"{int(fighter.damage)}%", True, dmg_color)
            surface.blit(dmg, (x + 100, y + 30))
            
            for s in range(fighter.stocks):
                sx = x + 10 + s * 22
                sy = y + 58
                pygame.draw.circle(surface, fighter.char_data['color'], (sx, sy), 8)
    
    def draw_results(self, surface):
        surface.fill(DARK_BLUE)
        
        result = FONT_HUGE.render("GAME SET!", True, GOLD)
        surface.blit(result, (SCREEN_WIDTH//2 - result.get_width()//2, 80))
        
        if self.winner:
            winner_text = FONT_LARGE.render(f"{self.winner.char_data['name']} WINS!", True, 
                                           self.winner.char_data['color'])
            surface.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, 180))
            
            pygame.draw.circle(surface, self.winner.char_data['color'], (400, 320), 60)
            pygame.draw.circle(surface, self.winner.char_data['color2'], (400, 300), 25)
            pygame.draw.circle(surface, WHITE, (395, 295), 6)
            pygame.draw.circle(surface, BLACK, (397, 295), 3)
        else:
            draw_text = FONT_LARGE.render("DRAW!", True, GRAY)
            surface.blit(draw_text, (SCREEN_WIDTH//2 - draw_text.get_width()//2, 200))
        
        stats_y = 420
        for i, fighter in enumerate(self.fighters):
            x = 150 + i * 300
            
            name = FONT_MEDIUM.render(fighter.char_data['name'], True, fighter.char_data['color'])
            surface.blit(name, (x, stats_y))
            
            kos = FONT_SMALL.render(f"KOs: {fighter.kos}", True, WHITE)
            falls = FONT_SMALL.render(f"Falls: {fighter.falls}", True, WHITE)
            surface.blit(kos, (x, stats_y + 35))
            surface.blit(falls, (x, stats_y + 60))
        
        hint = FONT_MEDIUM.render("Press any key to continue", True, GRAY)
        surface.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 60))
    
    def run(self):
        running = True
        
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
            
            keys = pygame.key.get_pressed()
            
            if self.state == GameState.INTRO:
                self.handle_intro(events, keys)
                self.draw_intro(screen)
            elif self.state == GameState.TITLE:
                self.handle_title(events, keys)
                self.draw_title(screen)
            elif self.state == GameState.MAIN_MENU:
                self.handle_main_menu(events, keys)
                self.draw_main_menu(screen)
            elif self.state == GameState.MODE_SELECT:
                self.handle_mode_select(events, keys)
                self.draw_mode_select(screen)
            elif self.state == GameState.CHAR_SELECT:
                self.handle_char_select(events, keys)
                self.draw_char_select(screen)
            elif self.state == GameState.STAGE_SELECT:
                self.handle_stage_select(events, keys)
                self.draw_stage_select(screen)
            elif self.state == GameState.OPTIONS:
                self.handle_options(events, keys)
                self.draw_options(screen)
            elif self.state == GameState.DATA:
                self.handle_data(events, keys)
                self.draw_data(screen)
            elif self.state == GameState.BATTLE:
                self.handle_battle(events, keys)
                self.draw_battle(screen)
            elif self.state == GameState.RESULTS:
                self.handle_results(events, keys)
                self.draw_results(screen)
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()

# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("                    ULTRA!SMASH 64")
    print("              [by catsan and co] [C] 1999-2025")
    print("=" * 70)
    print()
    print("  COMPLETE SUPER SMASH BROS 64 RECREATION")
    print()
    print("  FEATURES:")
    print("  - All 12 Original Fighters")
    print("  - All 9 Original Stages")
    print("  - 1P Game / VS Mode / Training")
    print("  - Full Damage/Knockback System")
    print("  - Projectiles & Special Moves")
    print("  - CPU AI with Adjustable Difficulty")
    print()
    print("  CONTROLS:")
    print("  P1: WASD + F/G/H/J (Attack/Special/Shield/Grab)")
    print("  P2: Arrows + ,./;  (Attack/Special/Shield/Grab)")
    print("  ESC: Pause/Back")
    print()
    print("=" * 70)
    print()
    
    game = UltraSmash64()
    game.run()
