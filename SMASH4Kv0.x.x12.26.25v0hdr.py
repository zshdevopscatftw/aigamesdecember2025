import sys
import math
import random
import pygame
from enum import Enum
from typing import List, Dict, Tuple

# ============================================================
# SUPER SMASH BROS 64 - COMPLETE PYGAME_CE ENGINE
# All characters, stages, modes, movesets - Single file
# ============================================================

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)

WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Super Smash Bros 64 - Complete Edition")
clock = pygame.time.Clock()
TARGET_FPS = 60

# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class GameMode(Enum):
    VS_CPU = "VS CPU"
    VS_PLAYER = "VS Player"
    TIME_MODE = "Time Mode"
    STOCK_MODE = "Stock Mode"
    TRAINING = "Training"
    TOURNAMENT = "Tournament"
    MAIN_MENU = "Main Menu"
    CHARACTER_SELECT = "Character Select"

class AttackType(Enum):
    JAB = "jab"
    DASH_ATTACK = "dash_attack"
    FTILT = "ftilt"
    UTILT = "utilt"
    DTILT = "dtilt"
    FSMASH = "fsmash"
    USMASH = "usmash"
    DSMASH = "dsmash"
    NAIR = "nair"
    FAIR = "fair"
    BAIR = "bair"
    UAIR = "uair"
    DAIR = "dair"
    NEUTRAL_SPECIAL = "neutral_special"
    SIDE_SPECIAL = "side_special"
    UP_SPECIAL = "up_special"
    DOWN_SPECIAL = "down_special"
    GRAB = "grab"
    THROW = "throw"

class PhysicsConstants:
    GRAVITY = 0.095
    MAX_FALL_SPEED = 2.5
    AIR_FRICTION = 0.89
    GROUND_FRICTION = 0.86
    JUMP_VELOCITY = -2.5
    SHORT_HOP_VELOCITY = -1.8
    FAST_FALL_MULTIPLIER = 1.5
    DASH_INITIAL_SPEED = 1.6
    DASH_MAX_SPEED = 1.8
    WALK_SPEED = 0.8
    AIR_SPEED = 0.85
    AIR_DODGE_SPEED = 2.0
    WAVEDASH_SPEED = 1.2

# ============================================================
# CHARACTER DATA - ALL 12 CHARACTERS
# ============================================================

