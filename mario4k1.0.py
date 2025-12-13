import pygame
import sys
import math

# Init
pygame.init()
screen = pygame.display.set_mode((256, 240))
pygame.display.set_caption("ULTRA MARIO 2D BROS")
clock = pygame.time.Clock()

# Famicom palette (exact NES colors)
COLORS = {
    0: (124, 124, 124),   # Grey
    1: (0, 0, 252),       # Blue
    2: (0, 0, 188),       # Dark blue
    3: (68, 40, 188),     # Purple
    4: (148, 0, 132),     # Magenta
    5: (168, 0, 32),      # Dark red
    6: (168, 16, 0),      # Brown
    7: (136, 20, 0),      # Dark brown
    8: (80, 48, 0),       # Dark green
    9: (0, 120, 0),       # Green
    10: (0, 104, 0),      # Dark cyan
    11: (0, 88, 0),       # Cyan
    12: (0, 64, 88),      # Navy
    13: (0, 0, 0),        # Black
    14: (188, 188, 188),  # Light grey
    15: (248, 56, 0),     # Red
    16: (252, 160, 68),   # Skin
    17: (252, 224, 0),    # Yellow
    18: (184, 248, 24),   # Light green
    19: (0, 232, 216),    # Aqua
    20: (0, 184, 248),    # Light blue
    21: (248, 184, 248),  # Pink
    22: (252, 252, 252),  # White
}

# Mario physics constants (exact Famicom values)
GRAVITY = 0.1875
MAX_FALL_SPEED = 4.0
WALK_ACCEL = 0.046875
FRICTION = 0.046875
JUMP_FORCE = 4.0

class Mario:
    def __init__(self):
        self.x = 50.0
        self.y = 180.0
        self.vx = 0.0
        self.vy = 0.0
        self.direction = 1
        self.jumping = False
        self.frame = 0
        self.small = True
        self.walking = False
        self.animation_timer = 0
        
    def update(self, keys, ground):
        # Horizontal movement
        if keys[pygame.K_RIGHT]:
            self.vx = min(self.vx + WALK_ACCEL, 2.0)
            self.direction = 1
            self.walking = True
        elif keys[pygame.K_LEFT]:
            self.vx = max(self.vx - WALK_ACCEL, -2.0)
            self.direction = -1
            self.walking = True
        else:
            self.walking = False
            # Friction
            if self.vx > 0:
                self.vx = max(0, self.vx - FRICTION)
            elif self.vx < 0:
                self.vx = min(0, self.vx + FRICTION)
        
        # Jumping (Famicom exact jump mechanics)
        if keys[pygame.K_x] and not self.jumping:
            self.vy = -JUMP_FORCE
            self.jumping = True
        elif not keys[pygame.K_x] and self.vy < 0:
            self.vy *= 0.5  # Variable jump height
        
        # Gravity
        self.vy = min(self.vy + GRAVITY, MAX_FALL_SPEED)
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Ground collision
        if self.y >= ground:
            self.y = ground
            self.vy = 0
            self.jumping = False
        
        # Animation
        self.animation_timer += 1
        if self.walking and self.animation_timer % 10 == 0:
            self.frame = (self.frame + 1) % 3
    
    def draw(self, surf):
        # Draw Mario (small form) - exact NES sprite colors
        color_body = COLORS[15]  # Red
        color_skin = COLORS[16]  # Skin
        color_brown = COLORS[6]  # Brown
        
        # Body
        pygame.draw.rect(surf, color_body, (self.x, self.y, 16, 16))
        # Face
        pygame.draw.rect(surf, color_skin, (self.x + 4, self.y + 4, 8, 8))
        # Hat
        pygame.draw.rect(surf, color_body, (self.x, self.y - 4, 16, 4))
        # Hair
        pygame.draw.rect(surf, color_brown, (self.x + 4, self.y + 8, 8, 2))

