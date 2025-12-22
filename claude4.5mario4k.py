#!/usr/bin/env python3
"""
ULTRA MARIO 2D - SMB1 Style Platformer
Team Flames • Samsoft • 2025

A complete Super Mario Bros style platformer with:
- Full physics engine
- Enemies and power-ups
- Level generation
- Sound effects
- Menu system
"""

import math
import pygame
import sys
import random
from enum import Enum
from typing import List, Tuple, Optional

# ==================== CONSTANTS ====================
DEBUG_MODE = False

# ==================== PYGAME INIT ====================
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLORS = {
    "sky_blue": (135, 206, 235),
    "cloud_white": (255, 255, 255),
    "grass_green": (76, 175, 80),
    "dirt_brown": (139, 69, 19),
    "brick_red": (220, 20, 60),
    "coin_yellow": (255, 215, 0),
    "mario_red": (227, 11, 92),
    "mario_blue": (0, 120, 215),
    "text_gold": (255, 215, 0),
    "shadow_black": (30, 30, 30),
    "pipe_green": (0, 128, 0),
    "castle_gray": (128, 128, 128),
    "goomba_brown": (139, 69, 19),
    "koopa_green": (0, 100, 0),
    "powerup_red": (255, 0, 0),
    "starman_yellow": (255, 255, 0),
    "fireflower_orange": (255, 165, 0),
    "water_blue": (0, 191, 255),
    "lava_orange": (255, 140, 0),
    "flag_red": (255, 0, 0),
    "flag_white": (255, 255, 255),
}

# ==================== GAME STATES ====================
class MarioState(Enum):
    SMALL = "small"
    SUPER = "super"
    FIRE = "fire"
    INVINCIBLE = "invincible"

class GameState(Enum):
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    WORLD_MAP = "world_map"

# ==================== SOUND MANAGER ====================
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_on = True
        self.sfx_on = True
        
    def load_sounds(self):
        """Create procedural sounds"""
        self.sounds = {
            "jump": self.create_beep_sound(523.25, 0.1),
            "coin": self.create_beep_sound(659.25, 0.15),
            "powerup": self.create_beep_sound(783.99, 0.2),
            "bump": self.create_beep_sound(392.00, 0.1),
            "break": self.create_beep_sound(261.63, 0.15),
            "stomp": self.create_beep_sound(220.00, 0.1),
            "fireball": self.create_beep_sound(880.00, 0.08),
            "flagpole": self.create_beep_sound(1046.50, 0.3),
            "1up": self.create_beep_sound(1318.51, 0.25),
            "pipe": self.create_beep_sound(164.81, 0.2),
            "death": self.create_beep_sound(110.00, 0.5),
            "powerdown": self.create_beep_sound(130.81, 0.3),
        }
    
    def create_beep_sound(self, frequency, duration):
        """Create a simple beep sound"""
        sample_rate = 44100
        n_samples = int(round(duration * sample_rate))
        
        buf = bytearray()
        for i in range(n_samples):
            sample = int(127.0 * math.sin(frequency * math.pi * 2 * i / sample_rate)) + 128
            buf.append(sample & 0xff)
        
        return pygame.mixer.Sound(buffer=bytes(buf))
    
    def play(self, sound_name):
        if self.sfx_on and sound_name in self.sounds:
            self.sounds[sound_name].play()