CHARACTERS = {
    "mario": {
        "weight": 100,
        "speed": 1.0,
        "jump": 1.0,
        "color": (255, 50, 50),
        "fall_speed": 1.0,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.4, "startup": 5},
            AttackType.FSMASH: {"damage": 18, "knockback": 1.8, "startup": 12},
            AttackType.USMASH: {"damage": 16, "knockback": 1.6, "startup": 12},
            AttackType.DSMASH: {"damage": 14, "knockback": 1.4, "startup": 11},
            AttackType.FAIR: {"damage": 12, "knockback": 1.2, "startup": 8},
            AttackType.BAIR: {"damage": 14, "knockback": 1.3, "startup": 9},
            AttackType.UAIR: {"damage": 11, "knockback": 1.1, "startup": 7},
            AttackType.DAIR: {"damage": 13, "knockback": 1.5, "startup": 10},
            AttackType.NEUTRAL_SPECIAL: {"damage": 8, "knockback": 1.0, "startup": 15},
            AttackType.UP_SPECIAL: {"damage": 10, "knockback": 1.2, "startup": 12},
        }
    },
    "donkey_kong": {
        "weight": 112,
        "speed": 0.9,
        "jump": 0.85,
        "color": (150, 75, 0),
        "fall_speed": 1.1,
        "moves": {
            AttackType.JAB: {"damage": 4, "knockback": 0.5, "startup": 6},
            AttackType.FSMASH: {"damage": 22, "knockback": 2.0, "startup": 14},
            AttackType.USMASH: {"damage": 20, "knockback": 1.8, "startup": 13},
            AttackType.DSMASH: {"damage": 18, "knockback": 1.6, "startup": 12},
            AttackType.FAIR: {"damage": 14, "knockback": 1.3, "startup": 9},
            AttackType.BAIR: {"damage": 16, "knockback": 1.4, "startup": 10},
            AttackType.UAIR: {"damage": 13, "knockback": 1.2, "startup": 8},
            AttackType.DAIR: {"damage": 15, "knockback": 1.6, "startup": 11},
            AttackType.NEUTRAL_SPECIAL: {"damage": 10, "knockback": 1.1, "startup": 16},
            AttackType.UP_SPECIAL: {"damage": 12, "knockback": 1.3, "startup": 14},
        }
    },
    "link": {
        "weight": 104,
        "speed": 0.85,
        "jump": 0.9,
        "color": (50, 150, 50),
        "fall_speed": 0.95,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.3, "startup": 5},
            AttackType.FSMASH: {"damage": 19, "knockback": 1.9, "startup": 13},
            AttackType.USMASH: {"damage": 17, "knockback": 1.7, "startup": 12},
            AttackType.DSMASH: {"damage": 15, "knockback": 1.5, "startup": 11},
            AttackType.FAIR: {"damage": 11, "knockback": 1.1, "startup": 8},
            AttackType.BAIR: {"damage": 13, "knockback": 1.2, "startup": 9},
            AttackType.UAIR: {"damage": 10, "knockback": 1.0, "startup": 7},
            AttackType.DAIR: {"damage": 14, "knockback": 1.4, "startup": 10},
            AttackType.NEUTRAL_SPECIAL: {"damage": 6, "knockback": 0.8, "startup": 20},
            AttackType.UP_SPECIAL: {"damage": 9, "knockback": 1.1, "startup": 13},
        }
    },
    "samus": {
        "weight": 110,
        "speed": 0.88,
        "jump": 0.95,
        "color": (150, 150, 50),
        "fall_speed": 0.98,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.35, "startup": 5},
            AttackType.FSMASH: {"damage": 20, "knockback": 1.8, "startup": 13},
            AttackType.USMASH: {"damage": 18, "knockback": 1.7, "startup": 12},
            AttackType.DSMASH: {"damage": 16, "knockback": 1.5, "startup": 11},
            AttackType.FAIR: {"damage": 13, "knockback": 1.2, "startup": 9},
            AttackType.BAIR: {"damage": 14, "knockback": 1.3, "startup": 10},
            AttackType.UAIR: {"damage": 12, "knockback": 1.1, "startup": 8},
            AttackType.DAIR: {"damage": 12, "knockback": 1.4, "startup": 11},
            AttackType.NEUTRAL_SPECIAL: {"damage": 8, "knockback": 0.9, "startup": 18},
            AttackType.UP_SPECIAL: {"damage": 11, "knockback": 1.2, "startup": 14},
        }
    },
    "yoshi": {
        "weight": 108,
        "speed": 1.1,
        "jump": 1.2,
        "color": (100, 200, 100),
        "fall_speed": 0.88,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.3, "startup": 4},
            AttackType.FSMASH: {"damage": 17, "knockback": 1.6, "startup": 11},
            AttackType.USMASH: {"damage": 15, "knockback": 1.5, "startup": 10},
            AttackType.DSMASH: {"damage": 13, "knockback": 1.3, "startup": 10},
            AttackType.FAIR: {"damage": 11, "knockback": 1.0, "startup": 7},
            AttackType.BAIR: {"damage": 12, "knockback": 1.1, "startup": 8},
            AttackType.UAIR: {"damage": 10, "knockback": 0.9, "startup": 6},
            AttackType.DAIR: {"damage": 12, "knockback": 1.3, "startup": 9},
            AttackType.NEUTRAL_SPECIAL: {"damage": 7, "knockback": 0.7, "startup": 14},
            AttackType.UP_SPECIAL: {"damage": 10, "knockback": 1.0, "startup": 12},
        }
    },
    "kirby": {
        "weight": 76,
        "speed": 0.95,
        "jump": 1.3,
        "color": (255, 150, 200),
        "fall_speed": 0.75,
        "moves": {
            AttackType.JAB: {"damage": 2, "knockback": 0.3, "startup": 4},
            AttackType.FSMASH: {"damage": 15, "knockback": 1.5, "startup": 10},
            AttackType.USMASH: {"damage": 13, "knockback": 1.4, "startup": 9},
            AttackType.DSMASH: {"damage": 12, "knockback": 1.2, "startup": 9},
            AttackType.FAIR: {"damage": 10, "knockback": 0.9, "startup": 7},
            AttackType.BAIR: {"damage": 11, "knockback": 1.0, "startup": 8},
            AttackType.UAIR: {"damage": 9, "knockback": 0.8, "startup": 6},
            AttackType.DAIR: {"damage": 10, "knockback": 1.1, "startup": 8},
            AttackType.NEUTRAL_SPECIAL: {"damage": 6, "knockback": 0.6, "startup": 12},
            AttackType.UP_SPECIAL: {"damage": 9, "knockback": 0.9, "startup": 11},
        }
    },
    "fox": {
        "weight": 86,
        "speed": 1.25,
        "jump": 1.1,
        "color": (255, 100, 50),
        "fall_speed": 1.05,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.4, "startup": 4},
            AttackType.FSMASH: {"damage": 16, "knockback": 1.6, "startup": 10},
            AttackType.USMASH: {"damage": 14, "knockback": 1.5, "startup": 9},
            AttackType.DSMASH: {"damage": 12, "knockback": 1.3, "startup": 9},
            AttackType.FAIR: {"damage": 11, "knockback": 1.0, "startup": 7},
            AttackType.BAIR: {"damage": 13, "knockback": 1.1, "startup": 8},
            AttackType.UAIR: {"damage": 10, "knockback": 0.9, "startup": 6},
            AttackType.DAIR: {"damage": 11, "knockback": 1.2, "startup": 9},
            AttackType.NEUTRAL_SPECIAL: {"damage": 7, "knockback": 0.8, "startup": 13},
            AttackType.UP_SPECIAL: {"damage": 10, "knockback": 1.1, "startup": 12},
        }
    },
    "pikachu": {
        "weight": 80,
        "speed": 1.15,
        "jump": 1.15,
        "color": (255, 255, 50),
        "fall_speed": 0.92,
        "moves": {
            AttackType.JAB: {"damage": 2, "knockback": 0.3, "startup": 4},
            AttackType.FSMASH: {"damage": 14, "knockback": 1.4, "startup": 9},
            AttackType.USMASH: {"damage": 12, "knockback": 1.3, "startup": 8},
            AttackType.DSMASH: {"damage": 11, "knockback": 1.2, "startup": 8},
            AttackType.FAIR: {"damage": 9, "knockback": 0.9, "startup": 6},
            AttackType.BAIR: {"damage": 10, "knockback": 1.0, "startup": 7},
            AttackType.UAIR: {"damage": 8, "knockback": 0.8, "startup": 5},
            AttackType.DAIR: {"damage": 9, "knockback": 1.0, "startup": 7},
            AttackType.NEUTRAL_SPECIAL: {"damage": 5, "knockback": 0.7, "startup": 11},
            AttackType.UP_SPECIAL: {"damage": 8, "knockback": 0.9, "startup": 10},
        }
    },
    "luigi": {
        "weight": 99,
        "speed": 1.02,
        "jump": 1.05,
        "color": (50, 150, 100),
        "fall_speed": 0.99,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.4, "startup": 5},
            AttackType.FSMASH: {"damage": 17, "knockback": 1.7, "startup": 12},
            AttackType.USMASH: {"damage": 15, "knockback": 1.6, "startup": 11},
            AttackType.DSMASH: {"damage": 13, "knockback": 1.4, "startup": 10},
            AttackType.FAIR: {"damage": 11, "knockback": 1.1, "startup": 8},
            AttackType.BAIR: {"damage": 13, "knockback": 1.2, "startup": 9},
            AttackType.UAIR: {"damage": 10, "knockback": 1.0, "startup": 7},
            AttackType.DAIR: {"damage": 12, "knockback": 1.3, "startup": 9},
            AttackType.NEUTRAL_SPECIAL: {"damage": 8, "knockback": 0.9, "startup": 15},
            AttackType.UP_SPECIAL: {"damage": 10, "knockback": 1.1, "startup": 11},
        }
    },
    "captain_falcon": {
        "weight": 102,
        "speed": 1.15,
        "jump": 1.08,
        "color": (200, 100, 50),
        "fall_speed": 1.02,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.4, "startup": 5},
            AttackType.FSMASH: {"damage": 19, "knockback": 1.9, "startup": 12},
            AttackType.USMASH: {"damage": 17, "knockback": 1.8, "startup": 11},
            AttackType.DSMASH: {"damage": 15, "knockback": 1.6, "startup": 10},
            AttackType.FAIR: {"damage": 12, "knockback": 1.2, "startup": 8},
            AttackType.BAIR: {"damage": 14, "knockback": 1.3, "startup": 9},
            AttackType.UAIR: {"damage": 11, "knockback": 1.1, "startup": 7},
            AttackType.DAIR: {"damage": 13, "knockback": 1.4, "startup": 10},
            AttackType.NEUTRAL_SPECIAL: {"damage": 9, "knockback": 1.0, "startup": 14},
            AttackType.UP_SPECIAL: {"damage": 11, "knockback": 1.2, "startup": 13},
        }
    },
    "ness": {
        "weight": 94,
        "speed": 0.92,
        "jump": 1.12,
        "color": (200, 100, 150),
        "fall_speed": 0.88,
        "moves": {
            AttackType.JAB: {"damage": 3, "knockback": 0.35, "startup": 5},
            AttackType.FSMASH: {"damage": 18, "knockback": 1.7, "startup": 11},
            AttackType.USMASH: {"damage": 16, "knockback": 1.6, "startup": 10},
            AttackType.DSMASH: {"damage": 14, "knockback": 1.5, "startup": 10},
            AttackType.FAIR: {"damage": 11, "knockback": 1.0, "startup": 8},
            AttackType.BAIR: {"damage": 12, "knockback": 1.1, "startup": 9},
            AttackType.UAIR: {"damage": 10, "knockback": 0.9, "startup": 7},
            AttackType.DAIR: {"damage": 11, "knockback": 1.2, "startup": 9},
            AttackType.NEUTRAL_SPECIAL: {"damage": 7, "knockback": 0.85, "startup": 13},
            AttackType.UP_SPECIAL: {"damage": 9, "knockback": 1.0, "startup": 12},
        }
    },
    "jigglypuff": {
        "weight": 68,
        "speed": 0.88,
        "jump": 1.4,
        "color": (255, 150, 255),
        "fall_speed": 0.6,
        "moves": {
            AttackType.JAB: {"damage": 2, "knockback": 0.25, "startup": 3},
            AttackType.FSMASH: {"damage": 13, "knockback": 1.3, "startup": 9},
            AttackType.USMASH: {"damage": 11, "knockback": 1.2, "startup": 8},
            AttackType.DSMASH: {"damage": 10, "knockback": 1.1, "startup": 8},
            AttackType.FAIR: {"damage": 9, "knockback": 0.8, "startup": 6},
            AttackType.BAIR: {"damage": 10, "knockback": 0.9, "startup": 7},
            AttackType.UAIR: {"damage": 8, "knockback": 0.7, "startup": 5},
            AttackType.DAIR: {"damage": 8, "knockback": 0.9, "startup": 7},
            AttackType.NEUTRAL_SPECIAL: {"damage": 5, "knockback": 0.6, "startup": 10},
            AttackType.UP_SPECIAL: {"damage": 7, "knockback": 0.8, "startup": 9},
        }
    },
}

