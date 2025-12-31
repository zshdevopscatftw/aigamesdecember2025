import pygame
import random
import math

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -12
MOVE_SPEED = 5
TILE_SIZE = 32

# Colors
SKY_BLUE = (92, 148, 252)
UNDERGROUND_BLACK = (0, 0, 0)
CASTLE_BLACK = (20, 20, 20)
WATER_BLUE = (0, 80, 180)
GROUND_BROWN = (180, 100, 50)
UNDERGROUND_BLUE = (60, 90, 180)
BRICK_ORANGE = (220, 120, 70)
BRICK_BLUE = (60, 100, 200)
QUESTION_YELLOW = (255, 220, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MARIO_RED = (255, 50, 50)
MARIO_BLUE = (30, 100, 255)
MARIO_SKIN = (255, 200, 150)
LAVA_ORANGE = (255, 100, 0)
CASTLE_GRAY = (100, 100, 100)
FLAGPOLE_GREEN = (0, 180, 0)

def darken(color, amount=40):
    return tuple(max(0, c - amount) for c in color)

def lighten(color, amount=40):
    return tuple(min(255, c + amount) for c in color)

# Level themes
THEMES = {
    "overworld": {"bg": SKY_BLUE, "ground": GROUND_BROWN, "brick": BRICK_ORANGE},
    "underground": {"bg": UNDERGROUND_BLACK, "ground": UNDERGROUND_BLUE, "brick": BRICK_BLUE},
    "castle": {"bg": CASTLE_BLACK, "ground": CASTLE_GRAY, "brick": CASTLE_GRAY},
    "water": {"bg": WATER_BLUE, "ground": GROUND_BROWN, "brick": BRICK_ORANGE},
    "athletic": {"bg": (150, 200, 255), "ground": GROUND_BROWN, "brick": BRICK_ORANGE},
}

class Mario:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.width = 16
        self.height = 32
        self.on_ground = False
        self.facing_right = True
        self.state = "small"
        self.jumping = False
        self.animation_frame = 0
        self.invincible = 0
        self.star_power = 0
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.fire_cooldown = 0
        self.swimming = False
        
    def update(self, keys, platforms, enemies, items, fireballs, level_width, theme, pipes):
        self.swimming = theme == "water"
        gravity = 0.2 if self.swimming else GRAVITY
        max_fall = 4 if self.swimming else 15
        jump_str = -6 if self.swimming else JUMP_STRENGTH
        
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED
            self.facing_right = True
            
        # Jumping/Swimming
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            if self.swimming:
                self.vel_y = -3
            elif self.on_ground:
                self.vel_y = jump_str
                self.on_ground = False
                self.jumping = True
                
        # Fire attack
        if (keys[pygame.K_x] or keys[pygame.K_LSHIFT]) and self.state == "fire" and self.fire_cooldown <= 0:
            direction = 1 if self.facing_right else -1
            fireballs.append(Fireball(self.x + 8, self.y + 16, direction))
            self.fire_cooldown = 20
            
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
            
        # Apply gravity
        self.vel_y += gravity
        if self.vel_y > max_fall:
            self.vel_y = max_fall
            
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Keep on screen
        if self.x < 0:
            self.x = 0
            
        # Fall death
        if self.y > SCREEN_HEIGHT + 50:
            self.lives -= 1
            if self.lives <= 0:
                return "game_over"
            return "died"
            
        # Platform collision
        self.on_ground = False
        for platform in platforms:
            if self.collides_with_platform(platform):
                # Bottom collision (landing)
                if self.vel_y > 0 and self.y + self.height - self.vel_y <= platform.y:
                    self.y = platform.y - self.height
                    self.on_ground = True
                    self.vel_y = 0
                    self.jumping = False
                # Top collision (hitting block)
                elif self.vel_y < 0 and self.y - self.vel_y >= platform.y + platform.height:
                    self.y = platform.y + platform.height
                    self.vel_y = 0
                    if platform.type == "question" and not platform.hit:
                        platform.hit = True
                        if platform.contains:
                            items.append(Item(platform.x, platform.y - 32, platform.contains))
                    elif platform.type == "brick" and self.state != "small":
                        platform.destroyed = True
                # Side collision
                elif self.vel_x > 0:
                    self.x = platform.x - self.width
                elif self.vel_x < 0:
                    self.x = platform.x + platform.width
                    
        # Pipe collision and entry
        for pipe in pipes:
            if self.collides_with_platform(pipe):
                if self.vel_y > 0 and self.y + self.height - self.vel_y <= pipe.y:
                    self.y = pipe.y - self.height
                    self.on_ground = True
                    self.vel_y = 0
                # Check for pipe entry
                if pipe.destination and keys[pygame.K_DOWN]:
                    if abs(self.x - pipe.x) < 20:
                        return ("warp", pipe.destination)
                        
        # Enemy collision
        if self.invincible <= 0 and self.star_power <= 0:
            for enemy in enemies:
                if enemy.alive and self.collides_with(enemy):
                    if self.vel_y > 0 and self.y + self.height < enemy.y + enemy.height:
                        self.vel_y = -10
                        if isinstance(enemy, Koopa):
                            if enemy.shell_mode:
                                enemy.kicked = True
                                enemy.vel_x = 5 if self.facing_right else -5
                            else:
                                enemy.shell_mode = True
                                enemy.vel_x = 0
                        else:
                            enemy.alive = False
                        self.score += 100
                    else:
                        if self.state == "fire":
                            self.state = "big"
                            self.invincible = 60
                        elif self.state == "big":
                            self.state = "small"
                            self.invincible = 60
                        else:
                            self.lives -= 1
                            if self.lives <= 0:
                                return "game_over"
                            return "died"
        elif self.star_power > 0:
            for enemy in enemies:
                if enemy.alive and self.collides_with(enemy):
                    enemy.alive = False
                    self.score += 200
                            
        # Item collision
        for item in items:
            if self.collides_with(item) and item.active:
                item.active = False
                if item.type == "coin":
                    self.coins += 1
                    self.score += 200
                    if self.coins >= 100:
                        self.coins = 0
                        self.lives += 1
                elif item.type == "mushroom":
                    if self.state == "small":
                        self.state = "big"
                    self.score += 1000
                elif item.type == "fire_flower":
                    self.state = "fire"
                    self.score += 1000
                elif item.type == "star":
                    self.star_power = 600
                    self.score += 1000
                elif item.type == "1up":
                    self.lives += 1
                    self.score += 0
                    
        self.animation_frame = (self.animation_frame + 1) % 30
        
        if self.invincible > 0:
            self.invincible -= 1
        if self.star_power > 0:
            self.star_power -= 1
            
        return "playing"
        
    def collides_with(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
                
    def collides_with_platform(self, platform):
        if hasattr(platform, 'destroyed') and platform.destroyed:
            return False
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y)
                
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        height = 32 if self.state != "small" else 24
        body_y = self.y + (32 - height)
        
        if self.invincible > 0 and self.invincible % 4 < 2:
            return
            
        # Star power rainbow effect
        if self.star_power > 0:
            colors = [(255,0,0), (255,165,0), (255,255,0), (0,255,0), (0,0,255)]
            body_color = colors[(self.animation_frame // 3) % len(colors)]
        elif self.state == "fire":
            body_color = WHITE
        else:
            body_color = MARIO_RED
            
        pygame.draw.rect(screen, body_color, (screen_x + 4, body_y, 8, height - 8))
        pygame.draw.rect(screen, MARIO_SKIN, (screen_x + 4, self.y + 4, 8, 8))
        
        hat_x = screen_x + 8 if self.facing_right else screen_x
        pygame.draw.rect(screen, MARIO_BLUE, (hat_x, self.y + 4, 8, 4))
        
        pygame.draw.rect(screen, body_color, (screen_x + 2, body_y + height - 8, 4, 8))
        pygame.draw.rect(screen, body_color, (screen_x + 10, body_y + height - 8, 4, 8))

class Platform:
    def __init__(self, x, y, width, height, type="ground", contains=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type
        self.contains = contains
        self.hit = False
        self.destroyed = False
        
    def draw(self, screen, camera_x, theme_colors):
        if self.destroyed:
            return
        screen_x = self.x - camera_x
        
        if screen_x < -self.width or screen_x > SCREEN_WIDTH:
            return
            
        if self.type == "ground":
            color = theme_colors["ground"]
            pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
            pygame.draw.rect(screen, darken(color, 20), (screen_x, self.y, self.width, self.height), 1)
        elif self.type == "brick":
            color = theme_colors["brick"]
            pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
            pygame.draw.rect(screen, darken(color), (screen_x, self.y, self.width, self.height), 2)
        elif self.type == "question":
            color = (100, 100, 100) if self.hit else QUESTION_YELLOW
            pygame.draw.rect(screen, color, (screen_x, self.y, self.width, self.height))
            pygame.draw.rect(screen, darken(color), (screen_x, self.y, self.width, self.height), 2)
            if not self.hit:
                font = pygame.font.Font(None, 24)
                text = font.render("?", True, (100, 50, 0))
                screen.blit(text, (screen_x + 10, self.y + 5))
        elif self.type == "block":
            pygame.draw.rect(screen, CASTLE_GRAY, (screen_x, self.y, self.width, self.height))
            pygame.draw.rect(screen, darken(CASTLE_GRAY), (screen_x, self.y, self.width, self.height), 2)

class Pipe:
    def __init__(self, x, y, height=64, destination=None):
        self.x = x
        self.y = y
        self.width = 48
        self.height = height
        self.destination = destination
        
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        if screen_x < -self.width or screen_x > SCREEN_WIDTH:
            return
        pygame.draw.rect(screen, GREEN, (screen_x, self.y, self.width, self.height))
        pygame.draw.rect(screen, DARK_GREEN, (screen_x - 4, self.y, self.width + 8, 24))
        pygame.draw.rect(screen, darken(GREEN), (screen_x, self.y, self.width, self.height), 2)

class Flagpole:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 300
        self.flag_y = y + 20
        
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        pygame.draw.rect(screen, FLAGPOLE_GREEN, (screen_x, self.y, 8, self.height))
        pygame.draw.circle(screen, (255, 215, 0), (screen_x + 4, self.y), 8)
        # Flag
        points = [(screen_x + 8, self.flag_y), (screen_x + 40, self.flag_y + 16), (screen_x + 8, self.flag_y + 32)]
        pygame.draw.polygon(screen, GREEN, points)

class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.vel_x = -2
        self.vel_y = 0
        self.alive = True
        self.animation_frame = 0
        
    def update(self, platforms):
        if not self.alive:
            return
        self.x += self.vel_x
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        for platform in platforms:
            if hasattr(platform, 'destroyed') and platform.destroyed:
                continue
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                
        self.animation_frame = (self.animation_frame + 1) % 60
        
    def draw(self, screen, camera_x):
        if not self.alive:
            return
        screen_x = self.x - camera_x
        if screen_x < -32 or screen_x > SCREEN_WIDTH + 32:
            return
        pygame.draw.ellipse(screen, (180, 100, 50), (screen_x, self.y, self.width, self.height))
        pygame.draw.ellipse(screen, WHITE, (screen_x + 3, self.y + 3, 4, 5))
        pygame.draw.ellipse(screen, WHITE, (screen_x + 9, self.y + 3, 4, 5))
        pygame.draw.ellipse(screen, BLACK, (screen_x + 4, self.y + 5, 2, 2))
        pygame.draw.ellipse(screen, BLACK, (screen_x + 10, self.y + 5, 2, 2))

class Koopa:
    def __init__(self, x, y, color="green"):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 24
        self.vel_x = -2
        self.vel_y = 0
        self.alive = True
        self.shell_mode = False
        self.kicked = False
        self.color = (0, 200, 0) if color == "green" else (200, 0, 0)
        
    def update(self, platforms):
        if not self.alive:
            return
        if self.shell_mode and self.kicked:
            self.x += self.vel_x
        elif not self.shell_mode:
            self.x += self.vel_x
            
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        for platform in platforms:
            if hasattr(platform, 'destroyed') and platform.destroyed:
                continue
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                
    def draw(self, screen, camera_x):
        if not self.alive:
            return
        screen_x = self.x - camera_x
        if screen_x < -32 or screen_x > SCREEN_WIDTH + 32:
            return
        if self.shell_mode:
            pygame.draw.ellipse(screen, self.color, (screen_x, self.y + 8, 16, 16))
        else:
            pygame.draw.ellipse(screen, self.color, (screen_x, self.y, 16, 16))
            pygame.draw.rect(screen, (255, 200, 150), (screen_x + 4, self.y + 12, 8, 12))

class PiranhaPlant:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_y = y
        self.width = 24
        self.height = 32
        self.alive = True
        self.timer = 0
        self.state = "hiding"
        
    def update(self, platforms):
        self.timer += 1
        if self.state == "hiding" and self.timer > 60:
            self.state = "rising"
            self.timer = 0
        elif self.state == "rising":
            self.y -= 1
            if self.y <= self.base_y - 32:
                self.state = "waiting"
                self.timer = 0
        elif self.state == "waiting" and self.timer > 90:
            self.state = "lowering"
            self.timer = 0
        elif self.state == "lowering":
            self.y += 1
            if self.y >= self.base_y:
                self.state = "hiding"
                self.timer = 0
                
    def draw(self, screen, camera_x):
        if not self.alive:
            return
        screen_x = self.x - camera_x
        pygame.draw.ellipse(screen, GREEN, (screen_x, self.y, 24, 16))
        pygame.draw.rect(screen, (0, 150, 0), (screen_x + 8, self.y + 10, 8, 32))
        # Teeth
        pygame.draw.rect(screen, WHITE, (screen_x + 4, self.y + 8, 4, 4))
        pygame.draw.rect(screen, WHITE, (screen_x + 16, self.y + 8, 4, 4))

class HammerBro:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 24
        self.vel_x = 1
        self.vel_y = 0
        self.alive = True
        self.timer = 0
        self.hammers = []
        
    def update(self, platforms):
        if not self.alive:
            return
        self.timer += 1
        
        # Movement
        self.x += self.vel_x
        if random.random() < 0.02:
            self.vel_x = -self.vel_x
        if random.random() < 0.01:
            self.vel_y = -8
            
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Throw hammer
        if self.timer % 60 == 0:
            self.hammers.append({"x": self.x, "y": self.y, "vel_x": -3, "vel_y": -6})
            
        # Update hammers
        for h in self.hammers:
            h["x"] += h["vel_x"]
            h["vel_y"] += 0.3
            h["y"] += h["vel_y"]
        self.hammers = [h for h in self.hammers if h["y"] < SCREEN_HEIGHT]
        
        for platform in platforms:
            if hasattr(platform, 'destroyed') and platform.destroyed:
                continue
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                
    def draw(self, screen, camera_x):
        if not self.alive:
            return
        screen_x = self.x - camera_x
        pygame.draw.rect(screen, (0, 150, 0), (screen_x, self.y, 16, 24))
        pygame.draw.rect(screen, WHITE, (screen_x + 2, self.y + 16, 12, 8))
        # Draw hammers
        for h in self.hammers:
            hx = h["x"] - camera_x
            pygame.draw.rect(screen, (139, 69, 19), (hx, h["y"], 8, 16))
            pygame.draw.rect(screen, (100, 100, 100), (hx - 2, h["y"], 12, 6))

class Bowser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 48
        self.vel_x = -1
        self.vel_y = 0
        self.alive = True
        self.health = 5
        self.timer = 0
        self.fireballs = []
        
    def update(self, platforms):
        if not self.alive:
            return
        self.timer += 1
        
        self.x += self.vel_x
        if random.random() < 0.01:
            self.vel_x = -self.vel_x
        if random.random() < 0.02:
            self.vel_y = -6
            
        self.vel_y += GRAVITY
        self.y += self.vel_y
        
        # Breathe fire
        if self.timer % 90 == 0:
            self.fireballs.append({"x": self.x - 20, "y": self.y + 20, "vel_x": -4})
            
        for f in self.fireballs:
            f["x"] += f["vel_x"]
        self.fireballs = [f for f in self.fireballs if f["x"] > -50]
        
        for platform in platforms:
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width and
                self.vel_y > 0):
                self.y = platform.y - self.height
                self.vel_y = 0
                
    def draw(self, screen, camera_x):
        if not self.alive:
            return
        screen_x = self.x - camera_x
        # Body
        pygame.draw.rect(screen, (0, 100, 0), (screen_x, self.y, 48, 48))
        # Shell
        pygame.draw.ellipse(screen, (139, 69, 19), (screen_x + 8, self.y + 8, 32, 32))
        # Head
        pygame.draw.rect(screen, (0, 150, 0), (screen_x - 16, self.y + 8, 24, 24))
        # Eyes
        pygame.draw.circle(screen, RED, (screen_x - 8, self.y + 16), 4)
        pygame.draw.circle(screen, RED, (screen_x, self.y + 16), 4)
        # Horns
        pygame.draw.polygon(screen, (200, 150, 50), [(screen_x - 12, self.y + 8), (screen_x - 8, self.y - 8), (screen_x - 4, self.y + 8)])
        pygame.draw.polygon(screen, (200, 150, 50), [(screen_x + 4, self.y + 8), (screen_x + 8, self.y - 8), (screen_x + 12, self.y + 8)])
        # Fireballs
        for f in self.fireballs:
            fx = f["x"] - camera_x
            pygame.draw.circle(screen, (255, 100, 0), (int(fx), int(f["y"])), 8)
            pygame.draw.circle(screen, (255, 200, 0), (int(fx), int(f["y"])), 4)

class Item:
    def __init__(self, x, y, type="coin"):
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.type = type
        self.active = True
        self.vel_y = -4
        self.vel_x = 2 if type in ["mushroom", "1up", "star"] else 0
        self.animation_frame = 0
        self.emerged = type == "coin"
        
    def update(self, platforms):
        if not self.emerged:
            self.y += self.vel_y
            self.vel_y += 0.1
            if self.vel_y >= 0:
                self.emerged = True
                self.vel_y = 0
                if self.type in ["mushroom", "1up", "star"]:
                    self.vel_x = 2
        else:
            if self.type in ["mushroom", "1up", "star"]:
                self.vel_y += GRAVITY
                self.x += self.vel_x
                self.y += self.vel_y
                
                for platform in platforms:
                    if hasattr(platform, 'destroyed') and platform.destroyed:
                        continue
                    if (self.y + self.height >= platform.y and 
                        self.y + self.height <= platform.y + 10 and
                        self.x + self.width > platform.x and 
                        self.x < platform.x + platform.width):
                        self.y = platform.y - self.height
                        self.vel_y = 0
                    # Side collision
                    if (self.y + self.height > platform.y and
                        self.y < platform.y + platform.height):
                        if self.x + self.width > platform.x and self.x < platform.x:
                            self.vel_x = -abs(self.vel_x)
                        elif self.x < platform.x + platform.width and self.x + self.width > platform.x + platform.width:
                            self.vel_x = abs(self.vel_x)
                            
        self.animation_frame = (self.animation_frame + 1) % 60
        
    def draw(self, screen, camera_x):
        if not self.active:
            return
        screen_x = self.x - camera_x
        
        if self.type == "coin":
            size = 10 + math.sin(self.animation_frame * 0.2) * 2
            pygame.draw.circle(screen, (255, 220, 0), (int(screen_x + 8), int(self.y + 8)), int(size / 2))
        elif self.type == "mushroom":
            pygame.draw.ellipse(screen, RED, (screen_x, self.y, 16, 10))
            pygame.draw.rect(screen, WHITE, (screen_x + 4, self.y + 8, 8, 8))
        elif self.type == "fire_flower":
            pygame.draw.circle(screen, (255, 100, 0), (screen_x + 8, self.y + 6), 6)
            pygame.draw.rect(screen, GREEN, (screen_x + 6, self.y + 10, 4, 8))
        elif self.type == "star":
            points = []
            for i in range(5):
                angle = math.pi / 2 + i * 2 * math.pi / 5
                points.append((screen_x + 8 + math.cos(angle) * 8, self.y + 8 - math.sin(angle) * 8))
                angle += math.pi / 5
                points.append((screen_x + 8 + math.cos(angle) * 4, self.y + 8 - math.sin(angle) * 4))
            color = (255, 255, 0) if self.animation_frame % 10 < 5 else (255, 200, 100)
            pygame.draw.polygon(screen, color, points)
        elif self.type == "1up":
            pygame.draw.ellipse(screen, GREEN, (screen_x, self.y, 16, 10))
            pygame.draw.rect(screen, WHITE, (screen_x + 4, self.y + 8, 8, 8))

class Fireball:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.vel_x = 6 * direction
        self.vel_y = 0
        self.active = True
        
    def update(self, platforms, enemies):
        self.vel_y += 0.3
        self.x += self.vel_x
        self.y += self.vel_y
        
        for platform in platforms:
            if hasattr(platform, 'destroyed') and platform.destroyed:
                continue
            if (self.y + self.height >= platform.y and 
                self.y + self.height <= platform.y + 10 and
                self.x + self.width > platform.x and 
                self.x < platform.x + platform.width):
                self.y = platform.y - self.height
                self.vel_y = -4
                
        for enemy in enemies:
            if enemy.alive and (self.x < enemy.x + enemy.width and
                self.x + self.width > enemy.x and
                self.y < enemy.y + enemy.height and
                self.y + self.height > enemy.y):
                enemy.alive = False
                self.active = False
                
        if self.y > SCREEN_HEIGHT or self.x < -50 or self.x > 10000:
            self.active = False
            
    def draw(self, screen, camera_x):
        if not self.active:
            return
        screen_x = self.x - camera_x
        pygame.draw.circle(screen, (255, 100, 0), (int(screen_x + 4), int(self.y + 4)), 4)

class LevelData:
    @staticmethod
    def get_level(world, stage):
        """Generate level data based on world and stage"""
        level_width = 3200 + (world - 1) * 200
        platforms = []
        enemies = []
        items = []
        pipes = []
        flagpole = None
        
        # Determine theme
        if stage == 2:
            theme = "underground"
        elif stage == 4:
            theme = "castle"
        elif stage == 3 and world in [2, 7]:
            theme = "athletic"
        elif world == 2 and stage == 2:
            theme = "water"
        else:
            theme = "overworld"
            
        ground_y = SCREEN_HEIGHT - 50
        
        # Create ground with gaps
        x = 0
        while x < level_width:
            gap_chance = 0.05 + world * 0.01
            gap_size = random.randint(64, 128) if random.random() < gap_chance and x > 400 else 0
            
            if gap_size > 0:
                x += gap_size
            else:
                segment_length = random.randint(128, 512)
                platforms.append(Platform(x, ground_y, segment_length, 50, "ground"))
                x += segment_length
                
        # Add platforms and blocks
        for i in range(10 + world * 3):
            px = random.randint(200, level_width - 200)
            py = random.randint(250, 450)
            ptype = random.choice(["brick", "brick", "question", "ground"])
            pwidth = random.randint(32, 128)
            
            contains = None
            if ptype == "question":
                contains = random.choice(["coin", "coin", "coin", "mushroom", "fire_flower"])
                pwidth = 32
                
            platforms.append(Platform(px, py, pwidth, 32, ptype, contains))
            
        # Add stairs near end
        stair_x = level_width - 400
        for i in range(8):
            platforms.append(Platform(stair_x + i * 32, ground_y - (i + 1) * 32, 32, (i + 1) * 32, "block"))
            
        # Add pipes
        for i in range(3 + world):
            pipe_x = random.randint(300, level_width - 500)
            pipe_height = random.choice([64, 96, 128])
            destination = None
            if stage == 1 and i == 0:
                destination = "bonus"
            pipes.append(Pipe(pipe_x, ground_y - pipe_height, pipe_height, destination))
            if random.random() < 0.3:
                enemies.append(PiranhaPlant(pipe_x + 12, ground_y - pipe_height))
                
        # Add enemies based on difficulty
        enemy_count = 5 + world * 2 + stage
        for i in range(enemy_count):
            ex = random.randint(400, level_width - 200)
            ey = ground_y - 16
            enemy_type = random.random()
            
            if enemy_type < 0.6:
                enemies.append(Goomba(ex, ey))
            elif enemy_type < 0.85:
                enemies.append(Koopa(ex, ey - 8, random.choice(["green", "red"])))
            elif world >= 3 and enemy_type < 0.95:
                enemies.append(HammerBro(ex, ey - 8))
                
        # Castle levels have Bowser
        if stage == 4:
            enemies.append(Bowser(level_width - 300, ground_y - 64))
            # Add lava pits
            for i in range(3):
                lava_x = random.randint(500, level_width - 500)
                platforms.append(Platform(lava_x, ground_y, 96, 50, "ground"))  # Remove ground for lava
                
        # Add flagpole (not for castle levels)
        if stage != 4:
            flagpole = Flagpole(level_width - 150, ground_y - 300)
            
        # Add bonus items
        for i in range(2):
            ix = random.randint(200, level_width - 200)
            iy = random.randint(200, 350)
            item_type = random.choice(["coin", "coin", "1up"])
            items.append(Item(ix, iy, item_type))
            
        return {
            "width": level_width,
            "theme": theme,
            "platforms": platforms,
            "enemies": enemies,
            "items": items,
            "pipes": pipes,
            "flagpole": flagpole,
            "mario_start": (100, ground_y - 50)
        }

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Bros - Complete Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.world = 1
        self.stage = 1
        self.load_level()
        
    def load_level(self):
        level_data = LevelData.get_level(self.world, self.stage)
        self.level_width = level_data["width"]
        self.theme = level_data["theme"]
        self.platforms = level_data["platforms"]
        self.enemies = level_data["enemies"]
        self.items = level_data["items"]
        self.pipes = level_data["pipes"]
        self.flagpole = level_data["flagpole"]
        self.fireballs = []
        
        start_x, start_y = level_data["mario_start"]
        if not hasattr(self, 'mario'):
            self.mario = Mario(start_x, start_y)
        else:
            self.mario.x = start_x
            self.mario.y = start_y
            self.mario.vel_x = 0
            self.mario.vel_y = 0
            
        self.game_state = "playing"
        self.time = 400
        self.camera_x = 0
        self.level_complete = False
        self.level_complete_timer = 0
        
    def next_level(self):
        self.stage += 1
        if self.stage > 4:
            self.stage = 1
            self.world += 1
            if self.world > 8:
                self.game_state = "victory"
                return
        self.load_level()
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.world = 1
                    self.stage = 1
                    self.mario = Mario(100, 400)
                    self.load_level()
                elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.next_level()
                    
    def update(self):
        if self.game_state != "playing":
            return
            
        if self.level_complete:
            self.level_complete_timer += 1
            if self.level_complete_timer > 120:
                self.next_level()
            return
            
        keys = pygame.key.get_pressed()
        
        result = self.mario.update(keys, self.platforms, self.enemies, self.items, 
                                   self.fireballs, self.level_width, self.theme, self.pipes)
        
        if result == "game_over":
            self.game_state = "game_over"
        elif result == "died":
            self.load_level()
        elif isinstance(result, tuple) and result[0] == "warp":
            self.mario.score += 1000
            
        # Check flagpole
        if self.flagpole and self.mario.x > self.flagpole.x - 20 and self.mario.x < self.flagpole.x + 20:
            self.level_complete = True
            self.mario.score += max(0, self.time) * 10
            
        for enemy in self.enemies:
            enemy.update(self.platforms)
            # Check Bowser fireballs hitting Mario
            if isinstance(enemy, Bowser):
                for f in enemy.fireballs:
                    if (self.mario.x < f["x"] + 16 and self.mario.x + self.mario.width > f["x"] and
                        self.mario.y < f["y"] + 16 and self.mario.y + self.mario.height > f["y"]):
                        if self.mario.invincible <= 0 and self.mario.star_power <= 0:
                            if self.mario.state != "small":
                                self.mario.state = "small"
                                self.mario.invincible = 60
                            else:
                                self.mario.lives -= 1
                                if self.mario.lives <= 0:
                                    self.game_state = "game_over"
                                else:
                                    self.load_level()
            # Check Hammer Bro hammers
            if isinstance(enemy, HammerBro):
                for h in enemy.hammers:
                    if (self.mario.x < h["x"] + 8 and self.mario.x + self.mario.width > h["x"] and
                        self.mario.y < h["y"] + 16 and self.mario.y + self.mario.height > h["y"]):
                        if self.mario.invincible <= 0 and self.mario.star_power <= 0:
                            if self.mario.state != "small":
                                self.mario.state = "small"
                                self.mario.invincible = 60
                            else:
                                self.mario.lives -= 1
                                if self.mario.lives <= 0:
                                    self.game_state = "game_over"
                                else:
                                    self.load_level()
                                    
        for item in self.items:
            item.update(self.platforms)
            
        for fireball in self.fireballs:
            fireball.update(self.platforms, self.enemies)
        self.fireballs = [f for f in self.fireballs if f.active]
        
        # Remove dead enemies
        self.enemies = [e for e in self.enemies if e.alive]
        # Remove destroyed platforms
        self.platforms = [p for p in self.platforms if not (hasattr(p, 'destroyed') and p.destroyed)]
        
        self.camera_x = self.mario.x - SCREEN_WIDTH // 3
        if self.camera_x < 0:
            self.camera_x = 0
        if self.camera_x > self.level_width - SCREEN_WIDTH:
            self.camera_x = self.level_width - SCREEN_WIDTH
            
        if pygame.time.get_ticks() % 1000 < 16:
            self.time -= 1
            if self.time <= 0:
                self.mario.lives -= 1
                if self.mario.lives <= 0:
                    self.game_state = "game_over"
                else:
                    self.load_level()
                    
    def draw(self):
        theme_colors = THEMES[self.theme]
        self.screen.fill(theme_colors["bg"])
        
        # Draw decorations
        if self.theme == "overworld":
            for i in range(5):
                cloud_x = (i * 300 - self.camera_x // 3) % (SCREEN_WIDTH + 200) - 100
                pygame.draw.ellipse(self.screen, WHITE, (cloud_x, 50, 80, 40))
                pygame.draw.ellipse(self.screen, WHITE, (cloud_x + 30, 40, 60, 30))
                
            for i in range(3):
                bush_x = (i * 500 - self.camera_x // 2) % (SCREEN_WIDTH + 200) - 100
                pygame.draw.ellipse(self.screen, (0, 180, 0), (bush_x, SCREEN_HEIGHT - 70, 100, 40))
                pygame.draw.ellipse(self.screen, (0, 180, 0), (bush_x + 30, SCREEN_HEIGHT - 80, 60, 40))
                
        elif self.theme == "castle":
            # Draw lava at bottom
            for i in range(0, SCREEN_WIDTH, 20):
                lava_y = SCREEN_HEIGHT - 30 + math.sin((i + pygame.time.get_ticks() / 100) * 0.1) * 5
                pygame.draw.rect(self.screen, LAVA_ORANGE, (i, lava_y, 20, 50))
                pygame.draw.rect(self.screen, (255, 200, 0), (i, lava_y, 20, 5))
                
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x, theme_colors)
            
        for pipe in self.pipes:
            pipe.draw(self.screen, self.camera_x)
            
        if self.flagpole:
            self.flagpole.draw(self.screen, self.camera_x)
            
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
            
        for item in self.items:
            item.draw(self.screen, self.camera_x)
            
        for fireball in self.fireballs:
            fireball.draw(self.screen, self.camera_x)
            
        self.mario.draw(self.screen, self.camera_x)
        
        self.draw_hud()
        
        if self.game_state != "playing" or self.level_complete:
            self.draw_overlay()
            
        pygame.display.flip()
        
    def draw_hud(self):
        font = pygame.font.Font(None, 32)
        
        world_text = font.render(f"WORLD {self.world}-{self.stage}", True, WHITE)
        self.screen.blit(world_text, (10, 10))
        
        score_text = font.render(f"SCORE: {self.mario.score:06d}", True, WHITE)
        self.screen.blit(score_text, (200, 10))
        
        coin_text = font.render(f"x{self.mario.coins:02d}", True, WHITE)
        pygame.draw.circle(self.screen, (255, 220, 0), (420, 18), 8)
        self.screen.blit(coin_text, (435, 10))
        
        time_text = font.render(f"TIME: {max(0, self.time):03d}", True, WHITE)
        self.screen.blit(time_text, (550, 10))
        
        lives_text = font.render(f"x{self.mario.lives}", True, WHITE)
        pygame.draw.rect(self.screen, MARIO_RED, (710, 10, 12, 20))
        self.screen.blit(lives_text, (730, 10))
        
    def draw_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)
        
        if self.game_state == "game_over":
            text = font_large.render("GAME OVER", True, RED)
        elif self.game_state == "victory":
            text = font_large.render("CONGRATULATIONS!", True, (255, 215, 0))
        elif self.level_complete:
            text = font_large.render(f"WORLD {self.world}-{self.stage} CLEAR!", True, WHITE)
            
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.screen.blit(text, text_rect)
        
        if self.game_state == "victory":
            sub_text = font_small.render(f"Final Score: {self.mario.score}", True, WHITE)
        else:
            sub_text = font_small.render("Press R to Restart | CTRL+N for Next Level", True, WHITE)
        sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(sub_text, sub_rect)

if __name__ == "__main__":
    game = Game()
    game.run()
