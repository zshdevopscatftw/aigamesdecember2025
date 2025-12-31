import pygame
import sys
import math

"""
ULTRA!MARIO 2D BROS INFDEV v3.2
[C] 1985 NINTENDO
[C] 2025-2026 SAMSOFT

Prototype / Fan-style platformer
Built with Pygame
FILES = OFF (procedural sprites only)
Sprite Animation System v1.0
"""

# ======================
# CONFIG
# ======================
W, H = 800, 480
FPS = 60
GRAVITY = 0.8
JUMP_POWER = -14
SPEED = 4
ANIMATION_SPEED = 6  # Lower = faster animation

STATE_MENU = 0
STATE_GAME = 1

# ======================
# INIT
# ======================
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("ULTRA!MARIO 2D BROS INFDEV v3.2")
clock = pygame.time.Clock()

# ======================
# COLORS
# ======================
SKY = (92, 148, 252)
GROUND = (106, 190, 48)
ENEMY = (80, 40, 20)
COIN = (252, 216, 0)
FLAG = (255, 255, 255)
TEXT = (0, 0, 0)
WHITE = (255, 255, 255)

# SMB1 NES PALETTE (2C02 PPU ACCURATE)
RED_NES = (181, 49, 32)    # 0x16
BROWN_NES = (136, 112, 0)  # 0x0A
SKIN_NES = (252, 152, 56)  # 0x27
BLACK_NES = (0, 0, 0)      # 0x0F (for outlines)

# ======================
# FONTS
# ======================
title_font = pygame.font.SysFont("Courier", 48, bold=True)
menu_font = pygame.font.SysFont("Courier", 20, bold=True)
hud_font = pygame.font.SysFont(None, 24)

# ======================
# PROCEDURAL MARIO SPRITE FRAMES
# ======================
def make_mario_frame(pixels_grid, scale=2):
    """Universal function to create any Mario frame from a pixel grid."""
    color_map = {
        "R": RED_NES,      # Red (Hat, Overalls)
        "H": BROWN_NES,    # Brown (Hair, Shirt, Shoes)
        "S": SKIN_NES,     # Skin
        "B": BLACK_NES,    # Black (outline/details)
        ".": (0, 0, 0, 0)  # Transparent
    }
    
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    
    for y, row in enumerate(pixels_grid):
        for x, c in enumerate(row):
            if c in color_map:
                surf.set_at((x, y), color_map[c])
    
    return pygame.transform.scale(surf, (16 * scale, 16 * scale))

# SMALL MARIO SPRITE DEFINITIONS (16x16 grids)
MARIO_STAND = [
    ".......RRRRR....",
    "......RRRRRRRRR.",
    "......HHSSSH....",
    ".....HSSHSSSH...",
    ".....HSSHSSSH...",
    ".....HSSSSS.HH..",
    ".....HHHHHHH....",
    "......RRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRR..RRR...",
    "....HHH....HHH..",
    "...HHHH....HHHH.",
    "................",
    "................",
    "................"
]

MARIO_WALK1 = [
    ".......RRRRR....",
    "......RRRRRRRRR.",
    "......HHSSSH....",
    ".....HSSHSSSH...",
    ".....HSSHSSSH...",
    ".....HSSSSS.HH..",
    ".....HHHHHHH....",
    "......RRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRR..RRR...",
    "....HHH...HHH...",
    "...HHHH..HHH....",
    "................",
    "................",
    "................"
]

MARIO_WALK2 = [
    ".......RRRRR....",
    "......RRRRRRRRR.",
    "......HHSSSH....",
    ".....HSSHSSSH...",
    ".....HSSHSSSH...",
    ".....HSSSSS.HH..",
    ".....HHHHHHH....",
    "......RRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRR..RRR...",
    "....HHH.HHH.....",
    "...HHHHHHH......",
    "................",
    "................",
    "................"
]

