import pygame
import sys

# Init
pygame.init()
SCALE = 2
NES_W, NES_H = 256, 240
screen = pygame.display.set_mode((600, 400))
nes_surface = pygame.Surface((NES_W, NES_H))
pygame.display.set_caption("ULTRA MARIO 2D BROS")
clock = pygame.time.Clock()

# Famicom palette (exact NES colors)
PAL = {
    'black': (0, 0, 0),
    'white': (252, 252, 252),
    'sky': (92, 148, 252),
    'red': (200, 76, 12),
    'darkred': (136, 20, 0),
    'skin': (252, 152, 56),
    'brown': (200, 76, 12),
    'darkbrown': (136, 20, 0),
    'orange': (228, 92, 16),
    'brick': (200, 76, 12),
    'brickdark': (136, 20, 0),
    'bricklight': (228, 132, 80),
    'ground': (228, 92, 16),
    'grounddark': (136, 20, 0),
    'green': (0, 168, 0),
    'darkgreen': (0, 120, 0),
    'goomba': (172, 80, 36),
    'goombadark': (116, 52, 20),
    'yellow': (248, 184, 0),
    'question': (228, 132, 80),
    'pipe': (0, 168, 68),
    'pipedark': (0, 120, 0),
    'pipelight': (128, 208, 16),
}

# Authentic NES Mario sprites (16x16 small mario)
MARIO_STAND = [
    "......RRRR......",
    ".....RRRRRR.....",
    ".....BBBBSB.....",
    "....BSBSSBS.....",
    "....BSSBSSBS....",
    "....BBSSSSBB....",
    "......SSSS......",
    "....RRBRR.......",
    "...RRRBRRRB.....",
    "..RRRRBRRRRB....",
    "..SSRBBBRSS.....",
    "..SSSBBBBSSS....",
    "..SSBBBBBSS.....",
    "....BBB.BBB.....",
    "...BBB...BBB....",
    "...BB.....BB....",
]

MARIO_RUN1 = [
    "......RRRR......",
    ".....RRRRRR.....",
    ".....BBBBSB.....",
    "....BSBSSBS.....",
    "....BSSBSSBS....",
    "....BBSSSSBB....",
    "......SSSS......",
    "....RRRRRBB.....",
    "..BBRRRRRRBB....",
    "..BBRRRRRRRBB...",
    "..BBSSRRRSS.....",
    "....SSRRRSSS....",
    "...SSRRRRRSS....",
    "...RRRR..BB.....",
    "...RRRR.........",
    "....BBBB........",
]

MARIO_RUN2 = [
    "......RRRR......",
    ".....RRRRRR.....",
    ".....BBBBSB.....",
    "....BSBSSBS.....",
    "....BSSBSSBS....",
    "....BBSSSSBB....",
    "......SSSS......",
    ".....RRBRRB.....",
    "....RRRBRRRB....",
    "....RRRRRRRR....",
    "....SSRBBRSS....",
    "...SSSBBBBSSS...",
    "...SSBBBBBBSS...",
    "....BBBB.BB.....",
    ".....BB..BB.....",
    "..........BB....",
]

MARIO_RUN3 = [
    "................",
    "......RRRR......",
    ".....RRRRRR.....",
    ".....BBBBSB.....",
    "....BSBSSBS.....",
    "....BSSBSSBS....",
    "....BBSSSSBB....",
    "......SSSSBB....",
    ".....RRRRRBB....",
    "....RRRRRRBB....",
    "...BBRRRRRR.....",
    "...BBSSRRSS.....",
    "...BSSSRRSSS....",
    "..BB.RRRR.......",
    "......BBBB......",
    ".....BBBB.......",
]

MARIO_JUMP = [
    "......BBB.......",
    "......RRRR......",
    ".....RRRRRR.....",
    ".....BBBBSB.....",
    "....BSBSSBS.....",
    "....BSSBSSBS....",
    "....BBSSSSBB....",
    "......SSSS......",
    "...BRRRRRRRRB...",
    "..BBRRRRRRRRRBB.",
    "..SSRRRBBRRRRSS.",
    "..SSSBBBBBBSSS..",
    "..SSBBBBBBBBSS..",
    "....BBBB.BBBB...",
    "...BBB....BBB...",
    "..BBB......BBB..",
]

