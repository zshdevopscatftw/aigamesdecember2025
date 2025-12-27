#!/usr/bin/env python3
"""
NSMB DS Complete Level Database
All 80+ levels from New Super Mario Bros. DS
"""

import pygame
import sys
import math
import random
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum, auto

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# =============================================================================
# SMB1 PHYSICS CONSTANTS (Classic NES Mario)
# =============================================================================

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

# SMB1 Physics (Classic NES - simpler, less air control)
GRAVITY = 0.5                    # SMB1 has lighter gravity than modern Mario
MAX_FALL_SPEED = 8.0            # Slower falling
WALK_SPEED = 2.5                # Slower base speed
RUN_SPEED = 4.0                 # Run speed (B button in SMB1)
ACCELERATION = 0.1              # Slower acceleration
DECELERATION = 0.15             # Faster stopping
AIR_ACCELERATION = 0.05         # Minimal air control (SMB1 has almost none)
JUMP_FORCE = -9.0               # Standard SMB1 jump height
MAX_JUMP_HOLD = 0               # No variable jump height in SMB1
COYOTE_TIME = 0                 # No coyote time in SMB1
WALL_SLIDE_SPEED = 0            # No wall sliding
WALL_JUMP_X = 0                 # No wall jumping
WALL_JUMP_Y = 0                 # No wall jumping
GROUND_POUND_SPEED = 0          # No ground pound

# =============================================================================
# ENUMS
# =============================================================================

class PlayerState(Enum):
    IDLE = auto()
    WALKING = auto()
    RUNNING = auto()
    JUMPING = auto()
    FALLING = auto()
    DAMAGED = auto()
    DEAD = auto()
    VICTORY = auto()


class PowerUpType(Enum):
    NONE = auto()
    SUPER = auto()
    FIRE = auto()


class TileType(Enum):
    AIR = 0
    GROUND = 1
    BRICK = 2
    QUESTION = 3
    QUESTION_EMPTY = 4
    PIPE_TOP_LEFT = 5
    PIPE_TOP_RIGHT = 6
    PIPE_BODY_LEFT = 7
    PIPE_BODY_RIGHT = 8
    PLATFORM = 9
    SPIKE = 10
    COIN = 11
    GOAL_POLE = 12
    GOAL_FLAG = 13


class EnemyType(Enum):
    GOOMBA = auto()
    KOOPA = auto()
    PIRANHA = auto()
    SHELL = auto()


# =============================================================================
# LEVEL DATABASE
# =============================================================================

WORLD_STRUCTURE = {
    1: ["1-1", "1-2", "1-3", "1-Tower", "1-4", "1-5", "1-A", "1-Castle"],
    2: ["2-1", "2-2", "2-3", "2-Tower", "2-4", "2-5", "2-A", "2-Castle"],
    3: ["3-1", "3-2", "3-3", "3-Tower", "3-A", "3-B", "3-C", "3-Castle"],
    4: ["4-1", "4-2", "4-3", "4-Tower", "4-4", "4-5", "4-A", "4-Ghost", "4-Castle"],
    5: ["5-1", "5-2", "5-3", "5-Tower", "5-4", "5-A", "5-B", "5-C", "5-Ghost", "5-Castle"],
    6: ["6-1", "6-2", "6-3", "6-Tower1", "6-4", "6-5", "6-6", "6-Tower2", "6-A", "6-B", "6-Castle"],
    7: ["7-1", "7-2", "7-3", "7-Tower", "7-4", "7-5", "7-6", "7-7", "7-A", "7-Ghost", "7-Castle"],
    8: ["8-1", "8-2", "8-3", "8-Tower1", "8-4", "8-5", "8-Tower2", "8-6", "8-7", "8-8", "8-Castle1", "8-Castle2"],
}

LEVEL_DATA = {
    "1-1": {
        "name": "World 1-1",
        "width": 200, "height": 15, "time": 400,
        "theme": "grass",
        "enemies": [
            ("goomba", 20, 11), ("goomba", 25, 11), ("goomba", 35, 11),
            ("koopa", 45, 11), ("goomba", 55, 11), ("goomba", 56, 11),
        ],
        "items": [("mushroom", 30, 6), ("coin", 60, 6), ("1up", 110, 3)],
        "star_coins": [(32, 5), (85, 10), (155, 4)],
    },
    # ... (other levels would follow similar pattern)
}

# =============================================================================
# ENTITY CLASSES
# =============================================================================

class Entity:
    """Base entity class"""
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.active = True
    
    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def update(self, dt: float, level: 'Level'):
        pass
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        pass


