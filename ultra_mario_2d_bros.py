#!/usr/bin/env python3
"""
Ultra Mario 2D Bros
An authentic Super Mario Bros 1 style platformer in Pygame
By Team Flames / Samsoft

Features authentic SMB1 physics:
- Acceleration-based movement with momentum
- Variable jump height (hold to jump higher)
- Skidding when changing direction
- Power-up system (Mushroom, Fire Flower, Star)
- Question blocks and breakable bricks
- Authentic enemy AI (Goombas, Koopas)
- Coin collection and scoring
- Lives and game over system
"""

import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()

# =============================================================================
# CONSTANTS - Authentic SMB1 Values
# =============================================================================

# Screen settings
SCREEN_WIDTH = 768  # 256 * 3 (NES resolution scaled)
SCREEN_HEIGHT = 672  # 224 * 3
FPS = 60
TILE_SIZE = 48  # 16 * 3

# Physics constants (scaled from original NES values)
GRAVITY = 0.9375  # SMB1 gravity
MAX_FALL_SPEED = 12.0
WALK_ACCEL = 0.09375
RUN_ACCEL = 0.140625
WALK_SPEED = 4.5
RUN_SPEED = 7.5
FRICTION = 0.9375
AIR_FRICTION = 0.984375
SKID_DECEL = 0.3

# Jump physics (variable height based on hold)
JUMP_VELOCITY = -12.75
JUMP_HOLD_GRAVITY = 0.3
JUMP_RELEASE_GRAVITY = 0.9375

# SMB1 Color Palette (authentic NES colors)
COL_SKY = (92, 148, 252)
COL_BLACK = (0, 0, 0)
COL_WHITE = (252, 252, 252)
COL_BRICK = (200, 76, 12)
COL_BRICK_DARK = (136, 20, 0)
COL_BLOCK = (228, 92, 16)
COL_QUESTION = (252, 152, 56)
COL_GROUND = (228, 92, 16)
COL_GROUND_DARK = (136, 20, 0)
COL_PIPE_GREEN = (0, 168, 0)
COL_PIPE_LIGHT = (128, 208, 16)
COL_MARIO_RED = (228, 0, 88)
COL_MARIO_SKIN = (252, 152, 56)
COL_MARIO_BROWN = (136, 20, 0)
COL_LUIGI_GREEN = (0, 168, 0)
COL_GOOMBA = (228, 92, 16)
COL_GOOMBA_DARK = (136, 20, 0)
COL_KOOPA_GREEN = (0, 168, 0)
COL_KOOPA_YELLOW = (252, 188, 60)
COL_COIN = (252, 188, 60)
COL_COIN_DARK = (228, 92, 16)
COL_MUSHROOM_RED = (228, 0, 88)
COL_MUSHROOM_WHITE = (252, 252, 252)
COL_FIRE_ORANGE = (252, 152, 56)
COL_STAR_YELLOW = (252, 188, 60)
COL_CLOUD = (252, 252, 252)
COL_BUSH_GREEN = (0, 168, 0)
COL_HILL_GREEN = (0, 168, 68)
COL_CASTLE_GRAY = (188, 188, 188)
COL_FLAG_GREEN = (0, 168, 0)
COL_POLE_GRAY = (188, 188, 188)

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3
STATE_LEVEL_CLEAR = 4
STATE_WIN = 5

# Mario states
MARIO_SMALL = 0
MARIO_BIG = 1
MARIO_FIRE = 2

# Tile types
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BRICK = 2
TILE_QUESTION = 3
TILE_QUESTION_EMPTY = 4
TILE_BLOCK = 5
TILE_PIPE_TL = 6
TILE_PIPE_TR = 7
TILE_PIPE_L = 8
TILE_PIPE_R = 9
TILE_FLAG_POLE = 10
TILE_FLAG_TOP = 11
TILE_CASTLE = 12

# Power-up types
POWERUP_MUSHROOM = 0
POWERUP_FIREFLOWER = 1
POWERUP_STAR = 2
POWERUP_1UP = 3

# =============================================================================
# SPRITE DRAWING FUNCTIONS (Rectangle-based authentic look)
# =============================================================================

def draw_mario_small(surface, x, y, facing_right=True, frame=0):
    """Draw small Mario using rectangles (16x16 scaled to 48x48)"""
    s = 3  # Scale factor
    
    # Flip offset for facing left
    def px(local_x):
        if facing_right:
            return x + local_x * s
        else:
            return x + (15 - local_x) * s
    
    # Hat
    pygame.draw.rect(surface, COL_MARIO_RED, (px(3), y + 1*s, 5*s, 2*s) if facing_right else (x + 8*s, y + 1*s, 5*s, 2*s))
    pygame.draw.rect(surface, COL_MARIO_RED, (px(2), y + 3*s, 8*s, 1*s) if facing_right else (x + 6*s, y + 3*s, 8*s, 1*s))
    
    # Face
    pygame.draw.rect(surface, COL_MARIO_SKIN, (px(2), y + 4*s, 3*s, 3*s) if facing_right else (x + 11*s, y + 4*s, 3*s, 3*s))
    pygame.draw.rect(surface, COL_MARIO_BROWN, (px(5), y + 4*s, 3*s, 1*s) if facing_right else (x + 8*s, y + 4*s, 3*s, 1*s))  # Hair
    pygame.draw.rect(surface, COL_MARIO_SKIN, (px(3), y + 5*s, 5*s, 2*s) if facing_right else (x + 8*s, y + 5*s, 5*s, 2*s))
    
    # Body (overalls)
    pygame.draw.rect(surface, COL_MARIO_RED, (px(1), y + 7*s, 6*s, 2*s) if facing_right else (x + 9*s, y + 7*s, 6*s, 2*s))
    pygame.draw.rect(surface, COL_MARIO_BROWN, (px(3), y + 8*s, 3*s, 5*s) if facing_right else (x + 10*s, y + 8*s, 3*s, 5*s))
    
    # Feet
    pygame.draw.rect(surface, COL_MARIO_BROWN, (px(1), y + 13*s, 3*s, 3*s) if facing_right else (x + 12*s, y + 13*s, 3*s, 3*s))
    pygame.draw.rect(surface, COL_MARIO_BROWN, (px(5), y + 13*s, 3*s, 3*s) if facing_right else (x + 8*s, y + 13*s, 3*s, 3*s))