GOOMBA_1 = [
    "......BBBB......",
    "....BBBBBBBB....",
    "...BBBBBBBBBB...",
    "..BBWWBBBBWWBB..",
    "..BWWWBBBBWWWB..",
    ".BBWKKBBBBKKWBB.",
    ".BBBWWBBBBWWBBB.",
    ".BBBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBBB.",
    "..BBBBBBBBBBBB..",
    "....BBBBBBBB....",
    "...SSSSSSSSSS...",
    "..SSSS....SSSS..",
    ".SSSS......SSSS.",
    ".SSS........SSS.",
    "................",
]

GOOMBA_2 = [
    "......BBBB......",
    "....BBBBBBBB....",
    "...BBBBBBBBBB...",
    "..BBWWBBBBWWBB..",
    "..BWWWBBBBWWWB..",
    ".BBWKKBBBBKKWBB.",
    ".BBBWWBBBBWWBBB.",
    ".BBBBBBBBBBBBBB.",
    ".BBBBBBBBBBBBBB.",
    "..BBBBBBBBBBBB..",
    "....BBBBBBBB....",
    "...SSSSSSSSSS...",
    "....SSSSSSSS....",
    "..SSSS....SSSS..",
    "................",
    "................",
]

BRICK_TILE = [
    "LLLLLLLDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "DDDDDDDDDDDDDDDD",
    "DDDLLLLLLLLDLLLL",
    "DDDLLLLLLLLDLLLL",
    "DDDLLLLLLLLDLLLL",
    "DDDDDDDDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "DDDDDDDDDDDDDDDD",
    "DDDLLLLLLLLDLLLL",
    "DDDLLLLLLLLDLLLL",
    "DDDLLLLLLLLDLLLL",
    "DDDDDDDDDDDDDDDD",
]

GROUND_TILE = [
    "GGGGGGGGGGGGGGGG",
    "GLLGLLLGLLGLLLGL",
    "GLLLLLLLLLLLLLLL",
    "LLLLLLLLLLLLLLLL",
    "DDDDDDDDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "DDDDDDDDDDDDDDDD",
    "DDDLLLLLLLLDLLLL",
    "DDDLLLLLLLLDLLLL",
    "DDDDDDDDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "LLLLLLLDDDDDDDDD",
    "DDDDDDDDDDDDDDDD",
    "DDDLLLLLLLLDLLLL",
    "DDDLLLLLLLLDLLLL",
]

QUESTION_TILE = [
    "LLLLLLLLLLLLLLLD",
    "LDDDDDDDDDDDDDD.",
    "LD..DDDDDDD..DD.",
    "LD.DDDD.DDDD.DD.",
    "LD.DDDDDDDDD.DD.",
    "LD.DDDDDDDDD.DD.",
    "LD......DDDD.DD.",
    "LDDDDDDDDDDD.DD.",
    "LDDDDD.DDDDD.DD.",
    "LDDDDD.DDDDD.DD.",
    "LDDDDDDDDDDD.DD.",
    "LDDDDD.DDDDD.DD.",
    "LDDDDD.DDDDD.DD.",
    "LD...........DD.",
    "L...............",
    "D...............",
]

PIPE_TOP_L = [
    "DDDDDDDDDDDDDDDD",
    "DLLLLLLLLLLLLLLG",
    "DLGGGGGGGGGGGGGG",
    "DLGGGGGGGGGGGGGG",
    "DLGGGGGGGGGGGGGG",
    "DLLLLLLLLLLLLLLG",
    "DDDDDDDDDDDDDDDD",
    "..DLLLLLLLLLLG..",
    "..DLGGGGGGGGG...",
    "..DLGGGGGGGGG...",
    "..DLGGGGGGGGG...",
    "..DLGGGGGGGGG...",
    "..DLGGGGGGGGG...",
    "..DLGGGGGGGGG...",
    "..DLGGGGGGGGG...",
    "..DLGGGGGGGGG...",
]