MARIO_JUMP = [
    ".......RRRRR....",
    "......RRRRRRRRR.",
    "......HHSSSH....",
    ".....HSSHSSSH...",
    ".....HSSHSSSH...",
    ".....HSSSSS.HH..",
    ".....HHHHHHH....",
    "......RRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRR..RRR...",
    "....HHH....HHH..",
    "...HHHH....HHHH.",
    "...............H",
    ".............HHH",
    "...........HHHHH"
]

MARIO_SKID = [
    ".......RRRRR....",
    "......RRRRRRRRR.",
    "......HHSSSH....",
    ".....HSSHSSSH...",
    ".....HSSHSSSH...",
    ".....HSSSSS.HH..",
    ".....HHHHHHH....",
    "......RRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRRRRRRR...",
    ".....RRR..RRR...",
    "....HHH....HHH..",
    "...HHHH....HHHH.",
    "...............H",
    ".............HHH",
    "...........HHHHH"
]

# Generate all sprite frames
MARIO_FRAMES = {
    'stand': make_mario_frame(MARIO_STAND, scale=2),
    'walk1': make_mario_frame(MARIO_WALK1, scale=2),
    'walk2': make_mario_frame(MARIO_WALK2, scale=2),
    'jump': make_mario_frame(MARIO_JUMP, scale=2),
    'skid': make_mario_frame(MARIO_SKID, scale=2)
}

# ======================
# PROCEDURAL ENEMY SPRITES
# ======================
def make_goomba_frame(pixels_grid, scale=2):
    """Create Goomba enemy sprites."""
    color_map = {
        "B": BLACK_NES,    # Black
        "D": (120, 60, 40),# Dark brown
        "L": (160, 100, 60),# Light brown
        "E": (200, 160, 120),# Eye white
        ".": (0, 0, 0, 0)  # Transparent
    }
    
    surf = pygame.Surface((16, 16), pygame.SRCALPHA)
    
    for y, row in enumerate(pixels_grid):
        for x, c in enumerate(row):
            if c in color_map:
                surf.set_at((x, y), color_map[c])
    
    return pygame.transform.scale(surf, (16 * scale, 16 * scale))

GOOMBA_FRAME1 = [
    "................",
    "................",
    "....BBBBBBBB....",
    "...BDDDDDDDDB...",
    "..BDDDDDDDDDDB..",
    ".BDDDDDDDDDDDDB.",
    ".BDDLDDDDLDDDDB.",
    "BDDDLLLLLLLDDDDB",
    "BDDDLLLLLLLDDDDB",
    "BDDDLEEEEEELDDDB",
    ".BDDDLEEEELDDDB.",
    ".BDDDDLLLLDDDDB.",
    "..BDDDDDDDDDDB..",
    "...BDDDDDDDDB...",
    "....BBBBBBBB....",
    "................"
]

GOOMBA_FRAME2 = [
    "................",
    "................",
    "................",
    "....BBBBBBBB....",
    "...BDDDDDDDDB...",
    "..BDDDDDDDDDDB..",
    ".BDDDDDDDDDDDDB.",
    "BDDDLLLLLLLDDDDB",
    "BDDDLLLLLLLDDDDB",
    "BDDDLEEEEEELDDDB",
    ".BDDDLEEEELDDDB.",
    ".BDDDDLLLLDDDDB.",
    "..BDDDDDDDDDDB..",
    "...BDDDDDDDDB...",
    "....BBBBBBBB....",
    "................"
]

ENEMY_FRAMES = {
    'goomba1': make_goomba_frame(GOOMBA_FRAME1, scale=2),
    'goomba2': make_goomba_frame(GOOMBA_FRAME2, scale=2)
}