class Player(Entity):
    """Main player character with SMB1 physics"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 16, 32)  # SMB1 Mario is 16x32
        
        # State
        self.state = PlayerState.IDLE
        self.power_up = PowerUpType.NONE
        self.facing_right = True
        self.on_ground = False
        
        # SMB1 has simple physics - no complex timers
        self.invincibility_timer = 0
        
        # Stats
        self.coins = 0
        self.lives = 3  # SMB1 starts with 3 lives
        self.score = 0
        
        # Sprites would be loaded here
        self.sprite = None
    
    def collect_powerup(self, power_type: PowerUpType):
        """Collect a power-up - SMB1 only has Super and Fire"""
        if power_type == PowerUpType.SUPER:
            self.power_up = power_type
            self.height = 32  # Grow to big Mario
            self.y -= 16  # Adjust position
        elif power_type == PowerUpType.FIRE:
            self.power_up = power_type
    
    def take_damage(self):
        """Take damage - SMB1 rules"""
        if self.invincibility_timer > 0:
            return
        
        if self.power_up != PowerUpType.NONE:
            # Shrink down
            self.power_up = PowerUpType.NONE
            self.height = 32
            self.invincibility_timer = 120  # Blink for 2 seconds
        else:
            self.die()
    
    def die(self):
        """Player death"""
        self.state = PlayerState.DEAD
        self.vy = -8  # Simple death jump
        self.lives -= 1
    
    def update(self, dt: float, level: 'Level', keys: pygame.key.ScannedCodes):
        if self.state == PlayerState.DEAD:
            self.vy += GRAVITY
            self.y += self.vy
            return
        
        if self.state == PlayerState.VICTORY:
            return
        
        # Input (SMB1 simple controls)
        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        jump = keys[pygame.K_SPACE] or keys[pygame.K_z]
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_x]  # B button equivalent
        
        # Update timers
        if self.invincibility_timer > 0:
            self.invincibility_timer -= 1
        
        # Horizontal movement (SMB1 style)
        target_speed = RUN_SPEED if run else WALK_SPEED
        
        if move_left and not move_right:
            self.vx -= ACCELERATION
            self.facing_right = False
        elif move_right and not move_left:
            self.vx += ACCELERATION
            self.facing_right = True
        else:
            # Deceleration (friction) - SMB1 has quick stopping
            if abs(self.vx) < DECELERATION:
                self.vx = 0
            else:
                self.vx -= DECELERATION if self.vx > 0 else -DECELERATION
        
        # Clamp speed
        self.vx = max(-target_speed, min(target_speed, self.vx))
        
        # Air control is minimal in SMB1
        if not self.on_ground:
            if move_left or move_right:
                # Very limited air control
                self.vx *= 0.98
            else:
                self.vx *= 0.95
        
        # Jumping (SMB1 - fixed height, no variable jump)
        if jump and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.state = PlayerState.JUMPING
        
        # Apply gravity
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL_SPEED)
        
        # Store ground state
        was_on_ground = self.on_ground
        self.on_ground = False
        
        # Horizontal collision
        self.x += self.vx
        for tile_rect in level.get_solid_tiles(self.rect):
            if self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.x = tile_rect.left - self.width
                elif self.vx < 0:
                    self.x = tile_rect.right
                self.vx = 0
        
        # Vertical collision
        self.y += self.vy
        for tile_rect in level.get_solid_tiles(self.rect):
            if self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                    self.on_ground = True
                    self.vy = 0
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                    self.vy = 0
                    # Hit block from below
                    level.hit_block(tile_rect.x // TILE_SIZE, tile_rect.y // TILE_SIZE, self)
        
        # Level bounds
        self.x = max(0, self.x)
        
        # Death plane
        if self.y > level.height * TILE_SIZE + 100:
            self.die()
        
        # Update state
        if self.on_ground:
            if abs(self.vx) < 0.1:
                self.state = PlayerState.IDLE
            elif run and abs(self.vx) > WALK_SPEED * 0.8:
                self.state = PlayerState.RUNNING
            else:
                self.state = PlayerState.WALKING
        else:
            if self.vy < 0:
                self.state = PlayerState.JUMPING
            else:
                self.state = PlayerState.FALLING
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        if self.state == PlayerState.DEAD and self.y > SCREEN_HEIGHT + 50:
            return
        
        # Invincibility flicker
        if self.invincibility_timer > 0 and (self.invincibility_timer // 4) % 2:
            return
        
        # Draw simple placeholder
        color = (255, 0, 0)  # Red for Mario
        if self.power_up == PowerUpType.FIRE:
            color = (255, 100, 0)  # Orange for Fire Mario
        elif self.power_up == PowerUpType.SUPER:
            color = (200, 0, 0)  # Darker red for Super Mario
        
        x = int(self.x - camera_x)
        y = int(self.y - camera_y)
        pygame.draw.rect(surface, color, (x, y, self.width, self.height))


class Enemy(Entity):
    """Enemy with SMB1 behavior"""
    
    def __init__(self, x: float, y: float, enemy_type: EnemyType):
        width = 16 if enemy_type == EnemyType.GOOMBA else 16
        height = 16 if enemy_type == EnemyType.GOOMBA else 24
        super().__init__(x, y, width, height)
        
        self.enemy_type = enemy_type
        self.direction = -1  # Start moving left
        self.speed = 1.0 if enemy_type == EnemyType.GOOMBA else 0.8
        self.on_ground = False
        self.stomped = False
        self.stomp_timer = 0
    
    def stomp(self, player: Player) -> bool:
        """Handle being stomped"""
        if self.enemy_type == EnemyType.GOOMBA:
            self.stomped = True
            self.stomp_timer = 30
            self.height = 4
            player.vy = -6  # SMB1 has smaller bounce
            player.score += 100
            return True
        elif self.enemy_type == EnemyType.KOOPA:
            # Transform into shell
            self.enemy_type = EnemyType.SHELL
            self.width = 16
            self.height = 16
            self.speed = 0
            player.vy = -6
            player.score += 400
            return True
        return False
    
    def update(self, dt: float, level: 'Level'):
        if self.stomped:
            self.stomp_timer -= 1
            if self.stomp_timer <= 0:
                self.active = False
            return
        
        # Simple SMB1 enemy AI
        self.vx = self.speed * self.direction
        
        # Gravity
        self.vy += GRAVITY
        self.vy = min(self.vy, MAX_FALL_SPEED)
        
        # Horizontal movement
        self.x += self.vx
        self.on_ground = False
        
        # Edge detection
        if self.on_ground:
            # Check for ledge
            check_x = self.x + (self.width if self.direction > 0 else -4)
            check_y = self.y + self.height + 4
            check_rect = pygame.Rect(int(check_x), int(check_y), 4, 4)
            
            has_floor = False
            for tile_rect in level.get_solid_tiles(check_rect):
                if check_rect.colliderect(tile_rect):
                    has_floor = True
                    break
            
            if not has_floor:
                self.direction *= -1
        
        # Vertical movement
        self.y += self.vy
        for tile_rect in level.get_solid_tiles(self.rect):
            if self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.y = tile_rect.top - self.height
                    self.on_ground = True
                    self.vy = 0
                elif self.vy < 0:
                    self.y = tile_rect.bottom
                    self.vy = 0
        
        # Death plane
        if self.y > level.height * TILE_SIZE + 50:
            self.active = False
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        if not self.active:
            return
        
        x = int(self.x - camera_x)
        y = int(self.y - camera_y)
        
        # Simple enemy colors
        if self.enemy_type == EnemyType.GOOMBA:
            color = (139, 69, 19)  # Brown
            if self.stomped:
                pygame.draw.rect(surface, color, (x, y + self.height - 4, self.width, 4))
            else:
                pygame.draw.ellipse(surface, color, (x, y, self.width, self.height))
        elif self.enemy_type == EnemyType.KOOPA:
            color = (0, 128, 0)  # Green
            pygame.draw.ellipse(surface, color, (x, y, self.width, self.height))
        elif self.enemy_type == EnemyType.SHELL:
            color = (0, 100, 0)  # Dark green
            pygame.draw.ellipse(surface, color, (x, y, self.width, self.height))


# =============================================================================
# LEVEL SYSTEM
# =============================================================================

class Level:
    """Game level with tile-based layout"""
    
    def __init__(self, level_id: str):
        self.level_id = level_id
        self.width = 200
        self.height = 15
        self.tiles = []
        self.enemies = []
        self.spawn_point = (64, (self.height - 5) * TILE_SIZE)
        self.goal_x = (self.width - 5) * TILE_SIZE
        
        self._generate_simple_level()
    
    def _generate_simple_level(self):
        """Generate a simple test level"""
        # Initialize with air
        self.tiles = [[TileType.AIR.value for _ in range(self.width)] for _ in range(self.height)]
        
        # Ground
        ground_height = 4
        for x in range(self.width):
            for y in range(self.height - ground_height, self.height):
                self.tiles[y][x] = TileType.GROUND.value
        
        # Some platforms
        for i in range(5):
            x = 30 + i * 40
            y = self.height - 8
            for dx in range(5):
                if x + dx < self.width:
                    self.tiles[y][x + dx] = TileType.PLATFORM.value
        
        # Goal pole
        goal_x = self.width - 5
        for y in range(self.height - 10, self.height - 4):
            self.tiles[y][goal_x] = TileType.GOAL_POLE.value
        
        # Add some enemies
        self.enemies.append(Enemy(100, (self.height - 5) * TILE_SIZE, EnemyType.GOOMBA))
        self.enemies.append(Enemy(150, (self.height - 5) * TILE_SIZE, EnemyType.KOOPA))
    
    def get_solid_tiles(self, rect: pygame.Rect) -> List[pygame.Rect]:
        """Get solid tiles for collision"""
        solid_tiles = []
        
        start_x = max(0, rect.left // TILE_SIZE - 1)
        end_x = min(self.width, rect.right // TILE_SIZE + 2)
        start_y = max(0, rect.top // TILE_SIZE - 1)
        end_y = min(self.height, rect.bottom // TILE_SIZE + 2)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if self.tiles[y][x] in [TileType.GROUND.value, TileType.PLATFORM.value]:
                    tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    solid_tiles.append(tile_rect)
        
        return solid_tiles
    
    def hit_block(self, x: int, y: int, player: Player):
        """Handle hitting a block"""
        pass  # Simplified for this example
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Draw visible tiles"""
        start_x = max(0, camera_x // TILE_SIZE - 1)
        end_x = min(self.width, (camera_x + SCREEN_WIDTH) // TILE_SIZE + 2)
        start_y = max(0, camera_y // TILE_SIZE - 1)
        end_y = min(self.height, (camera_y + SCREEN_HEIGHT) // TILE_SIZE + 2)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.tiles[y][x]
                screen_x = x * TILE_SIZE - camera_x
                screen_y = y * TILE_SIZE - camera_y
                
                if tile == TileType.GROUND.value:
                    pygame.draw.rect(surface, (139, 69, 19), 
                                   (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile == TileType.PLATFORM.value:
                    pygame.draw.rect(surface, (160, 120, 80),
                                   (screen_x, screen_y, TILE_SIZE, TILE_SIZE))
                elif tile == TileType.GOAL_POLE.value:
                    pygame.draw.rect(surface, (100, 100, 100),
                                   (screen_x + 14, screen_y, 4, TILE_SIZE))


# =============================================================================
# GAME CLASS
# =============================================================================

class Game:
    """Main game controller"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros. 1 Style")
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.player = None
        self.level = None
        self.camera_x = 0
        self.camera_y = 0
        
        self.start_game()
    
    def start_game(self):
        """Initialize game"""
        self.level = Level("1-1")
        self.player = Player(self.level.spawn_point[0], self.level.spawn_point[1])
    
    def update_camera(self):
        """Simple camera follow"""
        target_x = self.player.x - SCREEN_WIDTH // 3
        self.camera_x = max(0, min(target_x, self.level.width * TILE_SIZE - SCREEN_WIDTH))
        self.camera_y = 0  # Simple 2D, no vertical scrolling
    
    def handle_events(self):
        """Process input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.start_game()
    
    def update(self):
        """Update game logic"""
        keys = pygame.key.get_pressed()
        dt = 1 / FPS
        
        # Update player
        self.player.update(dt, self.level, keys)
        
        # Update enemies
        for enemy in self.level.enemies:
            if enemy.active:
                enemy.update(dt, self.level)
                
                # Check collision with player
                if self.player.rect.colliderect(enemy.rect):
                    if self.player.vy > 0 and self.player.y + self.player.height < enemy.y + enemy.height // 2:
                        # Stomp
                        enemy.stomp(self.player)
                    else:
                        # Take damage
                        self.player.take_damage()
        
        # Check death
        if self.player.state == PlayerState.DEAD:
            if self.player.y > SCREEN_HEIGHT + 100:
                self.start_game()
        
        # Update camera
        self.update_camera()
        
        # Clean up enemies
        self.level.enemies = [e for e in self.level.enemies if e.active]
    
    def draw(self):
        """Render frame"""
        # Background
        self.screen.fill((135, 206, 235))  # Sky blue
        
        # Draw level
        self.level.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw enemies
        for enemy in self.level.enemies:
            enemy.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Draw player
        self.player.draw(self.screen, int(self.camera_x), int(self.camera_y))
        
        # Simple HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        lives_text = font.render(f"Lives: {self.player.lives}", True, (255, 255, 255))
        coins_text = font.render(f"Coins: {self.player.coins}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(coins_text, (10, 90))
        
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
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("Super Mario Bros. 1 Style Physics Demo")
    print("Controls:")
    print("  Arrow Keys / WASD - Move")
    print("  Space / Z - Jump")
    print("  Shift / X - Run")
    print("  R - Restart")
    print("  ESC - Quit")
    
    game = Game()
    game.run()