def draw_mario_big(surface, x, y, facing_right=True, frame=0, fire=False):
    """Draw big/fire Mario using rectangles (16x32 scaled to 48x96)"""
    s = 3  # Scale factor
    
    main_color = COL_FIRE_ORANGE if fire else COL_MARIO_RED
    
    # Hat
    pygame.draw.rect(surface, main_color, (x + 4*s, y + 1*s, 8*s, 3*s))
    pygame.draw.rect(surface, main_color, (x + 2*s, y + 4*s, 12*s, 2*s))
    
    # Face
    pygame.draw.rect(surface, COL_MARIO_SKIN, (x + 3*s, y + 6*s, 10*s, 6*s))
    pygame.draw.rect(surface, COL_MARIO_BROWN, (x + 3*s, y + 6*s, 6*s, 2*s))  # Hair
    
    # Body
    pygame.draw.rect(surface, main_color, (x + 2*s, y + 12*s, 12*s, 4*s))
    pygame.draw.rect(surface, COL_MARIO_SKIN, (x + 0*s, y + 14*s, 3*s, 4*s))  # Left arm
    pygame.draw.rect(surface, COL_MARIO_SKIN, (x + 13*s, y + 14*s, 3*s, 4*s))  # Right arm
    
    # Overalls
    pygame.draw.rect(surface, COL_MARIO_BROWN if fire else (0, 0, 168), (x + 3*s, y + 16*s, 10*s, 8*s))
    pygame.draw.rect(surface, main_color, (x + 5*s, y + 16*s, 6*s, 2*s))  # Belt area
    
    # Legs
    pygame.draw.rect(surface, COL_MARIO_BROWN if fire else (0, 0, 168), (x + 2*s, y + 24*s, 5*s, 6*s))
    pygame.draw.rect(surface, COL_MARIO_BROWN if fire else (0, 0, 168), (x + 9*s, y + 24*s, 5*s, 6*s))
    
    # Shoes
    pygame.draw.rect(surface, COL_MARIO_BROWN, (x + 1*s, y + 30*s, 6*s, 2*s))
    pygame.draw.rect(surface, COL_MARIO_BROWN, (x + 9*s, y + 30*s, 6*s, 2*s))

def draw_goomba(surface, x, y, frame=0):
    """Draw Goomba enemy"""
    s = 3
    # Body
    pygame.draw.rect(surface, COL_GOOMBA, (x + 2*s, y + 4*s, 12*s, 8*s))
    pygame.draw.rect(surface, COL_GOOMBA, (x + 4*s, y + 2*s, 8*s, 2*s))
    # Eyes
    pygame.draw.rect(surface, COL_BLACK, (x + 3*s, y + 5*s, 3*s, 3*s))
    pygame.draw.rect(surface, COL_BLACK, (x + 10*s, y + 5*s, 3*s, 3*s))
    pygame.draw.rect(surface, COL_WHITE, (x + 4*s, y + 5*s, 2*s, 2*s))
    pygame.draw.rect(surface, COL_WHITE, (x + 10*s, y + 5*s, 2*s, 2*s))
    # Feet
    feet_offset = (frame % 2) * 2
    pygame.draw.rect(surface, COL_GOOMBA_DARK, (x + 1*s + feet_offset, y + 12*s, 5*s, 4*s))
    pygame.draw.rect(surface, COL_GOOMBA_DARK, (x + 10*s - feet_offset, y + 12*s, 5*s, 4*s))

def draw_koopa(surface, x, y, facing_right=True, frame=0):
    """Draw Koopa Troopa enemy"""
    s = 3
    # Shell
    pygame.draw.rect(surface, COL_KOOPA_GREEN, (x + 3*s, y + 8*s, 10*s, 10*s))
    pygame.draw.rect(surface, COL_KOOPA_YELLOW, (x + 5*s, y + 10*s, 6*s, 6*s))
    # Head
    pygame.draw.rect(surface, COL_KOOPA_YELLOW, (x + 6*s, y + 2*s, 4*s, 6*s))
    # Eyes
    pygame.draw.rect(surface, COL_WHITE, (x + 6*s, y + 3*s, 3*s, 2*s))
    pygame.draw.rect(surface, COL_BLACK, (x + 7*s, y + 3*s, 1*s, 2*s))
    # Feet
    pygame.draw.rect(surface, COL_KOOPA_YELLOW, (x + 2*s, y + 18*s, 4*s, 3*s))
    pygame.draw.rect(surface, COL_KOOPA_YELLOW, (x + 10*s, y + 18*s, 4*s, 3*s))

def draw_shell(surface, x, y, color=COL_KOOPA_GREEN):
    """Draw Koopa shell"""
    s = 3
    pygame.draw.rect(surface, color, (x + 2*s, y + 4*s, 12*s, 10*s))
    pygame.draw.rect(surface, COL_KOOPA_YELLOW, (x + 4*s, y + 6*s, 8*s, 6*s))

def draw_mushroom(surface, x, y, is_1up=False):
    """Draw Super Mushroom or 1-Up Mushroom"""
    s = 3
    cap_color = COL_BUSH_GREEN if is_1up else COL_MUSHROOM_RED
    # Cap
    pygame.draw.rect(surface, cap_color, (x + 2*s, y + 2*s, 12*s, 8*s))
    pygame.draw.rect(surface, cap_color, (x + 4*s, y + 1*s, 8*s, 1*s))
    # Spots
    pygame.draw.rect(surface, COL_WHITE, (x + 4*s, y + 3*s, 3*s, 3*s))
    pygame.draw.rect(surface, COL_WHITE, (x + 9*s, y + 3*s, 3*s, 3*s))
    pygame.draw.rect(surface, COL_WHITE, (x + 6*s, y + 6*s, 4*s, 2*s))
    # Stem
    pygame.draw.rect(surface, COL_MUSHROOM_WHITE, (x + 5*s, y + 10*s, 6*s, 5*s))

def draw_fire_flower(surface, x, y, frame=0):
    """Draw Fire Flower"""
    s = 3
    colors = [COL_FIRE_ORANGE, COL_MUSHROOM_RED, COL_WHITE, COL_FIRE_ORANGE]
    petal_color = colors[frame % 4]
    # Petals
    pygame.draw.rect(surface, petal_color, (x + 6*s, y + 1*s, 4*s, 3*s))  # Top
    pygame.draw.rect(surface, petal_color, (x + 2*s, y + 4*s, 4*s, 4*s))  # Left
    pygame.draw.rect(surface, petal_color, (x + 10*s, y + 4*s, 4*s, 4*s))  # Right
    # Center
    pygame.draw.rect(surface, COL_WHITE, (x + 5*s, y + 4*s, 6*s, 4*s))
    pygame.draw.rect(surface, COL_BLACK, (x + 6*s, y + 5*s, 4*s, 2*s))
    # Stem
    pygame.draw.rect(surface, COL_BUSH_GREEN, (x + 6*s, y + 8*s, 4*s, 8*s))

