import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -11  # Slightly adjusted for sprite feel
SPEED = 3
SCALE = 2 # Global scaling for pixel art

# Colors
TRANSPARENT = (0, 0, 0, 0)
SKY_BLUE = (146, 144, 255) # NES Sky
WHITE = (255, 255, 255)

# --- SPRITE DATA (Procedural Pixel Art) ---
# 0: Transparent, 1: Outline/Black, 2: Skin, 3: Red (Clothes), 4: Blue/Overalls, 5: Brown (Shoes/Goomba), 6: Gold (Buttons/Coins)
# 7: Ground Brown, 8: Leaf Green, 9: Question Orange

PALETTE = {
    0: (0, 0, 0, 0),
    1: (0, 0, 0),
    2: (255, 206, 150), # Skin
    3: (216, 40, 0),    # Red
    4: (0, 112, 236),   # Blue
    5: (136, 112, 0),   # Brown
    6: (252, 152, 56),  # Goomba/Coin detail
    7: (200, 76, 12),   # Ground/Brick Red
    8: (0, 168, 0),     # Pipe Green
    9: (252, 188, 176)  # Question block shiny
}

# 12x16 Small Mario Idle
SPRITE_MARIO_SMALL_IDLE = [
    [0,0,0,3,3,3,3,3,0,0,0,0],
    [0,0,3,3,3,3,3,3,3,3,3,0],
    [0,0,5,5,5,2,2,5,2,0,0,0],
    [0,5,2,5,2,2,2,5,2,2,2,0],
    [0,5,2,5,5,2,2,2,5,2,2,2],
    [0,5,5,2,2,2,2,5,5,5,5,0],
    [0,0,0,2,2,2,2,2,2,2,0,0],
    [0,0,3,3,4,3,3,3,0,0,0,0],
    [0,3,3,3,4,3,3,4,3,3,3,0],
    [3,3,3,3,4,4,4,4,3,3,3,3],
    [2,2,3,4,6,4,4,6,4,3,2,2],
    [2,2,2,4,4,4,4,4,4,2,2,2],
    [2,2,4,4,4,4,4,4,4,4,2,2],
    [0,0,4,4,4,0,0,4,4,4,0,0],
    [0,5,5,5,0,0,0,0,5,5,5,0],
    [5,5,5,5,0,0,0,0,5,5,5,5]
]