PIPE_TOP_R = [
    "DDDDDDDDDDDDDDDD",
    "GLLLLLLLLLLLLLLG",
    "GGGGGGGGGGGGGGDG",
    "GGGGGGGGGGGGGGDG",
    "GGGGGGGGGGGGGGDG",
    "GLLLLLLLLLLLLLDG",
    "DDDDDDDDDDDDDDDD",
    "..GLLLLLLLLLLD..",
    "...GGGGGGGGGD...",
    "...GGGGGGGGGD...",
    "...GGGGGGGGGD...",
    "...GGGGGGGGGD...",
    "...GGGGGGGGGD...",
    "...GGGGGGGGGD...",
    "...GGGGGGGGGD...",
    "...GGGGGGGGGD...",
]

def draw_sprite(surf, data, x, y, color_map, flip=False):
    """Draw a sprite from string data with color mapping"""
    for row_idx, row in enumerate(data):
        chars = list(reversed(row)) if flip else list(row)
        for col_idx, char in enumerate(chars):
            if char in color_map and char != '.':
                pygame.draw.rect(surf, color_map[char], (x + col_idx, y + row_idx, 1, 1))

# Physics constants (NES accurate)
GRAVITY = 0.25
MAX_FALL = 4.5
WALK_ACCEL = 0.055
RUN_ACCEL = 0.09
FRICTION = 0.05
WALK_MAX = 1.5
RUN_MAX = 2.5
JUMP_FORCE = 4.2

class Mario:
    def __init__(self):
        self.x, self.y = 40.0, 176.0
        self.vx, self.vy = 0.0, 0.0
        self.dir = 1
        self.jumping = False
        self.grounded = False
        self.frame = 0
        self.anim_timer = 0
        self.jump_held = False
        self.color_map = {'R': PAL['red'], 'B': PAL['darkbrown'], 'S': PAL['skin'], '.': None}
        
    def update(self, keys):
        running = keys[pygame.K_z]
        accel = RUN_ACCEL if running else WALK_ACCEL
        max_speed = RUN_MAX if running else WALK_MAX
        
        if keys[pygame.K_RIGHT]:
            self.vx = min(self.vx + accel, max_speed)
            self.dir = 1
        elif keys[pygame.K_LEFT]:
            self.vx = max(self.vx - accel, -max_speed)
            self.dir = -1
        else:
            if self.vx > 0: self.vx = max(0, self.vx - FRICTION)
            elif self.vx < 0: self.vx = min(0, self.vx + FRICTION)
        
        if keys[pygame.K_x] and self.grounded and not self.jumping:
            jump_power = JUMP_FORCE + abs(self.vx) * 0.15
            self.vy = -jump_power
            self.jumping = True
            self.jump_held = True
            self.grounded = False
        
        if not keys[pygame.K_x]:
            if self.jump_held and self.vy < -1.5:
                self.vy = -1.5
            self.jump_held = False
        
        self.vy = min(self.vy + GRAVITY, MAX_FALL)
        self.x += self.vx
        self.y += self.vy
        
        if self.x < 0: self.x = 0
        
        self.anim_timer += 1
        if abs(self.vx) > 0.1 and self.grounded:
            speed = 8 - int(abs(self.vx) * 2)
            if self.anim_timer % max(3, speed) == 0:
                self.frame = (self.frame + 1) % 3
        elif self.grounded:
            self.frame = 0
    
    def draw(self, surf, cam_x):
        dx = int(self.x - cam_x)
        dy = int(self.y)
        flip = self.dir < 0
        
        if not self.grounded:
            sprite = MARIO_JUMP
        elif abs(self.vx) > 0.1:
            sprites = [MARIO_RUN1, MARIO_RUN2, MARIO_RUN3]
            sprite = sprites[self.frame % 3]
        else:
            sprite = MARIO_STAND
        
        draw_sprite(surf, sprite, dx, dy, self.color_map, flip)

class Block:
    def __init__(self, x, y, btype="brick"):
        self.x, self.y = x, y
        self.type = btype
        self.hit = False
        self.frame = 0
        
    def draw(self, surf, cam_x):
        dx = int(self.x - cam_x)
        if self.type == "brick":
            cmap = {'L': PAL['brick'], 'D': PAL['brickdark']}
            draw_sprite(surf, BRICK_TILE, dx, self.y, cmap)
        elif self.type == "ground":
            cmap = {'L': PAL['ground'], 'D': PAL['grounddark'], 'G': PAL['green']}
            draw_sprite(surf, GROUND_TILE, dx, self.y, cmap)
        elif self.type == "question":
            cmap = {'L': PAL['yellow'], 'D': PAL['question'], '.': PAL['black']}
            draw_sprite(surf, QUESTION_TILE, dx, self.y, cmap)
        elif self.type == "pipe_tl":
            cmap = {'L': PAL['pipelight'], 'G': PAL['pipe'], 'D': PAL['pipedark'], '.': None}
            draw_sprite(surf, PIPE_TOP_L, dx, self.y, cmap)
        elif self.type == "pipe_tr":
            cmap = {'L': PAL['pipelight'], 'G': PAL['pipe'], 'D': PAL['pipedark'], '.': None}
            draw_sprite(surf, PIPE_TOP_R, dx, self.y, cmap)

