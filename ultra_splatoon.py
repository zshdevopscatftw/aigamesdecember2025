#!/usr/bin/env python3
"""
Ultra!Splatoon 0.1 — Pygame Tech Demo
A Splatoon-inspired ink shooter with RPG elements
600x400 resolution
"""

import pygame
import math
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum, auto

# ============================================================================
# CONSTANTS
# ============================================================================
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Game grid (scaled down for performance)
GRID_W = 150
GRID_H = 100
SCALE = SCREEN_WIDTH / GRID_W

# Teams
TEAM_NONE = 0
TEAM_PLAYER = 1
TEAM_ENEMY = 2

# Colors
COLOR_BG = (14, 15, 18)
COLOR_WALL = (40, 42, 50)
COLOR_TEXT = (238, 238, 255)
COLOR_TEXT_DIM = (136, 136, 153)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

# Ink palettes (player, enemy)
PALETTES = [
    {"ink": (65, 163, 255), "dark": (27, 74, 136), "roller": (160, 210, 255)},
    {"ink": (255, 61, 110), "dark": (122, 27, 48), "roller": (255, 193, 208)},
    {"ink": (118, 255, 65), "dark": (42, 122, 27), "roller": (202, 255, 182)},
    {"ink": (255, 212, 65), "dark": (122, 94, 27), "roller": (255, 239, 177)},
    {"ink": (195, 65, 255), "dark": (74, 27, 122), "roller": (224, 160, 255)},
    {"ink": (255, 140, 65), "dark": (122, 61, 27), "roller": (255, 201, 160)},
]
ENEMY_COLOR = (255, 107, 138)


# ============================================================================
# GAME STATE
# ============================================================================
class GameState(Enum):
    BOOT_NINTENDO = auto()
    BOOT_SAMSOFT = auto()
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    WIN = auto()
    LOSE = auto()


# ============================================================================
# GAME DATA
# ============================================================================
@dataclass
class Player:
    x: float = GRID_W / 2
    y: float = GRID_H / 2
    vx: float = 0
    vy: float = 0
    angle: float = 0
    speed_base: float = 2.2
    hp: int = 100
    hp_max: int = 100
    ink: float = 100
    xp: int = 0
    xp_to: int = 100
    level: int = 1
    dash_cooldown: float = 0
    gear_tier: int = 0
    perks: dict = field(default_factory=lambda: {"ink_eff": 0, "swim_speed": 0, "bomb_power": 0})
    
    def reset(self):
        self.x = GRID_W / 2
        self.y = GRID_H / 2
        self.vx = 0
        self.vy = 0
        self.hp = self.hp_max
        self.ink = 100
        self.dash_cooldown = 0


@dataclass
class Enemy:
    x: float
    y: float
    hp: int = 40
    cooldown: float = 0
    target_x: float = GRID_W / 2
    target_y: float = GRID_H / 2
    dead: bool = False


@dataclass
class Bomb:
    x: float
    y: float
    vx: float
    vy: float
    team: int
    power: int
    timer: float = 0
    life: float = 0.6
    dead: bool = False


@dataclass
class Pellet:
    x: float
    y: float
    vx: float
    vy: float
    team: int
    timer: float = 0
    life: float = 0.2
    dead: bool = False


# ============================================================================
# SOUND SYSTEM (Simple beeps using pygame mixer)
# ============================================================================
class SoundSystem:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.enabled = True
    
    def beep(self, freq=440, duration=60, volume=0.3):
        if not self.enabled:
            return
        try:
            sample_rate = 22050
            n_samples = int(sample_rate * duration / 1000)
            buf = []
            for i in range(n_samples):
                t = i / sample_rate
                # Decay envelope
                env = max(0, 1 - (i / n_samples) * 2)
                val = int(32767 * volume * env * math.sin(2 * math.pi * freq * t))
                buf.append(max(-32767, min(32767, val)))
            
            # Create sound from buffer
            import array
            sound_buffer = array.array('h', buf)
            sound = pygame.mixer.Sound(buffer=sound_buffer)
            sound.play()
        except:
            pass
    
    def spray(self):
        self.beep(700, 40, 0.15)
    
    def thud(self):
        self.beep(120, 80, 0.2)
    
    def bomb(self):
        self.beep(60, 150, 0.25)
    
    def level_up(self):
        for i in range(4):
            pygame.time.set_timer(pygame.USEREVENT + i, i * 80 + 1, loops=1)
    
    def win(self):
        for i in range(6):
            pygame.time.set_timer(pygame.USEREVENT + 10 + i, i * 100 + 1, loops=1)
    
    def lose(self):
        self.beep(200, 300, 0.3)


