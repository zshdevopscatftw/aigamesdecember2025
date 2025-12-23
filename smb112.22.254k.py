#!/usr/bin/env python3
# ============================================================
# TKINTER SUPER PLUMBER — SAMMY'S REMIX v0.2 (NES EDITION)
# Single File • FILES = OFF • 60 FPS
# [C] Samsoft • All Rights Reserved
# ============================================================

import tkinter as tk
import time
import random

# ================= CONFIG =================
WINDOW_WIDTH = 600   
WINDOW_HEIGHT = 400
FPS = 60

# Physics
GRAVITY = 0.7
FRICTION = 0.85
ACCELERATION = 0.5
JUMP_FORCE = -13 
MAX_SPEED = 5

BLOCK_SIZE = 30
LEVEL_HEIGHT = 14

# ================= COLORS & PALETTE (NES) =================
# Standard NES Color Palette
SKY_BLUE = "#5C94FC"
SKY_BLACK = "#000000"

# ================= SPRITE FACTORY =================
class SpriteFactory:
    def __init__(self):
        self.images = {}

    def get_sprite(self, name):
        return self.images.get(name)

    def generate_all(self):
        # 15x15 Pixel Art Templates (Zoomed x2 to 30x30)
        # NES Palette Mapping:
        # R = Red (#D70000), B = Blue (#0058F8), S = Skin (#FCA044), o = Brick Brown (#C84C0C), 
        # Y = Gold (#F8B800), # = Black (#000000), G = Pipe Green (#00B800), L = Dark Green (#005800),
        # W = White (#F8F8F8), g = Bush Green (#00A800), D = Dirt Brown (#784800),
        # H = Highlight (#FCA044), . = Transparent
        
        palette = {
            "R": "#D70000", # Red
            "B": "#0058F8", # Blue (Overalls)
            "S": "#FCA044", # Skin
            "o": "#C84C0C", # Brick Orange
            "Y": "#F8B800", # Q-Block Gold
            "#": "#000000", # Black
            "G": "#00B800", # Pipe Green (Light)
            "L": "#005800", # Pipe Green (Dark/Shadow)
            "g": "#00A800", # Bush Green
            "W": "#F8F8F8", # White (Clouds/Eyes)
            "D": "#784800", # Dirt Brown
            "X": "#F8D878", # Metal/Hard Block Highlight
            "M": "#787878", # Metal/Hard Block Base
            "Z": "#000000", # Castle Black
        }

        plans = {
            "mario": [
                ".....RRRRR.....",
                "....RRRRRRRR...",
                "....B#R#B#R....",
                "....BBB#BBB....",
                "....BBB#BBB....",
                "....S..#S..S...",
                "....SSS#SSS....",
                ".....SSSSS.....",
                "....BBB#BBB....",
                "....BBB.BBB....",
                "....BBB#BBB....",
                "...BBR...RBB...",
                "....R.....R....",
                "...RRR...RRR...",
                "...............",
            ],
            "goomba": [
                "...............",
                ".....oooooo....",
                "....oooooooo...",
                "...oooooooooo..",
                "...ooWWWWWWoo..",
                "...ooWo#oWooo..",
                "...oooooooooo..",
                "...oooo#ooooo..",
                "....oooooooo...",
                ".....oooooo....",
                "...B........B..",
                "...BB......BB..",
                "..BBB....BBB...",
                "..BB......BB...",
                "...............",
            ],
            "brick": [
                "ooooooooooooooo",
                "o#..o#..o#..o#o",
                "ooooooooooooooo",
                "o#..o#..o#..o#o",
                "ooooooooooooooo",
                "o#..o#..o#..o#o",
                "ooooooooooooooo",
                "o#..o#..o#..o#o",
                "ooooooooooooooo",
                "o#..o#..o#..o#o",
                "ooooooooooooooo",
                "o#..o#..o#..o#o",
                "ooooooooooooooo",
                "o#..o#..o#..o#o",
                "ooooooooooooooo",
            ],
             "floor": [
                "ggggggggggggggg",
                "ggggggggggggggg",
                "DDDDDDDDDDDDDDD",
                "D#..D#..D#..D#D",
                "DDDDDDDDDDDDDDD",
                "D#..D#..D#..D#D",
                "DDDDDDDDDDDDDDD",
                "D#..D#..D#..D#D",
                "DDDDDDDDDDDDDDD",
                "D#..D#..D#..D#D",
                "DDDDDDDDDDDDDDD",
                "D#..D#..D#..D#D",
                "DDDDDDDDDDDDDDD",
                "D#..D#..D#..D#D",
                "DDDDDDDDDDDDDDD",
            ],
            "qblock": [
                "YYYYYYYYYYYYYYY",
                "Y#############Y",
                "Y#YY#Y#YY#Y#YY#Y",
                "Y#YY#Y#YY#Y#YY#Y",
                "Y#YY#Y#YY#Y#YY#Y",
                "Y#YYYYYYYYYYY#Y",
                "Y#YY#YYYYY#YY#Y",
                "Y#YY#YYYYY#YY#Y",
                "Y#YY#YYYYY#YY#Y",
                "Y#YYYYYYYYYYY#Y",
                "Y#YY#YYYYY#YY#Y",
                "Y#YY#YYYYY#YY#Y",
                "Y#YY#YYYYY#YY#Y",
                "Y#############Y",
                "YYYYYYYYYYYYYYY",
            ],
            "solid": [
                "XXXXXXXXXXXXXXX",
                "XMMMMMMMMMMMMMX",
                "XMMXXMMXXMMXXMM",
                "XMMXXMMXXMMXXMM",
                "XMMMMMMMMMMMMMX",
                "XMMXXMMXXMMXXMM",
                "XMMXXMMXXMMXXMM",
                "XMMMMMMMMMMMMMX",
                "XMMXXMMXXMMXXMM",
                "XMMXXMMXXMMXXMM",
                "XMMMMMMMMMMMMMX",
                "XMMXXMMXXMMXXMM",
                "XMMXXMMXXMMXXMM",
                "XMMMMMMMMMMMMMX",
                "XXXXXXXXXXXXXXX",
            ],
            # --- PIPES WITH SHADING ---
            "pipe_tl": [
                "LLLLLLLLLLLLLLL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LLLLLLLLLLLLLLL",
                "...............",
                "...............",
                "...............",
                "..............."
            ],
            "pipe_tr": [
                "LLLLLLLLLLLLLLL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LLLLLLLLLLLLLLL",
                "...............",
                "...............",
                "...............",
                "..............."
            ],
            "pipe_bl": [
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL"
            ],
            "pipe_br": [
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL",
                "LGGGGGGGGGGGGGL"
            ],
            # --- DECOR ---
            "cloud": [
                "...............",
                "...............",
                ".....WWWWW.....",
                "...WW.....WW...",
                "..WW.......WW..",
                ".W...........W.",
                ".W...........W.",
                "..WW.......WW..",
                "...WW.....WW...",
                ".....WWWWW.....",
                "...............",
                "...............",
                "...............",
                "...............",
                "..............."
            ],
            "bush": [
                "...............",
                "...............",
                ".....ggggg.....",
                "...gggggggggg..",
                "..gggggggggggg.",
                ".ggggggggggggg.",
                ".ggggggggggggg.",
                "..gggggggggggg.",
                "...gggggggggg..",
                ".....ggggg.....",
                "...............",
                "...............",
                "...............",
                "...............",
                "..............."
            ],
            "castle": [
                "ooooooooooooooo",
                "o#o#o#o#o#o#o#o",
                "ooooooooooooooo",
                "o#o#o#o#o#o#o#o",
                "ooooooooooooooo",
                "o#o#o#o#o#o#o#o",
                "ooooooooooooooo",
                "o#o#o#o#o#o#o#o",
                "ooooooooooooooo",
                "o#o#o#o#o#o#o#o",
                "ooooooooooooooo",
                "o#o#o#o#o#o#o#o",
                "ooooooooooooooo",
                "o#o#o#o#o#o#o#o",
                "ooooooooooooooo",
            ]
        }

        for name, pixels in plans.items():
            img = tk.PhotoImage(width=15, height=15)
            for y, row in enumerate(pixels):
                for x, char in enumerate(row):
                    if char in palette:
                        img.put(palette[char], (x, y))
            
            # Zoom to 30x30
            self.images[name] = img.zoom(2)
            
