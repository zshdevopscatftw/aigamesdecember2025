#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS V0
NES-Accurate Edition • Pure Tkinter • FILES = OFF

© 1985 Nintendo
© Samsoft 2025
"""

import tkinter as tk
import math

# ============================================================
# ENGINE CONFIG
# ============================================================
FPS = 60
FRAME_MS = 16
NES_W, NES_H = 256, 240
SCALE = 3
WIDTH, HEIGHT = NES_W * SCALE, NES_H * SCALE

# ============================================================
# NES 2C02 PPU EXACT PALETTE
# ============================================================
PAL = {
    '_': None,
    # Mario (red hat, blue overalls)
    'R': '#D82800',  # Red - hat/shirt
    'B': '#0000A8',  # Blue - overalls  
    'S': '#FCA044',  # Skin tone
    'N': '#6B420C',  # Brown - hair/shoes
    'n': '#3B2400',  # Dark brown
    'K': '#000000',  # Black
    'W': '#FCFCFC',  # White
    'O': '#FC9838',  # Orange
    # Goomba - accurate browns
    'G': '#C84C0C',  # Goomba body (dark orange-brown)
    'g': '#FC9838',  # Goomba light (tan)
    'E': '#503000',  # Goomba feet (dark)
    # Koopa
    'T': '#00A800',  # Green shell
    't': '#58F858',  # Light green highlight
    # Pipe - proper greens
    'P': '#00A800',  # Pipe main green
    'p': '#58F858',  # Pipe highlight
    'd': '#003800',  # Pipe dark shadow
    # Blocks
    'Q': '#E4A000',  # Question gold
    'q': '#FCE4A0',  # Question highlight
    'C': '#C84C0C',  # Brick orange
    'c': '#FC9838',  # Brick highlight
    # Ground
    'F': '#FC9838',  # Ground top
    'f': '#C84C0C',  # Ground shadow
    # Coin
    'Y': '#FC9838',  # Coin gold
    'y': '#E4A000',  # Coin dark
    # Cloud/Bush
    'L': '#FCFCFC',  # Cloud white
    'l': '#9CDCFC',  # Cloud shadow
    'H': '#00A800',  # Bush/hill green
    'h': '#58F858',  # Bush highlight
}

SKY = '#5C94FC'

# ============================================================
# MARIO SPRITES - SMB1 NES ACCURATE
# ============================================================

# Small Mario Stand (16x16)
S_STAND = [
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSS____",
    "__RRBBBBRR__",
    "_RRRBBBBRRR_",
    "_RRRBBBBRRR_",
    "_SSBBBBBBSS_",
    "_SSBBBBBBSS_",
    "___BBBBBB___",
    "___BB__BB___",
    "__NNN__NNN__",
    "_NNNN__NNNN_",
]

# Small Mario Walk 1
S_WALK1 = [
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSS____",
    "__RRRBBBRR__",
    "_RRRRBBBRRR_",
    "_RRRBBBBRRR_",
    "_SSBBBBBBS__",
    "__SBBBBBB___",
    "___BBBBB____",
    "__NN__NNNN__",
    "_NNN____NN__",
    "____________",
]

# Small Mario Walk 2
S_WALK2 = [
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSSN___",
    "___RRBBBNN__",
    "__RRRBBBNN__",
    "__RRBBBB_N__",
    "_SSBBBBBBS__",
    "_SSBBBBBSS__",
    "___BBBBBB___",
    "___NN__NN___",
    "___NN__NN___",
    "____________",
]

# Small Mario Walk 3
S_WALK3 = [
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSS____",
    "__NRRBBBRR__",
    "_NNRRBBBRRR_",
    "NN_RBBBBRRR_",
    "_SSBBBBBBSS_",
    "__SSBBBBSS__",
    "___BBBBBB___",
    "_NNNN__NN___",
    "_NN___NNN___",
    "____________",
]

# Small Mario Jump
S_JUMP = [
    "___NNN______",
    "__NNNNN_RRR_",
    "__NNSSRRRR__",
    "_NSNSSSRRR__",
    "_NSNSSSKSSS_",
    "_NNNSSSKSS__",
    "___SSSSSS___",
    "__RRBBBRRR__",
    "_RRRBBBRRRR_",
    "RRRRBBBBRRSS",
    "SSBBBBBBBSS_",
    "_SSBBBBBSS__",
    "__SSBBBBSS__",
    "__NNN_______",
    "_NNNN_______",
    "NNNN________",
]

# Big Mario Stand (16x32)
B_STAND = [
    "____RRRR____",
    "___RRRRRR___",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NNSNSSSK__",
    "__NSNSSSKSS_",
    "__NNNSSSKKK_",
    "___SSSSSS___",
    "__RRRBBRRR__",
    "_RRRRBBRRRR_",
    "_RRRRBBRRRRR",
    "_SSRRBBBBRSS",
    "_SSSBBBBBRSS",
    "_SSBBBBBBSS_",
    "___BBBBBB___",
    "___BBBBBB___",
    "___BBRRRB___",
    "__RRRRRRRR__",
    "_RRRRRRRRRR_",
    "_RRRRRRRRRR_",
    "_SSRRRRRSS__",
    "_SSSRBBBRSS_",
    "__SSBBBBSS__",
    "___BBBBBB___",
    "___BB__BB___",
    "__NNN__NNN__",
    "_NNNN__NNNN_",
    "NNNNN__NNNNN",
]

# ============================================================
# GOOMBA - SMB1 NES ACCURATE (16x16)
# ============================================================

GOOMBA1 = [
    "______GG______",
    "_____GGGG_____",
    "____GGGGGG____",
    "___GGGGGGGG___",
    "__GgWWGGWWgG__",
    "__GgWKGGKWgG__",
    "__GGggGGggGG__",
    "___GGGGGGGG___",
    "____GGGGGG____",
    "_____gggg_____",
    "____EE__EE____",
    "___EE____EE___",
]

GOOMBA2 = [
    "______GG______",
    "_____GGGG_____",
    "____GGGGGG____",
    "___GGGGGGGG___",
    "__GgWWGGWWgG__",
    "__GgWKGGKWgG__",
    "__GGggGGggGG__",
    "___GGGGGGGG___",
    "____GGGGGG____",
    "_____gggg_____",
    "____EEEEEE____",
    "_____EEEE_____",
]

GOOMBA_FLAT = [
    "__GGGGGGGGGG__",
    "__GgWWGGWWgG__",
    "__GgWKGGKWgG__",
    "___GGGGGGGG___",
    "____EEEEEE____",
]

# ============================================================
# KOOPA - SMB1 NES ACCURATE (16x24)
# ============================================================

KOOPA = [
    "____TTTT____",
    "___TTTTTT___",
    "__TTWWWWTT__",
    "__TWKWWKWT__",
    "__TWWWWWWT__",
    "___TTTTTT___",
    "__tTTTTTTt__",
    "_tTTTTTTTTt_",
    "_TTTTTTTTTT_",
    "_TTTTttTTTT_",
    "_TTTttttTTT_",
    "_TTTtWWtTTT_",
    "_TTTtWWtTTT_",
    "_TTTttttTTT_",
    "__TTttttTT__",
    "___TTTTTT___",
    "____EEEE____",
    "___EE__EE___",
    "__EE____EE__",
]

KOOPA_SHELL = [
    "___TTTTTT___",
    "__TTTTTTTT__",
    "_TTTTttTTTT_",
    "_TTTttttTTT_",
    "TTTTtWWtTTTT",
    "TTTTtWWtTTTT",
    "_TTTttttTTT_",
    "__TTTTTTTT__",
    "___TTTTTT___",
]

# ============================================================
# PIPE - SMB1 NES ACCURATE (32x32 top, 32x16 body)
# ============================================================

PIPE_TOP = [
    "ddPPPPPPPPPPPPPPPPPPPPPPPPPPPPdd",
    "dPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPddddddddddddddddddddddddddPPd",
    "dPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPd",
    "dddddddddddddddddddddddddddddddd",
    "dddddddddddddddddddddddddddddddd",
]

PIPE_BODY = [
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
]

# ============================================================
# QUESTION BLOCK - SMB1 (16x16)
# ============================================================

Q_BLOCK = [
    "dddddddddddddddd",
    "dQQQQQQQQQQQQQQd",
    "dQqqqqqqqqqqqqQd",
    "dQqqddddqqqqqqQd",
    "dQqddqqddqqqqqQd",
    "dQqqqqqddqqqqqQd",
    "dQqqqqddqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqqqqqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqqqqqqqqqqQd",
    "dQQQQQQQQQQQQQQd",
    "dddddddddddddddd",
    "________________",
]

EMPTY_BLOCK = [
    "dddddddddddddddd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dddddddddddddddd",
    "________________",
]

# ============================================================
# BRICK - SMB1 (16x16)
# ============================================================

BRICK = [
    "dddddddddddddddd",
    "dCCCdCCCCCdCCCcd",
    "dCCCdCCCCCdCCCcd",
    "dccccdccccdccccd",
    "dddddddddddddddd",
    "dCCCCCdCCCdCCCcd",
    "dCCCCCdCCCdCCCcd",
    "dcccccdcccdccccd",
    "dddddddddddddddd",
    "dCCCdCCCCCdCCCcd",
    "dCCCdCCCCCdCCCcd",
    "dccccdccccdccccd",
    "dddddddddddddddd",
    "dCCCCCdCCCdCCCcd",
    "dcccccdcccdccccd",
    "dddddddddddddddd",
]

# ============================================================
# GROUND - SMB1 (16x16)
# ============================================================

GROUND = [
    "FFFFFFFFFFFFFFff",
    "FFFFFFFFFFFFFFff",
    "ffffffffffffffff",
    "dddddddddddddddd",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "ffffffffffffffff",
]

# ============================================================
# COIN - SMB1 (8x14)
# ============================================================

COIN1 = [
    "_YYYY_",
    "YyyyyY",
    "YyYYyY",
    "YyddyY",
    "YyddyY",
    "YyddyY",
    "YyddyY",
    "YyddyY",
    "YyddyY",
    "YyYYyY",
    "YyyyyY",
    "_YYYY_",
]

COIN2 = [
    "__YY__",
    "_YyyY_",
    "_YddY_",
    "_YddY_",
    "_YddY_",
    "_YddY_",
    "_YddY_",
    "_YddY_",
    "_YddY_",
    "_YddY_",
    "_YyyY_",
    "__YY__",
]

COIN3 = [
    "__Y___",
    "__Y___",
    "__d___",
    "__d___",
    "__d___",
    "__d___",
    "__d___",
    "__d___",
    "__d___",
    "__d___",
    "__Y___",
    "__Y___",
]

# ============================================================
# CLOUD - SMB1 (32x12)
# ============================================================

CLOUD = [
    "_______LL_______LL_______",
    "_____LLLLLL___LLLLLL_____",
    "___LLLLLLLLLLLLLLLLLLLL__",
    "__LLLLLLLLLLLLLLLLLLLLLL_",
    "_LLLLLLLLLLLLLLLLLLLLLLLL",
    "LLLLLLLLLLLLLLLLLLLLLLLLL",
    "LLLLLLLLLLLLLLLLLLLLLLLLl",
    "LLLLLLLLLLLLLLLLLLLLLLLll",
    "_LLLLLLLLLLLLLLLLLLLLLll_",
    "__lLLLLLLLLLLLLLLLLLll___",
    "____llLLLLLLLLLLllll_____",
]

# ============================================================
# BUSH - SMB1 (24x12)
# ============================================================

BUSH = [
    "________HH________",
    "______HHHHHH______",
    "____HHHHHHHHHH____",
    "__hHHHHHHHHHHHHh__",
    "_hHHHHHHHHHHHHHHh_",
    "hHHHHHHHHHHHHHHHHh",
    "HHHHHHHHHHHHHHHHHH",
    "HHHHHHHHHHHHHHHHHH",
]

# ============================================================
# FLAG - SMB1 (16x16 flag, pole separate)
# ============================================================

FLAG = [
    "RRRRRRRR",
    "RRRRRRRR",
    "RRRRRRRR",
    "RRRRRRRR",
    "RRRRRRRR",
    "RRRRRRRR",
    "RRRRRRRR",
    "RRRRRRRR",
    "RRRRR___",
    "RRRR____",
    "RRR_____",
    "RR______",
    "R_______",
]

FLAGPOLE_BALL = [
    "__PP__",
    "_PPPP_",
    "PPPPPP",
    "PPPPPP",
    "_PPPP_",
    "__PP__",
]

# ============================================================
# CASTLE - SMB1 (32x24)
# ============================================================

CASTLE = [
    "___NN__________NN___",
    "___NN__________NN___",
    "___NN__________NN___",
    "NNNNNNNN____NNNNNNNN",
    "NNNNNNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNNNNNN",
    "NNddNNNNNNNNNNddNNNN",
    "NNddNNNNNNNNNNddNNNN",
    "NNddNNNNddddNNddNNNN",
    "NNddNNNNddddNNddNNNN",
    "NNNNNNNNddddNNNNNNNN",
    "NNNNNNNNddddNNNNNNNN",
]

# ============================================================
# MUSHROOM POWERUP (16x16)
# ============================================================

MUSHROOM = [
    "____RRRRRR____",
    "__RRRRRRRRRR__",
    "_RRRWWWWWWRRR_",
    "_RRWWWWWWWWRR_",
    "RRRWWWWWWWWRRR",
    "RRWWWWWWWWWWRR",
    "RRWWWWWWWWWWRR",
    "_RRWWWWWWWWRR_",
    "_RRRWWWWWWRRR_",
    "__RRRRRRRRRR__",
    "___SSSSSSSS___",
    "___SSSSSSSS___",
    "____SSSSSS____",
]

# ============================================================
# RENDERER
# ============================================================
class Renderer:
    def __init__(self, canvas, scale):
        self.canvas = canvas
        self.scale = scale
    
    def draw(self, x, y, sprite, flip=False):
        s = self.scale
        for ri, row in enumerate(sprite):
            for ci, ch in enumerate(row):
                if ch == '_' or ch not in PAL or PAL[ch] is None:
                    continue
                col = PAL[ch]
                px = x + (len(row) - 1 - ci if flip else ci) * s
                py = y + ri * s
                self.canvas.create_rectangle(
                    px, py, px + s, py + s,
                    fill=col, outline=col, width=0
                )
    
    def rect(self, x, y, w, h, color):
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=color, outline=color, width=0
        )
    
    def text(self, x, y, txt, color='#FCFCFC', size=8, anchor='nw'):
        self.canvas.create_text(
            x, y, text=txt, fill=color,
            font=('Courier', size, 'bold'), anchor=anchor
        )

# ============================================================
# LEVEL GENERATOR
# ============================================================
def make_level(world, stage):
    lvl = {
        'width': 3584,
        'ground': [],
        'bricks': [],
        'questions': [],
        'pipes': [],
        'enemies': [],
        'coins': [],
        'flag_x': 3200,
        'castle_x': 3280,
    }
    
    # Ground with gaps
    gaps = []
    if world >= 2: gaps.append((800, 48))
    if world >= 4: gaps.append((1600, 64))
    if world >= 6: gaps.append((2400, 80))
    
    for x in range(0, lvl['width'], 16):
        in_gap = any(gx <= x < gx + gw for gx, gw in gaps)
        if not in_gap:
            lvl['ground'].append({'x': x, 'y': 208})
    
    # Platforms
    plats = [(320, 144, 4), (640, 128, 3), (960, 144, 5), (1280, 112, 3),
             (1600, 144, 4), (1920, 128, 3), (2240, 144, 4), (2560, 128, 3)]
    for px, py, cnt in plats[:3 + world]:
        for i in range(cnt):
            lvl['bricks'].append({'x': px + i*16, 'y': py, 'hit': False})
    
    # Question blocks
    qb = [(256, 144, 'coin'), (352, 144, 'mush'), (512, 128, 'coin'),
          (736, 144, 'coin'), (864, 96, 'mush'), (1024, 144, 'coin'),
          (1200, 128, 'coin'), (1440, 144, 'mush'), (1680, 128, 'coin')]
    for qx, qy, item in qb[:4 + world]:
        lvl['questions'].append({'x': qx, 'y': qy, 'item': item, 'hit': False})
    
    # Pipes - proper heights
    pipes = [(448, 32), (608, 48), (912, 48), (1168, 64),
             (1488, 48), (1808, 32), (2128, 48), (2448, 64)]
    for px, ph in pipes[:2 + world]:
        lvl['pipes'].append({'x': px, 'y': 208 - ph, 'h': ph})
    
    # Enemies
    enemies = [(352, 'goomba'), (544, 'goomba'), (720, 'goomba'), (880, 'goomba'),
               (1056, 'goomba'), (1232, 'koopa'), (1408, 'goomba'), (1584, 'goomba'),
               (1760, 'koopa'), (1936, 'goomba'), (2112, 'goomba'), (2288, 'goomba')]
    for ex, et in enemies[:3 + world * 2]:
        lvl['enemies'].append({
            'x': float(ex), 'y': 192.0, 'type': et,
            'vx': -0.5, 'alive': True, 'stomped': False, 'timer': 0, 'frame': 0
        })
    
    # Coins
    coins = [(288, 112, 3), (528, 80, 5), (1120, 96, 4),
             (1552, 96, 5), (1840, 112, 3), (2320, 96, 4)]
    for cx, cy, cnt in coins[:3 + world]:
        for i in range(cnt):
            lvl['coins'].append({'x': cx + i*16, 'y': cy, 'got': False})
    
    return lvl

# ============================================================
# PHYSICS
# ============================================================
class Phys:
    GRAVITY = 0.4
    JUMP = -7.0
    MAX_FALL = 7.0
    WALK = 0.12
    RUN = 0.18
    FRICTION = 0.9
    MAX_WALK = 2.0
    MAX_RUN = 3.5

# ============================================================
# GAME
# ============================================================
class Game:
    def __init__(self, root):
        self.root = root
        root.title("ULTRA MARIO 2D BROS V0")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)
        root.configure(bg='black')
        
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT,
                                 bg=SKY, highlightthickness=0)
        self.canvas.pack()
        
        self.r = Renderer(self.canvas, SCALE)
        
        self.keys = set()
        root.bind('<KeyPress>', lambda e: self.keys.add(e.keysym.lower()))
        root.bind('<KeyRelease>', lambda e: self.keys.discard(e.keysym.lower()))
        
        self.state = 'menu'
        self.menu_sel = 0
        self.frame = 0
        
        self.player = None
        self.camera = 0
        self.world = 1
        self.stage = 1
        self.level = None
        
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.time = 400
        self.big = False
        
        self.particles = []
        
        self.loop()
    
    def loop(self):
        self.canvas.delete('all')
        
        if self.state == 'menu':
            self.update_menu()
            self.draw_menu()
        elif self.state == 'play':
            self.update_game()
            self.draw_game()
        elif self.state == 'dead':
            self.update_dead()
            self.draw_game()
        elif self.state == 'over':
            self.draw_over()
            self.update_over()
        elif self.state == 'clear':
            self.draw_clear()
            self.update_clear()
        
        self.frame += 1
        self.root.after(FRAME_MS, self.loop)
    
    # ========== MENU ==========
    def update_menu(self):
        if 'up' in self.keys:
            self.menu_sel = (self.menu_sel - 1) % 2
            self.keys.discard('up')
        if 'down' in self.keys:
            self.menu_sel = (self.menu_sel + 1) % 2
            self.keys.discard('down')
        if self.keys & {'return', 'z', 'space'}:
            self.keys -= {'return', 'z', 'space'}
            if self.menu_sel == 0:
                self.start()
            else:
                self.root.destroy()
    
    def draw_menu(self):
        self.r.rect(0, 0, WIDTH, HEIGHT, SKY)
        
        # Ground
        for x in range(0, WIDTH, 16 * SCALE):
            self.r.draw(x, 208 * SCALE, GROUND)
        
        # Clouds
        for i in range(4):
            cx = ((i * 200 + self.frame) % (WIDTH + 200)) - 100
            self.r.draw(int(cx), (35 + i * 12) * SCALE, CLOUD)
        
        # Bushes
        for i in range(3):
            self.r.draw((40 + i * 100) * SCALE, 196 * SCALE, BUSH)
        
        # Pipe on menu
        self.r.draw(50 * SCALE, 176 * SCALE, PIPE_TOP)
        
        # Goomba walking
        goomba_x = (self.frame * 0.5) % 200 + 100
        gf = GOOMBA1 if (self.frame // 12) % 2 == 0 else GOOMBA2
        self.r.draw(int(goomba_x) * SCALE, 196 * SCALE, gf)
        
        # Title box
        self.r.rect(WIDTH//2 - 180, 30 * SCALE, 360, 65 * SCALE, '#000000')
        self.r.rect(WIDTH//2 - 177, 30 * SCALE + 3, 354, 65 * SCALE - 6, '#200000')
        
        # Title
        self.r.text(WIDTH//2, 42 * SCALE, "ULTRA MARIO 2D BROS V0",
                    '#FCE4A0', 11 * SCALE // 2, 'n')
        self.r.text(WIDTH//2, 62 * SCALE, "© 1985 Nintendo",
                    '#FCFCFC', 6 * SCALE // 2, 'n')
        self.r.text(WIDTH//2, 74 * SCALE, "© Samsoft 2025",
                    '#FCFCFC', 6 * SCALE // 2, 'n')
        
        # Mario walking on menu
        mario_x = WIDTH//2 - 20
        walk_frame = (self.frame // 8) % 4
        sprites = [S_STAND, S_WALK1, S_WALK2, S_WALK3]
        self.r.draw(mario_x, 110 * SCALE, sprites[walk_frame])
        
        # Menu box
        self.r.rect(WIDTH//2 - 100, 140 * SCALE, 200, 45 * SCALE, '#000000')
        self.r.rect(WIDTH//2 - 97, 140 * SCALE + 3, 194, 45 * SCALE - 6, '#200000')
        
        # Options
        opts = ["1 PLAYER GAME", "EXIT"]
        for i, t in enumerate(opts):
            y = 150 * SCALE + i * 16 * SCALE
            color = '#FCE4A0' if i == self.menu_sel else '#FCFCFC'
            if i == self.menu_sel:
                cursor_x = WIDTH//2 - 85 + int(math.sin(self.frame * 0.2) * 3)
                self.r.text(cursor_x, y, "►", '#FC0000', 8 * SCALE // 2, 'nw')
            self.r.text(WIDTH//2 - 55, y, t, color, 6 * SCALE // 2, 'nw')
        
        # Bottom
        self.r.text(WIDTH//2, 200 * SCALE, "WORLDS 1-1 TO 8-4",
                    '#FCFCFC', 5 * SCALE // 2, 'n')
    
    # ========== GAME ==========
    def start(self):
        self.state = 'play'
        self.world = 1
        self.stage = 1
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.big = False
        self.load()
    
    def load(self):
        self.level = make_level(self.world, self.stage)
        self.camera = 0
        self.time = 400
        self.particles = []
        
        self.player = {
            'x': 48.0, 'y': 192.0,
            'vx': 0.0, 'vy': 0.0,
            'dir': 1, 'ground': True,
            'walk': 0, 'inv': 0
        }
    
    def update_game(self):
        if self.frame % 24 == 0 and self.time > 0:
            self.time -= 1
            if self.time <= 0:
                self.die()
                return
        
        self.update_player()
        self.update_enemies()
        self.update_particles()
        self.check_collisions()
        
        target = self.player['x'] - NES_W // 2 + 32
        self.camera = max(0, min(target, self.level['width'] - NES_W))
        
        if self.player['x'] >= self.level['flag_x']:
            self.complete()
    
    def update_player(self):
        p = self.player
        
        moving = False
        run = 'x' in self.keys or 'shift_l' in self.keys
        
        if 'left' in self.keys or 'a' in self.keys:
            p['vx'] -= Phys.RUN if run else Phys.WALK
            p['dir'] = -1
            moving = True
        if 'right' in self.keys or 'd' in self.keys:
            p['vx'] += Phys.RUN if run else Phys.WALK
            p['dir'] = 1
            moving = True
        
        if not moving:
            p['vx'] *= Phys.FRICTION
            if abs(p['vx']) < 0.05:
                p['vx'] = 0
        
        cap = Phys.MAX_RUN if run else Phys.MAX_WALK
        p['vx'] = max(-cap, min(cap, p['vx']))
        
        jkeys = {'z', 'space', 'w', 'up'}
        if jkeys & self.keys and p['ground']:
            p['vy'] = Phys.JUMP
            p['ground'] = False
        
        if p['vy'] < 0 and not (jkeys & self.keys):
            p['vy'] = max(p['vy'], -2)
        
        p['vy'] += Phys.GRAVITY
        p['vy'] = min(p['vy'], Phys.MAX_FALL)
        
        p['x'] += p['vx']
        p['y'] += p['vy']
        
        if p['x'] < self.camera:
            p['x'] = self.camera
        if p['x'] < 0:
            p['x'] = 0
        
        p['ground'] = False
        ph = 28 if self.big else 16
        
        for g in self.level['ground']:
            if self.collide(p['x'], p['y'], 12, ph, g['x'], g['y'], 16, 32):
                if p['vy'] > 0:
                    p['y'] = g['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
        
        for pipe in self.level['pipes']:
            if self.collide(p['x'], p['y'], 12, ph, pipe['x'] + 4, pipe['y'], 24, pipe['h']):
                if p['vy'] > 0 and p['y'] + ph > pipe['y'] and p['y'] < pipe['y']:
                    p['y'] = pipe['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
                elif p['vx'] > 0:
                    p['x'] = pipe['x'] + 4 - 12
                elif p['vx'] < 0:
                    p['x'] = pipe['x'] + 28
        
        for brick in self.level['bricks']:
            if brick['hit']:
                continue
            if self.collide(p['x'], p['y'], 12, ph, brick['x'], brick['y'], 16, 16):
                if p['vy'] < 0:
                    p['y'] = brick['y'] + 16
                    p['vy'] = 0
                    if self.big:
                        brick['hit'] = True
                        self.score += 50
                        self.particles.append({
                            'x': brick['x'], 'y': brick['y'],
                            't': 'brk', 'life': 20, 'vy': -3
                        })
                elif p['vy'] > 0:
                    p['y'] = brick['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
        
        for q in self.level['questions']:
            if q['hit']:
                continue
            if self.collide(p['x'], p['y'], 12, ph, q['x'], q['y'], 16, 16):
                if p['vy'] < 0:
                    p['y'] = q['y'] + 16
                    p['vy'] = 0
                    q['hit'] = True
                    if q['item'] == 'coin':
                        self.coins += 1
                        self.score += 200
                        self.particles.append({
                            'x': q['x'], 'y': q['y'] - 16,
                            't': 'coin', 'life': 30, 'vy': -4
                        })
                    else:
                        if not self.big:
                            self.big = True
                        self.score += 1000
                elif p['vy'] > 0:
                    p['y'] = q['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
        
        if p['y'] > NES_H:
            self.die()
            return
        
        if moving and p['ground']:
            if self.frame % 6 == 0:
                p['walk'] = (p['walk'] + 1) % 4
        elif not moving:
            p['walk'] = 0
        
        if p['inv'] > 0:
            p['inv'] -= 1
    
    def update_enemies(self):
        for e in self.level['enemies']:
            if not e['alive']:
                continue
            if e['stomped']:
                e['timer'] += 1
                if e['timer'] > 30:
                    e['alive'] = False
                continue
            
            e['x'] += e['vx']
            e['frame'] = (self.frame // 12) % 2
            
            if e['x'] < 0:
                e['vx'] = abs(e['vx'])
            if e['x'] > self.level['width'] - 16:
                e['vx'] = -abs(e['vx'])
            
            for pipe in self.level['pipes']:
                if e['x'] + 14 > pipe['x'] + 4 and e['x'] < pipe['x'] + 28:
                    if e['y'] + 16 > pipe['y']:
                        e['vx'] *= -1
                        e['x'] += e['vx'] * 2
    
    def update_particles(self):
        for pt in self.particles[:]:
            pt['y'] += pt.get('vy', -2)
            pt['life'] -= 1
            if pt['life'] <= 0:
                self.particles.remove(pt)
    
    def check_collisions(self):
        p = self.player
        ph = 28 if self.big else 16
        
        for c in self.level['coins']:
            if c['got']:
                continue
            if self.collide(p['x'], p['y'], 12, ph, c['x'], c['y'], 6, 12):
                c['got'] = True
                self.coins += 1
                self.score += 200
        
        for e in self.level['enemies']:
            if not e['alive'] or e['stomped']:
                continue
            ew = 14
            eh = 12 if e['type'] == 'goomba' else 18
            if self.collide(p['x'], p['y'], 12, ph, e['x'], e['y'], ew, eh):
                if p['vy'] > 0 and p['y'] + ph - 6 < e['y']:
                    e['stomped'] = True
                    e['vx'] = 0
                    p['vy'] = -4
                    self.score += 100
                elif p['inv'] <= 0:
                    if self.big:
                        self.big = False
                        p['inv'] = 90
                    else:
                        self.die()
    
    def collide(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
    
    def die(self):
        self.state = 'dead'
        self.player['vy'] = -6
        self.player['vx'] = 0
        self.death_timer = 0
    
    def complete(self):
        self.state = 'clear'
        self.score += self.time * 50
    
    def update_dead(self):
        self.player['vy'] += Phys.GRAVITY
        self.player['y'] += self.player['vy']
        self.death_timer += 1
        
        if self.death_timer > 120:
            self.lives -= 1
            if self.lives <= 0:
                self.state = 'over'
            else:
                self.load()
                self.state = 'play'
    
    # ========== DRAWING ==========
    def draw_game(self):
        cx = self.camera
        
        self.r.rect(0, 0, WIDTH, HEIGHT, SKY)
        
        # Clouds
        for i in range(12):
            cloud_x = (i * 300 - cx * 0.3) % (NES_W * 3) - 150
            if -50 < cloud_x < NES_W + 50:
                self.r.draw(int(cloud_x * SCALE), (32 + (i % 3) * 20) * SCALE, CLOUD)
        
        # Bushes
        for i in range(20):
            bush_x = i * 180 - cx
            if -30 < bush_x < NES_W + 30:
                self.r.draw(int(bush_x * SCALE), 196 * SCALE, BUSH)
        
        # Ground
        for g in self.level['ground']:
            sx = g['x'] - cx
            if -16 < sx < NES_W + 16:
                self.r.draw(int(sx * SCALE), g['y'] * SCALE, GROUND)
                self.r.draw(int(sx * SCALE), (g['y'] + 16) * SCALE, GROUND)
        
        # Pipes
        for pipe in self.level['pipes']:
            sx = pipe['x'] - cx
            if -32 < sx < NES_W + 32:
                self.r.draw(int(sx * SCALE), pipe['y'] * SCALE, PIPE_TOP)
                # Draw pipe body segments
                for by in range(16, pipe['h'], 16):
                    self.r.draw(int(sx * SCALE), (pipe['y'] + by) * SCALE, PIPE_BODY)
        
        # Bricks
        for brick in self.level['bricks']:
            if brick['hit']:
                continue
            sx = brick['x'] - cx
            if -16 < sx < NES_W + 16:
                self.r.draw(int(sx * SCALE), brick['y'] * SCALE, BRICK)
        
        # Question blocks
        for q in self.level['questions']:
            sx = q['x'] - cx
            if -16 < sx < NES_W + 16:
                sprite = EMPTY_BLOCK if q['hit'] else Q_BLOCK
                self.r.draw(int(sx * SCALE), q['y'] * SCALE, sprite)
        
        # Coins
        coin_frames = [COIN1, COIN2, COIN3, COIN2]
        cf = coin_frames[(self.frame // 8) % 4]
        for c in self.level['coins']:
            if c['got']:
                continue
            sx = c['x'] - cx
            if -16 < sx < NES_W + 16:
                self.r.draw(int((sx + 4) * SCALE), c['y'] * SCALE, cf)
        
        # Enemies
        for e in self.level['enemies']:
            if not e['alive']:
                continue
            sx = e['x'] - cx
            if -16 < sx < NES_W + 16:
                if e['type'] == 'goomba':
                    if e['stomped']:
                        self.r.draw(int(sx * SCALE), (e['y'] + 6) * SCALE, GOOMBA_FLAT)
                    else:
                        gf = GOOMBA1 if e['frame'] == 0 else GOOMBA2
                        self.r.draw(int(sx * SCALE), (e['y'] + 4) * SCALE, gf)
                else:
                    if e['stomped']:
                        self.r.draw(int(sx * SCALE), (e['y'] + 4) * SCALE, KOOPA_SHELL)
                    else:
                        self.r.draw(int(sx * SCALE), (e['y'] - 4) * SCALE, KOOPA)
        
        # Flagpole
        flag_sx = self.level['flag_x'] - cx
        if -16 < flag_sx < NES_W + 16:
            # Pole
            for y in range(64, 208, 8):
                self.r.rect(
                    int((flag_sx + 14) * SCALE), y * SCALE,
                    4 * SCALE, 8 * SCALE, '#00A800'
                )
            # Ball
            self.r.draw(int((flag_sx + 11) * SCALE), 58 * SCALE, FLAGPOLE_BALL)
            # Flag
            self.r.draw(int((flag_sx + 18) * SCALE), 70 * SCALE, FLAG)
        
        # Castle
        castle_sx = self.level['castle_x'] - cx
        if -64 < castle_sx < NES_W + 64:
            self.r.draw(int(castle_sx * SCALE), 172 * SCALE, CASTLE)
        
        # Particles
        for pt in self.particles:
            sx = pt['x'] - cx
            if pt['t'] == 'coin':
                self.r.draw(int(sx * SCALE), int(pt['y'] * SCALE), COIN1)
            elif pt['t'] == 'brk':
                self.r.rect(
                    int(sx * SCALE), int(pt['y'] * SCALE),
                    8 * SCALE, 8 * SCALE, '#C84C0C'
                )
        
        self.draw_player()
        self.draw_hud()
    
    def draw_player(self):
        p = self.player
        sx = (p['x'] - self.camera) * SCALE
        
        if p['inv'] > 0 and (self.frame // 4) % 2 == 0:
            return
        
        if not p['ground']:
            sprite = S_JUMP
        elif abs(p['vx']) > 0.1:
            walk_sprites = [S_WALK1, S_WALK2, S_WALK3, S_WALK2]
            sprite = walk_sprites[p['walk'] % 4]
        else:
            sprite = S_STAND
        
        if self.big:
            sprite = B_STAND
            self.r.draw(int(sx), int((p['y'] - 12) * SCALE), sprite, flip=(p['dir'] < 0))
        else:
            self.r.draw(int(sx), int(p['y'] * SCALE), sprite, flip=(p['dir'] < 0))
    
    def draw_hud(self):
        self.r.rect(0, 0, WIDTH, 26 * SCALE, '#000000')
        
        self.r.text(8 * SCALE, 4 * SCALE, "MARIO", '#FCFCFC', 5 * SCALE // 2)
        self.r.text(8 * SCALE, 13 * SCALE, f"{self.score:06d}", '#FCFCFC', 5 * SCALE // 2)
        
        self.r.draw(75 * SCALE, 11 * SCALE, COIN1)
        self.r.text(85 * SCALE, 13 * SCALE, f"×{self.coins:02d}", '#FCFCFC', 5 * SCALE // 2)
        
        self.r.text(130 * SCALE, 4 * SCALE, "WORLD", '#FCFCFC', 5 * SCALE // 2)
        self.r.text(134 * SCALE, 13 * SCALE, f"{self.world}-{self.stage}", '#FCFCFC', 5 * SCALE // 2)
        
        self.r.text(190 * SCALE, 4 * SCALE, "TIME", '#FCFCFC', 5 * SCALE // 2)
        time_col = '#FCFCFC' if self.time > 100 else '#FC0000'
        self.r.text(193 * SCALE, 13 * SCALE, f"{self.time:03d}", time_col, 5 * SCALE // 2)
        
        self.r.text(235 * SCALE, 13 * SCALE, f"×{self.lives}", '#FCFCFC', 5 * SCALE // 2)
    
    def draw_over(self):
        self.r.rect(0, 0, WIDTH, HEIGHT, '#000000')
        self.r.text(WIDTH // 2, HEIGHT // 2 - 20 * SCALE, "GAME OVER",
                    '#FCFCFC', 10 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2 + 20 * SCALE, "PRESS ENTER",
                    '#FCE4A0', 6 * SCALE // 2, 'center')
    
    def update_over(self):
        if self.keys & {'return', 'z', 'space'}:
            self.keys -= {'return', 'z', 'space'}
            self.state = 'menu'
    
    def draw_clear(self):
        self.r.rect(0, 0, WIDTH, HEIGHT, '#000000')
        self.r.text(WIDTH // 2, HEIGHT // 2 - 30 * SCALE,
                    f"WORLD {self.world}-{self.stage}", '#FCA044', 8 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2,
                    "COURSE CLEAR!", '#FCFCFC', 10 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2 + 30 * SCALE,
                    f"SCORE: {self.score}", '#FCFCFC', 6 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2 + 50 * SCALE,
                    "PRESS ENTER", '#FCE4A0', 5 * SCALE // 2, 'center')
    
    def update_clear(self):
        if self.keys & {'return', 'z', 'space'}:
            self.keys -= {'return', 'z', 'space'}
            self.stage += 1
            if self.stage > 4:
                self.stage = 1
                self.world += 1
            if self.world > 8:
                self.state = 'menu'
            else:
                self.load()
                self.state = 'play'

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  ULTRA MARIO 2D BROS V0")
    print("  © 1985 Nintendo")
    print("  © Samsoft 2025")
    print("=" * 55)
    print("\n  Controls:")
    print("    ← →  / A D   : Move")
    print("    Z / Space / W : Jump")
    print("    X / Shift     : Run")
    print("=" * 55)
    
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