class Goomba:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx = -0.5
        self.alive = True
        self.squished = False
        self.squish_timer = 0
        self.frame = 0
        self.anim_timer = 0
        self.color_map = {'B': PAL['goomba'], 'W': PAL['white'], 'K': PAL['black'], 'S': PAL['goombadark'], '.': None}
        
    def update(self):
        if self.squished:
            self.squish_timer += 1
            if self.squish_timer > 30:
                self.alive = False
            return
        if not self.alive: return
        self.x += self.vx
        self.anim_timer += 1
        if self.anim_timer % 12 == 0:
            self.frame = 1 - self.frame
    
    def draw(self, surf, cam_x):
        if not self.alive: return
        dx = int(self.x - cam_x)
        if self.squished:
            pygame.draw.rect(surf, PAL['goomba'], (dx + 2, self.y + 12, 12, 4))
        else:
            sprite = GOOMBA_1 if self.frame == 0 else GOOMBA_2
            draw_sprite(surf, sprite, dx, self.y, self.color_map)

class Cloud:
    def __init__(self, x, y, size=1):
        self.x, self.y, self.size = x, y, size
    def draw(self, surf, cam_x):
        dx = int(self.x - cam_x * 0.5)
        for i in range(self.size):
            pygame.draw.ellipse(surf, PAL['white'], (dx + i * 14, self.y, 20, 14))
        pygame.draw.ellipse(surf, PAL['white'], (dx + 4, self.y - 6, 16, 12))

class Bush:
    def __init__(self, x, y, size=1):
        self.x, self.y, self.size = x, y, size
    def draw(self, surf, cam_x):
        dx = int(self.x - cam_x)
        for i in range(self.size):
            pygame.draw.ellipse(surf, PAL['green'], (dx + i * 14, self.y, 20, 14))
        pygame.draw.ellipse(surf, PAL['green'], (dx + 6, self.y - 5, 14, 10))