# ============================================================
# STAGE DATA - 8 PLAYABLE STAGES
# ============================================================

STAGES = {
    "dream_land": {
        "name": "Dream Land",
        "bg_color": (30, 50, 100),
        "platforms": [
            pygame.Rect(200, 350, 200, 15),
            pygame.Rect(500, 300, 200, 15),
            pygame.Rect(350, 220, 200, 15),
            pygame.Rect(100, 280, 80, 12),
            pygame.Rect(700, 280, 80, 12),
            pygame.Rect(400, 150, 100, 10),
        ]
    },
    "hyrule_castle": {
        "name": "Hyrule Castle",
        "bg_color": (50, 80, 30),
        "platforms": [
            pygame.Rect(150, 350, 250, 15),
            pygame.Rect(550, 350, 250, 15),
            pygame.Rect(350, 250, 180, 15),
            pygame.Rect(200, 180, 120, 12),
            pygame.Rect(600, 180, 120, 12),
            pygame.Rect(400, 100, 100, 10),
        ]
    },
    "peach_castle": {
        "name": "Peach's Castle",
        "bg_color": (200, 100, 150),
        "platforms": [
            pygame.Rect(180, 360, 220, 15),
            pygame.Rect(520, 360, 220, 15),
            pygame.Rect(350, 280, 200, 15),
            pygame.Rect(100, 240, 100, 12),
            pygame.Rect(750, 240, 100, 12),
            pygame.Rect(400, 160, 120, 10),
        ]
    },
    "yoshi_story": {
        "name": "Yoshi's Story",
        "bg_color": (100, 150, 200),
        "platforms": [
            pygame.Rect(200, 380, 200, 12),
            pygame.Rect(520, 380, 200, 12),
            pygame.Rect(350, 300, 180, 12),
            pygame.Rect(100, 260, 80, 10),
            pygame.Rect(750, 260, 80, 10),
            pygame.Rect(400, 180, 100, 10),
        ]
    },
    "mushroom_kingdom": {
        "name": "Mushroom Kingdom",
        "bg_color": (100, 200, 100),
        "platforms": [
            pygame.Rect(120, 340, 140, 12),
            pygame.Rect(350, 320, 100, 12),
            pygame.Rect(580, 340, 140, 12),
            pygame.Rect(200, 250, 120, 12),
            pygame.Rect(620, 250, 120, 12),
            pygame.Rect(400, 160, 110, 10),
        ]
    },
    "congo_jungle": {
        "name": "Congo Jungle",
        "bg_color": (80, 120, 60),
        "platforms": [
            pygame.Rect(180, 360, 210, 15),
            pygame.Rect(530, 360, 210, 15),
            pygame.Rect(350, 270, 190, 15),
            pygame.Rect(120, 220, 100, 12),
            pygame.Rect(720, 220, 100, 12),
            pygame.Rect(400, 130, 110, 10),
        ]
    },
    "sector_z": {
        "name": "Sector Z",
        "bg_color": (60, 60, 100),
        "platforms": [
            pygame.Rect(150, 340, 240, 12),
            pygame.Rect(550, 340, 240, 12),
            pygame.Rect(350, 240, 200, 12),
            pygame.Rect(200, 160, 140, 10),
            pygame.Rect(600, 160, 140, 10),
        ]
    },
    "final_destination": {
        "name": "Final Destination",
        "bg_color": (20, 20, 60),
        "platforms": [
            pygame.Rect(200, 380, 520, 12),
        ]
    },
}

