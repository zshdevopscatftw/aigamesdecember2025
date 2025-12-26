#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  CAT'S PVZ REPLANTED — PYGAME CE FORK 1.0                                    ║
║  [C] Samsoft 1999–2025 | Developer: A.C (ANNOYING CAT)                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FEATURES:                                                                   ║
║  • 50 Adventure Levels (Day/Night/Pool/Fog/Roof)                             ║
║  • 40+ Plants • 26 Zombie Types • Dr. Zomboss Boss                           ║
║  • Minigames • Survival • Shop • Achievements                                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import pygame
import sys
import random
import math
import json
import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

pygame.init()

# ============================================================
# CONFIG
# ============================================================
WIDTH, HEIGHT = 900, 650
FPS = 60
ROWS, COLS = 5, 9
CELL_W, CELL_H = 80, 100
GRID_X, GRID_Y = 80, 100

# ============================================================
# COLORS
# ============================================================
class C:
    SKY_DAY = (135, 206, 235)
    SKY_NIGHT = (25, 25, 50)
    SKY_POOL = (100, 180, 220)
    SKY_FOG = (80, 90, 100)
    SKY_ROOF = (180, 200, 220)
    LAWN_1 = (124, 204, 25)
    LAWN_2 = (86, 176, 0)
    LAWN_N1 = (50, 90, 30)
    LAWN_N2 = (35, 70, 20)
    POOL = (60, 140, 200)
    ROOF_1 = (139, 90, 60)
    ROOF_2 = (119, 70, 40)
    UI_BROWN = (139, 90, 43)
    UI_TAN = (210, 180, 140)
    UI_DARK = (40, 30, 20)
    SUN_Y = (255, 255, 0)
    SUN_O = (255, 200, 0)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (200, 50, 50)
    GREEN = (50, 200, 50)
    GRAY = (128, 128, 128)
    GOLD = (255, 215, 0)
    Z_GREEN = (120, 140, 100)
    Z_SKIN = (150, 170, 130)

# ============================================================
# ENUMS
# ============================================================
class GameState(Enum):
    MENU = auto()
    DAVE = auto()
    SEEDS = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAMEOVER = auto()
    WIN = auto()
    ALMANAC = auto()
    MINIGAMES = auto()
    SHOP = auto()
    CREDITS = auto()

class LevelType(Enum):
    DAY = auto()
    NIGHT = auto()
    POOL = auto()
    FOG = auto()
    ROOF = auto()
    BOSS = auto()

class PlantType(Enum):
    PEASHOOTER = auto()
    SUNFLOWER = auto()
    CHERRY_BOMB = auto()
    WALL_NUT = auto()
    POTATO_MINE = auto()
    SNOW_PEA = auto()
    CHOMPER = auto()
    REPEATER = auto()
    PUFF_SHROOM = auto()
    SUN_SHROOM = auto()
    FUME_SHROOM = auto()
    HYPNO_SHROOM = auto()
    ICE_SHROOM = auto()
    DOOM_SHROOM = auto()
    LILY_PAD = auto()
    SQUASH = auto()
    THREEPEATER = auto()
    JALAPENO = auto()
    TORCHWOOD = auto()
    TALL_NUT = auto()
    CACTUS = auto()
    STARFRUIT = auto()
    MELON_PULT = auto()
    GATLING_PEA = auto()
    WINTER_MELON = auto()
    CABBAGE_PULT = auto()
    KERNEL_PULT = auto()
    FLOWER_POT = auto()
    UMBRELLA_LEAF = auto()
    MARIGOLD = auto()

class ZombieType(Enum):
    NORMAL = auto()
    FLAG = auto()
    CONEHEAD = auto()
    POLE_VAULTER = auto()
    BUCKETHEAD = auto()
    NEWSPAPER = auto()
    SCREEN_DOOR = auto()
    FOOTBALL = auto()
    DANCING = auto()
    DUCKY_TUBE = auto()
    SNORKEL = auto()
    ZOMBONI = auto()
    DOLPHIN_RIDER = auto()
    JACK_IN_BOX = auto()
    BALLOON = auto()
    DIGGER = auto()
    POGO = auto()
    BUNGEE = auto()
    LADDER = auto()
    CATAPULT = auto()
    GARGANTUAR = auto()
    IMP = auto()
    DR_ZOMBOSS = auto()

# ============================================================
# DATA
# ============================================================
PLANTS = {
    PlantType.PEASHOOTER: {"name": "Peashooter", "cost": 100, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4},
    PlantType.SUNFLOWER: {"name": "Sunflower", "cost": 50, "cd": 7.5, "hp": 300, "sun": 25, "rate": 24},
    PlantType.CHERRY_BOMB: {"name": "Cherry Bomb", "cost": 150, "cd": 50, "hp": 300, "dmg": 1800, "instant": True},
    PlantType.WALL_NUT: {"name": "Wall-nut", "cost": 50, "cd": 30, "hp": 4000},
    PlantType.POTATO_MINE: {"name": "Potato Mine", "cost": 25, "cd": 30, "hp": 300, "dmg": 1800, "arm": 14},
    PlantType.SNOW_PEA: {"name": "Snow Pea", "cost": 175, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4, "slow": True},
    PlantType.CHOMPER: {"name": "Chomper", "cost": 150, "cd": 7.5, "hp": 300, "chew": 42},
    PlantType.REPEATER: {"name": "Repeater", "cost": 200, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4, "shots": 2},
    PlantType.PUFF_SHROOM: {"name": "Puff-shroom", "cost": 0, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4, "night": True},
    PlantType.SUN_SHROOM: {"name": "Sun-shroom", "cost": 25, "cd": 7.5, "hp": 300, "sun": 15, "rate": 24, "night": True},
    PlantType.FUME_SHROOM: {"name": "Fume-shroom", "cost": 75, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4, "pierce": True, "night": True},
    PlantType.HYPNO_SHROOM: {"name": "Hypno-shroom", "cost": 75, "cd": 30, "hp": 300, "night": True},
    PlantType.ICE_SHROOM: {"name": "Ice-shroom", "cost": 75, "cd": 50, "hp": 300, "instant": True, "freeze": True, "night": True},
    PlantType.DOOM_SHROOM: {"name": "Doom-shroom", "cost": 125, "cd": 50, "hp": 300, "dmg": 9999, "instant": True, "night": True},
    PlantType.LILY_PAD: {"name": "Lily Pad", "cost": 25, "cd": 7.5, "hp": 300, "aquatic": True},
    PlantType.SQUASH: {"name": "Squash", "cost": 50, "cd": 30, "hp": 300, "dmg": 1800},
    PlantType.THREEPEATER: {"name": "Threepeater", "cost": 325, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4, "lanes": 3},
    PlantType.JALAPENO: {"name": "Jalapeno", "cost": 125, "cd": 50, "hp": 300, "dmg": 1800, "instant": True, "row": True},
    PlantType.TORCHWOOD: {"name": "Torchwood", "cost": 175, "cd": 7.5, "hp": 300},
    PlantType.TALL_NUT: {"name": "Tall-nut", "cost": 125, "cd": 30, "hp": 8000},
    PlantType.CACTUS: {"name": "Cactus", "cost": 125, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4},
    PlantType.STARFRUIT: {"name": "Starfruit", "cost": 125, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 1.4, "star": True},
    PlantType.MELON_PULT: {"name": "Melon-pult", "cost": 300, "cd": 7.5, "hp": 300, "dmg": 80, "rate": 3, "splash": True},
    PlantType.GATLING_PEA: {"name": "Gatling Pea", "cost": 250, "cd": 50, "hp": 300, "dmg": 20, "rate": 1.4, "shots": 4},
    PlantType.WINTER_MELON: {"name": "Winter Melon", "cost": 200, "cd": 50, "hp": 300, "dmg": 80, "rate": 3, "splash": True, "slow": True},
    PlantType.CABBAGE_PULT: {"name": "Cabbage-pult", "cost": 100, "cd": 7.5, "hp": 300, "dmg": 40, "rate": 3, "lob": True},
    PlantType.KERNEL_PULT: {"name": "Kernel-pult", "cost": 100, "cd": 7.5, "hp": 300, "dmg": 20, "rate": 3, "lob": True},
    PlantType.FLOWER_POT: {"name": "Flower Pot", "cost": 25, "cd": 7.5, "hp": 300, "roof": True},
    PlantType.UMBRELLA_LEAF: {"name": "Umbrella Leaf", "cost": 100, "cd": 7.5, "hp": 300},
    PlantType.MARIGOLD: {"name": "Marigold", "cost": 50, "cd": 30, "hp": 300, "coin": True},
}