def draw_star(surface, x, y, frame=0):
    """Draw Star power-up"""
    s = 3
    colors = [COL_STAR_YELLOW, COL_FIRE_ORANGE, COL_MUSHROOM_WHITE, COL_BUSH_GREEN]
    color = colors[frame % 4]
    # Star shape approximation
    pygame.draw.rect(surface, color, (x + 6*s, y + 1*s, 4*s, 4*s))
    pygame.draw.rect(surface, color, (x + 1*s, y + 5*s, 14*s, 4*s))
    pygame.draw.rect(surface, color, (x + 3*s, y + 9*s, 4*s, 4*s))
    pygame.draw.rect(surface, color, (x + 9*s, y + 9*s, 4*s, 4*s))
    # Eyes
    pygame.draw.rect(surface, COL_BLACK, (x + 5*s, y + 5*s, 2*s, 2*s))
    pygame.draw.rect(surface, COL_BLACK, (x + 9*s, y + 5*s, 2*s, 2*s))

def draw_coin(surface, x, y, frame=0):
    """Draw animated coin"""
    s = 3
    # Animate width for spinning effect
    widths = [12, 8, 4, 2, 4, 8, 12, 12]
    w = widths[frame % 8]
    offset = (12 - w) // 2
    pygame.draw.rect(surface, COL_COIN, (x + (2 + offset)*s, y + 2*s, w*s, 12*s))
    if w > 4:
        pygame.draw.rect(surface, COL_COIN_DARK, (x + (4 + offset)*s, y + 4*s, (w-4)*s, 8*s))