# 16x16 Goomba
SPRITE_GOOMBA = [
    [0,0,0,0,0,0,5,5,5,5,0,0,0,0,0,0],
    [0,0,0,0,5,5,5,5,5,5,5,5,0,0,0,0],
    [0,0,0,5,5,5,5,5,5,5,5,5,5,0,0,0],
    [0,0,5,5,5,5,5,5,5,5,5,5,5,5,0,0],
    [0,0,5,1,1,5,5,5,5,5,5,1,1,5,0,0],
    [0,5,5,1,2,1,5,5,5,5,1,2,1,5,5,0],
    [0,5,5,1,2,1,5,5,5,5,1,2,1,5,5,0],
    [0,5,5,1,1,5,5,5,5,5,5,1,1,5,5,0],
    [0,5,5,5,5,5,2,2,2,2,5,5,5,5,5,0],
    [0,5,5,5,5,5,2,2,2,2,5,5,5,5,5,0],
    [0,0,5,5,5,5,5,5,5,5,5,5,5,5,0,0],
    [0,0,0,5,5,5,5,5,5,5,5,5,5,0,0,0],
    [0,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0],
    [0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0],
    [0,0,1,1,1,1,1,0,0,1,1,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
]

# 16x16 Brick
SPRITE_BRICK = [
    [7,7,7,7,7,1,7,7,7,7,7,7,7,7,1,7],
    [7,7,7,7,7,1,7,7,7,7,7,7,7,7,1,7],
    [7,7,7,7,7,1,7,7,7,7,7,7,7,7,1,7],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [7,7,1,7,7,7,7,7,7,7,7,7,7,1,7,7],
    [7,7,1,7,7,7,7,7,7,7,7,7,7,1,7,7],
    [7,7,1,7,7,7,7,7,7,7,7,7,7,1,7,7],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [7,7,7,7,7,1,7,7,7,7,7,7,7,7,1,7],
    [7,7,7,7,7,1,7,7,7,7,7,7,7,7,1,7],
    [7,7,7,7,7,1,7,7,7,7,7,7,7,7,1,7],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [7,7,1,7,7,7,7,7,7,7,7,7,7,1,7,7],
    [7,7,1,7,7,7,7,7,7,7,7,7,7,1,7,7],
    [7,7,1,7,7,7,7,7,7,7,7,7,7,1,7,7],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# 16x16 Question Block
SPRITE_QBLOCK = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,1,1,1,1,1,6,6,6,6,6,1],
    [1,6,6,6,1,1,9,9,9,1,1,6,6,6,6,1],
    [1,6,6,6,1,1,9,6,9,1,1,6,6,6,6,1],
    [1,6,6,6,6,6,6,9,1,1,6,6,6,6,6,1],
    [1,6,6,6,6,6,1,1,1,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,1,1,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,1,1,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,1,1,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1],
    [1,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

def create_sprite(data, width_px, height_px, scale=2):
    """Converts the sprite data array into a Pygame surface."""
    surface = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
    for y, row in enumerate(data):
        for x, color_code in enumerate(row):
            if color_code in PALETTE:
                color = PALETTE[color_code]
                if color[3] if len(color) > 3 else 255 != 0: # Check alpha
                    surface.set_at((x, y), color)
    
    return pygame.transform.scale(surface, (width_px * scale, height_px * scale))

class AssetManager:
    def __init__(self):
        self.sprites = {}
        self.load_procedural_sprites()

    def load_procedural_sprites(self):
        # Generate surfaces from the data arrays
        self.sprites['mario_small'] = create_sprite(SPRITE_MARIO_SMALL_IDLE, 12, 16, SCALE)
        self.sprites['goomba'] = create_sprite(SPRITE_GOOMBA, 16, 16, SCALE)
        self.sprites['brick'] = create_sprite(SPRITE_BRICK, 16, 16, SCALE)
        self.sprites['qblock'] = create_sprite(SPRITE_QBLOCK, 16, 16, SCALE)
        
        # Procedural Pipe (Simple generated)
        pipe_surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pipe_surf.fill((0, 180, 0)) # Base Green
        pygame.draw.rect(pipe_surf, (0, 120, 0), (0,0, 32, 32), 2) # Outline
        pygame.draw.rect(pipe_surf, (100, 220, 100), (4, 4, 4, 24)) # Highlight
        self.sprites['pipe'] = pygame.transform.scale(pipe_surf, (32 * SCALE, 32 * SCALE))
        
        # Procedural Ground
        ground_surf = pygame.Surface((16, 16))
        ground_surf.fill((200, 76, 12)) # Reddish brown
        pygame.draw.rect(ground_surf, (0,0,0), (0,0,16,16), 1)
        # Add some texture
        pygame.draw.line(ground_surf, (0,0,0), (4,4), (12,4), 1)
        pygame.draw.line(ground_surf, (0,0,0), (4,8), (12,8), 1)
        self.sprites['ground'] = pygame.transform.scale(ground_surf, (16*SCALE, 16*SCALE))

assets = None # Global asset holder

class Mario:
    def __init__(self):
        self.width = 12 * SCALE
        self.height = 16 * SCALE
        self.x = 50
        self.y = SCREEN_HEIGHT - 100
        self.vel_y = 0
        self.vel_x = 0
        self.jumping = False
        self.direction = 1  # 1 for right, -1 for left
        self.powerup = 0  # 0=small
        self.lives = 3
        self.coins = 0
        self.score = 0
        self.grounded = False

    def update(self, platforms, enemies, blocks, keys=None):
        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Movement
        self.x += self.vel_x

        # Keep on screen bounds
        if self.x < 0: self.x = 0
        if self.x > SCREEN_WIDTH * 10: self.x = SCREEN_WIDTH * 10 

        self.grounded = False
        
        # Platform collision (Top down)
        mario_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            # Simple collision logic
            p_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            
            if mario_rect.colliderect(p_rect):
                # Falling onto platform
                if self.vel_y > 0 and self.y + self.height - self.vel_y <= platform.y + 10:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.jumping = False
                    self.grounded = True
                # Hitting head
                elif self.vel_y < 0 and self.y - self.vel_y >= platform.y + platform.height:
                    self.y = platform.y + platform.height
                    self.vel_y = 2
                    if isinstance(platform, Block):
                        platform.hit(self)

        # Ground floor safety
        if self.y >= SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.jumping = False
            self.grounded = True

        # Enemy collision
        mario_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for enemy in enemies[:]:
            e_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
            if mario_rect.colliderect(e_rect):
                # Stomp
                if self.vel_y > 0 and self.y + self.height < enemy.y + enemy.height * 0.5:
                    enemies.remove(enemy)
                    self.vel_y = -8
                    self.score += 100
                else:
                    self.lives -= 1
                    self.reset_position()

    def reset_position(self):
        self.x = 50
        self.y = SCREEN_HEIGHT - 100
        self.vel_x = 0
        self.vel_y = 0

    def jump(self):
        if self.grounded:
            self.vel_y = JUMP_STRENGTH
            self.jumping = True
            self.grounded = False

    def draw(self, screen, camera_x):
        sprite = assets.sprites['mario_small']
        
        # Flip sprite if facing left
        if self.direction == -1:
            sprite = pygame.transform.flip(sprite, True, False)
            
        screen.blit(sprite, (self.x - camera_x, self.y))

class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 16 * SCALE
        self.height = 16 * SCALE
        self.vel_x = -1
        self.frame = 0
        self.frame_timer = 0

    def update(self, platforms):
        self.x += self.vel_x
        
        # Animation timer
        self.frame_timer += 1
        if self.frame_timer > 10:
            self.frame = 1 - self.frame
            self.frame_timer = 0

        # Simple turnaround logic (screen bounds or arbitrary limits for this demo)
        if self.x < 0: self.vel_x = 1
        
        # Check wall collisions
        # (Simplified for single file demo)

    def draw(self, screen, camera_x):
        sprite = assets.sprites['goomba']
        # Simple "waddle" effect by flipping every few frames (or use distinct sprites if we had them)
        if self.frame == 1:
            sprite = pygame.transform.flip(sprite, True, False)
        
        screen.blit(sprite, (self.x - camera_x, self.y))

class Platform:
    def __init__(self, x, y, width, height, type="ground"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type

    def draw(self, screen, camera_x):
        # Tiling logic for sprite platforms
        if self.type == "ground":
            tile = assets.sprites['ground']
            tile_w = tile.get_width()
            tile_h = tile.get_height()
            
            # Draw tiles covering the rect
            for i in range(0, int(self.width), tile_w):
                for j in range(0, int(self.height), tile_h):
                    if i + tile_w <= self.width and j + tile_h <= self.height:
                         screen.blit(tile, (self.x + i - camera_x, self.y + j))
        elif self.type == "pipe":
            # Just stretch the pipe sprite for this demo
            scaled_pipe = pygame.transform.scale(assets.sprites['pipe'], (int(self.width), int(self.height)))
            screen.blit(scaled_pipe, (self.x - camera_x, self.y))
        else:
             pygame.draw.rect(screen, (100,100,100), (self.x - camera_x, self.y, self.width, self.height))

class Block(Platform):
    def __init__(self, x, y, type="normal"):
        super().__init__(x, y, 16 * SCALE, 16 * SCALE, "block")
        self.type = type # "normal" (brick) or "coin" (question)
        self.active = True
        self.bump_y = 0

    def hit(self, mario):
        if self.active:
            self.bump_y = -5 # Visual bump
            if self.type == "coin":
                mario.coins += 1
                mario.score += 200
                self.active = False
            elif self.type == "normal":
                # Break visual logic here
                pass

    def update(self):
        if self.bump_y < 0:
            self.bump_y += 1

    def draw(self, screen, camera_x):
        offset_y = self.bump_y
        
        if self.type == "coin":
            if self.active:
                sprite = assets.sprites['qblock']
            else:
                sprite = assets.sprites['brick'] # Turned to stone/brown
                # Gray out for used block
                sprite = sprite.copy()
                sprite.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_SUB)
        else:
            sprite = assets.sprites['brick']

        screen.blit(sprite, (self.x - camera_x, self.y + offset_y))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Super Mario Clone - Sprite Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Initialize Assets
        global assets
        assets = AssetManager()
        
        self.reset_game()

    def reset_game(self):
        self.mario = Mario()
        self.camera_x = 0
        
        # Level Design
        self.platforms = [
            Platform(0, SCREEN_HEIGHT - 32, SCREEN_WIDTH * 10, 32, "ground"),
            Platform(600, SCREEN_HEIGHT - 64, 64, 64, "pipe"),
            Platform(900, SCREEN_HEIGHT - 96, 64, 96, "pipe"),
        ]

        self.blocks = [
            Block(300, SCREEN_HEIGHT - 120, "coin"),
            Block(332, SCREEN_HEIGHT - 120, "normal"),
            Block(364, SCREEN_HEIGHT - 120, "coin"),
            Block(332, SCREEN_HEIGHT - 184, "coin"),
            Block(400, SCREEN_HEIGHT - 120, "normal"),
        ]

        self.enemies = [
            Goomba(400, SCREEN_HEIGHT - 64),
            Goomba(700, SCREEN_HEIGHT - 64),
            Goomba(1000, SCREEN_HEIGHT - 64),
        ]
        
        self.all_platforms = self.platforms + self.blocks

    def run(self):
        running = True
        
        while running:
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.mario.jump()
                    elif event.key == pygame.K_r:
                        self.reset_game()

            # Game Logic
            keys = pygame.key.get_pressed()
            self.mario.vel_x = 0
            if keys[pygame.K_LEFT]:
                self.mario.vel_x = -SPEED
                self.mario.direction = -1
            elif keys[pygame.K_RIGHT]:
                self.mario.vel_x = SPEED
                self.mario.direction = 1

            self.mario.update(self.all_platforms, self.enemies, self.blocks)
            
            for enemy in self.enemies:
                enemy.update(self.platforms)
                
            for block in self.blocks:
                block.update()

            # Camera Follow
            target_cam = self.mario.x - SCREEN_WIDTH // 3
            if target_cam < 0: target_cam = 0
            # Smooth camera
            self.camera_x += (target_cam - self.camera_x) * 0.1

            # Drawing
            self.screen.fill(SKY_BLUE)
            
            # Draw platforms
            for platform in self.platforms:
                platform.draw(self.screen, self.camera_x)
                
            for block in self.blocks:
                block.draw(self.screen, self.camera_x)

            for enemy in self.enemies:
                enemy.draw(self.screen, self.camera_x)
            
            self.mario.draw(self.screen, self.camera_x)

            # HUD
            score_text = self.font.render(f"MARIO  x {self.mario.lives}   COINS {self.mario.coins}   SCORE {self.mario.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