# ======================
# PROCEDURAL COIN SPRITE
# ======================
def make_coin_sprite(scale=2):
    """Create animated coin sprite."""
    coin_surfs = []
    
    # 4 animation frames for spinning coin
    coin_frames = [
        [
            "................",
            "................",
            ".....YYYYYY.....",
            "...YYYYYYYYYY...",
            "..YYYYYYYYYYYY..",
            ".YYYYYYYYYYYYYY.",
            ".YYYYGGGGGGYYYY.",
            "YYYYGGGGGGGGYYYY",
            "YYYYGGGGGGGGYYYY",
            ".YYYYGGGGGGYYYY.",
            ".YYYYYYYYYYYYYY.",
            "..YYYYYYYYYYYY..",
            "...YYYYYYYYYY...",
            ".....YYYYYY.....",
            "................",
            "................"
        ],
        [
            "................",
            "................",
            "......YYYY......",
            "...YYYYYYYYYY...",
            "..YYYYYYYYYYYY..",
            ".YYGGGGGGGGGGYY.",
            ".YGGGGGGGGGGGGY.",
            "YGGGGGGGGGGGGGGY",
            "YGGGGGGGGGGGGGGY",
            ".YGGGGGGGGGGGGY.",
            ".YYGGGGGGGGGGYY.",
            "..YYYYYYYYYYYY..",
            "...YYYYYYYYYY...",
            "......YYYY......",
            "................",
            "................"
        ]
    ]
    
    color_map = {
        "Y": COIN,          # Yellow
        "G": (220, 190, 0), # Darker yellow
        ".": (0, 0, 0, 0)
    }
    
    for frame_grid in coin_frames:
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        for y, row in enumerate(frame_grid):
            for x, c in enumerate(row):
                if c in color_map:
                    surf.set_at((x, y), color_map[c])
        coin_surfs.append(pygame.transform.scale(surf, (16 * scale, 16 * scale)))
    
    return coin_surfs

COIN_SPRITES = make_coin_sprite(scale=1)