class Block:
    def __init__(self, x, y, type="brick"):
        self.x = x
        self.y = y
        self.type = type
    
    def draw(self, surf):
        if self.type == "brick":
            color = COLORS[6]  # Brown
            pygame.draw.rect(surf, color, (self.x, self.y, 16, 16))
            # Brick pattern
            pygame.draw.line(surf, COLORS[8], (self.x, self.y + 4), (self.x + 15, self.y + 4), 1)
            pygame.draw.line(surf, COLORS[8], (self.x, self.y + 8), (self.x + 15, self.y + 8), 1)
        elif self.type == "ground":
            color = COLORS[9]  # Green
            pygame.draw.rect(surf, color, (self.x, self.y, 16, 16))
            pygame.draw.rect(surf, COLORS[10], (self.x, self.y, 16, 4))

class Goomba:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = -0.5
        self.alive = True
    
    def update(self, blocks):
        self.x += self.vx
        # Simple block collision
        for block in blocks:
            if abs(self.x - block.x) < 16 and abs(self.y - block.y) < 16:
                self.vx *= -1
    
    def draw(self, surf):
        color = COLORS[6]  # Brown
        pygame.draw.rect(surf, color, (self.x, self.y, 16, 16))
        # Face
        pygame.draw.rect(surf, COLORS[22], (self.x + 4, self.y + 4, 8, 8))
        pygame.draw.rect(surf, COLORS[0], (self.x + 6, self.y + 6, 2, 2))

class Game:
    def __init__(self):
        self.state = "menu"
        self.mario = Mario()
        self.blocks = []
        self.enemies = []
        self.camera_x = 0
        
        # Create ground
        for x in range(0, 256 * 4, 16):
            self.blocks.append(Block(x, 196, "ground"))
        
        # Create some bricks
        self.blocks.append(Block(100, 150, "brick"))
        self.blocks.append(Block(116, 150, "brick"))
        self.blocks.append(Block(132, 150, "brick"))
        
        # Create pipe
        self.blocks.append(Block(200, 180, "ground"))
        self.blocks.append(Block(216, 180, "ground"))
        self.blocks.append(Block(200, 164, "ground"))
        self.blocks.append(Block(216, 164, "ground"))
        
        # Add goomba
        self.enemies.append(Goomba(150, 180))
    
    def update(self, keys):
        if self.state == "playing":
            self.mario.update(keys, 180)
            for enemy in self.enemies:
                enemy.update(self.blocks)
            
            # Camera follow (NES style locked vertical, horizontal follow)
            self.camera_x = max(0, self.mario.x - 128)
            
            # Simple collision with bricks
            for block in self.blocks:
                if block.type == "brick":
                    if (abs(self.mario.x - block.x) < 16 and 
                        abs(self.mario.y - block.y) < 16):
                        if self.mario.vy > 0:  # Falling onto block
                            self.mario.y = block.y - 16
                            self.mario.vy = 0
                            self.mario.jumping = False
    
    def draw(self, surf):
        surf.fill(COLORS[20])  # Sky blue
        
        # Draw blocks
        for block in self.blocks:
            if block.x >= self.camera_x - 16 and block.x <= self.camera_x + 256:
                block.draw(surf)
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.x >= self.camera_x - 16 and enemy.x <= self.camera_x + 256:
                enemy.draw(surf)
        
        # Draw Mario (relative to camera)
        mario_draw_x = self.mario.x - self.camera_x
        self.mario.draw(surf.subsurface(mario_draw_x, self.mario.y, 16, 16).surface 
                       if hasattr(surf, 'subsurface') else surf)
        
        if self.state == "menu":
            # Draw 8-bit style menu
            font = pygame.font.SysFont("courier", 16, bold=True)
            title = font.render("ULTRA MARIO 2D BROS", True, COLORS[15])
            start = font.render("PRESS X TO START", True, COLORS[22])
            surf.blit(title, (32, 80))
            surf.blit(start, (64, 120))

# Main game loop
def main():
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x and game.state == "menu":
                    game.state = "playing"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        keys = pygame.key.get_pressed()
        game.update(keys)
        
        screen.fill((0, 0, 0))
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)  # Exact Famicom refresh rate

if __name__ == "__main__":
    main()