# ================= LEVEL GEN =================
def generate_level_data(world, stage):
    # Determine Level Type
    level_type = (stage - 1) % 4 + 1
    is_underground = level_type == 2
    is_castle = level_type == 4
    
    bg = SKY_BLUE
    if is_underground: bg = SKY_BLACK
    elif is_castle: bg = SKY_BLACK

    # --- WORLD 1-1 SPECIAL RECREATION ---
    if world == 1 and stage == 1:
        length = 220
        data = [[" " for _ in range(length)] for _ in range(LEVEL_HEIGHT)]
        
        def add_block(x, y, t): 
            if 0 <= LEVEL_HEIGHT-3-y < LEVEL_HEIGHT:
                data[LEVEL_HEIGHT-3-y][x] = t
        
        def add_pipe(x, h):
            for i in range(h):
                y_pos = LEVEL_HEIGHT-3-i
                if i == h - 1: # TOP
                    data[y_pos][x] = '['   
                    data[y_pos][x+1] = ']' 
                else:          
                    data[y_pos][x] = 'P'   
                    data[y_pos][x+1] = 'p' 

        def add_enemy(x): data[LEVEL_HEIGHT-3][x] = 'E'
        def add_floor(start, end):
            for x in range(start, end):
                data[LEVEL_HEIGHT-1][x] = '1'
                data[LEVEL_HEIGHT-2][x] = '1'
        
        # Ground with pits
        add_floor(0, 69)
        add_floor(71, 86)
        add_floor(89, 153)
        add_floor(155, 220)

        # SCENE 1: Start
        add_block(16, 3, '?') 
        add_block(20, 3, '2') 
        add_block(21, 3, '?') 
        add_block(22, 3, '2')
        add_block(23, 3, '?') 
        add_block(24, 3, '2')
        add_block(22, 7, '?') 
        add_enemy(22)

        # SCENE 2: Pipes (Shortened!)
        add_pipe(28, 2)
        add_pipe(38, 3)
        add_pipe(46, 4)
        add_enemy(41)
        add_enemy(52)
        add_enemy(54)
        add_pipe(57, 4) 

        # SCENE 3: Hidden 1-up Area
        add_block(64, 4, '?') 
        add_enemy(78)
        add_enemy(80)
        
        # SCENE 4: The Rows
        add_block(77, 3, '2')
        add_block(78, 3, '?')
        add_block(79, 3, '2')
        for i in range(80, 88): add_block(i, 7, '2')
        
        # SCENE 5: Starman
        for i in range(91, 95): add_block(i, 7, '?')
        add_block(94, 3, '2')
        add_enemy(97)
        add_enemy(99)
        add_enemy(110)
        add_enemy(112)
        add_enemy(120)
        add_enemy(125)

        # SCENE 6: The Stairs
        base = 134
        for i in range(4):
            for h in range(i+1): data[LEVEL_HEIGHT-3-h][base+i] = 'Q'
        
        base = 140
        for i in range(4):
            for h in range(i+1): data[LEVEL_HEIGHT-3-h][base+i] = 'Q'
        for h in range(4): data[LEVEL_HEIGHT-3-h][base+4] = 'Q'

        base = 148
        for i in range(8):
             for h in range(i+1): data[LEVEL_HEIGHT-3-h][base+i] = 'Q'
        
        # Flag
        flag_x = 168
        for h in range(1, 10):
            data[LEVEL_HEIGHT-2-h][flag_x] = 'F'
        data[LEVEL_HEIGHT-11][flag_x] = 'G'
        
        # Castle
        cx = 175
        for x in range(cx, cx+5):
            for y in range(4):
                 data[LEVEL_HEIGHT-2-y][x] = 'K' 
            if x % 2 == 0: data[LEVEL_HEIGHT-6][x] = 'K'
        
        # Decor (Clouds/Bushes)
        for i in range(0, 200, 10):
             if random.random() < 0.2:
                  y_cloud = random.randint(2, 5)
                  data[y_cloud][i] = 'C' 
                  data[y_cloud][i+1] = 'C'
                  data[y_cloud][i+2] = 'C'
             if random.random() < 0.15:
                 if data[LEVEL_HEIGHT-3][i] == " ":
                     data[LEVEL_HEIGHT-3][i] = 'B'
                     data[LEVEL_HEIGHT-3][i+1] = 'B'

        return {"map": ["".join(r) for r in data], "bg": bg}

    # Fallback Empty
    length = 150
    data = [[" " for _ in range(length)] for _ in range(LEVEL_HEIGHT)]
    return {"map": ["".join(r) for r in data], "bg": bg}