# ============================================================================
# MAIN GAME CLASS
# ============================================================================
class UltraSplatoon:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Ultra!Splatoon 0.1")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        self.sound = SoundSystem()
        
        # Game state
        self.state = GameState.BOOT_NINTENDO
        self.state_timer = 0
        self.palette_index = 0
        
        # Ink grid
        self.ink_owner = [[TEAM_NONE] * GRID_H for _ in range(GRID_W)]
        self.ink_alpha = [[0.0] * GRID_H for _ in range(GRID_W)]
        self.walls = [[False] * GRID_H for _ in range(GRID_W)]
        
        # Entities
        self.player = Player()
        self.enemies: List[Enemy] = []
        self.bombs: List[Bomb] = []
        self.pellets: List[Pellet] = []
        
        # Match
        self.match_time = 0
        self.match_duration = 180
        self.splat_count = 0
        self.spawn_timer = 0
        
        # Input
        self.keys = {}
        self.mouse_pos = (0, 0)
        self.mouse_down = False
        self.mouse_right = False
        
        # Perk choices
        self.perk_choices = []
        
        # Toast message
        self.toast_text = ""
        self.toast_timer = 0
        
        # Pre-render ink surface for performance
        self.ink_surface = pygame.Surface((GRID_W, GRID_H))
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            
            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.keys[event.key] = True
                    self.handle_keydown(event.key)
                elif event.type == pygame.KEYUP:
                    self.keys[event.key] = False
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.mouse_down = True
                    elif event.button == 3:
                        self.mouse_right = True
                    self.handle_click(event.button)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.mouse_down = False
                    elif event.button == 3:
                        self.mouse_right = False
                # Sound event timers
                elif event.type >= pygame.USEREVENT and event.type < pygame.USEREVENT + 4:
                    i = event.type - pygame.USEREVENT
                    self.sound.beep(440 + 160 * i, 80, 0.2)
                elif event.type >= pygame.USEREVENT + 10 and event.type < pygame.USEREVENT + 16:
                    i = event.type - pygame.USEREVENT - 10
                    self.sound.beep(330 + 110 * i, 100, 0.2)
            
            # Update
            self.update(dt)
            
            # Draw
            self.draw()
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()
    
    def handle_keydown(self, key):
        if self.state == GameState.BOOT_NINTENDO or self.state == GameState.BOOT_SAMSOFT:
            self.state_timer = 999  # Skip
        
        elif self.state == GameState.MAIN_MENU:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.start_game()
        
        elif self.state == GameState.PLAYING:
            if key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
            elif key == pygame.K_q and self.player.ink >= 15:
                self.throw_bomb()
            elif key == pygame.K_e and self.perk_choices:
                self.apply_perk(self.perk_choices.pop(0))
            elif key == pygame.K_r:
                self.palette_index = (self.palette_index + 1) % len(PALETTES)
                self.show_toast("Palette swapped!")
        
        elif self.state == GameState.PAUSED:
            if key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif key == pygame.K_m:
                self.state = GameState.MAIN_MENU
        
        elif self.state in (GameState.WIN, GameState.LOSE):
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.state = GameState.MAIN_MENU
    
    def handle_click(self, button):
        if self.state == GameState.MAIN_MENU and button == 1:
            self.start_game()
        elif self.state in (GameState.WIN, GameState.LOSE) and button == 1:
            self.state = GameState.MAIN_MENU
    
    def start_game(self):
        self.state = GameState.PLAYING
        self.reset_level()
        self.show_toast("Tech Demo — Paint to win!")
    
    def reset_level(self):
        # Clear grids
        for x in range(GRID_W):
            for y in range(GRID_H):
                self.ink_owner[x][y] = TEAM_NONE
                self.ink_alpha[x][y] = 0
                self.walls[x][y] = False
        
        # Generate tech demo level
        self.generate_tech_demo()
        
        # Reset player
        self.player.reset()
        
        # Initial ink
        self.paint_circle(int(self.player.x), int(self.player.y), 10, TEAM_PLAYER, 1.0)
        
        # Reset entities
        self.enemies.clear()
        self.bombs.clear()
        self.pellets.clear()
        
        # Spawn initial enemies
        for _ in range(3):
            self.spawn_enemy()
        
        # Reset match
        self.match_time = 0
        self.splat_count = 0
        self.spawn_timer = 2.0
        self.perk_choices.clear()
    
    def generate_tech_demo(self):
        """Generate the tech demo level layout"""
        # Border walls
        for x in range(GRID_W):
            self.walls[x][0] = True
            self.walls[x][GRID_H - 1] = True
        for y in range(GRID_H):
            self.walls[0][y] = True
            self.walls[GRID_W - 1][y] = True
        
        # Central structure
        cx, cy = GRID_W // 2, GRID_H // 2
        for dx in range(-15, 16):
            for dy in range(-8, 9):
                x, y = cx + dx, cy + dy
                if 0 < x < GRID_W - 1 and 0 < y < GRID_H - 1:
                    # Hollow rectangle
                    if abs(dx) > 12 or abs(dy) > 5:
                        continue
                    if abs(dx) < 10 and abs(dy) < 3:
                        continue
                    self.walls[x][y] = True
        
        # Corner pillars
        corners = [(25, 20), (GRID_W - 26, 20), (25, GRID_H - 21), (GRID_W - 26, GRID_H - 21)]
        for cx, cy in corners:
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    x, y = cx + dx, cy + dy
                    if 0 < x < GRID_W - 1 and 0 < y < GRID_H - 1:
                        if dx * dx + dy * dy <= 25:
                            self.walls[x][y] = True
        
        # Side barriers
        for x in range(35, 55):
            self.walls[x][35] = True
            self.walls[x][36] = True
            self.walls[x][GRID_H - 36] = True
            self.walls[x][GRID_H - 37] = True
        for x in range(GRID_W - 55, GRID_W - 35):
            self.walls[x][35] = True
            self.walls[x][36] = True
            self.walls[x][GRID_H - 36] = True
            self.walls[x][GRID_H - 37] = True
    
    def spawn_enemy(self):
        attempts = 0
        while attempts < 20:
            side = random.randint(0, 3)
            if side == 0:
                x, y = random.randint(5, GRID_W - 6), 5
            elif side == 1:
                x, y = random.randint(5, GRID_W - 6), GRID_H - 6
            elif side == 2:
                x, y = 5, random.randint(5, GRID_H - 6)
            else:
                x, y = GRID_W - 6, random.randint(5, GRID_H - 6)
            
            if not self.is_wall(x, y):
                self.enemies.append(Enemy(x=float(x), y=float(y)))
                return
            attempts += 1
    
    def throw_bomb(self):
        self.player.ink -= 15
        power = 12 + self.player.perks["bomb_power"] * 4
        angle = self.player.angle
        self.bombs.append(Bomb(
            x=self.player.x,
            y=self.player.y,
            vx=math.cos(angle) * 4,
            vy=math.sin(angle) * 4,
            team=TEAM_PLAYER,
            power=power
        ))
        self.sound.bomb()
    
    def apply_perk(self, perk):
        self.player.perks[perk["key"]] += 1
        self.show_toast(f"Perk: {perk['name']}")
        self.sound.level_up()
    
    def roll_perks(self):
        pool = [
            {"key": "ink_eff", "name": "Ink Efficiency +1"},
            {"key": "swim_speed", "name": "Swim Speed +1"},
            {"key": "bomb_power", "name": "Bomb Power +1"},
        ]
        random.shuffle(pool)
        return pool[:2]
    
    def show_toast(self, text):
        self.toast_text = text
        self.toast_timer = 2.0
    
    def is_wall(self, x, y):
        ix, iy = int(round(x)), int(round(y))
        if ix < 0 or iy < 0 or ix >= GRID_W or iy >= GRID_H:
            return True
        return self.walls[ix][iy]
    
    def paint_circle(self, cx, cy, r, team, alpha=0.8):
        r2 = r * r
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                x, y = cx + dx, cy + dy
                if 0 <= x < GRID_W and 0 <= y < GRID_H:
                    if not self.walls[x][y] and dx * dx + dy * dy <= r2:
                        self.ink_owner[x][y] = team
                        current = self.ink_alpha[x][y]
                        delta = alpha if team == TEAM_PLAYER else -alpha
                        self.ink_alpha[x][y] = max(-1, min(1, current + delta))
    
    def flood_spray(self, cx, cy, steps, team, spread=8):
        for _ in range(int(steps)):
            angle = random.random() * math.pi * 2
            dist = random.random() * spread
            x = int(round(cx + math.cos(angle) * dist))
            y = int(round(cy + math.sin(angle) * dist))
            x = max(0, min(GRID_W - 1, x))
            y = max(0, min(GRID_H - 1, y))
            if not self.walls[x][y]:
                self.paint_circle(x, y, random.randint(1, 2), team, 0.5)
    
    def territory_ratio(self, team):
        owned = 0
        total = 0
        for x in range(GRID_W):
            for y in range(GRID_H):
                if self.walls[x][y]:
                    continue
                total += 1
                if self.ink_owner[x][y] == team and self.ink_alpha[x][y] > 0:
                    owned += 1
        return owned / total if total > 0 else 0
    
    def update(self, dt):
        self.state_timer += dt
        self.toast_timer = max(0, self.toast_timer - dt)
        
        if self.state == GameState.BOOT_NINTENDO:
            if self.state_timer > 2.0:
                self.state = GameState.BOOT_SAMSOFT
                self.state_timer = 0
        
        elif self.state == GameState.BOOT_SAMSOFT:
            if self.state_timer > 2.0:
                self.state = GameState.MAIN_MENU
                self.state_timer = 0
        
        elif self.state == GameState.PLAYING:
            self.update_game(dt)
    
    def update_game(self, dt):
        self.match_time += dt
        
        # Check win/lose conditions
        if self.match_time >= self.match_duration:
            p_terr = self.territory_ratio(TEAM_PLAYER)
            e_terr = self.territory_ratio(TEAM_ENEMY)
            if p_terr > e_terr:
                self.state = GameState.WIN
                self.sound.win()
            else:
                self.state = GameState.LOSE
                self.sound.lose()
            return
        
        if self.territory_ratio(TEAM_PLAYER) > 0.85:
            self.state = GameState.WIN
            self.sound.win()
            return
        
        # Update player
        self.update_player(dt)
        
        # Update enemies
        for enemy in self.enemies:
            self.update_enemy(enemy, dt)
        self.enemies = [e for e in self.enemies if not e.dead]
        
        # Update bombs
        for bomb in self.bombs:
            self.update_bomb(bomb, dt)
        self.bombs = [b for b in self.bombs if not b.dead]
        
        # Update pellets
        for pellet in self.pellets:
            self.update_pellet(pellet, dt)
        self.pellets = [p for p in self.pellets if not p.dead]
        
        # Spawn enemies
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            p_terr = self.territory_ratio(TEAM_PLAYER)
            self.spawn_timer = 2.2 - p_terr * 1.6
        
        # Spray pellets from mouse
        if self.mouse_down and random.random() < 0.9:
            self.pellets.append(Pellet(
                x=self.player.x,
                y=self.player.y,
                vx=math.cos(self.player.angle) * 5,
                vy=math.sin(self.player.angle) * 5,
                team=TEAM_PLAYER
            ))
    
    def update_player(self, dt):
        p = self.player
        
        # Get ink under player
        ix, iy = int(round(p.x)), int(round(p.y))
        my_ink = 0
        enemy_ink = 0
        if 0 <= ix < GRID_W and 0 <= iy < GRID_H:
            if self.ink_owner[ix][iy] == TEAM_PLAYER:
                my_ink = max(0, self.ink_alpha[ix][iy])
            elif self.ink_owner[ix][iy] == TEAM_ENEMY:
                enemy_ink = max(0, self.ink_alpha[ix][iy])
        
        # Calculate speed
        swim_mul = 1 + p.perks["swim_speed"] * 0.25
        speed = (p.speed_base + my_ink * 2.0) * swim_mul
        if enemy_ink > 0:
            speed *= 0.6
        
        # Movement input
        ax, ay = 0, 0
        if self.keys.get(pygame.K_w) or self.keys.get(pygame.K_UP):
            ay -= 1
        if self.keys.get(pygame.K_s) or self.keys.get(pygame.K_DOWN):
            ay += 1
        if self.keys.get(pygame.K_a) or self.keys.get(pygame.K_LEFT):
            ax -= 1
        if self.keys.get(pygame.K_d) or self.keys.get(pygame.K_RIGHT):
            ax += 1
        
        mag = math.hypot(ax, ay) or 1
        p.vx = (ax / mag) * speed
        p.vy = (ay / mag) * speed
        
        # Dash
        p.dash_cooldown = max(0, p.dash_cooldown - dt)
        if self.keys.get(pygame.K_SPACE) and p.ink > 10 and p.dash_cooldown <= 0 and my_ink > 0.1:
            p.ink -= 10
            p.vx *= 2.5
            p.vy *= 2.5
            p.dash_cooldown = 0.5
            self.sound.spray()
        
        # Apply movement with collision
        nx = p.x + p.vx * dt * 60
        ny = p.y + p.vy * dt * 60
        if not self.is_wall(nx, p.y):
            p.x = max(2, min(GRID_W - 3, nx))
        if not self.is_wall(p.x, ny):
            p.y = max(2, min(GRID_H - 3, ny))
        
        # Aim at mouse
        mx = self.mouse_pos[0] / SCALE
        my = self.mouse_pos[1] / SCALE
        p.angle = math.atan2(my - p.y, mx - p.x)
        
        # Sprayer (LMB)
        if self.mouse_down and p.ink > 0:
            eff = 1 + p.perks["ink_eff"] * 0.35
            spray_x = int(round(p.x + math.cos(p.angle) * 4))
            spray_y = int(round(p.y + math.sin(p.angle) * 4))
            self.flood_spray(spray_x, spray_y, 8 * eff, TEAM_PLAYER, 7 + eff)
            p.ink = max(0, p.ink - 0.25 / eff)
            if random.random() < 0.3:
                self.sound.spray()
        
        # Roller (RMB)
        if self.mouse_right and p.ink > 0:
            eff = 1 + p.perks["ink_eff"] * 0.2
            r = 4 + p.perks["swim_speed"]
            self.paint_circle(int(round(p.x)), int(round(p.y)), r, TEAM_PLAYER, 0.9)
            p.ink = max(0, p.ink - 0.2 / eff)
            if random.random() < 0.1:
                self.sound.thud()
        
        # Regenerate ink
        if my_ink > 0.2:
            p.ink = min(100, p.ink + 15 * dt)
        else:
            p.ink = min(100, p.ink + 5 * dt)
    
    def update_enemy(self, e: Enemy, dt):
        e.cooldown = max(0, e.cooldown - dt)
        
        # Retarget occasionally
        if random.random() < 0.02:
            e.target_x = self.player.x + random.uniform(-40, 40)
            e.target_y = self.player.y + random.uniform(-30, 30)
        
        # Move toward target
        dx = e.target_x - e.x
        dy = e.target_y - e.y
        dist = math.hypot(dx, dy) or 1
        speed = 1.6
        
        nx = e.x + (dx / dist) * speed * dt * 60
        ny = e.y + (dy / dist) * speed * dt * 60
        
        if not self.is_wall(nx, e.y):
            e.x = max(2, min(GRID_W - 3, nx))
        if not self.is_wall(e.x, ny):
            e.y = max(2, min(GRID_H - 3, ny))
        
        # Paint trail
        self.paint_circle(int(round(e.x)), int(round(e.y)), 3, TEAM_ENEMY, 0.8)
        
        # Attack player
        player_dist = math.hypot(self.player.x - e.x, self.player.y - e.y)
        ix, iy = int(round(e.x)), int(round(e.y))
        on_enemy_ink = False
        if 0 <= ix < GRID_W and 0 <= iy < GRID_H:
            on_enemy_ink = self.ink_owner[ix][iy] == TEAM_ENEMY and self.ink_alpha[ix][iy] > 0.15
        
        if player_dist < 6 and e.cooldown <= 0 and on_enemy_ink:
            self.player.hp -= 6
            e.cooldown = 0.6
            if self.player.hp <= 0:
                self.state = GameState.LOSE
                self.sound.lose()
        
        # Check death
        if e.hp <= 0:
            e.dead = True
            self.splat_count += 1
            self.player.xp += 25
            
            # Level up
            if self.player.xp >= self.player.xp_to:
                self.player.level += 1
                self.player.xp = 0
                self.player.xp_to = int(self.player.xp_to * 1.35)
                self.perk_choices = self.roll_perks()
                self.show_toast("Level up! Press E for perk")
                self.sound.level_up()
            
            # Gear drop
            if random.random() < 0.12:
                tiers = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
                r = random.random()
                new_tier = 4 if r > 0.985 else 3 if r > 0.94 else 2 if r > 0.75 else 1 if r > 0.45 else 0
                if new_tier > self.player.gear_tier:
                    self.player.gear_tier = new_tier
                    self.show_toast(f"Gear: {tiers[new_tier]}")
            
            self.sound.thud()
    
    def update_bomb(self, b: Bomb, dt):
        b.timer += dt
        
        nx = b.x + b.vx * dt * 60
        ny = b.y + b.vy * dt * 60
        if not self.is_wall(nx, b.y):
            b.x = nx
        if not self.is_wall(b.x, ny):
            b.y = ny
        
        if b.timer >= b.life:
            self.paint_circle(int(round(b.x)), int(round(b.y)), b.power, b.team, 1.0)
            
            # Damage enemies in radius
            for e in self.enemies:
                dist = math.hypot(e.x - b.x, e.y - b.y)
                if dist <= b.power:
                    e.hp -= 25
            
            b.dead = True
    
    def update_pellet(self, p: Pellet, dt):
        p.timer += dt
        p.x += p.vx * dt * 60
        p.y += p.vy * dt * 60
        
        if not self.is_wall(p.x, p.y):
            self.paint_circle(int(round(p.x)), int(round(p.y)), 1, p.team, 0.7)
        
        if p.timer >= p.life:
            p.dead = True
        
        # Damage enemies
        for e in self.enemies:
            dist = math.hypot(e.x - p.x, e.y - p.y)
            if dist < 3:
                e.hp -= 3
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        if self.state == GameState.BOOT_NINTENDO:
            self.draw_boot_screen("Nintendo", "presents")
        
        elif self.state == GameState.BOOT_SAMSOFT:
            self.draw_boot_screen("SAMSOFT", "presents")
        
        elif self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        
        elif self.state == GameState.PLAYING:
            self.draw_game()
            self.draw_hud()
        
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_pause_overlay()
        
        elif self.state == GameState.WIN:
            self.draw_game()
            self.draw_result_overlay(True)
        
        elif self.state == GameState.LOSE:
            self.draw_game()
            self.draw_result_overlay(False)
    
    def draw_boot_screen(self, company, subtitle):
        # Fade effect
        alpha = min(1, self.state_timer / 0.5)
        if self.state_timer > 1.5:
            alpha = max(0, 1 - (self.state_timer - 1.5) / 0.5)
        
        # Company name
        text = self.font_large.render(company, True, COLOR_TEXT)
        text.set_alpha(int(alpha * 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(text, rect)
        
        # Subtitle
        text2 = self.font_small.render(subtitle, True, COLOR_TEXT_DIM)
        text2.set_alpha(int(alpha * 255))
        rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(text2, rect2)
    
    def draw_main_menu(self):
        # Title with gradient effect (simulated)
        title = "Ultra!Splatoon"
        palette = PALETTES[int(self.state_timer * 2) % len(PALETTES)]
        title_surf = self.font_large.render(title, True, palette["ink"])
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)
        
        # Version
        version = self.font_small.render("v0.1 Tech Demo", True, COLOR_TEXT_DIM)
        version_rect = version.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(version, version_rect)
        
        # Instructions
        instructions = [
            "WASD - Move",
            "Mouse - Aim",
            "LMB - Spray • RMB - Roller",
            "Q - Bomb • E - Perk • R - Palette",
            "SPACE - Dash (in ink)",
            "",
            "Paint the map to win!",
        ]
        
        for i, line in enumerate(instructions):
            text = self.font_tiny.render(line, True, COLOR_TEXT_DIM)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 22))
            self.screen.blit(text, rect)
        
        # Start prompt (blinking)
        if int(self.state_timer * 2) % 2 == 0:
            start = self.font_medium.render("Press ENTER or CLICK to Start", True, COLOR_TEXT)
            start_rect = start.get_rect(center=(SCREEN_WIDTH // 2, 360))
            self.screen.blit(start, start_rect)
    
    def draw_game(self):
        palette = PALETTES[self.palette_index]
        
        # Render ink field to surface
        for x in range(GRID_W):
            for y in range(GRID_H):
                if self.walls[x][y]:
                    color = COLOR_WALL
                else:
                    owner = self.ink_owner[x][y]
                    alpha_val = self.ink_alpha[x][y]
                    
                    if owner == TEAM_PLAYER and alpha_val > 0:
                        t = max(0, min(1, alpha_val))
                        color = (
                            int(COLOR_BG[0] + (palette["ink"][0] - COLOR_BG[0]) * t),
                            int(COLOR_BG[1] + (palette["ink"][1] - COLOR_BG[1]) * t),
                            int(COLOR_BG[2] + (palette["ink"][2] - COLOR_BG[2]) * t),
                        )
                    elif owner == TEAM_ENEMY and alpha_val > 0:
                        t = max(0, min(1, alpha_val))
                        color = (
                            int(COLOR_BG[0] + (ENEMY_COLOR[0] - COLOR_BG[0]) * t),
                            int(COLOR_BG[1] + (ENEMY_COLOR[1] - COLOR_BG[1]) * t),
                            int(COLOR_BG[2] + (ENEMY_COLOR[2] - COLOR_BG[2]) * t),
                        )
                    else:
                        color = COLOR_BG
                
                self.ink_surface.set_at((x, y), color)
        
        # Scale up and blit
        scaled = pygame.transform.scale(self.ink_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(scaled, (0, 0))
        
        # Draw entities
        for pellet in self.pellets:
            px, py = int(pellet.x * SCALE), int(pellet.y * SCALE)
            pygame.draw.circle(self.screen, COLOR_WHITE, (px, py), 2)
        
        for bomb in self.bombs:
            bx, by = int(bomb.x * SCALE), int(bomb.y * SCALE)
            pygame.draw.circle(self.screen, COLOR_WHITE, (bx, by), int(4 * SCALE))
        
        for enemy in self.enemies:
            ex, ey = int(enemy.x * SCALE), int(enemy.y * SCALE)
            pygame.draw.circle(self.screen, ENEMY_COLOR, (ex, ey), int(3 * SCALE))
            pygame.draw.rect(self.screen, COLOR_BLACK, (ex - 2, ey - 2, 4, 4))
        
        # Player
        px, py = int(self.player.x * SCALE), int(self.player.y * SCALE)
        pygame.draw.circle(self.screen, palette["roller"], (px, py), int(3.5 * SCALE))
        
        # Aim indicator
        aim_x = px + int(math.cos(self.player.angle) * 15)
        aim_y = py + int(math.sin(self.player.angle) * 15)
        pygame.draw.rect(self.screen, COLOR_BLACK, (aim_x - 2, aim_y - 2, 4, 4))
    
    def draw_hud(self):
        # Top-left stats panel
        panel_rect = pygame.Rect(8, 8, 180, 80)
        pygame.draw.rect(self.screen, (20, 22, 28, 200), panel_rect, border_radius=6)
        
        # Level, XP, Gear
        stats_text = f"Lvl {self.player.level}  XP {self.player.xp}/{self.player.xp_to}"
        text = self.font_tiny.render(stats_text, True, COLOR_TEXT)
        self.screen.blit(text, (14, 14))
        
        gear_tiers = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
        gear_text = f"Gear: {gear_tiers[self.player.gear_tier]}"
        text = self.font_tiny.render(gear_text, True, COLOR_TEXT_DIM)
        self.screen.blit(text, (14, 30))
        
        # HP bar
        pygame.draw.rect(self.screen, (40, 40, 40), (14, 48, 160, 8), border_radius=4)
        hp_width = int(160 * (self.player.hp / self.player.hp_max))
        pygame.draw.rect(self.screen, (255, 100, 120), (14, 48, hp_width, 8), border_radius=4)
        
        # Ink bar
        pygame.draw.rect(self.screen, (40, 40, 40), (14, 60, 160, 8), border_radius=4)
        ink_width = int(160 * (self.player.ink / 100))
        palette = PALETTES[self.palette_index]
        pygame.draw.rect(self.screen, palette["ink"], (14, 60, ink_width, 8), border_radius=4)
        
        # Ink percentage
        ink_text = f"Ink: {int(self.player.ink)}%"
        text = self.font_tiny.render(ink_text, True, COLOR_TEXT_DIM)
        self.screen.blit(text, (14, 72))
        
        # Perks
        perks = []
        if self.player.perks["ink_eff"]:
            perks.append(f"Eff{self.player.perks['ink_eff']}")
        if self.player.perks["swim_speed"]:
            perks.append(f"Swim{self.player.perks['swim_speed']}")
        if self.player.perks["bomb_power"]:
            perks.append(f"Bomb{self.player.perks['bomb_power']}")
        perk_str = " ".join(perks) if perks else ""
        if perk_str:
            text = self.font_tiny.render(perk_str, True, COLOR_TEXT_DIM)
            self.screen.blit(text, (80, 72))
        
        # Top center - map info
        map_text = self.font_small.render("Tech Demo Arena", True, COLOR_TEXT)
        map_rect = map_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(map_text, map_rect)
        
        # Time remaining
        time_left = max(0, self.match_duration - self.match_time)
        mins = int(time_left // 60)
        secs = int(time_left % 60)
        time_text = self.font_tiny.render(f"{mins}:{secs:02d}", True, COLOR_TEXT_DIM)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 38))
        self.screen.blit(time_text, time_rect)
        
        # Territory bar at bottom
        bar_width = 300
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 24
        
        p_terr = self.territory_ratio(TEAM_PLAYER)
        e_terr = self.territory_ratio(TEAM_ENEMY)
        
        pygame.draw.rect(self.screen, (30, 30, 30), (bar_x, bar_y, bar_width, 16), border_radius=8)
        
        # Player territory (left side)
        p_width = int(bar_width * p_terr)
        if p_width > 0:
            palette = PALETTES[self.palette_index]
            pygame.draw.rect(self.screen, palette["ink"], (bar_x, bar_y, p_width, 16), border_radius=8)
        
        # Enemy territory (right side)
        e_width = int(bar_width * e_terr)
        if e_width > 0:
            pygame.draw.rect(self.screen, ENEMY_COLOR, (bar_x + bar_width - e_width, bar_y, e_width, 16), border_radius=8)
        
        # Territory percentages
        p_text = self.font_tiny.render(f"{int(p_terr * 100)}%", True, COLOR_TEXT)
        self.screen.blit(p_text, (bar_x - 35, bar_y))
        e_text = self.font_tiny.render(f"{int(e_terr * 100)}%", True, COLOR_TEXT)
        self.screen.blit(e_text, (bar_x + bar_width + 8, bar_y))
        
        # Toast message
        if self.toast_timer > 0:
            alpha = min(1, self.toast_timer) * 255
            toast_surf = self.font_small.render(self.toast_text, True, COLOR_BLACK)
            toast_rect = toast_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            
            # Background
            bg_rect = toast_rect.inflate(20, 10)
            palette = PALETTES[self.palette_index]
            pygame.draw.rect(self.screen, palette["ink"], bg_rect, border_radius=6)
            self.screen.blit(toast_surf, toast_rect)
        
        # Controls hint
        hint = "WASD Move • LMB Spray • RMB Roll • Q Bomb • ESC Menu"
        hint_surf = self.font_tiny.render(hint, True, COLOR_TEXT_DIM)
        self.screen.blit(hint_surf, (8, SCREEN_HEIGHT - 18))
    
    def draw_pause_overlay(self):
        # Dim overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        text = self.font_large.render("PAUSED", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text, rect)
        
        # Options
        text2 = self.font_small.render("ESC - Resume • M - Menu", True, COLOR_TEXT_DIM)
        rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(text2, rect2)
    
    def draw_result_overlay(self, won: bool):
        # Colored overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        if won:
            overlay.fill((65, 163, 255, 220))
        else:
            overlay.fill((255, 61, 110, 220))
        self.screen.blit(overlay, (0, 0))
        
        # Result text
        title = "VICTORY!" if won else "SPLATTED!"
        text = self.font_large.render(title, True, COLOR_WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(text, rect)
        
        # Stats
        p_terr = int(self.territory_ratio(TEAM_PLAYER) * 100)
        e_terr = int(self.territory_ratio(TEAM_ENEMY) * 100)
        stats = f"Territory: {p_terr}% • Splats: {self.splat_count}"
        text2 = self.font_small.render(stats, True, COLOR_WHITE)
        rect2 = text2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(text2, rect2)
        
        # Continue
        text3 = self.font_small.render("Press ENTER or CLICK to continue", True, COLOR_WHITE)
        rect3 = text3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(text3, rect3)


# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    game = UltraSplatoon()
    game.run()