# ======================
# PLAYER WITH ANIMATION
# ======================
class Player:
    def __init__(self):
        # Hitbox adjusted for the visual sprite
        self.rect = pygame.Rect(50, 300, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        
        # Animation state
        self.animation_timer = 0
        self.current_frame = 'stand'
        self.walk_frame = 0
        self.is_jumping = False
        self.is_moving = False
        self.was_moving = False
        
        # Movement tracking
        self.last_x = self.rect.x
        self.skid_timer = 0

    def update(self, keys):
        dx = 0
        self.is_moving = False
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            dx = -SPEED
            self.is_moving = True
            if self.facing_right and self.on_ground:
                self.facing_right = False
                self.skid_timer = 10  # Start skid animation
            
        if keys[pygame.K_RIGHT]:
            dx = SPEED
            self.is_moving = True
            if not self.facing_right and self.on_ground:
                self.facing_right = True
                self.skid_timer = 10  # Start skid animation
        
        # Apply movement
        self.rect.x += dx
        self.collide(dx, 0)
        
        # Vertical movement (gravity)
        self.vel_y += GRAVITY
        dy = self.vel_y
        self.rect.y += dy
        
        # Ground check
        self.on_ground = False
        self.collide(0, dy)
        
        # Jump state
        self.is_jumping = not self.on_ground and self.vel_y < 0
        
        # Update animation
        self.update_animation(dx)
        
        # Update skid timer
        if self.skid_timer > 0:
            self.skid_timer -= 1

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_POWER
            self.is_jumping = True

    def collide(self, dx, dy):
        for tile in tiles:
            if self.rect.colliderect(tile):
                if dx > 0:
                    self.rect.right = tile.left
                if dx < 0:
                    self.rect.left = tile.right
                if dy > 0:
                    self.rect.bottom = tile.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                if dy < 0:
                    self.rect.top = tile.bottom
                    self.vel_y = 0

    def update_animation(self, dx):
        """Update player animation state based on movement."""
        self.animation_timer += 1
        
        # Determine animation state
        if self.is_jumping:
            self.current_frame = 'jump'
            self.walk_frame = 0
        elif self.skid_timer > 0 and self.on_ground:
            self.current_frame = 'skid'
            self.walk_frame = 0
        elif self.is_moving and self.on_ground:
            # Walking animation cycle
            if self.animation_timer % ANIMATION_SPEED == 0:
                self.walk_frame = 1 - self.walk_frame  # Toggle between 0 and 1
            
            if self.walk_frame == 0:
                self.current_frame = 'walk1'
            else:
                self.current_frame = 'walk2'
        else:
            # Standing still
            self.current_frame = 'stand'
            self.walk_frame = 0

    def get_sprite(self):
        """Get the current sprite frame, flipped if facing left."""
        sprite = MARIO_FRAMES[self.current_frame]
        if not self.facing_right:
            sprite = pygame.transform.flip(sprite, True, False)
        return sprite

# ======================
# ENEMY CLASS
# ======================
class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.direction = -1
        self.animation_timer = 0
        self.current_frame = 0
        
    def update(self):
        self.rect.x += self.direction * 2
        
        # Boundary check
        if self.rect.left < 300 or self.rect.right > 500:
            self.direction *= -1
            
        # Animation
        self.animation_timer += 1
        if self.animation_timer % 15 == 0:
            self.current_frame = 1 - self.current_frame
            
    def get_sprite(self):
        """Get current enemy sprite frame."""
        if self.current_frame == 0:
            return ENEMY_FRAMES['goomba1']
        else:
            return ENEMY_FRAMES['goomba2']

# ======================
# COIN CLASS
# ======================
class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 12, 12)
        self.animation_timer = 0
        self.collected = False
        
    def update(self):
        self.animation_timer += 1
        
    def get_sprite(self):
        """Get current coin sprite frame."""
        frame = (self.animation_timer // 10) % len(COIN_SPRITES)
        return COIN_SPRITES[frame]

# ======================
# WORLD SETUP
# ======================
def reset_world():
    global tiles, coins, enemies, flag, player, score, win, coin_objects
    
    tiles = []
    coins = []
    coin_objects = []
    enemies = []

    # Ground platform
    for x in range(0, W, 40):
        tiles.append(pygame.Rect(x, H - 40, 40, 40))

    # Floating platforms
    tiles += [
        pygame.Rect(200, 340, 120, 20),
        pygame.Rect(400, 280, 120, 20),
        pygame.Rect(600, 220, 120, 20),
    ]

    # Create coin objects
    coin_positions = [
        (230, 300), (250, 300), (270, 300),
        (430, 240), (450, 240), (470, 240),
        (630, 180), (650, 180), (670, 180)
    ]
    
    for x, y in coin_positions:
        coin_obj = Coin(x, y)
        coin_objects.append(coin_obj)
        coins.append(coin_obj.rect)

    # Enemies
    enemies.append(Enemy(350, H - 72))
    enemies.append(Enemy(450, H - 72))

    # Flag
    flag = pygame.Rect(740, H - 160, 10, 120)

    # Player
    player = Player()
    score = 0
    win = False

# ======================
# PROCEDURAL CLOUDS
# ======================
def draw_cloud(x, y, size=1.0):
    """Draw a procedural cloud."""
    cloud_color = (255, 255, 255)
    base_size = int(30 * size)
    
    # Cloud shape using circles
    points = [
        (x, y),
        (x + base_size, y - base_size//3),
        (x + base_size*2, y),
        (x + base_size, y + base_size//3),
        (x, y)
    ]
    
    # Draw cloud
    pygame.draw.polygon(screen, cloud_color, points)
    pygame.draw.circle(screen, cloud_color, (x + base_size//3, y - base_size//4), base_size//2)
    pygame.draw.circle(screen, cloud_color, (x + base_size, y - base_size//2), base_size//2)
    pygame.draw.circle(screen, cloud_color, (x + base_size*5//3, y - base_size//4), base_size//2)
    pygame.draw.circle(screen, cloud_color, (x + base_size, y + base_size//4), base_size//2)

# ======================
# MENU DRAW
# ======================
def draw_menu(blink):
    screen.fill(SKY)
    
    # Draw background clouds
    for i in range(3):
        draw_cloud(100 + i*250, 80 + (i%2)*40, 1.0 + i*0.2)
    
    # Title
    title = title_font.render("ULTRA!MARIO 2D BROS", True, TEXT)
    title_shadow = title_font.render("ULTRA!MARIO 2D BROS", True, (64, 64, 64))
    screen.blit(title_shadow, (W//2 - title.get_width()//2 + 3, 123))
    screen.blit(title, (W//2 - title.get_width()//2, 120))
    
    # Subtitle with animated effect
    subtitle = menu_font.render("INFDEV v3.2", True, TEXT)
    subtitle_rect = subtitle.get_rect(center=(W//2, 180))
    
    # Pulsing effect
    pulse = math.sin(pygame.time.get_ticks() * 0.002) * 10
    subtitle_rect.y += int(pulse)
    screen.blit(subtitle, subtitle_rect)
    
    # Blinking "PRESS START"
    if blink:
        press = menu_font.render("PRESS START", True, TEXT)
        screen.blit(press, (W//2 - press.get_width()//2, 260))
        
        # Draw small Mario as cursor
        mario_cursor = MARIO_FRAMES['stand']
        screen.blit(mario_cursor, (W//2 - press.get_width()//2 - 40, 260))
    
    # Credits
    credit = menu_font.render("(C) 1985 NINTENDO   (C) 2025-2026 SAMSOFT", True, TEXT)
    screen.blit(credit, (W//2 - credit.get_width()//2, 330))
    
    # Footer
    footer = menu_font.render("FILES=OFF • PROCEDURAL SPRITES • HACKER KITTY v3.2", True, (128, 128, 128))
    screen.blit(footer, (W//2 - footer.get_width()//2, 400))

# ======================
# GAME STATE
# ======================
game_state = STATE_MENU
blink_timer = 0
reset_world()

# ======================
# HUD FUNCTIONS
# ======================
def draw_hud():
    """Draw the heads-up display."""
    # Score display with background
    score_text = hud_font.render(f"COINS {score:03d}", True, WHITE)
    score_bg = pygame.Rect(8, 8, score_text.get_width() + 10, score_text.get_height() + 6)
    pygame.draw.rect(screen, (0, 0, 0, 128), score_bg, border_radius=3)
    pygame.draw.rect(screen, WHITE, score_bg, 1, border_radius=3)
    screen.blit(score_text, (15, 12))
    
    # Coin icon next to score
    coin_icon = COIN_SPRITES[0]
    screen.blit(coin_icon, (score_bg.right + 5, 10))
    
    # Lives indicator (placeholder)
    lives_text = hud_font.render("LIVES 3", True, WHITE)
    screen.blit(lives_text, (W - lives_text.get_width() - 15, 12))
    
    # Small Mario icon next to lives
    screen.blit(pygame.transform.scale(MARIO_FRAMES['stand'], (20, 20)), 
                (W - lives_text.get_width() - 35, 10))

# ======================
# DRAW GAME WORLD
# ======================
def draw_world():
    """Draw all game elements."""
    # Sky with gradient effect
    for y in range(0, H, 2):
        shade = min(255, SKY[1] + y//10)
        pygame.draw.line(screen, (SKY[0], shade, SKY[2]), (0, y), (W, y))
    
    # Clouds
    cloud_positions = [(100, 60), (400, 100), (700, 80), (300, 150)]
    for i, (x, y) in enumerate(cloud_positions):
        offset = math.sin(pygame.time.get_ticks() * 0.0005 + i) * 5
        draw_cloud(x + offset, y, 0.8 + i*0.1)
    
    # Ground and platforms
    for tile in tiles:
        # Main ground
        if tile.y == H - 40:
            pygame.draw.rect(screen, GROUND, tile)
            # Ground detail
            for i in range(0, tile.width, 4):
                pygame.draw.line(screen, (86, 170, 38), 
                               (tile.x + i, tile.bottom - 2), 
                               (tile.x + i, tile.bottom), 1)
        else:
            # Floating platforms
            pygame.draw.rect(screen, (140, 100, 60), tile)  # Brown platforms
            pygame.draw.rect(screen, (100, 70, 40), tile, 2)  # Border
    
    # Coins
    for coin_obj in coin_objects[:]:
        if not coin_obj.collected:
            coin_sprite = coin_obj.get_sprite()
            screen.blit(coin_sprite, (coin_obj.rect.x - 2, coin_obj.rect.y - 2))
            coin_obj.update()
    
    # Enemies
    for enemy in enemies:
        enemy_sprite = enemy.get_sprite()
        screen.blit(enemy_sprite, enemy.rect.topleft)
        enemy.update()
    
    # Flag with animation
    flag_color = FLAG
    if win:
        # Pulsing flag when level complete
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 50
        flag_color = (min(255, FLAG[0] + int(pulse)), 
                     min(255, FLAG[1] + int(pulse)), 
                     min(255, FLAG[2] + int(pulse)))
    
    pygame.draw.rect(screen, (200, 0, 0), (flag.x - 5, flag.y, 20, 10))  # Flag top
    pygame.draw.rect(screen, flag_color, flag)  # Flag pole
    pygame.draw.polygon(screen, flag_color, [  # Flag
        (flag.x + 10, flag.y + 10),
        (flag.x + 40, flag.y + 30),
        (flag.x + 10, flag.y + 50)
    ])
    
    # Draw Mario
    mario_sprite = player.get_sprite()
    screen.blit(mario_sprite, player.rect.topleft)
    
    # Draw HUD
    draw_hud()
    
    # Level complete message
    if win:
        win_font = pygame.font.SysFont("Courier", 36, bold=True)
        win_text = win_font.render("LEVEL COMPLETE!", True, WHITE)
        win_shadow = win_font.render("LEVEL COMPLETE!", True, (64, 64, 64))
        
        # Background
        win_bg = pygame.Rect(W//2 - 150, H//2 - 40, 300, 80)
        pygame.draw.rect(screen, (0, 0, 0, 200), win_bg, border_radius=10)
        pygame.draw.rect(screen, WHITE, win_bg, 2, border_radius=10)
        
        # Text with shadow
        screen.blit(win_shadow, (W//2 - win_text.get_width()//2 + 2, H//2 - win_text.get_height()//2 + 2))
        screen.blit(win_text, (W//2 - win_text.get_width()//2, H//2 - win_text.get_height()//2))
        
        # Continue prompt
        continue_font = pygame.font.SysFont(None, 24)
        continue_text = continue_font.render("Press SPACE to continue", True, (200, 200, 0))
        screen.blit(continue_text, (W//2 - continue_text.get_width()//2, H//2 + 20))

# ======================
# MAIN LOOP
# ======================
while True:
    clock.tick(FPS)
    blink_timer = (blink_timer + 1) % 60

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == STATE_MENU:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_world()
                    game_state = STATE_GAME

        elif game_state == STATE_GAME:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_z, pygame.K_UP):
                    player.jump()
                
                # Level reset (debug)
                if event.key == pygame.K_r:
                    reset_world()
                
                # Continue after win
                if win and event.key == pygame.K_SPACE:
                    reset_world()

    if game_state == STATE_MENU:
        draw_menu(blink_timer < 30)
        pygame.display.flip()
        continue

    # ======================
    # GAME LOGIC
    # ======================
    # Update player
    keys = pygame.key.get_pressed()
    player.update(keys)
    
    # Enemy collision
    for enemy in enemies[:]:
        if player.rect.colliderect(enemy.rect):
            if player.vel_y > 0 and player.rect.bottom < enemy.rect.centery:
                # Jump on enemy
                enemies.remove(enemy)
                player.vel_y = JUMP_POWER / 2
                score += 2  # Bonus points for stomping
            else:
                # Player hit
                pygame.quit()
                sys.exit()
    
    # Coin collection
    for coin_obj in coin_objects[:]:
        if not coin_obj.collected and player.rect.colliderect(coin_obj.rect):
            coin_obj.collected = True
            score += 1
    
    # Flag collision
    if player.rect.colliderect(flag):
        win = True
        # Slow down player
        player.rect.x = min(player.rect.x, flag.x - 32)
    
    # Draw everything
    draw_world()
    pygame.display.flip()