class Game:
    def __init__(self):
        self.state = "menu"
        self.mario = Mario()
        self.blocks = []
        self.enemies = []
        self.clouds = []
        self.bushes = []
        self.camera_x = 0
        self.score = 0
        self.coins = 0
        self.time = 400
        self.time_tick = 0
        self.build_level()
        
    def build_level(self):
        # Ground
        for x in range(0, 256 * 6, 16):
            if not (x >= 272 and x < 320):  # Pit
                self.blocks.append(Block(x, 208, "ground"))
                self.blocks.append(Block(x, 224, "ground"))
        
        # Bricks and questions
        for i, bx in enumerate([256, 272, 288, 304, 320]):
            self.blocks.append(Block(bx, 144, "question" if i == 2 else "brick"))
        
        self.blocks.append(Block(352, 144, "question"))
        
        # Stair blocks
        for i in range(4):
            for j in range(i + 1):
                self.blocks.append(Block(400 + i * 16, 192 - j * 16, "brick"))
        
        # Pipe
        self.blocks.append(Block(176, 176, "pipe_tl"))
        self.blocks.append(Block(192, 176, "pipe_tr"))
        self.blocks.append(Block(176, 192, "pipe_tl"))
        self.blocks.append(Block(192, 192, "pipe_tr"))
        
        # Enemies
        self.enemies.append(Goomba(200, 192))
        self.enemies.append(Goomba(340, 192))
        
        # Decoration
        self.clouds = [Cloud(60, 40, 2), Cloud(180, 30, 1), Cloud(320, 50, 3), Cloud(500, 35, 2)]
        self.bushes = [Bush(48, 200, 2), Bush(200, 200, 1), Bush(400, 200, 3)]
    
    def update(self, keys):
        if self.state != "playing": return
        
        self.mario.update(keys)
        for e in self.enemies: e.update()
        
        # Timer
        self.time_tick += 1
        if self.time_tick >= 24:
            self.time_tick = 0
            self.time = max(0, self.time - 1)
        
        # Ground collision
        self.mario.grounded = False
        ground_y = 192
        
        for block in self.blocks:
            if block.type in ["ground", "brick", "question", "pipe_tl", "pipe_tr"]:
                bx, by = block.x, block.y
                bw, bh = 16, 16
                
                mx, my = self.mario.x, self.mario.y
                mw, mh = 12, 16
                
                if mx + mw > bx and mx < bx + bw and my + mh > by and my < by + bh:
                    # Vertical collision
                    if self.mario.vy > 0 and my + mh - self.mario.vy <= by + 2:
                        self.mario.y = by - mh
                        self.mario.vy = 0
                        self.mario.grounded = True
                        self.mario.jumping = False
                    elif self.mario.vy < 0 and my - self.mario.vy >= by + bh - 2:
                        self.mario.y = by + bh
                        self.mario.vy = 0
                    # Horizontal collision
                    elif self.mario.vx > 0:
                        self.mario.x = bx - mw
                        self.mario.vx = 0
                    elif self.mario.vx < 0:
                        self.mario.x = bx + bw
                        self.mario.vx = 0
        
        # Pit death
        if self.mario.y > 240:
            self.mario.x, self.mario.y = 40, 176
            self.mario.vx, self.mario.vy = 0, 0
        
        # Enemy collision
        for e in self.enemies:
            if not e.alive or e.squished: continue
            if abs(self.mario.x - e.x) < 14 and abs(self.mario.y - e.y) < 16:
                if self.mario.vy > 0 and self.mario.y + 8 < e.y:
                    e.squished = True
                    self.mario.vy = -3.5
                    self.score += 100
        
        # Camera
        target = self.mario.x - 100
        self.camera_x = max(0, target)
    
    def draw(self, surf):
        surf.fill(PAL['sky'])
        
        # Clouds (parallax)
        for c in self.clouds: c.draw(surf, self.camera_x)
        
        # Bushes
        for b in self.bushes: b.draw(surf, self.camera_x)
        
        # Blocks
        for block in self.blocks:
            if -16 < block.x - self.camera_x < 272:
                block.draw(surf, self.camera_x)
        
        # Enemies
        for e in self.enemies:
            if -16 < e.x - self.camera_x < 272:
                e.draw(surf, self.camera_x)
        
        # Mario
        self.mario.draw(surf, self.camera_x)
        
        # HUD
        font = pygame.font.SysFont("courier", 8, bold=True)
        hud_y = 8
        surf.blit(font.render("MARIO", True, PAL['white']), (24, hud_y))
        surf.blit(font.render(f"{self.score:06d}", True, PAL['white']), (24, hud_y + 10))
        surf.blit(font.render(f"x{self.coins:02d}", True, PAL['white']), (100, hud_y + 10))
        surf.blit(font.render("WORLD", True, PAL['white']), (144, hud_y))
        surf.blit(font.render("1-1", True, PAL['white']), (152, hud_y + 10))
        surf.blit(font.render("TIME", True, PAL['white']), (200, hud_y))
        surf.blit(font.render(f"{self.time:3d}", True, PAL['white']), (204, hud_y + 10))
        
        if self.state == "menu":
            # Title
            title_font = pygame.font.SysFont("courier", 12, bold=True)
            surf.blit(title_font.render("ULTRA MARIO 2D BROS", True, PAL['red']), (52, 70))
            surf.blit(title_font.render("ULTRA MARIO 2D BROS", True, PAL['yellow']), (50, 68))
            
            surf.blit(font.render("(C) 2025 FLAMES CO", True, PAL['white']), (80, 100))
            surf.blit(font.render("PRESS X TO START", True, PAL['white']), (80, 140))
            surf.blit(font.render("ARROWS=MOVE X=JUMP Z=RUN", True, PAL['white']), (44, 160))

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
        
        nes_surface.fill((0, 0, 0))
        game.draw(nes_surface)
        
        # Scale NES surface to 600x400
        scaled = pygame.transform.scale(nes_surface, (600, 400))
        screen.blit(scaled, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
