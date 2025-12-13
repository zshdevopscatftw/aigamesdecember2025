import pygame
import sys

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (107, 140, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BRICK_RED = (200, 76, 12)
GROUND_BROWN = (100, 60, 20)
PIPE_GREEN = (0, 180, 0)
MARIO_RED = (255, 0, 0)
GOOMBA_BROWN = (165, 42, 42)
GOLD = (255, 215, 0)

# Physics
GRAVITY = 0.8
JUMP_POWER = -16
MOVE_SPEED = 5
FRICTION = 0.8  # Generic friction for sliding stops

# --- Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Create a simple Mario-like placeholder
        self.image = pygame.Surface((32, 32))
        self.image.fill(MARIO_RED)
        # Add a little 'M' or hat detail
        pygame.draw.rect(self.image, (255, 200, 200), (4, 4, 24, 12)) # Face
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.is_dead = False

    def update(self, keys, blocks, enemies):
        if self.is_dead:
            self.rect.y += 10 # Fall off screen
            return

        # Horizontal Movement
        self.velocity_x = 0
        if keys[pygame.K_LEFT]:
            self.velocity_x = -MOVE_SPEED
        if keys[pygame.K_RIGHT]:
            self.velocity_x = MOVE_SPEED

        self.rect.x += self.velocity_x

        # Horizontal Collisions
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.velocity_x > 0: # Moving right; Hit left side of wall
                self.rect.right = block.rect.left
            elif self.velocity_x < 0: # Moving left; Hit right side of wall
                self.rect.left = block.rect.right

        # Vertical Movement
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Vertical Collisions
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.velocity_y > 0: # Falling down; Hit top
                self.rect.bottom = block.rect.top
                self.velocity_y = 0
                self.on_ground = True
            elif self.velocity_y < 0: # Jumping up; Hit bottom
                self.rect.top = block.rect.bottom
                self.velocity_y = 0
                # Optional: Break block logic here

        # Enemy Collisions
        enemy_hits = pygame.sprite.spritecollide(self, enemies, False)
        for enemy in enemy_hits:
            # Check if we landed on top (Super Mario style stomp)
            if self.velocity_y > 0 and self.rect.bottom < enemy.rect.centery + 10:
                enemy.die()
                self.velocity_y = -8 # Bounce off enemy
            else:
                self.die()

        # Check death (fall off world)
        if self.rect.top > SCREEN_HEIGHT:
            self.die()

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_POWER

    def die(self):
        if not self.is_dead:
            self.is_dead = True
            self.velocity_y = -10 # Death hop
            print("Game Over!")

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, type='ground'):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.type = type
        
        if type == 'ground':
            self.image.fill(GROUND_BROWN)
            pygame.draw.rect(self.image, BLACK, (0,0,40,40), 1)
        elif type == 'brick':
            self.image.fill(BRICK_RED)
            pygame.draw.line(self.image, BLACK, (0, 10), (40, 10), 2)
            pygame.draw.line(self.image, BLACK, (0, 30), (40, 30), 2)
            pygame.draw.line(self.image, BLACK, (20, 0), (20, 10), 2)
            pygame.draw.line(self.image, BLACK, (10, 10), (10, 30), 2)
            pygame.draw.line(self.image, BLACK, (30, 10), (30, 30), 2)
        elif type == 'pipe':
            self.image = pygame.Surface((40, 80)) # Pipes are taller
            self.image.fill(PIPE_GREEN)
            pygame.draw.rect(self.image, (0, 120, 0), (0,0,40,20)) # Pipe rim
            pygame.draw.rect(self.image, BLACK, (0,0,40,80), 2)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill(GOOMBA_BROWN)
        # Eyes
        pygame.draw.rect(self.image, WHITE, (4, 4, 10, 10))
        pygame.draw.rect(self.image, WHITE, (18, 4, 10, 10))
        pygame.draw.rect(self.image, BLACK, (6, 6, 4, 4))
        pygame.draw.rect(self.image, BLACK, (20, 6, 4, 4))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = -1 # -1 left, 1 right
        self.speed = 2
        self.velocity_y = 0

    def update(self, blocks):
        # Gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y
        
        # Vertical collision (Land on ground)
        hits = pygame.sprite.spritecollide(self, blocks, False)
        for block in hits:
            if self.velocity_y > 0:
                self.rect.bottom = block.rect.top
                self.velocity_y = 0

        # Horizontal movement
        original_x = self.rect.x
        self.rect.x += self.speed * self.direction
        
        # Horizontal collision (Turn around on walls)
        hits = pygame.sprite.spritecollide(self, blocks, False)
        if hits:
            self.rect.x = original_x
            self.direction *= -1

    def die(self):
        self.kill()

# --- Level Map ---
# W = Ground, B = Brick, P = Pipe, E = Enemy, ' ' = Air
LEVEL_MAP = [
    "                                                                                ",
    "                                                                                ",
    "                                                                                ",
    "                                      BBB?BBB                                   ",
    "                                                                                ",
    "               B B B                                                            ",
    "                                                                   E            ",
    "                                E                            P     P            ",
    "       P                  B    BBBBBB                        P     P            ",
    "       P         E        B                              BB  P     P            ",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW   WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW   WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

# --- Game Setup ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Pygame Bros")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    blocks = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Level Generation
    player = None
    
    for row_index, row in enumerate(LEVEL_MAP):
        for col_index, tile in enumerate(row):
            x = col_index * 40
            y = row_index * 40
            
            if tile == 'W':
                b = Block(x, y, 'ground')
                blocks.add(b)
                all_sprites.add(b)
            elif tile == 'B':
                b = Block(x, y, 'brick')
                blocks.add(b)
                all_sprites.add(b)
            elif tile == 'P':
                # Only add pipe if it's the top part to avoid overlap visual issues in this simple version
                if row_index > 0 and LEVEL_MAP[row_index-1][col_index] != 'P':
                     b = Block(x, y, 'pipe')
                     blocks.add(b)
                     all_sprites.add(b)
            elif tile == 'E':
                e = Enemy(x, y + 8) # Adjust for size difference
                enemies.add(e)
                all_sprites.add(e)
    
    # Spawn player at start
    player = Player(100, 300)
    all_sprites.add(player)

    running = True
    camera_offset_x = 0

    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_r and player.is_dead:
                    main() # Simple restart
                    return

        # Updates
        keys = pygame.key.get_pressed()
        player.update(keys, blocks, enemies)
        enemies.update(blocks)

        # Camera Logic (Side Scrolling)
        # If player moves past 1/3 of the screen, move everything left
        if player.rect.x > SCREEN_WIDTH / 3:
            diff = player.rect.x - (SCREEN_WIDTH / 3)
            player.rect.x = SCREEN_WIDTH / 3
            camera_offset_x += diff
            for sprite in all_sprites:
                if sprite != player:
                    sprite.rect.x -= diff

        # Drawing
        screen.fill(SKY_BLUE)
        all_sprites.draw(screen)

        # UI
        if player.is_dead:
            text = font.render("GAME OVER - Press R to Restart", True, BLACK)
            screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