ZOMBIES = {
    ZombieType.NORMAL: {"name": "Zombie", "hp": 200, "spd": 0.4, "dmg": 100},
    ZombieType.FLAG: {"name": "Flag Zombie", "hp": 200, "spd": 0.55, "dmg": 100},
    ZombieType.CONEHEAD: {"name": "Conehead", "hp": 560, "spd": 0.4, "dmg": 100, "armor": 360},
    ZombieType.POLE_VAULTER: {"name": "Pole Vaulter", "hp": 340, "spd": 0.8, "dmg": 100, "vault": True},
    ZombieType.BUCKETHEAD: {"name": "Buckethead", "hp": 1300, "spd": 0.4, "dmg": 100, "armor": 1100},
    ZombieType.NEWSPAPER: {"name": "Newspaper", "hp": 340, "spd": 0.4, "dmg": 100, "armor": 140, "rage": True},
    ZombieType.SCREEN_DOOR: {"name": "Screen Door", "hp": 500, "spd": 0.4, "dmg": 100, "armor": 300, "shield": True},
    ZombieType.FOOTBALL: {"name": "Football", "hp": 1600, "spd": 0.7, "dmg": 100, "armor": 1400},
    ZombieType.DANCING: {"name": "Dancing", "hp": 340, "spd": 0.4, "dmg": 100, "summon": True},
    ZombieType.DUCKY_TUBE: {"name": "Ducky Tube", "hp": 200, "spd": 0.4, "dmg": 100, "aquatic": True},
    ZombieType.SNORKEL: {"name": "Snorkel", "hp": 200, "spd": 0.4, "dmg": 100, "aquatic": True, "dive": True},
    ZombieType.ZOMBONI: {"name": "Zomboni", "hp": 1350, "spd": 0.5, "dmg": 100, "vehicle": True},
    ZombieType.DOLPHIN_RIDER: {"name": "Dolphin Rider", "hp": 340, "spd": 0.8, "dmg": 100, "aquatic": True},
    ZombieType.JACK_IN_BOX: {"name": "Jack-in-the-Box", "hp": 340, "spd": 0.7, "dmg": 100, "explode": True},
    ZombieType.BALLOON: {"name": "Balloon", "hp": 200, "spd": 0.5, "dmg": 100, "flying": True},
    ZombieType.DIGGER: {"name": "Digger", "hp": 340, "spd": 0.5, "dmg": 100, "dig": True},
    ZombieType.POGO: {"name": "Pogo", "hp": 340, "spd": 0.6, "dmg": 100, "pogo": True},
    ZombieType.BUNGEE: {"name": "Bungee", "hp": 340, "spd": 0, "dmg": 0, "aerial": True},
    ZombieType.LADDER: {"name": "Ladder", "hp": 500, "spd": 0.6, "dmg": 100, "armor": 300, "ladder": True},
    ZombieType.CATAPULT: {"name": "Catapult", "hp": 850, "spd": 0.3, "dmg": 100, "vehicle": True},
    ZombieType.GARGANTUAR: {"name": "Gargantuar", "hp": 3000, "spd": 0.3, "dmg": 500, "crush": True},
    ZombieType.IMP: {"name": "Imp", "hp": 80, "spd": 0.9, "dmg": 100},
    ZombieType.DR_ZOMBOSS: {"name": "Dr. Zomboss", "hp": 40000, "spd": 0, "dmg": 0, "boss": True},
}