def draw_question_block(surface, x, y, empty=False, frame=0):
    """Draw Question Block"""
    s = 3
    if empty:
        pygame.draw.rect(surface, COL_BRICK_DARK, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, COL_GROUND_DARK, (x + s, y + s, TILE_SIZE - 2*s, TILE_SIZE - 2*s))
    else:
        colors = [COL_QUESTION, COL_FIRE_ORANGE, COL_COIN, COL_FIRE_ORANGE]
        color = colors[(frame // 8) % 4]
        pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(surface, COL_BLACK, (x + s, y + s, TILE_SIZE - 2*s, TILE_SIZE - 2*s))
        pygame.draw.rect(surface, color, (x + 2*s, y + 2*s, TILE_SIZE - 4*s, TILE_SIZE - 4*s))
        # Question mark
        pygame.draw.rect(surface, COL_BLACK, (x + 5*s, y + 4*s, 6*s, 2*s))
        pygame.draw.rect(surface, COL_BLACK, (x + 9*s, y + 5*s, 2*s, 4*s))
        pygame.draw.rect(surface, COL_BLACK, (x + 6*s, y + 8*s, 4*s, 2*s))
        pygame.draw.rect(surface, COL_BLACK, (x + 6*s, y + 11*s, 4*s, 2*s))

def draw_brick(surface, x, y):
    """Draw brick block"""
    s = 3
    pygame.draw.rect(surface, COL_BRICK, (x, y, TILE_SIZE, TILE_SIZE))
    # Brick pattern
    pygame.draw.rect(surface, COL_BLACK, (x, y + 7*s, TILE_SIZE, s))
    pygame.draw.rect(surface, COL_BLACK, (x + 7*s, y, s, 7*s))
    pygame.draw.rect(surface, COL_BLACK, (x + 3*s, y + 8*s, s, 8*s))
    pygame.draw.rect(surface, COL_BLACK, (x + 11*s, y + 8*s, s, 8*s))

def draw_ground(surface, x, y):
    """Draw ground block"""
    s = 3
    pygame.draw.rect(surface, COL_GROUND, (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surface, COL_GROUND_DARK, (x, y, TILE_SIZE, s))
    pygame.draw.rect(surface, COL_GROUND_DARK, (x, y, s, TILE_SIZE))

def draw_pipe(surface, x, y, is_top=False, is_left=True):
    """Draw pipe segment"""
    s = 3
    if is_top:
        pygame.draw.rect(surface, COL_PIPE_GREEN, (x, y, TILE_SIZE, TILE_SIZE))
        if is_left:
            pygame.draw.rect(surface, COL_PIPE_LIGHT, (x, y + s, 3*s, TILE_SIZE - s))
            pygame.draw.rect(surface, COL_BLACK, (x + TILE_SIZE - s, y, s, TILE_SIZE))
        else:
            pygame.draw.rect(surface, COL_BLACK, (x, y, s, TILE_SIZE))
            pygame.draw.rect(surface, COL_PIPE_LIGHT, (x + s, y + s, 3*s, TILE_SIZE - s))
        pygame.draw.rect(surface, COL_BLACK, (x, y, TILE_SIZE, s))
    else:
        pygame.draw.rect(surface, COL_PIPE_GREEN, (x, y, TILE_SIZE, TILE_SIZE))
        if is_left:
            pygame.draw.rect(surface, COL_PIPE_LIGHT, (x + 3*s, y, 3*s, TILE_SIZE))
        else:
            pygame.draw.rect(surface, COL_PIPE_LIGHT, (x + 2*s, y, 3*s, TILE_SIZE))

def draw_cloud(surface, x, y):
    """Draw decorative cloud"""
    s = 3
    pygame.draw.ellipse(surface, COL_CLOUD, (x, y + 2*s, 8*s, 6*s))
    pygame.draw.ellipse(surface, COL_CLOUD, (x + 6*s, y, 8*s, 8*s))
    pygame.draw.ellipse(surface, COL_CLOUD, (x + 12*s, y + 2*s, 8*s, 6*s))

def draw_bush(surface, x, y):
    """Draw decorative bush"""
    s = 3
    pygame.draw.ellipse(surface, COL_BUSH_GREEN, (x, y, 8*s, 6*s))
    pygame.draw.ellipse(surface, COL_BUSH_GREEN, (x + 5*s, y - 2*s, 8*s, 8*s))
    pygame.draw.ellipse(surface, COL_BUSH_GREEN, (x + 10*s, y, 8*s, 6*s))

def draw_hill(surface, x, y, size=1):
    """Draw decorative hill"""
    s = 3
    width = 24 * s * size
    height = 12 * s * size
    pygame.draw.ellipse(surface, COL_HILL_GREEN, (x, y, width, height * 2))
    pygame.draw.rect(surface, COL_SKY, (x, y, width, height // 2))

def draw_flag_pole(surface, x, y):
    """Draw flag pole"""
    s = 3
    # Pole
    pygame.draw.rect(surface, COL_POLE_GRAY, (x + 7*s, y, 2*s, TILE_SIZE))
    # Ball on top
    pygame.draw.rect(surface, COL_BUSH_GREEN, (x + 5*s, y, 6*s, 6*s))

def draw_flag(surface, x, y):
    """Draw the actual flag"""
    s = 3
    pygame.draw.rect(surface, COL_FLAG_GREEN, (x, y, 8*s, 6*s))

# =============================================================================
# GAME CLASSES
# =============================================================================

class Mario:
    """Player character with authentic SMB1 physics"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.facing_right = True
        self.on_ground = False
        self.jumping = False
        self.jump_held = False
        self.state = MARIO_SMALL
        self.invincible = 0  # Invincibility frames after damage
        self.star_power = 0  # Star power timer
        self.animation_frame = 0
        self.animation_timer = 0
        self.dead = False
        self.death_timer = 0
        self.win_state = False
        self.growing = 0  # Power-up animation timer
        
    def set_state(self, state):
        """Change Mario's power state"""
        old_state = self.state
        self.state = state
        if state == MARIO_SMALL:
            self.height = TILE_SIZE
        else:
            self.height = TILE_SIZE * 2
            if old_state == MARIO_SMALL:
                self.y -= TILE_SIZE  # Adjust position when growing
                self.growing = 60  # Animation frames
    
    def take_damage(self):
        """Handle Mario taking damage"""
        if self.invincible > 0 or self.star_power > 0:
            return
        
        if self.state == MARIO_SMALL:
            self.dead = True
            self.vel_y = -12
            self.death_timer = 180
        else:
            self.state = MARIO_SMALL
            self.height = TILE_SIZE
            self.invincible = 120
    
    def update(self, keys, level):
        """Update Mario with authentic SMB1 physics"""
        if self.dead:
            self.vel_y += GRAVITY
            self.y += self.vel_y
            self.death_timer -= 1
            return
        
        if self.growing > 0:
            self.growing -= 1
            return
        
        if self.win_state:
            # Slide down flagpole
            if self.vel_y < 5:
                self.vel_y = 5
            self.y += self.vel_y
            return
        
        # Decrement timers
        if self.invincible > 0:
            self.invincible -= 1
        if self.star_power > 0:
            self.star_power -= 1
        
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_z]
        
        # Horizontal movement with acceleration
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.facing_right = False
            accel = RUN_ACCEL if running else WALK_ACCEL
            max_speed = RUN_SPEED if running else WALK_SPEED
            
            # Check for skid
            if self.vel_x > 0 and self.on_ground:
                self.vel_x -= SKID_DECEL
            else:
                self.vel_x -= accel
                if self.vel_x < -max_speed:
                    self.vel_x = -max_speed
                    
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.facing_right = True
            accel = RUN_ACCEL if running else WALK_ACCEL
            max_speed = RUN_SPEED if running else WALK_SPEED
            
            # Check for skid
            if self.vel_x < 0 and self.on_ground:
                self.vel_x += SKID_DECEL
            else:
                self.vel_x += accel
                if self.vel_x > max_speed:
                    self.vel_x = max_speed
        else:
            # Apply friction
            if self.on_ground:
                self.vel_x *= FRICTION
            else:
                self.vel_x *= AIR_FRICTION
            
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0
        
        # Jumping with variable height
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_x] or keys[pygame.K_UP]
        
        if jump_pressed:
            if self.on_ground and not self.jump_held:
                self.vel_y = JUMP_VELOCITY
                self.on_ground = False
                self.jumping = True
                self.jump_held = True
            elif self.jumping and self.vel_y < 0:
                # Variable jump height - lower gravity while holding
                pass
        else:
            self.jump_held = False
            if self.jumping and self.vel_y < 0:
                self.jumping = False
        
        # Apply gravity (variable based on jump hold)
        if self.jumping and jump_pressed and self.vel_y < 0:
            self.vel_y += JUMP_HOLD_GRAVITY
        else:
            self.vel_y += GRAVITY
        
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        
        # Move horizontally and check collisions
        self.x += self.vel_x
        self.handle_horizontal_collisions(level)
        
        # Move vertically and check collisions
        self.y += self.vel_y
        self.handle_vertical_collisions(level)
        
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 6:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
        # Prevent falling off left edge
        if self.x < 0:
            self.x = 0
            self.vel_x = 0
    
    def handle_horizontal_collisions(self, level):
        """Handle horizontal tile collisions"""
        mario_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for tile in level.get_solid_tiles():
            tile_rect = pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if mario_rect.colliderect(tile_rect):
                if self.vel_x > 0:  # Moving right
                    self.x = tile_rect.left - self.width
                elif self.vel_x < 0:  # Moving left
                    self.x = tile_rect.right
                self.vel_x = 0
    
    def handle_vertical_collisions(self, level):
        """Handle vertical tile collisions"""
        mario_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = False
        
        for tile in level.get_solid_tiles():
            tile_rect = pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if mario_rect.colliderect(tile_rect):
                if self.vel_y > 0:  # Falling
                    self.y = tile_rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.jumping = False
                elif self.vel_y < 0:  # Jumping up
                    self.y = tile_rect.bottom
                    self.vel_y = 0
                    # Hit block from below
                    level.hit_block(tile[0], tile[1], self)
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface, camera_x):
        """Draw Mario"""
        x = self.x - camera_x
        
        # Blinking when invincible
        if self.invincible > 0 and (self.invincible // 4) % 2 == 0:
            return
        
        # Star power color cycling would go here
        
        if self.state == MARIO_SMALL:
            draw_mario_small(surface, x, self.y, self.facing_right, self.animation_frame)
        else:
            draw_mario_big(surface, x, self.y, self.facing_right, self.animation_frame, self.state == MARIO_FIRE)


class Enemy:
    """Base enemy class"""
    
    def __init__(self, x, y, enemy_type="goomba"):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.vel_x = -1.5
        self.vel_y = 0
        self.enemy_type = enemy_type
        self.alive = True
        self.squashed = False
        self.squash_timer = 0
        self.facing_right = False
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_shell = False
        self.shell_moving = False
    
    def update(self, level):
        """Update enemy"""
        if not self.alive:
            return
        
        if self.squashed:
            self.squash_timer -= 1
            if self.squash_timer <= 0:
                self.alive = False
            return
        
        # Apply gravity
        self.vel_y += GRAVITY * 0.5
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        
        # Move
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Check collisions with tiles
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for tile in level.get_solid_tiles():
            tile_rect = pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if enemy_rect.colliderect(tile_rect):
                if self.vel_y > 0:
                    self.y = tile_rect.top - self.height
                    self.vel_y = 0
                elif self.vel_x != 0:
                    self.vel_x = -self.vel_x
                    self.facing_right = not self.facing_right
        
        # Animation
        self.animation_timer += 1
        if self.animation_timer >= 8:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def stomp(self):
        """Handle being stomped by Mario"""
        if self.enemy_type == "goomba":
            self.squashed = True
            self.squash_timer = 30
            self.height = TILE_SIZE // 2
            self.y += TILE_SIZE // 2
        elif self.enemy_type == "koopa":
            if self.is_shell:
                # Kick shell
                self.shell_moving = not self.shell_moving
                if self.shell_moving:
                    self.vel_x = 8 if self.facing_right else -8
                else:
                    self.vel_x = 0
            else:
                # Enter shell
                self.is_shell = True
                self.vel_x = 0
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface, camera_x):
        """Draw enemy"""
        if not self.alive:
            return
        
        x = self.x - camera_x
        
        if self.squashed:
            # Draw squashed goomba
            pygame.draw.rect(surface, COL_GOOMBA, (x, self.y, self.width, self.height))
        elif self.is_shell:
            draw_shell(surface, x, self.y)
        elif self.enemy_type == "goomba":
            draw_goomba(surface, x, self.y, self.animation_frame)
        elif self.enemy_type == "koopa":
            draw_koopa(surface, x, self.y, self.facing_right, self.animation_frame)


class PowerUp:
    """Power-up item class"""
    
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.target_y = y  # For emerging animation
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.vel_x = 0
        self.vel_y = 0
        self.powerup_type = powerup_type
        self.active = True
        self.emerging = True
        self.animation_frame = 0
        self.animation_timer = 0
    
    def update(self, level):
        """Update power-up"""
        if not self.active:
            return
        
        if self.emerging:
            self.y -= 1
            if self.y <= self.target_y - TILE_SIZE:
                self.emerging = False
                if self.powerup_type in [POWERUP_MUSHROOM, POWERUP_1UP]:
                    self.vel_x = 2
            return
        
        # Movement for mushrooms
        if self.powerup_type in [POWERUP_MUSHROOM, POWERUP_1UP]:
            self.vel_y += GRAVITY * 0.5
            self.x += self.vel_x
            self.y += self.vel_y
            
            # Collisions
            rect = pygame.Rect(self.x, self.y, self.width, self.height)
            for tile in level.get_solid_tiles():
                tile_rect = pygame.Rect(tile[0] * TILE_SIZE, tile[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(tile_rect):
                    if self.vel_y > 0:
                        self.y = tile_rect.top - self.height
                        self.vel_y = 0
                    elif self.vel_x != 0:
                        self.vel_x = -self.vel_x
        
        # Animation for fire flower and star
        self.animation_timer += 1
        if self.animation_timer >= 4:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 8
    
    def collect(self, mario):
        """Handle collection by Mario"""
        if self.powerup_type == POWERUP_MUSHROOM:
            if mario.state == MARIO_SMALL:
                mario.set_state(MARIO_BIG)
            return 1000
        elif self.powerup_type == POWERUP_FIREFLOWER:
            mario.set_state(MARIO_FIRE)
            return 1000
        elif self.powerup_type == POWERUP_STAR:
            mario.star_power = 600  # 10 seconds
            return 1000
        elif self.powerup_type == POWERUP_1UP:
            return -1  # Signal for 1-up
        return 0
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surface, camera_x):
        """Draw power-up"""
        if not self.active:
            return
        
        x = self.x - camera_x
        
        if self.powerup_type == POWERUP_MUSHROOM:
            draw_mushroom(surface, x, self.y, False)
        elif self.powerup_type == POWERUP_1UP:
            draw_mushroom(surface, x, self.y, True)
        elif self.powerup_type == POWERUP_FIREFLOWER:
            draw_fire_flower(surface, x, self.y, self.animation_frame)
        elif self.powerup_type == POWERUP_STAR:
            draw_star(surface, x, self.y, self.animation_frame)


class Coin:
    """Collectible coin class"""
    
    def __init__(self, x, y, from_block=False):
        self.x = x
        self.y = y
        self.start_y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.active = True
        self.animation_frame = 0
        self.animation_timer = 0
        self.from_block = from_block
        self.rising = from_block
        self.rise_vel = -12 if from_block else 0
    
    def update(self):
        """Update coin"""
        if not self.active:
            return
        
        if self.rising:
            self.rise_vel += 0.8
            self.y += self.rise_vel
            if self.y >= self.start_y:
                self.active = False
            return
        
        self.animation_timer += 1
        if self.animation_timer >= 6:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 8
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x + 12, self.y + 6, self.width - 24, self.height - 12)
    
    def draw(self, surface, camera_x):
        """Draw coin"""
        if not self.active:
            return
        
        x = self.x - camera_x
        draw_coin(surface, x, self.y, self.animation_frame)


class Level:
    """Level class containing all tiles and entities"""
    
    def __init__(self, level_num=1):
        self.tiles = {}  # Dictionary of (x, y): tile_type
        self.enemies = []
        self.powerups = []
        self.coins = []
        self.decorations = []  # Clouds, bushes, hills
        self.level_width = 0
        self.level_height = SCREEN_HEIGHT // TILE_SIZE
        self.flag_x = 0
        self.animation_frame = 0
        self.animation_timer = 0
        
        self.load_level(level_num)
    
    def load_level(self, level_num):
        """Load level data"""
        # Clear existing
        self.tiles.clear()
        self.enemies.clear()
        self.powerups.clear()
        self.coins.clear()
        self.decorations.clear()
        
        ground_y = self.level_height - 2
        
        if level_num == 1:
            self.level_width = 212  # Tiles wide
            
            # Ground sections with gaps
            self.add_ground_section(0, 69, ground_y)
            self.add_ground_section(71, 86, ground_y)
            self.add_ground_section(89, 153, ground_y)
            self.add_ground_section(155, self.level_width, ground_y)
            
            # Question blocks
            self.add_tile(16, ground_y - 4, TILE_QUESTION)  # Coin
            self.add_tile(21, ground_y - 4, TILE_BRICK)
            self.add_tile(22, ground_y - 4, TILE_QUESTION)  # Mushroom
            self.add_tile(23, ground_y - 4, TILE_BRICK)
            self.add_tile(24, ground_y - 4, TILE_QUESTION)  # Coin
            self.add_tile(22, ground_y - 8, TILE_QUESTION)  # Coin
            
            # More blocks
            self.add_tile(77, ground_y - 4, TILE_QUESTION)  # Mushroom
            self.add_tile(79, ground_y - 4, TILE_BRICK)
            self.add_tile(80, ground_y - 8, TILE_BRICK)
            self.add_tile(81, ground_y - 8, TILE_BRICK)
            self.add_tile(82, ground_y - 8, TILE_BRICK)
            self.add_tile(83, ground_y - 8, TILE_BRICK)
            self.add_tile(84, ground_y - 8, TILE_BRICK)
            self.add_tile(85, ground_y - 8, TILE_BRICK)
            self.add_tile(86, ground_y - 8, TILE_BRICK)
            self.add_tile(87, ground_y - 8, TILE_BRICK)
            
            self.add_tile(91, ground_y - 8, TILE_BRICK)
            self.add_tile(92, ground_y - 8, TILE_BRICK)
            self.add_tile(93, ground_y - 8, TILE_BRICK)
            self.add_tile(94, ground_y - 8, TILE_QUESTION)  # Coin
            self.add_tile(94, ground_y - 4, TILE_BRICK)
            
            # Pipes
            self.add_pipe(28, ground_y - 2, 2)
            self.add_pipe(38, ground_y - 3, 3)
            self.add_pipe(46, ground_y - 4, 4)
            self.add_pipe(57, ground_y - 4, 4)
            self.add_pipe(163, ground_y - 2, 2)
            self.add_pipe(179, ground_y - 2, 2)
            
            # Stairs at end
            for i in range(8):
                for j in range(i + 1):
                    self.add_tile(134 + i, ground_y - 1 - j, TILE_BLOCK)
            
            for i in range(8):
                for j in range(8 - i):
                    self.add_tile(148 + i, ground_y - 1 - j, TILE_BLOCK)
            
            # Final staircase
            for i in range(8):
                for j in range(i + 1):
                    self.add_tile(181 + i, ground_y - 1 - j, TILE_BLOCK)
            
            # Flag pole
            self.flag_x = 198
            for i in range(10):
                self.add_tile(198, ground_y - 2 - i, TILE_FLAG_POLE)
            self.add_tile(198, ground_y - 12, TILE_FLAG_TOP)
            
            # Enemies
            self.enemies.append(Enemy(22 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(40 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(51 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(52.5 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(80 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "koopa"))
            self.enemies.append(Enemy(97 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(98.5 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(107 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(108.5 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(124 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            self.enemies.append(Enemy(125.5 * TILE_SIZE, (ground_y - 1) * TILE_SIZE, "goomba"))
            
            # Decorations
            self.decorations.append(("cloud", 8 * TILE_SIZE, 3 * TILE_SIZE))
            self.decorations.append(("cloud", 19 * TILE_SIZE, 2 * TILE_SIZE))
            self.decorations.append(("cloud", 36 * TILE_SIZE, 3 * TILE_SIZE))
            self.decorations.append(("cloud", 56 * TILE_SIZE, 2 * TILE_SIZE))
            self.decorations.append(("bush", 11 * TILE_SIZE, (ground_y) * TILE_SIZE - 18))
            self.decorations.append(("bush", 41 * TILE_SIZE, (ground_y) * TILE_SIZE - 18))
            self.decorations.append(("hill", 0, (ground_y) * TILE_SIZE - 36))
            self.decorations.append(("hill", 48 * TILE_SIZE, (ground_y) * TILE_SIZE - 36))
        
        elif level_num == 2:
            self.level_width = 220
            self.add_ground_section(0, self.level_width, ground_y)
            
            # Lots of question blocks
            for i in range(10):
                self.add_tile(10 + i * 8, ground_y - 4, TILE_QUESTION)
            
            # Brick ceiling sections
            for i in range(20):
                self.add_tile(30 + i, ground_y - 8, TILE_BRICK)
            
            # Pipe maze
            self.add_pipe(60, ground_y - 4, 4)
            self.add_pipe(70, ground_y - 6, 6)
            self.add_pipe(80, ground_y - 4, 4)
            self.add_pipe(90, ground_y - 8, 8)
            
            # Enemies
            for i in range(15):
                self.enemies.append(Enemy((20 + i * 12) * TILE_SIZE, (ground_y - 1) * TILE_SIZE, 
                                         "goomba" if i % 3 != 0 else "koopa"))
            
            # Flag
            self.flag_x = 210
            for i in range(10):
                self.add_tile(210, ground_y - 2 - i, TILE_FLAG_POLE)
            self.add_tile(210, ground_y - 12, TILE_FLAG_TOP)
        
        elif level_num == 3:
            self.level_width = 250
            
            # Platform level with gaps
            self.add_ground_section(0, 30, ground_y)
            self.add_ground_section(35, 60, ground_y)
            self.add_ground_section(65, 90, ground_y)
            self.add_ground_section(95, 130, ground_y)
            self.add_ground_section(135, 170, ground_y)
            self.add_ground_section(175, self.level_width, ground_y)
            
            # Floating platforms
            for i in range(5):
                for j in range(6):
                    self.add_tile(15 + i + (j * 25), ground_y - 5, TILE_BRICK)
            
            # Question blocks
            for i in range(8):
                self.add_tile(20 + i * 20, ground_y - 8, TILE_QUESTION)
            
            # Lots of enemies
            for i in range(20):
                self.enemies.append(Enemy((10 + i * 10) * TILE_SIZE, (ground_y - 1) * TILE_SIZE, 
                                         "goomba" if i % 2 == 0 else "koopa"))
            
            # Flag
            self.flag_x = 240
            for i in range(10):
                self.add_tile(240, ground_y - 2 - i, TILE_FLAG_POLE)
            self.add_tile(240, ground_y - 12, TILE_FLAG_TOP)
    
    def add_ground_section(self, start_x, end_x, y):
        """Add a section of ground"""
        for x in range(start_x, end_x):
            self.add_tile(x, y, TILE_GROUND)
            self.add_tile(x, y + 1, TILE_GROUND)
    
    def add_tile(self, x, y, tile_type):
        """Add a single tile"""
        self.tiles[(x, y)] = tile_type
    
    def add_pipe(self, x, y, height):
        """Add a pipe of given height"""
        # Top of pipe
        self.add_tile(x, y, TILE_PIPE_TL)
        self.add_tile(x + 1, y, TILE_PIPE_TR)
        # Body of pipe
        for i in range(1, height):
            self.add_tile(x, y + i, TILE_PIPE_L)
            self.add_tile(x + 1, y + i, TILE_PIPE_R)
    
    def get_solid_tiles(self):
        """Get list of solid tile positions"""
        solid_types = [TILE_GROUND, TILE_BRICK, TILE_QUESTION, TILE_QUESTION_EMPTY, 
                       TILE_BLOCK, TILE_PIPE_TL, TILE_PIPE_TR, TILE_PIPE_L, TILE_PIPE_R]
        return [(x, y) for (x, y), t in self.tiles.items() if t in solid_types]
    
    def hit_block(self, x, y, mario):
        """Handle Mario hitting a block from below"""
        if (x, y) not in self.tiles:
            return
        
        tile_type = self.tiles[(x, y)]
        
        if tile_type == TILE_QUESTION:
            self.tiles[(x, y)] = TILE_QUESTION_EMPTY
            # Spawn appropriate power-up or coin
            # For simplicity, alternate between coin and mushroom
            if random.random() < 0.7:
                self.coins.append(Coin(x * TILE_SIZE, y * TILE_SIZE, from_block=True))
            else:
                powerup_type = POWERUP_FIREFLOWER if mario.state != MARIO_SMALL else POWERUP_MUSHROOM
                self.powerups.append(PowerUp(x * TILE_SIZE, y * TILE_SIZE, powerup_type))
        
        elif tile_type == TILE_BRICK:
            if mario.state != MARIO_SMALL:
                # Break brick
                del self.tiles[(x, y)]
                # Could spawn brick particles here
            else:
                # Just bump it
                pass
    
    def update(self):
        """Update level animations and entities"""
        self.animation_timer += 1
        if self.animation_timer >= 4:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 16
        
        for enemy in self.enemies:
            enemy.update(self)
        
        for powerup in self.powerups:
            powerup.update(self)
        
        for coin in self.coins:
            coin.update()
        
        # Remove inactive items
        self.powerups = [p for p in self.powerups if p.active]
        self.coins = [c for c in self.coins if c.active or c.rising]
    
    def draw(self, surface, camera_x):
        """Draw all level elements"""
        # Background
        surface.fill(COL_SKY)
        
        # Decorations (behind tiles)
        for dec_type, dec_x, dec_y in self.decorations:
            x = dec_x - camera_x
            if -200 < x < SCREEN_WIDTH + 200:
                if dec_type == "cloud":
                    draw_cloud(surface, x, dec_y)
                elif dec_type == "bush":
                    draw_bush(surface, x, dec_y)
                elif dec_type == "hill":
                    draw_hill(surface, x, dec_y, 2)
        
        # Tiles
        for (tx, ty), tile_type in self.tiles.items():
            x = tx * TILE_SIZE - camera_x
            y = ty * TILE_SIZE
            
            # Only draw visible tiles
            if -TILE_SIZE < x < SCREEN_WIDTH + TILE_SIZE:
                if tile_type == TILE_GROUND:
                    draw_ground(surface, x, y)
                elif tile_type == TILE_BRICK:
                    draw_brick(surface, x, y)
                elif tile_type == TILE_QUESTION:
                    draw_question_block(surface, x, y, False, self.animation_frame)
                elif tile_type == TILE_QUESTION_EMPTY:
                    draw_question_block(surface, x, y, True)
                elif tile_type == TILE_BLOCK:
                    draw_ground(surface, x, y)
                elif tile_type == TILE_PIPE_TL:
                    draw_pipe(surface, x, y, True, True)
                elif tile_type == TILE_PIPE_TR:
                    draw_pipe(surface, x, y, True, False)
                elif tile_type == TILE_PIPE_L:
                    draw_pipe(surface, x, y, False, True)
                elif tile_type == TILE_PIPE_R:
                    draw_pipe(surface, x, y, False, False)
                elif tile_type in [TILE_FLAG_POLE, TILE_FLAG_TOP]:
                    draw_flag_pole(surface, x, y)
        
        # Coins
        for coin in self.coins:
            coin.draw(surface, camera_x)
        
        # Power-ups
        for powerup in self.powerups:
            powerup.draw(surface, camera_x)
        
        # Enemies
        for enemy in self.enemies:
            enemy.draw(surface, camera_x)


# =============================================================================
# MAIN GAME CLASS
# =============================================================================

class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultra Mario 2D Bros")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = STATE_MENU
        
        # Fonts
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        # Game variables
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.current_level = 1
        self.max_levels = 3
        self.time = 400
        self.time_timer = 0
        
        # Game objects
        self.mario = None
        self.level = None
        self.camera_x = 0
        
        # Menu
        self.menu_selection = 0
        self.menu_timer = 0
    
    def reset_game(self):
        """Reset game to initial state"""
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.current_level = 1
        self.load_level()
    
    def load_level(self):
        """Load current level"""
        self.level = Level(self.current_level)
        ground_y = (SCREEN_HEIGHT // TILE_SIZE) - 2
        self.mario = Mario(3 * TILE_SIZE, (ground_y - 2) * TILE_SIZE)
        self.camera_x = 0
        self.time = 400
        self.time_timer = 0
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.menu_selection = (self.menu_selection - 1) % 2
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.menu_selection = (self.menu_selection + 1) % 2
                    elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_x]:
                        if self.menu_selection == 0:
                            self.reset_game()
                            self.state = STATE_PLAYING
                        else:
                            self.running = False
                elif self.state == STATE_PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_PAUSED
                    elif event.key == pygame.K_p:
                        self.state = STATE_PAUSED
                elif self.state == STATE_PAUSED:
                    if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                        self.state = STATE_PLAYING
                elif self.state == STATE_GAME_OVER:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.state = STATE_MENU
                elif self.state == STATE_LEVEL_CLEAR:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.current_level += 1
                        if self.current_level > self.max_levels:
                            self.state = STATE_WIN
                        else:
                            self.load_level()
                            self.state = STATE_PLAYING
                elif self.state == STATE_WIN:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                        self.state = STATE_MENU
    
    def update(self):
        """Update game state"""
        if self.state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            
            # Update timer
            self.time_timer += 1
            if self.time_timer >= 24:  # About 2.5 seconds per time unit (authentic timing)
                self.time_timer = 0
                self.time -= 1
                if self.time <= 0:
                    self.mario.dead = True
                    self.mario.vel_y = -12
            
            # Update Mario
            self.mario.update(keys, self.level)
            
            # Check death
            if self.mario.dead:
                if self.mario.death_timer <= 0:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = STATE_GAME_OVER
                    else:
                        self.load_level()
                return
            
            # Check falling off screen
            if self.mario.y > SCREEN_HEIGHT:
                self.mario.dead = True
                self.mario.death_timer = 60
            
            # Check flag reached
            if self.mario.x >= self.level.flag_x * TILE_SIZE - TILE_SIZE:
                if not self.mario.win_state:
                    self.mario.win_state = True
                    self.mario.vel_y = 3
                    self.score += self.time * 50
                elif self.mario.y >= (SCREEN_HEIGHT // TILE_SIZE - 3) * TILE_SIZE:
                    self.state = STATE_LEVEL_CLEAR
            
            # Update level
            self.level.update()
            
            # Check enemy collisions
            for enemy in self.level.enemies:
                if not enemy.alive or enemy.squashed:
                    continue
                
                mario_rect = self.mario.get_rect()
                enemy_rect = enemy.get_rect()
                
                if mario_rect.colliderect(enemy_rect):
                    # Check if stomping
                    if self.mario.vel_y > 0 and mario_rect.bottom < enemy_rect.centery + 10:
                        enemy.stomp()
                        self.mario.vel_y = -8  # Bounce
                        self.score += 100
                    else:
                        if not enemy.is_shell or enemy.shell_moving:
                            self.mario.take_damage()
            
            # Check power-up collisions
            for powerup in self.level.powerups:
                if not powerup.active or powerup.emerging:
                    continue
                
                if self.mario.get_rect().colliderect(powerup.get_rect()):
                    points = powerup.collect(self.mario)
                    powerup.active = False
                    if points == -1:  # 1-up
                        self.lives += 1
                    else:
                        self.score += points
            
            # Check coin collisions
            for coin in self.level.coins:
                if not coin.active or coin.rising:
                    continue
                
                if self.mario.get_rect().colliderect(coin.get_rect()):
                    coin.active = False
                    self.coins += 1
                    self.score += 200
                    if self.coins >= 100:
                        self.coins = 0
                        self.lives += 1
            
            # Update camera
            target_x = self.mario.x - SCREEN_WIDTH // 3
            self.camera_x = max(0, min(target_x, self.level.level_width * TILE_SIZE - SCREEN_WIDTH))
        
        elif self.state == STATE_MENU:
            self.menu_timer += 1
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Score
        score_text = self.font_small.render(f"MARIO", True, COL_WHITE)
        self.screen.blit(score_text, (50, 20))
        score_val = self.font_small.render(f"{self.score:06d}", True, COL_WHITE)
        self.screen.blit(score_val, (50, 45))
        
        # Coins
        coin_text = self.font_small.render(f"x{self.coins:02d}", True, COL_WHITE)
        draw_coin(self.screen, 250, 30, self.level.animation_frame if self.level else 0)
        self.screen.blit(coin_text, (290, 35))
        
        # World
        world_text = self.font_small.render(f"WORLD", True, COL_WHITE)
        self.screen.blit(world_text, (420, 20))
        world_val = self.font_small.render(f"1-{self.current_level}", True, COL_WHITE)
        self.screen.blit(world_val, (435, 45))
        
        # Time
        time_text = self.font_small.render(f"TIME", True, COL_WHITE)
        self.screen.blit(time_text, (600, 20))
        time_val = self.font_small.render(f"{self.time:03d}", True, COL_WHITE)
        self.screen.blit(time_val, (610, 45))
        
        # Lives
        lives_text = self.font_small.render(f"x{self.lives}", True, COL_WHITE)
        self.screen.blit(lives_text, (710, 35))
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(COL_BLACK)
        
        # Title
        title1 = self.font_large.render("ULTRA MARIO", True, COL_MUSHROOM_RED)
        title2 = self.font_large.render("2D BROS", True, COL_MUSHROOM_RED)
        self.screen.blit(title1, (SCREEN_WIDTH // 2 - title1.get_width() // 2, 150))
        self.screen.blit(title2, (SCREEN_WIDTH // 2 - title2.get_width() // 2, 220))
        
        # Copyright
        copy_text = self.font_small.render("© TEAM FLAMES / SAMSOFT", True, COL_COIN)
        self.screen.blit(copy_text, (SCREEN_WIDTH // 2 - copy_text.get_width() // 2, 310))
        
        # Menu options
        options = ["1 PLAYER GAME", "QUIT"]
        for i, option in enumerate(options):
            color = COL_WHITE if i == self.menu_selection else (150, 150, 150)
            text = self.font_medium.render(option, True, color)
            y = 400 + i * 60
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        
        # Cursor (Mario)
        cursor_y = 400 + self.menu_selection * 60
        draw_mario_small(self.screen, SCREEN_WIDTH // 2 - 150, cursor_y)
        
        # Blinking "Press Start"
        if (self.menu_timer // 30) % 2 == 0:
            start_text = self.font_small.render("PRESS ENTER", True, COL_WHITE)
            self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 550))
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(COL_BLACK)
        
        text = self.font_large.render("GAME OVER", True, COL_MUSHROOM_RED)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250))
        
        score_text = self.font_medium.render(f"FINAL SCORE: {self.score}", True, COL_WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 350))
        
        continue_text = self.font_small.render("PRESS ENTER TO CONTINUE", True, COL_WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 450))
    
    def draw_level_clear(self):
        """Draw level clear screen"""
        self.screen.fill(COL_BLACK)
        
        text = self.font_large.render("LEVEL CLEAR!", True, COL_COIN)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200))
        
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, COL_WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 320))
        
        continue_text = self.font_small.render("PRESS ENTER TO CONTINUE", True, COL_WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 450))
    
    def draw_win(self):
        """Draw win screen"""
        self.screen.fill(COL_BLACK)
        
        text1 = self.font_large.render("CONGRATULATIONS!", True, COL_COIN)
        text2 = self.font_medium.render("YOU SAVED THE PRINCESS!", True, COL_MUSHROOM_RED)
        self.screen.blit(text1, (SCREEN_WIDTH // 2 - text1.get_width() // 2, 180))
        self.screen.blit(text2, (SCREEN_WIDTH // 2 - text2.get_width() // 2, 280))
        
        score_text = self.font_medium.render(f"FINAL SCORE: {self.score}", True, COL_WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 380))
        
        continue_text = self.font_small.render("PRESS ENTER TO RETURN TO MENU", True, COL_WHITE)
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, 480))
    
    def draw_paused(self):
        """Draw pause overlay"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        text = self.font_large.render("PAUSED", True, COL_WHITE)
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 280))
        
        resume_text = self.font_small.render("PRESS P OR ESC TO RESUME", True, COL_WHITE)
        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 380))
    
    def draw(self):
        """Main draw method"""
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_PLAYING or self.state == STATE_PAUSED:
            self.level.draw(self.screen, self.camera_x)
            self.mario.draw(self.screen, self.camera_x)
            self.draw_hud()
            if self.state == STATE_PAUSED:
                self.draw_paused()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
        elif self.state == STATE_LEVEL_CLEAR:
            self.draw_level_clear()
        elif self.state == STATE_WIN:
            self.draw_win()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    game = Game()
    game.run()