# ==================== MARIO PLAYER CLASS ====================
class Mario:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = 14
        self.gravity = 0.6
        self.max_fall_speed = 15
        
        self.state = MarioState.SMALL
        self.direction = 1  # 1 = right, -1 = left
        self.animation_frame = 0
        self.animation_timer = 0
        self.invincible_timer = 0
        self.fireball_cooldown = 0
        
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.time = 400
        
        self.on_ground = False
        self.is_crouching = False
        self.is_jumping = False
        self.is_running = False
        self.is_shooting = False
        
    def update(self, keys, platforms, enemies, items):
        """Update Mario's state"""
        # Handle horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.direction = -1
            self.is_running = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            self.direction = 1
            self.is_running = True
        if not (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            self.is_running = False
            
        # Handle jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = -self.jump_power
            self.on_ground = False
            self.is_jumping = True
            
        # Handle crouching
        self.is_crouching = (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.on_ground and self.state != MarioState.SMALL
        
        # Handle shooting fireballs
        if keys[pygame.K_z] and self.state == MarioState.FIRE and self.fireball_cooldown <= 0:
            self.is_shooting = True
            self.fireball_cooldown = 20
        else:
            self.is_shooting = False
            
        # Apply gravity
        self.vel_y += self.gravity
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
            
        # Update position
        new_x = self.x + self.vel_x
        new_y = self.y + self.vel_y
        
        # Check collisions with platforms
        self.on_ground = False
        mario_rect = pygame.Rect(new_x, new_y, self.width, self.height)
        
        for platform in platforms:
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            
            if mario_rect.colliderect(plat_rect):
                # Check from top
                if self.vel_y > 0 and mario_rect.bottom > plat_rect.top and self.y < plat_rect.top:
                    new_y = plat_rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                # Check from bottom
                elif self.vel_y < 0 and mario_rect.top < plat_rect.bottom and self.y > plat_rect.bottom:
                    new_y = plat_rect.bottom
                    self.vel_y = 0
                # Check from sides
                elif self.vel_x != 0:
                    if self.vel_x > 0 and mario_rect.right > plat_rect.left and self.x < plat_rect.left:
                        new_x = plat_rect.left - self.width
                    elif self.vel_x < 0 and mario_rect.left < plat_rect.right and self.x > plat_rect.right:
                        new_x = plat_rect.right
        
        # Update final position
        self.x = new_x
        self.y = new_y
        
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_frame = (self.animation_frame + 1) % 4
            self.animation_timer = 0
            
        # Update cooldowns
        if self.fireball_cooldown > 0:
            self.fireball_cooldown -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
        return []

    def draw(self, screen, camera_x):
        """Draw Mario"""
        screen_x = self.x - camera_x
        screen_y = self.y
        
        # Choose color based on state
        if self.state == MarioState.SMALL:
            color = COLORS["mario_red"]
            height = 32
        elif self.state == MarioState.SUPER:
            color = COLORS["mario_red"]
            height = 48
        elif self.state == MarioState.FIRE:
            color = COLORS["fireflower_orange"]
            height = 48
        elif self.state == MarioState.INVINCIBLE:
            if pygame.time.get_ticks() % 200 < 100:
                color = COLORS["starman_yellow"]
            else:
                color = COLORS["mario_red"]
            height = 48
        else:
            color = COLORS["mario_red"]
            height = 48
            
        # Draw Mario body
        body_rect = pygame.Rect(screen_x, screen_y + (48 - height), 32, height)
        pygame.draw.rect(screen, color, body_rect)
        
        # Draw overalls
        overalls_color = COLORS["mario_blue"]
        overalls_rect = pygame.Rect(screen_x + 8, screen_y + 20, 16, height - 16)
        pygame.draw.rect(screen, overalls_color, overalls_rect)
        
        # Draw hat
        hat_color = COLORS["mario_red"]
        hat_rect = pygame.Rect(screen_x, screen_y, 32, 8)
        pygame.draw.rect(screen, hat_color, hat_rect)
        
        # Draw face (eyes)
        eye_color = COLORS["cloud_white"]
        eye1 = (screen_x + 8, screen_y + 12)
        eye2 = (screen_x + 24, screen_y + 12)
        pygame.draw.circle(screen, eye_color, eye1, 3)
        pygame.draw.circle(screen, eye_color, eye2, 3)
        
        # Draw mustache if big
        if self.state != MarioState.SMALL:
            mustache_color = COLORS["shadow_black"]
            pygame.draw.line(screen, mustache_color, 
                           (screen_x + 8, screen_y + 16), 
                           (screen_x + 24, screen_y + 16), 3)
        
        # Draw running animation
        if self.is_running and self.on_ground:
            leg_color = COLORS["mario_blue"]
            leg_offset = math.sin(pygame.time.get_ticks() * 0.01) * 4
            pygame.draw.line(screen, leg_color,
                           (screen_x + 8, screen_y + height),
                           (screen_x + 8, screen_y + height + 8 + leg_offset), 3)
            pygame.draw.line(screen, leg_color,
                           (screen_x + 24, screen_y + height),
                           (screen_x + 24, screen_y + height + 8 - leg_offset), 3)

# ==================== GAME OBJECTS ====================
class GameObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        
class Block(GameObject):
    def __init__(self, x, y, block_type="brick"):
        super().__init__(x, y, 32, 32)
        self.type = block_type
        self.contains_item = None
        self.is_hit = False
        self.bump_offset = 0
        self.bump_direction = 1
        
    def update(self):
        if self.is_hit:
            self.bump_offset += self.bump_direction * 2
            if abs(self.bump_offset) >= 8:
                self.bump_direction *= -1
            if self.bump_offset <= 0 and self.bump_direction == -1:
                self.is_hit = False
                self.bump_offset = 0
                
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        screen_y = self.y - self.bump_offset
        
        if self.type == "brick":
            color = COLORS["brick_red"]
        elif self.type == "question":
            color = COLORS["coin_yellow"]
        elif self.type == "ground":
            color = COLORS["dirt_brown"]
        elif self.type == "pipe":
            color = COLORS["pipe_green"]
        else:
            color = COLORS["castle_gray"]
            
        pygame.draw.rect(screen, color, 
                        (screen_x, screen_y, self.width, self.height))
        
        # Add texture
        if self.type == "brick":
            pygame.draw.rect(screen, (200, 50, 50), 
                           (screen_x + 2, screen_y + 2, 
                            self.width - 4, self.height - 4))
        elif self.type == "question":
            font = pygame.font.Font(None, 24)
            text = font.render("?", True, COLORS["shadow_black"])
            screen.blit(text, (screen_x + 10, screen_y + 6))

class Coin(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 16)
        self.animation_frame = 0
        self.collected = False
        
    def update(self):
        self.animation_frame = (self.animation_frame + 1) % 60
        
    def draw(self, screen, camera_x):
        if not self.collected:
            screen_x = self.x - camera_x
            screen_y = self.y
            
            scale = 1.0 + 0.2 * math.sin(self.animation_frame * 0.1)
            coin_width = int(self.width * scale)
            coin_height = int(self.height * scale)
            
            pygame.draw.ellipse(screen, COLORS["coin_yellow"],
                              (screen_x - (coin_width - self.width) // 2,
                               screen_y - (coin_height - self.height) // 2,
                               coin_width, coin_height))
            
            pygame.draw.ellipse(screen, COLORS["text_gold"],
                              (screen_x + 4, screen_y + 4, 8, 8))

class Goomba(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 32, 32)
        self.vel_x = -1
        self.vel_y = 0
        self.direction = -1
        self.is_alive = True
        self.is_stomped = False
        self.stomp_timer = 0
        self.animation_frame = 0
        
    def update(self, platforms):
        if self.is_stomped:
            self.stomp_timer += 1
            if self.stomp_timer > 30:
                self.is_alive = False
            return
            
        self.x += self.vel_x
        self.animation_frame = (self.animation_frame + 1) % 60
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen, camera_x):
        if not self.is_alive:
            return
            
        screen_x = self.x - camera_x
        screen_y = self.y
        
        if self.is_stomped:
            pygame.draw.ellipse(screen, COLORS["goomba_brown"],
                              (screen_x, screen_y + 16, 32, 16))
        else:
            pygame.draw.ellipse(screen, COLORS["goomba_brown"],
                              (screen_x, screen_y, 32, 32))
            
            eye_color = COLORS["cloud_white"]
            pygame.draw.circle(screen, eye_color, (screen_x + 8, screen_y + 12), 4)
            pygame.draw.circle(screen, eye_color, (screen_x + 24, screen_y + 12), 4)
            
            eyebrow_color = COLORS["shadow_black"]
            pygame.draw.line(screen, eyebrow_color,
                           (screen_x + 6, screen_y + 8),
                           (screen_x + 10, screen_y + 10), 2)
            pygame.draw.line(screen, eyebrow_color,
                           (screen_x + 22, screen_y + 8),
                           (screen_x + 26, screen_y + 10), 2)

class PowerUp(GameObject):
    def __init__(self, x, y, power_type="mushroom"):
        super().__init__(x, y, 32, 32)
        self.type = power_type
        self.vel_x = 1
        self.vel_y = 0
        self.is_collected = False
        self.bounce_offset = 0
        
    def update(self):
        self.x += self.vel_x
        self.bounce_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5
        
    def draw(self, screen, camera_x):
        if not self.is_collected:
            screen_x = self.x - camera_x
            screen_y = self.y + self.bounce_offset
            
            if self.type == "mushroom":
                pygame.draw.ellipse(screen, COLORS["powerup_red"],
                                  (screen_x, screen_y + 16, 32, 16))
                pygame.draw.ellipse(screen, COLORS["cloud_white"],
                                  (screen_x + 4, screen_y, 24, 20))
            elif self.type == "fireflower":
                pygame.draw.ellipse(screen, COLORS["fireflower_orange"],
                                  (screen_x, screen_y, 32, 32))
                for i in range(4):
                    angle = i * 90 + pygame.time.get_ticks() * 0.01
                    px = screen_x + 16 + math.cos(math.radians(angle)) * 12
                    py = screen_y + 16 + math.sin(math.radians(angle)) * 12
                    pygame.draw.circle(screen, COLORS["lava_orange"], (int(px), int(py)), 6)

class Flagpole(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 16, 400)
        self.flag_position = 100
        self.flag_captured = False
        
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        pygame.draw.rect(screen, COLORS["castle_gray"],
                        (screen_x + 4, self.y, 8, self.height))
        
        if not self.flag_captured:
            flag_points = [
                (screen_x + 12, self.y + self.flag_position),
                (screen_x + 40, self.y + self.flag_position),
                (screen_x + 40, self.y + self.flag_position + 20),
                (screen_x + 12, self.y + self.flag_position + 20)
            ]
            pygame.draw.polygon(screen, COLORS["flag_red"], flag_points)
            pygame.draw.polygon(screen, COLORS["flag_white"], 
                              [(screen_x + 12, self.y + self.flag_position),
                               (screen_x + 40, self.y + self.flag_position + 10),
                               (screen_x + 12, self.y + self.flag_position + 20)])

# ==================== LEVEL ====================
class Level:
    def __init__(self, level_num=1):
        self.level_num = level_num
        self.width = 4000
        self.height = 600
        self.platforms = []
        self.blocks = []
        self.coins = []
        self.enemies = []
        self.powerups = []
        self.flagpole = None
        self.start_x = 100
        self.start_y = 400
        self.end_x = 3800
        
        self.generate_level()
        
    def generate_level(self):
        """Generate a Mario level"""
        # Ground
        for i in range(0, self.width, 32):
            self.blocks.append(Block(i, self.height - 32, "ground"))
            
        # Floating platforms
        platform_positions = [
            (300, 400), (500, 350), (700, 300),
            (900, 400), (1100, 350), (1300, 300),
            (1500, 400), (1700, 350), (1900, 300),
            (2100, 400), (2300, 350), (2500, 300),
        ]
        
        for x, y in platform_positions:
            for i in range(3):
                self.blocks.append(Block(x + i * 32, y, "brick"))
                
        # Question blocks
        question_positions = [
            (350, 300, "mushroom"),
            (750, 250, "coin"),
            (1150, 250, "fireflower"),
            (1550, 300, "coin"),
            (1950, 250, "mushroom"),
            (2350, 250, "coin"),
        ]
        
        for x, y, item in question_positions:
            block = Block(x, y, "question")
            block.contains_item = item
            self.blocks.append(block)
            
        # Coins
        coin_patterns = [
            (400, 200, 5, "horizontal"),
            (600, 150, 5, "vertical"),
            (1000, 200, 5, "horizontal"),
            (1400, 150, 5, "vertical"),
            (1800, 200, 5, "horizontal"),
            (2200, 150, 5, "vertical"),
        ]
        
        for x, y, count, pattern in coin_patterns:
            for i in range(count):
                if pattern == "horizontal":
                    self.coins.append(Coin(x + i * 40, y))
                else:
                    self.coins.append(Coin(x, y - i * 40))
                    
        # Enemies
        enemy_positions = [
            (450, self.height - 64),
            (850, self.height - 64),
            (1250, self.height - 64),
            (1650, self.height - 64),
            (2050, self.height - 64),
            (2450, self.height - 64),
        ]
        
        for x, y in enemy_positions:
            self.enemies.append(Goomba(x, y))
            
        # Pipes
        pipe_positions = [
            (600, self.height - 96, 2),
            (1200, self.height - 128, 3),
            (1800, self.height - 96, 2),
            (2400, self.height - 128, 3),
        ]
        
        for x, y, height in pipe_positions:
            for h in range(height):
                self.blocks.append(Block(x, y - h * 32, "pipe"))
                
        # Flagpole
        self.flagpole = Flagpole(self.end_x, self.height - 400)
        
    def draw_background(self, screen, camera_x):
        """Draw sky and clouds"""
        for y in range(0, self.height, 2):
            color_ratio = y / self.height
            sky_color = (
                int(135 + color_ratio * 60),
                int(206 - color_ratio * 60),
                int(235 - color_ratio * 60)
            )
            pygame.draw.line(screen, sky_color, (0, y), (SCREEN_WIDTH, y))
            
        # Clouds (parallax)
        cloud_positions = [
            (200 - camera_x * 0.5, 100),
            (500 - camera_x * 0.5, 150),
            (800 - camera_x * 0.5, 80),
            (1200 - camera_x * 0.5, 120),
            (1600 - camera_x * 0.5, 90),
            (2000 - camera_x * 0.5, 130),
            (2400 - camera_x * 0.5, 70),
            (2800 - camera_x * 0.5, 110),
            (3200 - camera_x * 0.5, 85),
            (3600 - camera_x * 0.5, 140),
        ]
        
        for x, y in cloud_positions:
            if -100 < x < SCREEN_WIDTH + 100:
                for i in range(3):
                    pygame.draw.ellipse(screen, COLORS["cloud_white"],
                                      (x + i * 25, y, 40, 25))
                    pygame.draw.ellipse(screen, COLORS["cloud_white"],
                                      (x + i * 25 - 10, y + 10, 40, 25))

# ==================== GAME ENGINE ====================
class MarioGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ULTRA MARIO 2D - Team Flames")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MAIN_MENU
        
        self.mario = None
        self.level = None
        self.camera_x = 0
        self.score = 0
        self.world = 1
        self.time_left = 400
        
        self.sound_manager = SoundManager()
        self.sound_manager.load_sounds()
        
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.main_menu_selection = 0
        self.main_menu_options = [
            "START GAME",
            "WORLD MAP",
            "OPTIONS",
            "CREDITS",
            "QUIT"
        ]
        
        self.load_game()
        
    def load_game(self):
        """Initialize game"""
        self.mario = Mario(100, 400)
        self.level = Level(1)
        self.camera_x = 0
        self.time_left = 400
        
    def handle_events(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MAIN_MENU:
                    if event.key == pygame.K_UP:
                        self.main_menu_selection = (self.main_menu_selection - 1) % len(self.main_menu_options)
                        self.sound_manager.play("coin")
                    elif event.key == pygame.K_DOWN:
                        self.main_menu_selection = (self.main_menu_selection + 1) % len(self.main_menu_options)
                        self.sound_manager.play("coin")
                    elif event.key == pygame.K_RETURN:
                        self.handle_menu_selection()
                        self.sound_manager.play("powerup")
                        
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                        self.sound_manager.play("bump")
                    elif event.key == pygame.K_p:
                        # Debug: Power-up
                        if self.mario.state == MarioState.SMALL:
                            self.mario.state = MarioState.SUPER
                        elif self.mario.state == MarioState.SUPER:
                            self.mario.state = MarioState.FIRE
                        self.sound_manager.play("powerup")
                        
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                        self.sound_manager.play("coin")
                        
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.load_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MAIN_MENU
                        
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        self.world += 1
                        self.level = Level(self.world)
                        self.mario = Mario(self.level.start_x, self.level.start_y)
                        self.camera_x = 0
                        self.time_left = 400
                        self.state = GameState.PLAYING
                        
    def handle_menu_selection(self):
        """Handle menu selection"""
        if self.main_menu_selection == 0:
            self.state = GameState.PLAYING
            self.load_game()
        elif self.main_menu_selection == 1:
            self.state = GameState.WORLD_MAP
        elif self.main_menu_selection == 2:
            self.show_options()
        elif self.main_menu_selection == 3:
            self.show_credits()
        elif self.main_menu_selection == 4:
            self.running = False
            
    def show_options(self):
        """Show options (placeholder)"""
        print("OPTIONS:")
        print("  Music:", "ON" if self.sound_manager.music_on else "OFF")
        print("  SFX:", "ON" if self.sound_manager.sfx_on else "OFF")
        print("\nControls:")
        print("  Arrow Keys / WASD: Move")
        print("  Space / W: Jump")
        print("  Z: Shoot (Fire Mario)")
        print("  P: Debug Power-up")
        print("  ESC: Pause")
        
    def show_credits(self):
        """Show credits (placeholder)"""
        print("\n" + "=" * 40)
        print("ULTRA MARIO 2D")
        print("=" * 40)
        print("Developed by: Team Flames")
        print("Published by: Samsoft")
        print("Engine: Pygame")
        print("\nOriginal Super Mario Bros")
        print("© Nintendo 1985")
        print("=" * 40 + "\n")

    def update(self):
        """Update game state"""
        if self.state != GameState.PLAYING:
            return
            
        keys = pygame.key.get_pressed()
        
        # Update Mario
        self.mario.update(keys, self.level.blocks, self.level.enemies, self.level.powerups)
        
        # Update camera
        self.camera_x = self.mario.x - SCREEN_WIDTH // 2
        if self.camera_x < 0:
            self.camera_x = 0
        if self.camera_x > self.level.width - SCREEN_WIDTH:
            self.camera_x = self.level.width - SCREEN_WIDTH
            
        # Update time
        if pygame.time.get_ticks() % 1000 < 16:  # Roughly every second
            self.time_left = max(0, self.time_left - 1)
            
        # Check level complete
        if self.mario.x >= self.level.end_x:
            self.state = GameState.LEVEL_COMPLETE
            self.sound_manager.play("flagpole")
            
        # Check game over
        if self.mario.y > self.level.height or self.time_left <= 0:
            self.mario.lives -= 1
            if self.mario.lives > 0:
                self.mario = Mario(self.level.start_x, self.level.start_y)
                self.camera_x = 0
                self.sound_manager.play("death")
            else:
                self.state = GameState.GAME_OVER
                self.sound_manager.play("death")
                
        # Update enemies
        for enemy in self.level.enemies:
            if enemy.is_alive:
                enemy.update(self.level.blocks)
                
        # Update coins
        for coin in self.level.coins:
            if not coin.collected:
                coin.update()
                
        # Check coin collection
        mario_rect = pygame.Rect(self.mario.x, self.mario.y, self.mario.width, self.mario.height)
        for coin in self.level.coins:
            if not coin.collected:
                coin_rect = pygame.Rect(coin.x, coin.y, coin.width, coin.height)
                if mario_rect.colliderect(coin_rect):
                    coin.collected = True
                    self.mario.coins += 1
                    self.mario.score += 100
                    self.sound_manager.play("coin")
                    
        # Check enemy collisions
        for enemy in self.level.enemies:
            if enemy.is_alive and not enemy.is_stomped:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if mario_rect.colliderect(enemy_rect):
                    # Check if stomping
                    if self.mario.vel_y > 0 and self.mario.y < enemy.y:
                        enemy.is_stomped = True
                        self.mario.vel_y = -8  # Bounce
                        self.mario.score += 200
                        self.sound_manager.play("stomp")
                    elif self.mario.invincible_timer <= 0:
                        # Take damage
                        if self.mario.state != MarioState.SMALL:
                            self.mario.state = MarioState.SMALL
                            self.mario.invincible_timer = 120
                            self.sound_manager.play("powerdown")
                        else:
                            self.mario.lives -= 1
                            if self.mario.lives > 0:
                                self.mario = Mario(self.level.start_x, self.level.start_y)
                                self.camera_x = 0
                                self.sound_manager.play("death")
                            else:
                                self.state = GameState.GAME_OVER
                                self.sound_manager.play("death")
                
    def draw_main_menu(self):
        """Draw main menu"""
        time_ms = pygame.time.get_ticks()
        
        # Animated background
        for y in range(0, SCREEN_HEIGHT, 2):
            color_ratio = y / SCREEN_HEIGHT
            pulse = math.sin(time_ms * 0.001 + y * 0.01) * 0.1 + 0.9
            r = int((135 + color_ratio * 60) * pulse)
            g = int((206 - color_ratio * 60) * pulse)
            b = int((235 - color_ratio * 60) * pulse)
            pygame.draw.line(self.screen, (min(255, r), min(255, g), min(255, b)), 
                           (0, y), (SCREEN_WIDTH, y))
            
        # Title
        title_text = "ULTRA MARIO 2D"
        title_surf = self.font_large.render(title_text, True, COLORS["mario_red"])
        shadow_surf = self.font_large.render(title_text, True, COLORS["shadow_black"])
        self.screen.blit(shadow_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2 + 3, 103))
        self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 100))
        
        # Subtitle
        subtitle = "Team Flames • Samsoft"
        subtitle_surf = self.font_medium.render(subtitle, True, COLORS["text_gold"])
        self.screen.blit(subtitle_surf, 
                        (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, 180))
        
        # Menu options
        for i, option in enumerate(self.main_menu_options):
            color = COLORS["text_gold"] if i == self.main_menu_selection else COLORS["cloud_white"]
            
            if i == self.main_menu_selection:
                sparkle_x = SCREEN_WIDTH // 2 - 150 + math.sin(time_ms * 0.005) * 10
                sparkle_y = 280 + i * 50
                pygame.draw.circle(self.screen, COLORS["starman_yellow"],
                                 (int(sparkle_x), int(sparkle_y)), 5)
                
            option_text = f"> {option}" if i == self.main_menu_selection else option
            option_surf = self.font_medium.render(option_text, True, color)
            self.screen.blit(option_surf,
                           (SCREEN_WIDTH // 2 - option_surf.get_width() // 2,
                            260 + i * 50))
            
        # Instructions
        instruct = "Use Arrow Keys to select, ENTER to choose"
        instruct_surf = self.font_small.render(instruct, True, COLORS["cloud_white"])
        self.screen.blit(instruct_surf,
                        (SCREEN_WIDTH // 2 - instruct_surf.get_width() // 2,
                         SCREEN_HEIGHT - 50))
        
    def draw_hud(self):
        """Draw HUD"""
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, 40))
        
        world_text = f"WORLD {self.world}-{self.level.level_num}"
        world_surf = self.font_small.render(world_text, True, COLORS["cloud_white"])
        self.screen.blit(world_surf, (20, 8))
        
        score_text = f"SCORE: {self.mario.score:06d}"
        score_surf = self.font_small.render(score_text, True, COLORS["cloud_white"])
        self.screen.blit(score_surf, (200, 8))
        
        coin_text = f"COINS: {self.mario.coins:02d}"
        coin_surf = self.font_small.render(coin_text, True, COLORS["coin_yellow"])
        self.screen.blit(coin_surf, (420, 8))
        
        time_text = f"TIME: {self.time_left}"
        time_color = COLORS["lava_orange"] if self.time_left < 100 else COLORS["cloud_white"]
        time_surf = self.font_small.render(time_text, True, time_color)
        self.screen.blit(time_surf, (580, 8))
        
        lives_text = f"LIVES: {self.mario.lives}"
        lives_surf = self.font_small.render(lives_text, True, COLORS["powerup_red"])
        self.screen.blit(lives_surf, (SCREEN_WIDTH - 120, 8))
        
    def draw_game(self):
        """Draw game world"""
        self.level.draw_background(self.screen, self.camera_x)
        
        for block in self.level.blocks:
            if -100 < block.x - self.camera_x < SCREEN_WIDTH + 100:
                block.draw(self.screen, self.camera_x)
                
        for coin in self.level.coins:
            if not coin.collected and -100 < coin.x - self.camera_x < SCREEN_WIDTH + 100:
                coin.draw(self.screen, self.camera_x)
                
        for enemy in self.level.enemies:
            if enemy.is_alive and -100 < enemy.x - self.camera_x < SCREEN_WIDTH + 100:
                enemy.draw(self.screen, self.camera_x)
                
        for powerup in self.level.powerups:
            if not powerup.is_collected and -100 < powerup.x - self.camera_x < SCREEN_WIDTH + 100:
                powerup.draw(self.screen, self.camera_x)
                
        if self.level.flagpole and -100 < self.level.flagpole.x - self.camera_x < SCREEN_WIDTH + 100:
            self.level.flagpole.draw(self.screen, self.camera_x)
            
        self.mario.draw(self.screen, self.camera_x)
        self.draw_hud()
        
    def draw_pause_screen(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = "PAUSED"
        pause_surf = self.font_large.render(pause_text, True, COLORS["text_gold"])
        self.screen.blit(pause_surf,
                        (SCREEN_WIDTH // 2 - pause_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 - 50))
        
        instruct = "Press ESC to continue"
        instruct_surf = self.font_medium.render(instruct, True, COLORS["cloud_white"])
        self.screen.blit(instruct_surf,
                        (SCREEN_WIDTH // 2 - instruct_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 50))
        
    def draw_level_complete(self):
        """Draw level complete screen"""
        time_ms = pygame.time.get_ticks()
        
        # Fireworks
        for i in range(10):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, 300)
            size = random.randint(10, 30)
            hue = (time_ms * 0.001 + i * 0.1) % 1.0
            color = pygame.Color(0)
            color.hsva = (hue * 360, 100, 100, 100)
            
            for j in range(8):
                angle = j * 45 + time_ms * 0.01
                length = size * (0.5 + 0.5 * math.sin(time_ms * 0.002))
                end_x = x + math.cos(math.radians(angle)) * length
                end_y = y + math.sin(math.radians(angle)) * length
                pygame.draw.line(self.screen, color, (x, y), (end_x, end_y), 3)
                
        complete_text = "WORLD COMPLETE!"
        complete_surf = self.font_large.render(complete_text, True, COLORS["text_gold"])
        self.screen.blit(complete_surf,
                        (SCREEN_WIDTH // 2 - complete_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 - 100))
        
        score_text = f"SCORE: {self.mario.score}"
        score_surf = self.font_medium.render(score_text, True, COLORS["cloud_white"])
        self.screen.blit(score_surf,
                        (SCREEN_WIDTH // 2 - score_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2))
        
        coins_text = f"COINS: {self.mario.coins}"
        coins_surf = self.font_medium.render(coins_text, True, COLORS["coin_yellow"])
        self.screen.blit(coins_surf,
                        (SCREEN_WIDTH // 2 - coins_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 50))
        
        continue_text = "Press ENTER to continue"
        continue_surf = self.font_small.render(continue_text, True, COLORS["cloud_white"])
        self.screen.blit(continue_surf,
                        (SCREEN_WIDTH // 2 - continue_surf.get_width() // 2,
                         SCREEN_HEIGHT - 100))
        
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = "GAME OVER"
        game_over_surf = self.font_large.render(game_over_text, True, COLORS["powerup_red"])
        self.screen.blit(game_over_surf,
                        (SCREEN_WIDTH // 2 - game_over_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 - 100))
        
        score_text = f"Final Score: {self.mario.score}"
        score_surf = self.font_medium.render(score_text, True, COLORS["cloud_white"])
        self.screen.blit(score_surf,
                        (SCREEN_WIDTH // 2 - score_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2))
        
        option1 = "Press ENTER to restart"
        option2 = "Press ESC for main menu"
        
        option1_surf = self.font_small.render(option1, True, COLORS["water_blue"])
        option2_surf = self.font_small.render(option2, True, COLORS["water_blue"])
        
        self.screen.blit(option1_surf,
                        (SCREEN_WIDTH // 2 - option1_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(option2_surf,
                        (SCREEN_WIDTH // 2 - option2_surf.get_width() // 2,
                         SCREEN_HEIGHT // 2 + 140))
        
    def run(self):
        """Main game loop"""
        print("=" * 50)
        print("  ULTRA MARIO 2D")
        print("  Team Flames • Samsoft • 2025")
        print("=" * 50)
        print("\nControls:")
        print("  Arrow Keys / WASD: Move")
        print("  Space / W: Jump")
        print("  Z: Shoot (Fire Mario)")
        print("  P: Debug Power-up")
        print("  ESC: Pause / Menu")
        print("=" * 50)
        
        while self.running:
            self.handle_events()
            
            if self.state == GameState.PLAYING:
                self.update()
                
            self.screen.fill(COLORS["sky_blue"])
            
            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.PAUSED:
                self.draw_game()
                self.draw_pause_screen()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.draw_level_complete()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.WORLD_MAP:
                self.draw_main_menu()  # Placeholder
            
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# ==================== MAIN ====================
if __name__ == "__main__":
    game = MarioGame()
    game.run()