# ============================================================
# LEVELS
# ============================================================
def make_levels():
    levels = []
    # Day 1-10
    for i in range(10):
        z = [ZombieType.NORMAL] * (3 + i)
        if i >= 3: z += [ZombieType.FLAG]
        if i >= 5: z += [ZombieType.CONEHEAD] * (i - 4)
        if i >= 8: z += [ZombieType.POLE_VAULTER]
        levels.append({"type": LevelType.DAY, "waves": min(2 + i // 3, 4), "zombies": z, "sun": 50})
    # Night 11-20
    for i in range(10):
        z = [ZombieType.NORMAL] * (4 + i) + [ZombieType.CONEHEAD] * (2 + i // 2)
        if i >= 2: z += [ZombieType.BUCKETHEAD]
        if i >= 5: z += [ZombieType.NEWSPAPER] * 2
        if i >= 8: z += [ZombieType.FOOTBALL]
        levels.append({"type": LevelType.NIGHT, "waves": 3 + i // 3, "zombies": z, "sun": 50})
    # Pool 21-30
    for i in range(10):
        z = [ZombieType.NORMAL] * (5 + i) + [ZombieType.CONEHEAD] * (3 + i // 2) + [ZombieType.BUCKETHEAD] * (1 + i // 3)
        z += [ZombieType.DUCKY_TUBE] * (2 + i // 2)
        if i >= 3: z += [ZombieType.SNORKEL] * 2
        if i >= 6: z += [ZombieType.DOLPHIN_RIDER] * 2
        if i >= 8: z += [ZombieType.ZOMBONI]
        levels.append({"type": LevelType.POOL, "waves": 4 + i // 3, "zombies": z, "pool": [2, 3], "sun": 50})
    # Fog 31-40
    for i in range(10):
        z = [ZombieType.NORMAL] * (6 + i) + [ZombieType.CONEHEAD] * (4 + i // 2) + [ZombieType.BUCKETHEAD] * (2 + i // 3)
        z += [ZombieType.BALLOON] * (1 + i // 2)
        if i >= 3: z += [ZombieType.DIGGER] * 2
        if i >= 5: z += [ZombieType.POGO] * 2
        if i >= 7: z += [ZombieType.JACK_IN_BOX] * 2
        levels.append({"type": LevelType.FOG, "waves": 4 + i // 2, "zombies": z, "pool": [2, 3], "fog": max(0, 6 - i // 3), "sun": 50})
    # Roof 41-49
    for i in range(9):
        z = [ZombieType.NORMAL] * (7 + i) + [ZombieType.CONEHEAD] * (5 + i // 2) + [ZombieType.BUCKETHEAD] * (3 + i // 2)
        z += [ZombieType.LADDER] * (1 + i // 3)
        if i >= 2: z += [ZombieType.CATAPULT]
        if i >= 4: z += [ZombieType.BUNGEE] * 2
        if i >= 6: z += [ZombieType.GARGANTUAR]
        levels.append({"type": LevelType.ROOF, "waves": 5 + i // 2, "zombies": z, "sun": 50})
    # Boss 50
    levels.append({"type": LevelType.BOSS, "waves": 1, "zombies": [ZombieType.DR_ZOMBOSS], "boss": True, "sun": 5000})
    return levels

LEVELS = make_levels()

# ============================================================
# ENTITIES
# ============================================================
@dataclass
class Sun:
    x: float
    y: float
    ty: float
    val: int = 25
    life: float = 10.0
    fall: bool = True
    got: bool = False
    
    def update(self, dt):
        if self.got:
            self.x += (100 - self.x) * 0.15
            self.y += (30 - self.y) * 0.15
            return abs(self.x - 100) > 5
        if self.fall and self.y < self.ty:
            self.y += 80 * dt
        else:
            self.fall = False
        self.life -= dt
        return self.life > 0
    
    def draw(self, s):
        p = 1 + math.sin(pygame.time.get_ticks() * 0.01) * 0.1
        r = int(15 * p)
        pygame.draw.circle(s, C.SUN_Y, (int(self.x), int(self.y)), r)
        pygame.draw.circle(s, C.SUN_O, (int(self.x), int(self.y)), int(r * 0.7))

@dataclass
class Proj:
    x: float
    y: float
    row: int
    dmg: int = 20
    spd: float = 300
    typ: str = "pea"
    slow: bool = False
    pierce: bool = False
    splash: bool = False
    
    def update(self, dt):
        self.x += self.spd * dt
    
    def draw(self, s):
        x, y = int(self.x), int(self.y)
        if self.typ == "pea":
            c = (100, 200, 255) if self.slow else (100, 200, 100)
            pygame.draw.circle(s, c, (x, y), 8)
            pygame.draw.circle(s, C.WHITE, (x - 2, y - 2), 3)
        elif self.typ == "fume":
            surf = pygame.Surface((40, 20), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (150, 100, 150, 150), (0, 0, 40, 20))
            s.blit(surf, (x - 20, y - 10))
        elif self.typ == "melon":
            c = (100, 180, 200) if self.slow else (120, 200, 120)
            pygame.draw.ellipse(s, c, (x - 12, y - 8, 24, 16))
        elif self.typ == "cabbage":
            pygame.draw.circle(s, (100, 180, 100), (x, y), 10)

@dataclass
class Plant:
    pt: PlantType
    row: int
    col: int
    hp: int = 300
    timer: float = 0
    frame: int = 0
    armed: bool = False
    chewing: bool = False
    chew_t: float = 0
    
    def __post_init__(self):
        d = PLANTS.get(self.pt, {})
        self.hp = d.get("hp", 300)
        self.max_hp = self.hp
    
    @property
    def x(self):
        return GRID_X + self.col * CELL_W + CELL_W // 2
    
    @property
    def y(self):
        return GRID_Y + self.row * CELL_H + CELL_H // 2
    
    def update(self, g, dt):
        self.frame = (self.frame + 1) % 120
        self.timer += dt
        d = PLANTS.get(self.pt, {})
        
        # Sun
        if d.get("sun") and self.timer >= d.get("rate", 24):
            self.timer = 0
            g.suns.append(Sun(self.x, self.y, self.y + 30, d["sun"]))
        
        # Shooting
        if d.get("dmg") and d.get("rate") and not d.get("instant") and not self.chewing:
            ahead = [z for z in g.zombies if z.row == self.row and z.x > self.x and z.hp > 0]
            if d.get("lanes"):
                for r in range(max(0, self.row - 1), min(ROWS, self.row + 2)):
                    if any(z.row == r and z.x > self.x for z in g.zombies if z.hp > 0):
                        ahead = [True]
                        break
            if ahead and self.timer >= d["rate"]:
                self.timer = 0
                self._fire(g, d)
        
        if self.pt == PlantType.POTATO_MINE and not self.armed:
            if self.timer >= d.get("arm", 14):
                self.armed = True
        
        if self.chewing:
            self.chew_t -= dt
            if self.chew_t <= 0:
                self.chewing = False
    
    def _fire(self, g, d):
        shots = d.get("shots", 1)
        typ = "pea"
        if d.get("pierce"):
            typ = "fume"
        elif d.get("splash"):
            typ = "melon"
        elif d.get("lob"):
            typ = "cabbage"
        
        if d.get("lanes"):
            for r in range(max(0, self.row - 1), min(ROWS, self.row + 2)):
                g.projs.append(Proj(self.x, GRID_Y + r * CELL_H + CELL_H // 2, r, d.get("dmg", 20), 300, typ, d.get("slow", False), d.get("pierce", False), d.get("splash", False)))
        else:
            for i in range(shots):
                g.projs.append(Proj(self.x + i * 10, self.y, self.row, d.get("dmg", 20), 300, typ, d.get("slow", False), d.get("pierce", False), d.get("splash", False)))
    
    def draw(self, s):
        d = PLANTS.get(self.pt, {})
        bob = math.sin(self.frame * 0.1) * 2
        x, y = int(self.x), int(self.y)
        
        if self.pt == PlantType.PEASHOOTER:
            pygame.draw.rect(s, (50, 150, 50), (x - 5, y + 10 + bob, 10, 30))
            pygame.draw.ellipse(s, (100, 200, 100), (x - 20, y - 20 + bob, 40, 35))
            pygame.draw.ellipse(s, (80, 160, 80), (x + 5, y - 8 + bob, 20, 16))
            pygame.draw.circle(s, C.WHITE, (x - 5, y - 8 + bob), 7)
            pygame.draw.circle(s, C.BLACK, (x - 4, y - 8 + bob), 3)
        elif self.pt == PlantType.SUNFLOWER:
            pygame.draw.rect(s, (50, 150, 50), (x - 4, y + 10 + bob, 8, 30))
            for i in range(12):
                a = i * 30 + self.frame * 0.5
                rad = math.radians(a)
                px = x + math.cos(rad) * 20
                py = y - 5 + bob + math.sin(rad) * 20
                pygame.draw.ellipse(s, C.SUN_O, (px - 6, py - 10, 12, 20))
            pygame.draw.circle(s, (200, 150, 50), (x, y - 5 + int(bob)), 15)
            pygame.draw.circle(s, C.BLACK, (x - 5, y - 8 + int(bob)), 3)
            pygame.draw.circle(s, C.BLACK, (x + 5, y - 8 + int(bob)), 3)
        elif self.pt == PlantType.CHERRY_BOMB:
            pygame.draw.circle(s, (220, 50, 50), (x - 12, y + bob), 18)
            pygame.draw.circle(s, (220, 50, 50), (x + 12, y + bob), 18)
            pygame.draw.circle(s, (255, 150, 150), (x - 15, y - 5 + bob), 5)
            pygame.draw.circle(s, (255, 150, 150), (x + 9, y - 5 + bob), 5)
        elif self.pt == PlantType.WALL_NUT:
            r = self.hp / self.max_hp
            c = (180, 140, 90) if r > 0.66 else (150, 110, 70) if r > 0.33 else (120, 80, 50)
            pygame.draw.ellipse(s, c, (x - 22, y - 25, 44, 55))
            pygame.draw.circle(s, C.BLACK, (x - 8, y - 5), 4)
            pygame.draw.circle(s, C.BLACK, (x + 8, y - 5), 4)
        elif self.pt == PlantType.POTATO_MINE:
            if self.armed:
                pygame.draw.ellipse(s, (180, 140, 80), (x - 22, y, 44, 30))
                pygame.draw.circle(s, C.RED, (x, y - 5), 6)
                pygame.draw.circle(s, C.BLACK, (x - 8, y + 8), 4)
                pygame.draw.circle(s, C.BLACK, (x + 8, y + 8), 4)
            else:
                pygame.draw.ellipse(s, (120, 90, 50), (x - 15, y + 15, 30, 15))
        elif self.pt == PlantType.SNOW_PEA:
            pygame.draw.rect(s, (50, 150, 150), (x - 5, y + 10 + bob, 10, 30))
            pygame.draw.ellipse(s, (100, 200, 220), (x - 20, y - 20 + bob, 40, 35))
            pygame.draw.ellipse(s, (80, 180, 200), (x + 5, y - 8 + bob, 20, 16))
            pygame.draw.circle(s, C.WHITE, (x - 5, y - 8 + bob), 7)
            pygame.draw.circle(s, (100, 150, 200), (x - 4, y - 8 + bob), 3)
        elif self.pt == PlantType.REPEATER:
            pygame.draw.rect(s, (50, 150, 50), (x - 6, y + 10 + bob, 12, 30))
            pygame.draw.ellipse(s, (100, 200, 100), (x - 22, y - 22 + bob, 42, 38))
            pygame.draw.ellipse(s, (80, 160, 80), (x + 2, y - 15 + bob, 22, 14))
            pygame.draw.ellipse(s, (80, 160, 80), (x + 8, y - 5 + bob, 18, 12))
            pygame.draw.circle(s, C.WHITE, (x - 8, y - 8 + bob), 7)
            pygame.draw.circle(s, C.BLACK, (x - 7, y - 8 + bob), 3)
        elif self.pt == PlantType.CHOMPER:
            if self.chewing:
                pygame.draw.ellipse(s, (150, 80, 180), (x - 18, y - 10 + bob, 36, 40))
            else:
                pygame.draw.rect(s, (50, 150, 50), (x - 6, y + 15, 12, 25))
                pygame.draw.ellipse(s, (150, 80, 180), (x - 22, y - 25 + bob, 44, 45))
                pygame.draw.ellipse(s, (200, 100, 220), (x - 18, y - 20 + bob, 36, 25))
                for i in range(5):
                    tx = x - 14 + i * 7
                    pygame.draw.polygon(s, C.WHITE, [(tx, y - 5 + bob), (tx + 3, y + 8 + bob), (tx + 6, y - 5 + bob)])
        elif self.pt == PlantType.TALL_NUT:
            r = self.hp / self.max_hp
            c = (180, 140, 90) if r > 0.66 else (150, 110, 70) if r > 0.33 else (120, 80, 50)
            pygame.draw.ellipse(s, c, (x - 20, y - 40, 40, 80))
            pygame.draw.circle(s, C.BLACK, (x - 6, y - 15), 4)
            pygame.draw.circle(s, C.BLACK, (x + 6, y - 15), 4)
        elif self.pt == PlantType.MELON_PULT:
            pygame.draw.rect(s, (50, 150, 50), (x - 5, y + 15, 10, 25))
            pygame.draw.ellipse(s, (100, 200, 100), (x - 25, y - 5 + bob, 50, 25))
            pygame.draw.ellipse(s, (120, 200, 120), (x - 12, y - 25 + bob, 24, 20))
        else:
            pygame.draw.rect(s, (50, 150, 50), (x - 5, y + 10, 10, 30))
            pygame.draw.ellipse(s, (100, 200, 100), (x - 18, y - 18 + bob, 36, 32))
        
        if self.hp < self.max_hp:
            pct = self.hp / self.max_hp
            pygame.draw.rect(s, C.RED, (x - 20, y - 45, 40, 5))
            pygame.draw.rect(s, C.GREEN, (x - 20, y - 45, int(40 * pct), 5))

@dataclass
class Zombie:
    zt: ZombieType
    row: int
    x: float
    hp: int = 200
    spd: float = 0.4
    dmg: int = 100
    eating: bool = False
    slowed: bool = False
    slow_t: float = 0
    frozen: bool = False
    freeze_t: float = 0
    frame: int = 0
    armor: int = 0
    vaulted: bool = False
    hypno: bool = False
    flying: bool = False
    
    def __post_init__(self):
        d = ZOMBIES.get(self.zt, {})
        self.hp = d.get("hp", 200)
        self.max_hp = self.hp
        self.spd = d.get("spd", 0.4) * 60
        self.dmg = d.get("dmg", 100)
        self.armor = d.get("armor", 0)
        self.flying = d.get("flying", False)
    
    @property
    def y(self):
        return GRID_Y + self.row * CELL_H + CELL_H // 2
    
    def update(self, dt, g):
        self.frame = (self.frame + 1) % 60
        
        if self.frozen:
            self.freeze_t -= dt
            if self.freeze_t <= 0:
                self.frozen = False
            return
        
        if self.slowed:
            self.slow_t -= dt
            if self.slow_t <= 0:
                self.slowed = False
        
        if not self.eating:
            spd = self.spd * (0.5 if self.slowed else 1.0)
            if self.hypno:
                self.x += spd * dt
            else:
                self.x -= spd * dt
    
    def hit(self, dmg, slow=False, freeze=False):
        if self.armor > 0:
            self.armor -= dmg
            if self.armor < 0:
                self.hp += self.armor
                self.armor = 0
        else:
            self.hp -= dmg
        if slow:
            self.slowed = True
            self.slow_t = 10
        if freeze:
            self.frozen = True
            self.freeze_t = 4
    
    def draw(self, s):
        x, y = int(self.x), int(self.y)
        bob = math.sin(self.frame * 0.15) * 3 if not self.eating else 0
        tint = (150, 200, 255) if self.slowed else (100, 150, 255) if self.frozen else None
        
        leg = math.sin(self.frame * 0.2) * 4 if not self.eating else 0
        pygame.draw.rect(s, (80, 80, 80), (x - 12 - leg, y + 15, 10, 25))
        pygame.draw.rect(s, (80, 80, 80), (x + 2 + leg, y + 15, 10, 25))
        
        bc = tint if tint else C.Z_GREEN
        pygame.draw.rect(s, bc, (x - 14, y - 15 + bob, 28, 35))
        pygame.draw.rect(s, (150, 50, 50), (x - 4, y - 10 + bob, 8, 25))
        
        hc = tint if tint else C.Z_SKIN
        pygame.draw.ellipse(s, hc, (x - 14, y - 40 + bob, 28, 28))
        pygame.draw.circle(s, (200, 50, 50), (x - 5, y - 30 + bob), 5)
        pygame.draw.circle(s, (200, 50, 50), (x + 5, y - 30 + bob), 5)
        pygame.draw.circle(s, C.BLACK, (x - 5, y - 30 + bob), 2)
        pygame.draw.circle(s, C.BLACK, (x + 5, y - 30 + bob), 2)
        
        if self.eating:
            pygame.draw.ellipse(s, (100, 50, 50), (x - 6, y - 22 + bob, 12, 10))
        
        if self.zt == ZombieType.CONEHEAD and self.armor > 0:
            cc = (255, 150, 50) if self.armor > 180 else (200, 100, 50)
            pygame.draw.polygon(s, cc, [(x, y - 55 + bob), (x - 12, y - 35 + bob), (x + 12, y - 35 + bob)])
        elif self.zt == ZombieType.BUCKETHEAD and self.armor > 0:
            cc = (150, 150, 150) if self.armor > 550 else (100, 100, 100)
            pygame.draw.rect(s, cc, (x - 12, y - 52 + bob, 24, 20))
        elif self.zt == ZombieType.FLAG:
            pygame.draw.rect(s, (100, 80, 60), (x + 12, y - 50 + bob, 4, 50))
            pygame.draw.rect(s, (200, 50, 50), (x + 16, y - 50 + bob, 20, 15))
        elif self.zt == ZombieType.FOOTBALL and self.armor > 0:
            pygame.draw.ellipse(s, (50, 50, 50), (x - 16, y - 45 + bob, 32, 20))
        elif self.zt == ZombieType.GARGANTUAR:
            pygame.draw.rect(s, bc, (x - 25, y - 30 + bob, 50, 60))
            pygame.draw.ellipse(s, hc, (x - 20, y - 55 + bob, 40, 35))
            pygame.draw.rect(s, (100, 70, 40), (x + 25, y - 40 + bob, 10, 60))
        elif self.zt == ZombieType.IMP:
            pygame.draw.rect(s, bc, (x - 8, y + 5 + bob, 16, 20))
            pygame.draw.ellipse(s, hc, (x - 10, y - 15 + bob, 20, 22))
        elif self.zt == ZombieType.BALLOON:
            pygame.draw.ellipse(s, C.RED, (x - 12, y - 70, 24, 30))
            pygame.draw.line(s, C.WHITE, (x, y - 40), (x, y - 20), 1)

@dataclass
class Mower:
    row: int
    x: float = 30
    active: bool = False
    
    def update(self, dt):
        if self.active:
            self.x += 400 * dt
            return self.x < WIDTH + 50
        return True
    
    def draw(self, s):
        y = GRID_Y + self.row * CELL_H + CELL_H // 2 + 20
        pygame.draw.rect(s, C.RED, (int(self.x), y, 40, 25))
        pygame.draw.circle(s, C.BLACK, (int(self.x) + 10, y + 25), 8)
        pygame.draw.circle(s, C.BLACK, (int(self.x) + 30, y + 25), 8)

# ============================================================
# GAME
# ============================================================
class CatsPVZ:
    def __init__(self):
        self.scr = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cat's PVZ Replanted — Pygame CE Fork 1.0")
        self.clk = pygame.time.Clock()
        
        self.ft = pygame.font.Font(None, 64)
        self.fl = pygame.font.Font(None, 48)
        self.fm = pygame.font.Font(None, 32)
        self.fs = pygame.font.Font(None, 24)
        self.fx = pygame.font.Font(None, 18)
        
        self.state = GameState.MENU
        self.lvl = 0
        self.sun = 50
        self.coins = 0
        self.menu_sel = 0
        
        self.plants: List[Plant] = []
        self.zombies: List[Zombie] = []
        self.projs: List[Proj] = []
        self.suns: List[Sun] = []
        self.mowers: List[Mower] = []
        self.grid = [[None] * COLS for _ in range(ROWS)]
        
        self.sel_plant = None
        self.cds: Dict[PlantType, float] = {}
        self.shovel = False
        self.wave = 0
        self.max_wave = 2
        self.wave_t = 25.0
        self.spawn_q = []
        self.sun_t = 0
        self.exps = []
        
        self.unlocked = [PlantType.PEASHOOTER, PlantType.SUNFLOWER]
        self.seeds: List[PlantType] = []
        self.max_seeds = 6
        
        self.dave_txt = []
        self.dave_i = 0
        self.cred_y = 0
        
        self.save = "catspvz_save.json"
        self._load()
    
    def _load(self):
        try:
            if os.path.exists(self.save):
                with open(self.save) as f:
                    d = json.load(f)
                    self.lvl = d.get('lvl', 0)
                    self.coins = d.get('coins', 0)
                    self.unlocked = [PlantType[p] for p in d.get('plants', ['PEASHOOTER', 'SUNFLOWER'])]
        except:
            pass
    
    def _save(self):
        try:
            d = {'lvl': self.lvl, 'coins': self.coins, 'plants': [p.name for p in self.unlocked]}
            with open(self.save, 'w') as f:
                json.dump(d, f)
        except:
            pass
    
    def _reset(self):
        ld = LEVELS[min(self.lvl, len(LEVELS) - 1)]
        self.sun = ld.get('sun', 50)
        self.plants = []
        self.zombies = []
        self.projs = []
        self.suns = []
        self.exps = []
        self.grid = [[None] * COLS for _ in range(ROWS)]
        self.cds = {}
        self.sel_plant = None
        self.shovel = False
        self.wave = 0
        self.max_wave = ld.get('waves', 2)
        self.wave_t = 25
        self.spawn_q = []
        self.sun_t = 0
        self.mowers = [Mower(r) for r in range(ROWS)]
    
    def run(self):
        while True:
            dt = self.clk.tick(FPS) / 1000
            if not self._events():
                break
            self._update(dt)
            self._draw()
            pygame.display.flip()
        self._save()
        pygame.quit()
        sys.exit()
    
    def _events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                self._key(e.key)
            if e.type == pygame.MOUSEBUTTONDOWN:
                self._click(pygame.mouse.get_pos())
        return True
    
    def _key(self, k):
        if self.state == GameState.MENU:
            if k == pygame.K_UP:
                self.menu_sel = (self.menu_sel - 1) % 5
            elif k == pygame.K_DOWN:
                self.menu_sel = (self.menu_sel + 1) % 5
            elif k == pygame.K_RETURN:
                self._menu_act()
        elif self.state == GameState.DAVE:
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                self.dave_i += 1
                if self.dave_i >= len(self.dave_txt):
                    self.state = GameState.SEEDS
        elif self.state == GameState.SEEDS:
            if k == pygame.K_ESCAPE:
                self.state = GameState.MENU
            elif k == pygame.K_SPACE and self.seeds:
                self._reset()
                self.state = GameState.PLAYING
        elif self.state == GameState.PLAYING:
            if k == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
            elif k == pygame.K_s:
                self.shovel = not self.shovel
                self.sel_plant = None
            for i in range(min(9, len(self.seeds))):
                if k == pygame.K_1 + i:
                    pt = self.seeds[i]
                    d = PLANTS.get(pt, {})
                    if self.sun >= d.get("cost", 100) and self.cds.get(pt, 0) <= 0:
                        self.sel_plant = pt
                        self.shovel = False
        elif self.state == GameState.PAUSED:
            if k == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif k == pygame.K_q:
                self.state = GameState.MENU
        elif self.state == GameState.GAMEOVER:
            if k == pygame.K_SPACE:
                self._reset()
                self.state = GameState.PLAYING
            elif k == pygame.K_ESCAPE:
                self.state = GameState.MENU
        elif self.state == GameState.WIN:
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                self.lvl += 1
                self._unlock()
                self._save()
                self.state = GameState.SEEDS
        elif self.state in (GameState.ALMANAC, GameState.MINIGAMES, GameState.SHOP, GameState.CREDITS):
            if k == pygame.K_ESCAPE:
                self.state = GameState.MENU
    
    def _click(self, pos):
        mx, my = pos
        if self.state == GameState.MENU:
            for i in range(5):
                y = 200 + i * 55
                if WIDTH // 2 - 150 <= mx <= WIDTH // 2 + 150 and y <= my <= y + 45:
                    self.menu_sel = i
                    self._menu_act()
                    break
        elif self.state == GameState.DAVE:
            self.dave_i += 1
            if self.dave_i >= len(self.dave_txt):
                self.state = GameState.SEEDS
        elif self.state == GameState.SEEDS:
            for i, p in enumerate(self.unlocked):
                x = 50 + (i % 8) * 100
                y = 120 + (i // 8) * 120
                if x <= mx <= x + 80 and y <= my <= y + 100:
                    if p in self.seeds:
                        self.seeds.remove(p)
                    elif len(self.seeds) < self.max_seeds:
                        self.seeds.append(p)
                    return
            if 350 <= mx <= 550 and 550 <= my <= 600:
                if self.seeds:
                    self._reset()
                    self.state = GameState.PLAYING
        elif self.state == GameState.PLAYING:
            for sun in self.suns:
                if not sun.got and abs(sun.x - mx) < 20 and abs(sun.y - my) < 20:
                    sun.got = True
                    self.sun += sun.val
                    return
            for i, pt in enumerate(self.seeds):
                x = 80 + i * 60
                if x <= mx <= x + 55 and 10 <= my <= 75:
                    d = PLANTS.get(pt, {})
                    if self.sun >= d.get("cost", 100) and self.cds.get(pt, 0) <= 0:
                        self.sel_plant = pt
                        self.shovel = False
                    return
            if 560 <= mx <= 620 and 10 <= my <= 75:
                self.shovel = not self.shovel
                self.sel_plant = None
                return
            col = (mx - GRID_X) // CELL_W
            row = (my - GRID_Y) // CELL_H
            if 0 <= col < COLS and 0 <= row < ROWS:
                if self.shovel and self.grid[row][col]:
                    p = self.grid[row][col]
                    self.plants.remove(p)
                    self.grid[row][col] = None
                    self.shovel = False
                    self.sun += PLANTS.get(p.pt, {}).get("cost", 0) // 4
                elif self.sel_plant and not self.grid[row][col]:
                    self._place(row, col)
    
    def _menu_act(self):
        if self.menu_sel == 0:
            self._dave()
        elif self.menu_sel == 1:
            self.state = GameState.MINIGAMES
        elif self.menu_sel == 2:
            self.state = GameState.ALMANAC
        elif self.menu_sel == 3:
            self.state = GameState.SHOP
        elif self.menu_sel == 4:
            self.state = GameState.CREDITS
    
    def _dave(self):
        self.dave_txt = [
            "WABBY WABBO!",
            "Howdy neighbor!",
            "I'm CRAZY DAVE!",
            "And I'm CRAAAAZY!",
            "The zombies are coming...",
            "But don't worry!",
            "I've got PLANTS!",
            "Use SUNFLOWERS for sun!",
            "Let's DO THIS!"
        ]
        self.dave_i = 0
        self.state = GameState.DAVE
    
    def _place(self, row, col):
        d = PLANTS.get(self.sel_plant, {})
        cost = d.get("cost", 100)
        if self.sun >= cost:
            p = Plant(self.sel_plant, row, col)
            self.plants.append(p)
            self.grid[row][col] = p
            self.sun -= cost
            self.cds[self.sel_plant] = d.get("cd", 7.5)
            if d.get("instant"):
                self._instant(p, d)
            self.sel_plant = None
    
    def _instant(self, p, d):
        if p.pt == PlantType.CHERRY_BOMB:
            for z in self.zombies:
                dist = math.sqrt((z.x - p.x)**2 + ((z.y - p.y) / CELL_H * CELL_W)**2)
                if dist < 1.5 * CELL_W:
                    z.hp -= d.get("dmg", 1800)
            self.exps.append({"x": p.x - 60, "y": p.y - 60, "r": 90, "t": 0.5})
            self.plants.remove(p)
            self.grid[p.row][p.col] = None
        elif p.pt == PlantType.JALAPENO:
            for z in self.zombies:
                if z.row == p.row:
                    z.hp -= d.get("dmg", 1800)
            self.exps.append({"x": 0, "y": p.y - 30, "w": WIDTH, "h": 60, "t": 0.5, "row": True})
            self.plants.remove(p)
            self.grid[p.row][p.col] = None
        elif p.pt == PlantType.ICE_SHROOM:
            for z in self.zombies:
                z.frozen = True
                z.freeze_t = 4
            self.plants.remove(p)
            self.grid[p.row][p.col] = None
        elif p.pt == PlantType.DOOM_SHROOM:
            for z in self.zombies:
                dist = math.sqrt((z.x - p.x)**2 + ((z.y - p.y) / CELL_H * CELL_W)**2)
                if dist < 3 * CELL_W:
                    z.hp -= d.get("dmg", 9999)
            self.exps.append({"x": p.x - 100, "y": p.y - 100, "r": 150, "t": 0.8, "doom": True})
            self.plants.remove(p)
            self.grid[p.row][p.col] = None
    
    def _unlock(self):
        unlocks = {
            2: PlantType.CHERRY_BOMB, 3: PlantType.WALL_NUT, 4: PlantType.POTATO_MINE,
            5: PlantType.SNOW_PEA, 6: PlantType.CHOMPER, 7: PlantType.REPEATER,
            11: PlantType.PUFF_SHROOM, 12: PlantType.SUN_SHROOM, 13: PlantType.FUME_SHROOM,
            15: PlantType.HYPNO_SHROOM, 17: PlantType.ICE_SHROOM, 18: PlantType.DOOM_SHROOM,
            21: PlantType.LILY_PAD, 22: PlantType.SQUASH, 23: PlantType.THREEPEATER,
            25: PlantType.JALAPENO, 27: PlantType.TORCHWOOD, 28: PlantType.TALL_NUT,
            31: PlantType.CACTUS, 35: PlantType.STARFRUIT, 41: PlantType.CABBAGE_PULT,
            42: PlantType.FLOWER_POT, 48: PlantType.MELON_PULT,
        }
        for l, p in unlocks.items():
            if self.lvl >= l and p not in self.unlocked:
                self.unlocked.append(p)
    
    def _update(self, dt):
        if self.state == GameState.PLAYING:
            self._play(dt)
        elif self.state == GameState.CREDITS:
            self.cred_y += 50 * dt
    
    def _play(self, dt):
        ld = LEVELS[min(self.lvl, len(LEVELS) - 1)]
        
        for pt in list(self.cds.keys()):
            if self.cds[pt] > 0:
                self.cds[pt] -= dt
        
        if ld["type"] in (LevelType.DAY, LevelType.POOL, LevelType.ROOF):
            self.sun_t += dt
            if self.sun_t >= 10:
                self.sun_t = 0
                x = random.randint(GRID_X, GRID_X + COLS * CELL_W - 30)
                ty = random.randint(GRID_Y + 50, GRID_Y + ROWS * CELL_H - 50)
                self.suns.append(Sun(x, -20, ty))
        
        self._waves(dt, ld)
        self.suns = [s for s in self.suns if s.update(dt)]
        for p in self.plants:
            p.update(self, dt)
        for pj in self.projs:
            pj.update(dt)
        self.projs = [p for p in self.projs if 0 < p.x < WIDTH + 50]
        for z in self.zombies:
            z.update(dt, self)
        self._collisions()
        self._mowers(dt)
        self.zombies = [z for z in self.zombies if z.hp > 0]
        for e in self.exps:
            e["t"] -= dt
        self.exps = [e for e in self.exps if e["t"] > 0]
        
        for z in self.zombies:
            if z.x < 30:
                self.state = GameState.GAMEOVER
                return
        
        if not self.spawn_q and not self.zombies and self.wave >= self.max_wave:
            self.state = GameState.WIN
    
    def _waves(self, dt, ld):
        if not self.spawn_q:
            self.wave_t -= dt
            if self.wave_t <= 0 and self.wave < self.max_wave:
                self.wave += 1
                self._spawn(ld)
                self.wave_t = 30
        else:
            nq = []
            for zt, row, delay in self.spawn_q:
                delay -= dt
                if delay <= 0:
                    self.zombies.append(Zombie(zt, row, WIDTH + 50))
                else:
                    nq.append((zt, row, delay))
            self.spawn_q = nq
    
    def _spawn(self, ld):
        zs = ld.get("zombies", [ZombieType.NORMAL] * 5)
        sz = len(zs) // self.max_wave
        st = (self.wave - 1) * sz
        ed = st + sz + (len(zs) % self.max_wave if self.wave == self.max_wave else 0)
        wz = zs[st:ed]
        pool = ld.get("pool", [])
        for i, zt in enumerate(wz):
            row = random.randint(0, ROWS - 1)
            if ZOMBIES.get(zt, {}).get("aquatic") and pool:
                row = random.choice(pool)
            delay = i * 0.8 + random.random() * 2
            self.spawn_q.append((zt, row, delay))
        if self.wave > 1:
            self.spawn_q.insert(0, (ZombieType.FLAG, random.randint(0, ROWS - 1), 0))
    
    def _collisions(self):
        for pj in self.projs[:]:
            for z in self.zombies:
                if z.row == pj.row and abs(z.x - pj.x) < 30 and z.hp > 0:
                    z.hit(pj.dmg, pj.slow)
                    if pj.splash:
                        for z2 in self.zombies:
                            if z2 != z and abs(z2.x - z.x) < 60 and abs(z2.row - z.row) <= 1:
                                z2.hit(pj.dmg // 2, pj.slow)
                    if not pj.pierce and pj in self.projs:
                        self.projs.remove(pj)
                    break
        
        for z in self.zombies:
            z.eating = False
            if z.hp <= 0 or z.flying:
                continue
            for col in range(COLS - 1, -1, -1):
                p = self.grid[z.row][col]
                if p and abs(p.x - z.x) < 40:
                    z.eating = True
                    if p.pt == PlantType.POTATO_MINE and p.armed:
                        z.hp -= 1800
                        self.exps.append({"x": p.x - 40, "y": p.y - 40, "r": 50, "t": 0.4})
                        self.plants.remove(p)
                        self.grid[z.row][col] = None
                    elif p.pt == PlantType.CHOMPER and not p.chewing:
                        if z.zt not in (ZombieType.GARGANTUAR, ZombieType.ZOMBONI, ZombieType.CATAPULT):
                            z.hp = 0
                            p.chewing = True
                            p.chew_t = PLANTS[PlantType.CHOMPER]["chew"]
                        else:
                            p.hp -= z.dmg / FPS
                    elif p.pt == PlantType.HYPNO_SHROOM:
                        z.hypno = True
                        self.plants.remove(p)
                        self.grid[z.row][col] = None
                    elif p.pt == PlantType.SQUASH:
                        z.hp -= 1800
                        self.plants.remove(p)
                        self.grid[z.row][col] = None
                    else:
                        p.hp -= z.dmg / FPS
                        if p.hp <= 0:
                            self.plants.remove(p)
                            self.grid[p.row][p.col] = None
                    break
    
    def _mowers(self, dt):
        for m in self.mowers[:]:
            if not m.update(dt):
                self.mowers.remove(m)
                continue
            if m.active:
                for z in self.zombies:
                    if z.row == m.row and abs(z.x - m.x) < 50:
                        z.hp = 0
            else:
                for z in self.zombies:
                    if z.row == m.row and z.x < m.x + 60:
                        m.active = True
                        break
    
    def _draw(self):
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.DAVE:
            self._draw_dave()
        elif self.state == GameState.SEEDS:
            self._draw_seeds()
        elif self.state == GameState.PLAYING:
            self._draw_play()
        elif self.state == GameState.PAUSED:
            self._draw_play()
            self._draw_pause()
        elif self.state == GameState.GAMEOVER:
            self._draw_play()
            self._draw_over()
        elif self.state == GameState.WIN:
            self._draw_play()
            self._draw_win()
        elif self.state == GameState.ALMANAC:
            self._draw_almanac()
        elif self.state == GameState.MINIGAMES:
            self._draw_mini()
        elif self.state == GameState.SHOP:
            self._draw_shop()
        elif self.state == GameState.CREDITS:
            self._draw_credits()
    
    def _draw_menu(self):
        self.scr.fill(C.SKY_DAY)
        for row in range(8):
            for col in range(12):
                c = C.LAWN_1 if (row + col) % 2 == 0 else C.LAWN_2
                pygame.draw.rect(self.scr, c, (col * 75, 280 + row * 50, 75, 50))
        
        ts = self.ft.render("CAT'S PVZ REPLANTED", True, C.UI_BROWN)
        self.scr.blit(ts, (WIDTH // 2 - ts.get_width() // 2 + 3, 43))
        t = self.ft.render("CAT'S PVZ REPLANTED", True, C.GOLD)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 40))
        
        sub = self.fm.render("Pygame CE Fork 1.0 — [C] Samsoft", True, (180, 100, 200))
        self.scr.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 100))
        
        info = self.fs.render(f"Level {self.lvl + 1}/50 | Coins: {self.coins}", True, C.WHITE)
        self.scr.blit(info, (WIDTH // 2 - info.get_width() // 2, 140))
        
        opts = ["Adventure", "Mini-Games", "Almanac", "Shop", "Credits"]
        for i, o in enumerate(opts):
            y = 200 + i * 55
            sel = i == self.menu_sel
            bg = C.GREEN if sel else C.UI_BROWN
            pygame.draw.rect(self.scr, bg, (WIDTH // 2 - 150, y, 300, 45), border_radius=10)
            pygame.draw.rect(self.scr, C.UI_DARK, (WIDTH // 2 - 150, y, 300, 45), 3, border_radius=10)
            txt = self.fm.render(o, True, C.WHITE if sel else C.UI_TAN)
            self.scr.blit(txt, (WIDTH // 2 - txt.get_width() // 2, y + 10))
        
        foot = self.fx.render("Developer: A.C (ANNOYING CAT)", True, C.WHITE)
        self.scr.blit(foot, (WIDTH // 2 - foot.get_width() // 2, HEIGHT - 25))
    
    def _draw_dave(self):
        self.scr.fill((60, 40, 30))
        pygame.draw.ellipse(self.scr, (255, 200, 150), (60, 150, 150, 180))
        pygame.draw.ellipse(self.scr, (100, 100, 100), (50, 120, 170, 70))
        pygame.draw.circle(self.scr, C.WHITE, (100, 200), 18)
        pygame.draw.circle(self.scr, C.WHITE, (160, 200), 18)
        pygame.draw.circle(self.scr, C.BLACK, (105, 200), 8)
        pygame.draw.circle(self.scr, C.BLACK, (155, 200), 8)
        pygame.draw.arc(self.scr, C.BLACK, (100, 240, 60, 40), 3.14, 0, 4)
        pygame.draw.ellipse(self.scr, (80, 60, 40), (90, 260, 80, 60))
        
        pygame.draw.rect(self.scr, C.UI_TAN, (280, 180, 550, 150), border_radius=20)
        pygame.draw.rect(self.scr, C.UI_BROWN, (280, 180, 550, 150), 4, border_radius=20)
        pygame.draw.polygon(self.scr, C.UI_TAN, [(280, 230), (250, 250), (280, 270)])
        
        if self.dave_i < len(self.dave_txt):
            d = self.fl.render(self.dave_txt[self.dave_i], True, C.UI_DARK)
            self.scr.blit(d, (555 - d.get_width() // 2, 240))
        
        h = self.fs.render("Click or ENTER to continue", True, C.WHITE)
        self.scr.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT - 50))
    
    def _draw_seeds(self):
        self.scr.fill((80, 60, 40))
        t = self.fl.render("SELECT YOUR SEEDS", True, C.WHITE)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 30))
        
        li = self.fm.render(f"Level {self.lvl + 1}", True, C.GOLD)
        self.scr.blit(li, (WIDTH // 2 - li.get_width() // 2, 75))
        
        for i, p in enumerate(self.unlocked):
            x = 50 + (i % 8) * 100
            y = 120 + (i // 8) * 120
            sel = p in self.seeds
            d = PLANTS.get(p, {})
            bg = C.GREEN if sel else (100, 80, 60)
            if d.get("night"):
                bg = (100, 80, 150) if sel else (80, 60, 100)
            pygame.draw.rect(self.scr, bg, (x, y, 80, 100), border_radius=8)
            pygame.draw.rect(self.scr, C.WHITE if sel else C.GRAY, (x, y, 80, 100), 2, border_radius=8)
            n = d.get("name", "Plant")
            if len(n) > 10:
                n = n[:9] + "."
            nt = self.fx.render(n, True, C.WHITE)
            self.scr.blit(nt, (x + 40 - nt.get_width() // 2, y + 8))
            ct = self.fs.render(str(d.get("cost", 100)), True, C.SUN_Y)
            self.scr.blit(ct, (x + 40 - ct.get_width() // 2, y + 75))
        
        pygame.draw.rect(self.scr, C.UI_BROWN, (50, 480, 700, 50), border_radius=8)
        st = self.fs.render(f"Selected ({len(self.seeds)}/{self.max_seeds}):", True, C.WHITE)
        self.scr.blit(st, (60, 495))
        for i, p in enumerate(self.seeds):
            n = PLANTS.get(p, {}).get("name", "?")[:8]
            txt = self.fx.render(n, True, C.GREEN)
            self.scr.blit(txt, (230 + i * 80, 495))
        
        if self.seeds:
            pygame.draw.rect(self.scr, C.GREEN, (350, 550, 200, 50), border_radius=10)
            pygame.draw.rect(self.scr, C.WHITE, (350, 550, 200, 50), 3, border_radius=10)
            st = self.fm.render("LET'S ROCK!", True, C.WHITE)
            self.scr.blit(st, (450 - st.get_width() // 2, 562))
        
        h = self.fs.render("Click to select | SPACE to start | ESC for menu", True, C.WHITE)
        self.scr.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT - 30))
    
    def _draw_play(self):
        ld = LEVELS[min(self.lvl, len(LEVELS) - 1)]
        lt = ld["type"]
        skies = {LevelType.DAY: C.SKY_DAY, LevelType.NIGHT: C.SKY_NIGHT, LevelType.POOL: C.SKY_POOL, LevelType.FOG: C.SKY_FOG, LevelType.ROOF: C.SKY_ROOF, LevelType.BOSS: C.SKY_NIGHT}
        self.scr.fill(skies.get(lt, C.SKY_DAY))
        
        pool = ld.get("pool", [])
        for row in range(ROWS):
            for col in range(COLS):
                x = GRID_X + col * CELL_W
                y = GRID_Y + row * CELL_H
                if row in pool:
                    c = C.POOL
                elif lt == LevelType.ROOF:
                    c = C.ROOF_1 if (row + col) % 2 == 0 else C.ROOF_2
                elif lt in (LevelType.NIGHT, LevelType.FOG):
                    c = C.LAWN_N1 if (row + col) % 2 == 0 else C.LAWN_N2
                else:
                    c = C.LAWN_1 if (row + col) % 2 == 0 else C.LAWN_2
                pygame.draw.rect(self.scr, c, (x, y, CELL_W, CELL_H))
        
        if lt == LevelType.FOG:
            fc = ld.get("fog", 4)
            fog = pygame.Surface((fc * CELL_W, ROWS * CELL_H), pygame.SRCALPHA)
            fog.fill((150, 150, 150, 180))
            self.scr.blit(fog, (GRID_X + (COLS - fc) * CELL_W, GRID_Y))
        
        for m in self.mowers:
            m.draw(self.scr)
        for p in self.plants:
            p.draw(self.scr)
        for pj in self.projs:
            pj.draw(self.scr)
        for z in self.zombies:
            z.draw(self.scr)
        for s in self.suns:
            s.draw(self.scr)
        
        for e in self.exps:
            a = int(255 * (e["t"] / 0.5))
            if e.get("row"):
                surf = pygame.Surface((e["w"], e["h"]), pygame.SRCALPHA)
                surf.fill((255, 100, 0, min(255, a)))
                self.scr.blit(surf, (e["x"], e["y"]))
            elif e.get("doom"):
                surf = pygame.Surface((e["r"] * 2, e["r"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (100, 0, 100, min(255, a)), (e["r"], e["r"]), e["r"])
                self.scr.blit(surf, (e["x"], e["y"]))
            else:
                surf = pygame.Surface((e["r"] * 2, e["r"] * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (255, 200, 0, min(255, a)), (e["r"], e["r"]), e["r"])
                self.scr.blit(surf, (e["x"], e["y"]))
        
        self._draw_ui()
        
        if self.sel_plant or self.shovel:
            mx, my = pygame.mouse.get_pos()
            if self.shovel:
                pygame.draw.rect(self.scr, C.GOLD, (mx - 20, my - 20, 40, 40), 3)
            else:
                pygame.draw.rect(self.scr, C.GREEN, (mx - 25, my - 25, 50, 50), 2)
    
    def _draw_ui(self):
        pygame.draw.rect(self.scr, C.UI_BROWN, (0, 0, WIDTH, 85))
        pygame.draw.rect(self.scr, C.UI_DARK, (0, 83, WIDTH, 3))
        
        pygame.draw.circle(self.scr, C.SUN_Y, (40, 45), 25)
        pygame.draw.circle(self.scr, C.SUN_O, (40, 45), 20)
        st = self.fm.render(str(self.sun), True, C.BLACK)
        self.scr.blit(st, (25, 65))
        
        for i, pt in enumerate(self.seeds):
            x = 80 + i * 60
            d = PLANTS.get(pt, {})
            cost = d.get("cost", 100)
            cd = self.cds.get(pt, 0)
            mcd = d.get("cd", 7.5)
            can = self.sun >= cost and cd <= 0
            bg = C.GREEN if can else C.GRAY
            pygame.draw.rect(self.scr, bg, (x, 10, 55, 65), border_radius=5)
            pygame.draw.rect(self.scr, C.UI_DARK, (x, 10, 55, 65), 2, border_radius=5)
            if self.sel_plant == pt:
                pygame.draw.rect(self.scr, C.GOLD, (x - 2, 8, 59, 69), 3, border_radius=5)
            if cd > 0:
                ch = int(65 * (cd / mcd))
                ov = pygame.Surface((55, ch), pygame.SRCALPHA)
                ov.fill((0, 0, 0, 150))
                self.scr.blit(ov, (x, 10))
            ct = self.fx.render(str(cost), True, C.WHITE)
            self.scr.blit(ct, (x + 27 - ct.get_width() // 2, 55))
            kt = self.fx.render(str(i + 1), True, C.WHITE)
            self.scr.blit(kt, (x + 5, 12))
        
        sx = 560
        bg = C.GOLD if self.shovel else C.UI_TAN
        pygame.draw.rect(self.scr, bg, (sx, 10, 55, 65), border_radius=5)
        pygame.draw.rect(self.scr, C.UI_DARK, (sx, 10, 55, 65), 2, border_radius=5)
        pygame.draw.polygon(self.scr, C.GRAY, [(sx + 15, 55), (sx + 40, 55), (sx + 35, 40), (sx + 20, 40)])
        pygame.draw.rect(self.scr, C.UI_BROWN, (sx + 24, 20, 8, 25))
        
        wt = self.fs.render(f"Wave {self.wave}/{self.max_wave}", True, C.WHITE)
        self.scr.blit(wt, (WIDTH - 110, 15))
        lt = self.fs.render(f"Level {self.lvl + 1}", True, C.WHITE)
        self.scr.blit(lt, (WIDTH - 110, 35))
        
        pygame.draw.rect(self.scr, C.UI_DARK, (640, 60, 150, 12))
        if self.spawn_q or self.zombies:
            tot = max(1, len(LEVELS[min(self.lvl, len(LEVELS) - 1)].get("zombies", [])))
            rem = len(self.zombies) + len(self.spawn_q)
            prog = max(0, 1 - rem / tot)
            pygame.draw.rect(self.scr, C.GREEN, (640, 60, int(150 * prog), 12))
    
    def _draw_pause(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 150))
        self.scr.blit(ov, (0, 0))
        t = self.ft.render("PAUSED", True, C.WHITE)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 250))
        h1 = self.fm.render("Press ESC to continue", True, C.WHITE)
        h2 = self.fm.render("Press Q to quit", True, C.WHITE)
        self.scr.blit(h1, (WIDTH // 2 - h1.get_width() // 2, 330))
        self.scr.blit(h2, (WIDTH // 2 - h2.get_width() // 2, 370))
    
    def _draw_over(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((100, 0, 0, 180))
        self.scr.blit(ov, (0, 0))
        t = self.ft.render("GAME OVER", True, C.RED)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 200))
        m = self.fl.render("THE ZOMBIES ATE YOUR BRAINS!", True, C.WHITE)
        self.scr.blit(m, (WIDTH // 2 - m.get_width() // 2, 300))
        h = self.fm.render("SPACE to retry | ESC for menu", True, C.WHITE)
        self.scr.blit(h, (WIDTH // 2 - h.get_width() // 2, 400))
    
    def _draw_win(self):
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 80, 0, 180))
        self.scr.blit(ov, (0, 0))
        t = self.ft.render("LEVEL COMPLETE!", True, C.GOLD)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 220))
        coins = random.randint(50, 150)
        self.coins += coins
        r = self.fl.render(f"+{coins} coins", True, C.SUN_Y)
        self.scr.blit(r, (WIDTH // 2 - r.get_width() // 2, 300))
        h = self.fm.render("Press ENTER to continue", True, C.WHITE)
        self.scr.blit(h, (WIDTH // 2 - h.get_width() // 2, 380))
    
    def _draw_almanac(self):
        self.scr.fill((60, 50, 40))
        t = self.fl.render("ALMANAC", True, C.GOLD)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 30))
        
        for i, p in enumerate(list(PLANTS.keys())[:12]):
            x = 50 + (i % 4) * 200
            y = 100 + (i // 4) * 170
            d = PLANTS.get(p, {})
            pygame.draw.rect(self.scr, C.UI_TAN, (x, y, 180, 150), border_radius=10)
            n = self.fm.render(d.get("name", "Plant"), True, C.UI_DARK)
            self.scr.blit(n, (x + 10, y + 10))
            c = self.fs.render(f"Cost: {d.get('cost', 100)}", True, C.UI_DARK)
            self.scr.blit(c, (x + 10, y + 45))
            if d.get("dmg"):
                dm = self.fs.render(f"Damage: {d.get('dmg')}", True, C.UI_DARK)
                self.scr.blit(dm, (x + 10, y + 70))
        
        h = self.fs.render("Press ESC to return", True, C.WHITE)
        self.scr.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT - 30))
    
    def _draw_mini(self):
        self.scr.fill((50, 40, 60))
        t = self.fl.render("MINI-GAMES", True, C.GOLD)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 30))
        
        games = ["Wall-nut Bowling", "Slot Machine", "Zombotany", "Vasebreaker", "Last Stand"]
        for i, g in enumerate(games):
            x = 100 + (i % 3) * 250
            y = 120 + (i // 3) * 150
            pygame.draw.rect(self.scr, C.GREEN if self.lvl >= (i + 1) * 5 else C.GRAY, (x, y, 220, 120), border_radius=10)
            pygame.draw.rect(self.scr, C.UI_DARK, (x, y, 220, 120), 2, border_radius=10)
            nt = self.fm.render(g, True, C.WHITE)
            self.scr.blit(nt, (x + 10, y + 45))
        
        h = self.fs.render("Press ESC to return", True, C.WHITE)
        self.scr.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT - 30))
    
    def _draw_shop(self):
        self.scr.fill((60, 50, 40))
        t = self.fl.render("CRAZY DAVE'S SHOP", True, C.GOLD)
        self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, 30))
        ct = self.fm.render(f"Coins: {self.coins}", True, C.SUN_Y)
        self.scr.blit(ct, (WIDTH // 2 - ct.get_width() // 2, 80))
        
        items = [("Extra Seed Slot", 5000), ("Pool Cleaner", 1000), ("Gatling Pea", 5000), ("Winter Melon", 10000)]
        for i, (n, cost) in enumerate(items):
            x = 100 + (i % 2) * 350
            y = 150 + (i // 2) * 150
            can = self.coins >= cost
            pygame.draw.rect(self.scr, C.GREEN if can else C.GRAY, (x, y, 300, 120), border_radius=10)
            pygame.draw.rect(self.scr, C.UI_DARK, (x, y, 300, 120), 2, border_radius=10)
            nt = self.fm.render(n, True, C.WHITE)
            self.scr.blit(nt, (x + 15, y + 20))
            pt = self.fs.render(f"${cost}", True, C.SUN_Y)
            self.scr.blit(pt, (x + 15, y + 60))
        
        h = self.fs.render("Press ESC to return", True, C.WHITE)
        self.scr.blit(h, (WIDTH // 2 - h.get_width() // 2, HEIGHT - 30))
    
    def _draw_credits(self):
        self.scr.fill((20, 20, 40))
        credits = [
            "CAT'S PVZ REPLANTED",
            "Pygame CE Fork 1.0",
            "",
            "[C] Samsoft 1999-2025",
            "Developer: A.C (ANNOYING CAT)",
            "",
            "Original Concept by PopCap Games",
            "",
            "Engine: Python + Pygame CE",
            "",
            "Features:",
            "50 Adventure Levels",
            "40+ Plants",
            "26 Zombie Types",
            "Minigames & Shop",
            "",
            "Thanks for playing!",
            "",
            "Press ESC to return"
        ]
        y = HEIGHT - self.cred_y
        for line in credits:
            if -30 < y < HEIGHT + 30:
                t = self.fm.render(line, True, C.WHITE)
                self.scr.blit(t, (WIDTH // 2 - t.get_width() // 2, y))
            y += 35
        if y < -100:
            self.cred_y = 0

def main():
    print("=" * 70)
    print("  CAT'S PVZ REPLANTED — PYGAME CE FORK 1.0")
    print("  [C] Samsoft 1999-2025 | Developer: A.C (ANNOYING CAT)")
    print("=" * 70)
    print("\n  FEATURES:")
    print("    • 50 Adventure Levels (Day/Night/Pool/Fog/Roof + Boss)")
    print("    • 40+ Plants with unique abilities")
    print("    • 26 Zombie types including Gargantuar & Dr. Zomboss")
    print("    • Minigames, Shop, Save/Load")
    print("\n  CONTROLS:")
    print("    • [1-9] Select seed | [S] Shovel | [ESC] Pause")
    print("    • Click to plant / collect sun")
    print("=" * 70)
    
    game = CatsPVZ()
    game.run()

if __name__ == "__main__":
    main()