# ================= OBJECTS =================
class GameObject:
    def __init__(self, c, x, y, w, h, img, tag):
        self.c = c
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        if img:
            self.rect = c.create_image(x, y, image=img, anchor="nw", tags=("scroll", tag))
        else:
            color = "green" if tag == "wall" else "red"
            self.rect = c.create_rectangle(x, y, x+w, y+h, fill=color, outline="", tags=("scroll", tag))
        self.vx = 0
        self.vy = 0

class Player:
    def __init__(self, c, x, y, sprite_factory):
        self.c = c
        self.x = x
        self.y = y
        self.w = BLOCK_SIZE * 0.8
        self.h = BLOCK_SIZE * 0.9
        self.sprite = sprite_factory.get_sprite("mario")
        self.rect = c.create_image(x, y, image=self.sprite, anchor="nw", tags="player")
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.score = 0
        self.coins = 0
        self.dead = False

    def update(self, keys):
        if self.dead: return

        if keys.get("Left"): self.vx -= ACCELERATION
        if keys.get("Right"): self.vx += ACCELERATION
        
        self.vx *= FRICTION
        
        if keys.get("space") and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
        
        if not keys.get("space") and self.vy < -4:
            self.vy = -4

        self.vy += GRAVITY
        self.vx = max(-MAX_SPEED, min(MAX_SPEED, self.vx))
        self.vy = min(self.vy, 12) 

        if abs(self.vx) < 0.1: self.vx = 0