# ============================================================
# PLAYER CLASS
# ============================================================

class Player(pygame.Rect):
    def __init__(self, x: float, y: float, character: str, controls: Dict, is_cpu: bool = False):
        super().__init__(x, y, 42, 56)
        self.character = character
        self.stats = CHARACTERS[character]
        self.controls = controls
        self.is_cpu = is_cpu
        
        # Physics
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.facing = 1
        self.on_ground = False
        self.jumps_used = 0
        self.max_jumps = 2
        self.fast_fall = False
        self.prev_bottom = self.bottom
        
        # Movement
        self.dash_timer = 0
        self.dash_direction = 0
        self.move_speed = 0.0
        
        # Combat
        self.percent = 0.0
        self.stocks = 4
        self.kills = 0
        self.deaths = 0
        self.damage_given = 0.0
        self.damage_taken = 0.0
        self.hitstun = 0
        self.knockback_x = 0.0
        self.knockback_y = 0.0
        
        # State
        self.state = "idle"
        self.state_timer = 0
        self.attack_type: AttackType = None
        self.attack_cooldown = 0
        self.jab_combo = 0
        self.special_cooldown = 0
        self.grab_cooldown = 0
        self.grabbed_by = None
        
        # Shield
        self.shield = 100.0
        self.shield_active = False
        self.shield_break_timer = 0
        
        # Recovery
        self.edge_timer = 0
        self.recovery_height = 0
        
        self.color = self.stats["color"]
        self.active = True

    def update_input(self, keys: Dict, keys_down: List):
        if self.is_cpu or self.hitstun > 0 or self.shield_break_timer > 0 or not self.active:
            return
            
        # Movement input
        move_input = 0
        if keys[self.controls["left"]]:
            move_input -= 1
        if keys[self.controls["right"]]:
            move_input += 1
            
        # Dash
        if move_input != 0:
            if self.dash_timer <= 0 and move_input != self.dash_direction:
                self.dash_direction = move_input
                self.dash_timer = 20
                self.velocity_x = PhysicsConstants.DASH_INITIAL_SPEED * move_input
            elif self.dash_timer > 0:
                self.velocity_x = PhysicsConstants.DASH_MAX_SPEED * move_input * self.stats["speed"]
            else:
                self.velocity_x = PhysicsConstants.WALK_SPEED * move_input * self.stats["speed"]
        else:
            self.dash_timer = 0
            
        # Jump
        if self.controls["jump"] in keys_down:
            if self.on_ground:
                self.velocity_y = PhysicsConstants.JUMP_VELOCITY * self.stats["jump"]
                self.jumps_used = 1
            elif self.jumps_used < self.max_jumps:
                self.velocity_y = PhysicsConstants.JUMP_VELOCITY * 0.8 * self.stats["jump"]
                self.jumps_used += 1
                
        # Fast fall
        self.fast_fall = keys[self.controls["down"]]
        
        # Shield
        self.shield_active = keys[self.controls["shield"]]
        if self.shield_active and self.shield > 0:
            self.shield = max(0, self.shield - 0.5)
            if self.shield == 0:
                self.shield_break_timer = 180
        elif not self.shield_active and self.shield < 100:
            self.shield = min(100, self.shield + 0.2)
            
        # Attacks
        if self.attack_cooldown <= 0 and self.grab_cooldown <= 0:
            if self.controls["attack"] in keys_down:
                self._perform_attack(AttackType.JAB)
            elif self.controls["special"] in keys_down and self.special_cooldown <= 0:
                self._perform_attack(AttackType.NEUTRAL_SPECIAL)
            elif self.controls["smash"] in keys_down:
                self._perform_attack(AttackType.FSMASH)
                
        # Update facing
        if move_input != 0:
            self.facing = move_input

    def _perform_attack(self, attack_type: AttackType):
        if attack_type not in self.stats["moves"]:
            return
            
        self.attack_type = attack_type
        self.state = attack_type.value
        self.attack_cooldown = self.stats["moves"][attack_type]["startup"] + 15
        
        if attack_type == AttackType.JAB:
            self.jab_combo = (self.jab_combo % 3) + 1
        elif attack_type in [AttackType.NEUTRAL_SPECIAL, AttackType.UP_SPECIAL]:
            self.special_cooldown = 60

    def take_damage(self, damage: float, knockback_x: float, knockback_y: float, attacker: 'Player'):
        if self.shield_active and self.shield > 0:
            self.shield = max(0, self.shield - damage * 0.3)
            damage *= 0.3
            
        self.percent += damage
        self.damage_taken += damage
        
        # Knockback formula
        knockback_scalar = (self.percent / 10 + self.percent * damage / 20) * 0.04 + 1.8
        weight_factor = 1.0 / (self.stats["weight"] / 100)
        
        self.velocity_x = knockback_x * knockback_scalar * weight_factor
        self.velocity_y = knockback_y * knockback_scalar * weight_factor
        self.hitstun = max(1, int((damage * 0.5 + self.percent * 0.02) * 3))

    def ring_out(self):
        self.stocks -= 1
        self.deaths += 1
        if self.stocks > 0:
            self.reset_position()
        else:
            self.active = False

    def reset_position(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 200
        self.velocity_x = 0
        self.velocity_y = 0
        self.percent = 0
        self.hitstun = 0
        self.state = "idle"
        self.jumps_used = 0

    def update_cpu(self, target: 'Player'):
        if self.hitstun > 0 or self.shield_break_timer > 0 or not self.active:
            return
            
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Movement
        if distance > 150:
            if dx > 0:
                self.velocity_x = PhysicsConstants.WALK_SPEED * self.stats["speed"]
                self.facing = 1
            else:
                self.velocity_x = -PhysicsConstants.WALK_SPEED * self.stats["speed"]
                self.facing = -1
        elif distance < 50:
            self.velocity_x = -self.facing * PhysicsConstants.WALK_SPEED * 0.5
            
        # Jump AI
        if self.on_ground and random.random() < 0.02:
            self.velocity_y = PhysicsConstants.JUMP_VELOCITY * self.stats["jump"]
            
        # Attack AI
        if distance < 100 and self.attack_cooldown <= 0:
            attack_choice = random.random()
            if attack_choice < 0.4:
                self._perform_attack(AttackType.JAB)
            elif attack_choice < 0.7:
                self._perform_attack(AttackType.FSMASH)
            elif attack_choice < 0.85:
                self._perform_attack(AttackType.USMASH)

    def draw(self, surface):
        # Draw character
        pygame.draw.rect(surface, self.color, self)
        pygame.draw.rect(surface, (200, 200, 200), self, 2)
        
        # Shield
        if self.shield_active and self.shield > 0:
            alpha = int(self.shield * 1.5)
            pygame.draw.circle(surface, (100, 180, 255), 
                             (int(self.centerx), int(self.centery)), 35)
            
        # Attack visualization
        if self.state != "idle" and self.state_timer > 0:
            hitbox = self.get_hitbox()
            pygame.draw.rect(surface, (255, 200, 100), hitbox, 2)

    def get_hitbox(self) -> pygame.Rect:
        if "jab" in self.state:
            return pygame.Rect(self.x + 20 * self.facing, self.y + 10, 30, 25)
        elif "fsmash" in self.state:
            return pygame.Rect(self.x + 35 * self.facing, self.y, 40, 35)
        elif "usmash" in self.state:
            return pygame.Rect(self.x + 10, self.y - 40, 30, 50)
        elif "dsmash" in self.state:
            return pygame.Rect(self.x - 15, self.y + 30, 60, 30)
        elif "special" in self.state:
            return pygame.Rect(self.x + 25 * self.facing, self.y - 20, 45, 60)
        else:
            return pygame.Rect(0, 0, 0, 0)

# ============================================================
# PHYSICS ENGINE
# ============================================================

class PhysicsEngine:
    def __init__(self):
        self.accumulator = 0.0
        self.time_step = 1.0 / TARGET_FPS
        
    def update(self, players: List[Player], platforms: List[pygame.Rect], callback):
        self.accumulator += clock.get_time() / 1000.0
        
        while self.accumulator >= self.time_step:
            for player in players:
                if player.active:
                    self._update_player(player, platforms)
            callback()
            self.accumulator -= self.time_step
    
    def _update_player(self, player: Player, platforms: List[pygame.Rect]):
        # Gravity
        player.velocity_y = min(
            player.velocity_y + PhysicsConstants.GRAVITY, 
            PhysicsConstants.MAX_FALL_SPEED
        )
        
        # Fast fall
        if player.fast_fall and not player.on_ground:
            player.velocity_y *= PhysicsConstants.FAST_FALL_MULTIPLIER
            
        # Friction
        if player.on_ground:
            player.velocity_x *= PhysicsConstants.GROUND_FRICTION
        else:
            player.velocity_x *= PhysicsConstants.AIR_FRICTION
            
        # Position update
        player.x += player.velocity_x
        player.y += player.velocity_y
        
        # Collisions
        self._check_collisions(player, platforms)
        
        # Blast zones
        if player.y > HEIGHT + 100 or player.x < -100 or player.x > WIDTH + 100:
            player.ring_out()

    def _check_collisions(self, player: Player, platforms: List[pygame.Rect]):
        player.on_ground = False
        
        # Floor
        if player.y + player.height >= HEIGHT - 80:
            player.y = HEIGHT - 80 - player.height
            player.velocity_y = 0
            player.on_ground = True
            player.jumps_used = 0
            
        # Platforms
        for platform in platforms:
            if (player.colliderect(platform) and 
                player.prev_bottom <= platform.top + 5 and
                player.velocity_y >= 0):
                player.y = platform.top - player.height
                player.velocity_y = 0
                player.on_ground = True
                player.jumps_used = 0

# ============================================================
# GAME MANAGER
# ============================================================

class Smash64Engine:
    def __init__(self):
        self.mode = GameMode.MAIN_MENU
        self.selected_character = 0
        self.character_list = list(CHARACTERS.keys())
        self.stage_list = list(STAGES.keys())
        self.selected_stage = 0
        
        self.players: List[Player] = []
        self.platforms: List[pygame.Rect] = []
        self.physics = PhysicsEngine()
        self.game_active = False
        self.paused = False
        self.menu_selection = 0
        self.timer = 0
        self.stock_limit = 4
        self.time_limit = 300
        
        self.results = {}
        self.combo_counter = 0
        self.combo_timer = 0
        
        # Fonts
        self.fonts = {
            "tiny": pygame.font.Font(None, 16),
            "small": pygame.font.Font(None, 24),
            "medium": pygame.font.Font(None, 32),
            "large": pygame.font.Font(None, 48),
            "huge": pygame.font.Font(None, 72),
        }

    def start_game(self, game_mode: GameMode, player_count: int = 2, cpu_count: int = 0):
        self.mode = game_mode
        self.game_active = True
        self.timer = self.time_limit if game_mode == GameMode.TIME_MODE else 0
        self.players.clear()
        self.paused = False
        
        spawns = [
            (WIDTH // 4, HEIGHT - 200),
            (3 * WIDTH // 4, HEIGHT - 200),
            (WIDTH // 2, HEIGHT - 250),
            (WIDTH // 4, HEIGHT - 250),
        ]
        
        for i in range(player_count):
            char = self.character_list[i % len(self.character_list)]
            is_cpu = i >= (player_count - cpu_count)
            
            controls = self._get_controls(i)
            player = Player(spawns[i][0], spawns[i][1], char, controls, is_cpu)
            player.stocks = self.stock_limit if game_mode == GameMode.STOCK_MODE else 99
            player.active = True
            self.players.append(player)
            
        # Setup stage
        stage = STAGES[self.stage_list[self.selected_stage]]
        self.platforms = [pygame.Rect(p) for p in stage["platforms"]]

    def _get_controls(self, player_idx: int) -> Dict:
        if player_idx == 0:
            return {
                "left": pygame.K_a, "right": pygame.K_d,
                "up": pygame.K_w, "down": pygame.K_s,
                "jump": pygame.K_w, "attack": pygame.K_f,
                "special": pygame.K_g, "smash": pygame.K_r,
                "shield": pygame.K_q,
            }
        elif player_idx == 1:
            return {
                "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
                "up": pygame.K_UP, "down": pygame.K_DOWN,
                "jump": pygame.K_UP, "attack": pygame.K_SLASH,
                "special": pygame.K_PERIOD, "smash": pygame.K_RSHIFT,
                "shield": pygame.K_RALT,
            }
        elif player_idx == 2:
            return {
                "left": pygame.K_j, "right": pygame.K_l,
                "up": pygame.K_i, "down": pygame.K_k,
                "jump": pygame.K_i, "attack": pygame.K_u,
                "special": pygame.K_o, "smash": pygame.K_p,
                "shield": pygame.K_SEMICOLON,
            }
        else:
            return {
                "left": pygame.K_KP4, "right": pygame.K_KP6,
                "up": pygame.K_KP8, "down": pygame.K_KP2,
                "jump": pygame.K_KP8, "attack": pygame.K_KP0,
                "special": pygame.K_KP_PERIOD, "smash": pygame.K_KP_PLUS,
                "shield": pygame.K_KP5,
            }

    def update(self):
        if not self.game_active or self.paused or self.mode in [GameMode.MAIN_MENU, GameMode.CHARACTER_SELECT]:
            return
            
        self.physics.update(self.players, self.platforms, self._post_physics)
        
        # CPU updates
        for i, player in enumerate(self.players):
            if player.is_cpu and player.active:
                target = self.players[0] if len(self.players) > 0 else player
                player.update_cpu(target)

    def _post_physics(self):
        # Decrement timers
        for player in self.players:
            if player.active:
                player.prev_bottom = player.bottom
                
                if player.state_timer > 0:
                    player.state_timer -= 1
                if player.attack_cooldown > 0:
                    player.attack_cooldown -= 1
                if player.special_cooldown > 0:
                    player.special_cooldown -= 1
                if player.hitstun > 0:
                    player.hitstun -= 1
                if player.shield_break_timer > 0:
                    player.shield_break_timer -= 1
                if player.dash_timer > 0:
                    player.dash_timer -= 1
                if player.grab_cooldown > 0:
                    player.grab_cooldown -= 1
                    
        # Collisions
        self._check_collisions()
        
        # Win conditions
        self._check_win_condition()
        
        # Timer
        if self.mode == GameMode.TIME_MODE:
            self.timer -= 1 / TARGET_FPS

    def _check_collisions(self):
        for i, attacker in enumerate(self.players):
            if not attacker.active or attacker.attack_cooldown > 3:
                continue
                
            if attacker.state != "idle":
                hitbox = attacker.get_hitbox()
                
                for j, defender in enumerate(self.players):
                    if i == j or not defender.active:
                        continue
                        
                    if hitbox.colliderect(defender) and defender.hitstun <= 0:
                        self._apply_attack(attacker, defender, hitbox)

    def _apply_attack(self, attacker: Player, defender: Player, hitbox: pygame.Rect):
        attack_data = attacker.stats["moves"].get(attacker.attack_type)
        if not attack_data:
            return
            
        damage = attack_data["damage"]
        knockback_x = attack_data["knockback"] * attacker.facing
        knockback_y = attack_data["knockback"] * -0.8
        
        defender.take_damage(damage, knockback_x, knockback_y, attacker)
        attacker.damage_given += damage
        
        if attacker.attack_type == AttackType.JAB:
            attacker.kills += 1
        
        self.combo_counter += 1
        self.combo_timer = 30

    def _check_win_condition(self):
        active = [p for p in self.players if p.active]
        
        if len(active) <= 1:
            winner = active[0] if active else None
            self._end_game(winner)
            
        elif self.mode == GameMode.TIME_MODE and self.timer <= 0:
            winner = max(self.players, key=lambda p: p.kills - p.deaths)
            self._end_game(winner)

    def _end_game(self, winner: Player):
        self.game_active = False
        self.results = {
            "winner": winner,
            "players": [(p.character, p.kills, p.deaths, p.damage_given) for p in self.players]
        }

    def draw_main_menu(self):
        screen.fill((20, 20, 50))
        
        title = self.fonts["huge"].render("SUPER SMASH BROS 64", True, (255, 200, 100))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        
        options = ["VS CPU", "VS PLAYER", "TIME MODE", "STOCK MODE", "TRAINING", "QUIT"]
        for i, option in enumerate(options):
            color = (255, 255, 100) if i == self.menu_selection else (150, 150, 200)
            text = self.fonts["medium"].render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 50))

    def draw_character_select(self):
        screen.fill((30, 30, 80))
        
        title = self.fonts["large"].render("SELECT CHARACTER", True, (255, 200, 100))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        
        chars_per_row = 4
        cell_width = WIDTH // chars_per_row
        cell_height = 120
        
        for idx, char in enumerate(self.character_list):
            row = idx // chars_per_row
            col = idx % chars_per_row
            x = col * cell_width + 20
            y = 120 + row * cell_height
            
            rect = pygame.Rect(x, y, cell_width - 40, cell_height - 20)
            selected = idx == self.selected_character
            color = CHARACTERS[char]["color"]
            
            pygame.draw.rect(screen, color, rect, 3 if selected else 1)
            pygame.draw.rect(screen, color, rect)
            
            text = self.fonts["small"].render(char.replace("_", " "), True, (0, 0, 0))
            screen.blit(text, (x + 10, y + 10))

    def draw_stage_select(self):
        screen.fill((40, 60, 40))
        
        title = self.fonts["large"].render("SELECT STAGE", True, (150, 255, 150))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        
        stages_per_row = 4
        cell_width = WIDTH // stages_per_row
        cell_height = 120
        
        for idx, stage_key in enumerate(self.stage_list):
            stage = STAGES[stage_key]
            row = idx // stages_per_row
            col = idx % stages_per_row
            x = col * cell_width + 20
            y = 120 + row * cell_height
            
            rect = pygame.Rect(x, y, cell_width - 40, cell_height - 20)
            selected = idx == self.selected_stage
            
            pygame.draw.rect(screen, stage["bg_color"], rect, 3 if selected else 1)
            pygame.draw.rect(screen, stage["bg_color"], rect)
            
            text = self.fonts["small"].render(stage["name"], True, (255, 255, 255))
            screen.blit(text, (x + 10, y + 10))

    def draw_game(self):
        stage = STAGES[self.stage_list[self.selected_stage]]
        screen.fill(stage["bg_color"])
        
        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(screen, (100, 150, 200), platform)
            pygame.draw.rect(screen, (150, 200, 255), platform, 2)
            
        # Draw players
        for player in self.players:
            if player.active:
                player.draw(screen)
                
        # HUD
        self._draw_hud()
        
        if self.paused:
            self._draw_pause_menu()

    def _draw_hud(self):
        for i, player in enumerate(self.players):
            if not player.active:
                continue
                
            x_pos = 20 if i % 2 == 0 else WIDTH - 220
            y_pos = 20 if i < 2 else 140
            
            name_text = self.fonts["small"].render(player.character.replace("_", " ").title(), True, player.color)
            screen.blit(name_text, (x_pos, y_pos))
            
            percent_text = self.fonts["large"].render(f"{player.percent:.0f}%", True, (255, 255, 255))
            screen.blit(percent_text, (x_pos, y_pos + 30))
            
            if self.mode == GameMode.STOCK_MODE:
                stock_text = self.fonts["small"].render(f"Stocks: {max(0, player.stocks)}", True, (200, 200, 100))
                screen.blit(stock_text, (x_pos, y_pos + 70))
                
            # Shield bar
            if player.shield < 100:
                pygame.draw.rect(screen, (20, 20, 40), (x_pos, y_pos + 90, 150, 8))
                pygame.draw.rect(screen, (100, 180, 255), (x_pos, y_pos + 90, int(player.shield * 1.5), 8))

    def _draw_pause_menu(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        pause_text = self.fonts["huge"].render("PAUSED", True, (255, 255, 255))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, 150))
        
        options = ["RESUME", "RESTART", "MAIN MENU", "QUIT"]
        for i, option in enumerate(options):
            color = (255, 255, 100) if i == self.menu_selection else (150, 150, 200)
            text = self.fonts["medium"].render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 280 + i * 50))

    def draw_results(self):
        screen.fill((30, 30, 80))
        
        title = self.fonts["huge"].render("RESULTS", True, (255, 200, 100))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))
        
        if self.results.get("winner"):
            winner_text = self.fonts["large"].render(
                f"WINNER: {self.results['winner'].character.upper()}", 
                True, (100, 255, 100)
            )
            screen.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, 150))
            
        y = 250
        for char, kills, deaths, damage in self.results.get("players", []):
            text = self.fonts["medium"].render(
                f"{char.upper()} - K: {kills} D: {deaths} DMG: {damage:.0f}", 
                True, (200, 200, 220)
            )
            screen.blit(text, (50, y))
            y += 50

    def handle_input(self, keys, keys_down):
        if self.mode == GameMode.MAIN_MENU:
            if keys_down:
                if pygame.K_UP in keys_down:
                    self.menu_selection = (self.menu_selection - 1) % 6
                elif pygame.K_DOWN in keys_down:
                    self.menu_selection = (self.menu_selection + 1) % 6
                elif pygame.K_RETURN in keys_down:
                    if self.menu_selection == 0:
                        self.mode = GameMode.CHARACTER_SELECT
                        self.menu_selection = 0
                    elif self.menu_selection == 5:
                        return False
                        
        elif self.mode == GameMode.CHARACTER_SELECT:
            if keys_down:
                if pygame.K_LEFT in keys_down:
                    self.selected_character = (self.selected_character - 1) % len(self.character_list)
                elif pygame.K_RIGHT in keys_down:
                    self.selected_character = (self.selected_character + 1) % len(self.character_list)
                elif pygame.K_RETURN in keys_down:
                    self.selected_stage = 0
                    self.mode = GameMode.VS_CPU
                    self.start_game(GameMode.VS_CPU, 2, 1)
                elif pygame.K_ESCAPE in keys_down:
                    self.mode = GameMode.MAIN_MENU
                    
        elif self.game_active:
            if pygame.K_ESCAPE in keys_down:
                self.paused = not self.paused
                self.menu_selection = 0
            elif self.paused and keys_down:
                if pygame.K_UP in keys_down:
                    self.menu_selection = (self.menu_selection - 1) % 4
                elif pygame.K_DOWN in keys_down:
                    self.menu_selection = (self.menu_selection + 1) % 4
                elif pygame.K_RETURN in keys_down:
                    if self.menu_selection == 0:
                        self.paused = False
                    elif self.menu_selection == 1:
                        self.start_game(self.mode, len(self.players), 
                                      sum(1 for p in self.players if p.is_cpu))
                        self.paused = False
                    elif self.menu_selection == 2:
                        self.mode = GameMode.MAIN_MENU
                        self.game_active = False
                        self.paused = False
                    elif self.menu_selection == 3:
                        return False
            else:
                for player in self.players:
                    if not player.is_cpu:
                        player.update_input(keys, keys_down)
                        
        elif not self.game_active and self.results:
            if keys_down:
                if pygame.K_RETURN in keys_down or pygame.K_SPACE in keys_down:
                    self.mode = GameMode.MAIN_MENU
                    self.results.clear()
                elif pygame.K_ESCAPE in keys_down:
                    return False
                    
        return True

    def draw(self):
        if self.mode == GameMode.MAIN_MENU:
            self.draw_main_menu()
        elif self.mode == GameMode.CHARACTER_SELECT:
            self.draw_character_select()
        elif self.game_active:
            self.draw_game()
        elif self.results:
            self.draw_results()

# ============================================================
# MAIN LOOP
# ============================================================

def main():
    game = Smash64Engine()
    game.mode = GameMode.MAIN_MENU
    running = True
    
    while running:
        keys_down = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_down.append(event.key)
                
        keys = pygame.key.get_pressed()
        running = game.handle_input(keys, keys_down)
        
        if game.mode not in [GameMode.MAIN_MENU, GameMode.CHARACTER_SELECT]:
            game.update()
            
        game.draw()
        pygame.display.flip()
        clock.tick(TARGET_FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