class Enemy:
    def __init__(self, c, x, y, sprite_factory):
        self.c = c
        self.x = x
        self.y = y
        self.w = BLOCK_SIZE
        self.h = BLOCK_SIZE
        self.sprite = sprite_factory.get_sprite("goomba")
        self.rect = c.create_image(x, y, image=self.sprite, anchor="nw", tags=("scroll", "enemy"))
        self.vx = -1.5 
        self.vy = 0
        self.dead = False

    def update(self):
        if self.dead: return
        self.vy = min(self.vy + GRAVITY, 12)

# ================= GAME ENGINE =================
class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Sammy's Super Plumber v0.2 (NES Edition)")
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=SKY_BLUE)
        self.canvas.pack()

        # Init Sprites
        self.sprites = SpriteFactory()
        self.sprites.generate_all()

        self.keys = {}
        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)

        self.world = 1
        self.stage = 1
        self.total_scroll = 0
        
        self.setup_ui()
        self.load_level()
        self.loop()

    def key_down(self, e):
        self.keys[e.keysym] = True
    
    def key_up(self, e):
        self.keys[e.keysym] = False

    def setup_ui(self):
        self.hud_score = self.canvas.create_text(20, 20, anchor="nw", text="SCORE: 0", font=("Consolas", 14, "bold"), fill="white", tags="hud")
        self.hud_world = self.canvas.create_text(WINDOW_WIDTH-20, 20, anchor="ne", text="WORLD 1-1", font=("Consolas", 14, "bold"), fill="white", tags="hud")

    def load_level(self):
        # CLEANUP
        self.canvas.delete("scroll") 
        self.canvas.delete("player")
        self.canvas.delete("game_over") 
        
        self.walls = []
        self.enemies = []
        self.coins = []
        self.lava = []
        self.goals = []
        
        self.total_scroll = 0
        self.game_over = False

        data = generate_level_data(self.world, self.stage)
        self.canvas.configure(bg=data["bg"])
        self.canvas.itemconfig(self.hud_world, text=f"WORLD {self.world}-{self.stage}")

        for y, row in enumerate(data["map"]):
            for x, ch in enumerate(row):
                px, py = x * BLOCK_SIZE, y * BLOCK_SIZE
                
                # WALLS & BLOCKS
                if ch in ['1', '2', '?', 'Q', '[', ']', 'P', 'p', 'K']:
                    img = None
                    tag = "wall"
                    
                    if ch == '1': img = self.sprites.get_sprite("floor")
                    elif ch == '2': img = self.sprites.get_sprite("brick")
                    elif ch == '?': img = self.sprites.get_sprite("qblock")
                    elif ch == 'Q': img = self.sprites.get_sprite("solid")
                    elif ch == 'K': img = self.sprites.get_sprite("castle")
                    elif ch == '[': img = self.sprites.get_sprite("pipe_tl")
                    elif ch == ']': img = self.sprites.get_sprite("pipe_tr")
                    elif ch == 'P': img = self.sprites.get_sprite("pipe_bl")
                    elif ch == 'p': img = self.sprites.get_sprite("pipe_br")

                    if img:
                        self.walls.append(GameObject(self.canvas, px, py, BLOCK_SIZE, BLOCK_SIZE, img, tag))
                    else:
                        self.walls.append(GameObject(self.canvas, px, py, BLOCK_SIZE, BLOCK_SIZE, None, tag))

                # DECOR
                elif ch == 'C': 
                     self.canvas.create_image(px, py, image=self.sprites.get_sprite("cloud"), anchor="nw", tags=("scroll", "decor"))
                elif ch == 'B': 
                     self.canvas.create_image(px, py, image=self.sprites.get_sprite("bush"), anchor="nw", tags=("scroll", "decor"))

                # INTERACTABLES
                elif ch == 'E':
                    self.enemies.append(Enemy(self.canvas, px, py, self.sprites))
                elif ch == 'L':
                    self.lava.append(GameObject(self.canvas, px, py, BLOCK_SIZE, BLOCK_SIZE, None, "lava"))
                    self.canvas.itemconfig(self.lava[-1].rect, fill="red")
                elif ch == 'G':
                    self.goals.append(GameObject(self.canvas, px, py, BLOCK_SIZE, BLOCK_SIZE, None, "goal"))
                    self.canvas.itemconfig(self.goals[-1].rect, fill="gold")
                elif ch == 'F':
                     # Draw Flagpole segments with NES colors
                     self.canvas.create_line(px+BLOCK_SIZE/2, py, px+BLOCK_SIZE/2, py+BLOCK_SIZE, width=4, fill="#00A800", tags=("scroll", "decor"))
                elif ch == 'G': # The top ball
                     self.canvas.create_oval(px+5, py+5, px+25, py+25, fill="#00A800", outline="black", tags=("scroll", "decor"))

        self.player = Player(self.canvas, 100, 100, self.sprites)
        
        # Draw the actual flag cloth manually because it spans blocks or sits on top
        # Find the flag pole top
        for y, row in enumerate(data["map"]):
            for x, ch in enumerate(row):
                if ch == 'G':
                    px, py = x * BLOCK_SIZE, y * BLOCK_SIZE
                    # Draw the flag triangle
                    self.canvas.create_polygon(px+BLOCK_SIZE/2, py, px+BLOCK_SIZE+15, py+15, px+BLOCK_SIZE/2, py+30, fill="#00A800", outline="black", tags=("scroll", "decor"))

        self.canvas.tag_raise("hud")

    def check_collision(self, mover, targets):
        mx1, my1, mx2, my2 = self.canvas.bbox(mover.rect)
        for t in targets:
            tx1, ty1, tx2, ty2 = self.canvas.bbox(t.rect)
            if mx1 < tx2 and mx2 > tx1 and my1 < ty2 and my2 > ty1:
                return t
        return None

    def loop(self):
        if self.game_over:
            if self.keys.get("space"):
                self.load_level()
            self.root.after(50, self.loop)
            return

        # --- PLAYER MOVEMENT & PHYSICS ---
        self.player.update(self.keys)

        # X Movement
        self.canvas.move(self.player.rect, self.player.vx, 0)
        wall_hit = self.check_collision(self.player, self.walls)
        if wall_hit:
            if self.player.vx > 0:
                tx1, _, _, _ = self.canvas.bbox(wall_hit.rect)
                px1, py1, px2, py2 = self.canvas.bbox(self.player.rect)
                self.canvas.move(self.player.rect, tx1 - px2, 0)
            elif self.player.vx < 0:
                _, _, tx2, _ = self.canvas.bbox(wall_hit.rect)
                px1, py1, px2, py2 = self.canvas.bbox(self.player.rect)
                self.canvas.move(self.player.rect, tx2 - px1, 0)
            self.player.vx = 0

        # CAMERA SCROLLING
        px1, py1, px2, py2 = self.canvas.bbox(self.player.rect)
        center_x = WINDOW_WIDTH / 2
        
        if px1 > center_x and self.player.vx > 0:
            shift = px1 - center_x
            self.canvas.move(self.player.rect, -shift, 0) 
            self.canvas.move("scroll", -shift, 0) 
            self.total_scroll += shift

        # Y Movement
        self.canvas.move(self.player.rect, 0, self.player.vy)
        self.player.on_ground = False
        wall_hit = self.check_collision(self.player, self.walls)
        if wall_hit:
            if self.player.vy > 0: 
                _, ty1, _, _ = self.canvas.bbox(wall_hit.rect)
                _, _, _, py2 = self.canvas.bbox(self.player.rect)
                self.canvas.move(self.player.rect, 0, ty1 - py2)
                self.player.on_ground = True
                self.player.vy = 0
            elif self.player.vy < 0: 
                _, _, _, ty2 = self.canvas.bbox(wall_hit.rect)
                _, py1, _, _ = self.canvas.bbox(self.player.rect)
                self.canvas.move(self.player.rect, 0, ty2 - py1)
                self.player.vy = 0

        # --- ENTITIES ---
        px1, py1, px2, py2 = self.canvas.bbox(self.player.rect)
        if py1 > WINDOW_HEIGHT:
            self.die()

        for e in list(self.enemies):
            ex1, ey1, ex2, ey2 = self.canvas.bbox(e.rect)
            if ex2 < 0 or ex1 > WINDOW_WIDTH: continue
            
            e.update()
            self.canvas.move(e.rect, e.vx, 0)
            
            ew = self.check_collision(e, self.walls)
            if ew:
                e.vx *= -1
                self.canvas.move(e.rect, e.vx, 0)
            
            self.canvas.move(e.rect, 0, e.vy)
            ew = self.check_collision(e, self.walls)
            if ew:
                _, ty1, _, _ = self.canvas.bbox(ew.rect)
                _, _, _, ey2 = self.canvas.bbox(e.rect)
                self.canvas.move(e.rect, 0, ty1 - ey2)
                e.vy = 0

            if self.check_collision(self.player, [e]):
                p_bottom = py2 - self.player.vy
                e_top = ey1
                
                if p_bottom <= e_top + 10 and self.player.vy > 0:
                    self.canvas.delete(e.rect)
                    self.enemies.remove(e)
                    self.player.vy = -8
                    self.player.score += 100
                    self.update_score()
                else:
                    self.die()

        # Check goal (Castle entrance / Flag hit)
        # For this simple version, collision with the flag pole 'F' lines is hard,
        # so we check the 'goal' blocks if we placed them, or just x position
        if self.total_scroll > (168 * BLOCK_SIZE) - (WINDOW_WIDTH/2):
             self.win_level()

        if self.check_collision(self.player, self.lava):
            self.die()

        self.root.after(int(1000/FPS), self.loop)

    def update_score(self):
        self.canvas.itemconfig(self.hud_score, text=f"SCORE: {self.player.score}")

    def die(self):
        if self.game_over: return
        self.game_over = True
        self.player.dead = True
        self.canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, text="GAME OVER", fill="white", font=("Press Start 2P", 30, "bold"), tags="game_over") # Fallback font
        self.canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 40, text="Press SPACE to Retry", fill="white", font=("Arial", 16), tags="game_over")

    def win_level(self):
        self.stage += 1
        if self.stage > 4:
            self.stage = 1
            self.world += 1
        self.load_level()

if __name__ == "__main__":
    root = tk.Tk()
    Game(root)
    root.mainloop()
