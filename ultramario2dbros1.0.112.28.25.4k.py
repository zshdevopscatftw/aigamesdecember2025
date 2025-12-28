#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS - Optimized NES Clone (2025 Flames Co.)
60 FPS locked, NES-accurate sprites, flag win condition
"""

import pygame, sys, math, array

pygame.init()
pygame.mixer.init(44100, -16, 2, 512)

NES_W, NES_H = 256, 240
SCALE = 3
W, H = NES_W * SCALE, NES_H * SCALE
FPS = 60
TILE = 16

# NES physics
GRAV = 0.4
MAX_FALL = 4.5
M_ACCEL = 0.09375
M_DECEL = 0.0625
M_MAXW = 1.5
M_MAXR = 2.5
M_JUMP = -4.0
M_JUMP_HOLD = 0.2

# NES palette
PAL = {
    'sky': (92, 148, 252),
    'grd1': (0, 0, 0),
    'grd2': (200, 76, 12),
    'grd3': (228, 148, 88),
    'brk1': (200, 76, 12),
    'brk2': (228, 92, 16),
    'brk3': (252, 152, 56),
    'pip1': (0, 168, 0),
    'pip2': (0, 228, 0),
    'pip3': (0, 100, 0),
    'red': (228, 0, 88),
    'skn': (252, 188, 116),
    'brn': (136, 20, 0),
    'yel': (252, 188, 60),
    'blk': (0, 0, 0),
    'wht': (252, 252, 252),
    'org': (228, 92, 16),
    'grn': (0, 184, 0),
}

_sprite_cache = {}

def get_sprite(name, frame=0):
    key = (name, frame % 60)
    if key not in _sprite_cache:
        _sprite_cache[key] = _create_sprite(name, frame)
    return _sprite_cache[key]

def _create_sprite(name, frame):
    if name == 'mario_s':
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        px = [(5,0),(6,0),(7,0),(8,0),(9,0),
              (4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1)]
        for x,y in px: s.set_at((x,y), PAL['red'])
        hd = [(4,2),(5,2),(6,2),(7,2),(11,2),
              (3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(11,3),
              (3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4)]
        for x,y in hd: s.set_at((x,y), PAL['brn'])
        fc = [(8,2),(9,2),(10,2),(9,3),(10,3),(12,3),(12,4)]
        for x,y in fc: s.set_at((x,y), PAL['skn'])
        sk = [(3,5),(4,5),(8,5),(9,5),(10,5),(11,5),
              (3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),
              (4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7)]
        for x,y in sk: s.set_at((x,y), PAL['skn'])
        s.set_at((10,4), PAL['blk'])
        sh = [(5,8),(6,8),(7,8),(8,8),(9,8),(10,8),
              (4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),
              (4,10),(5,10),(10,10),(11,10)]
        for x,y in sh: s.set_at((x,y), PAL['red'])
        ov = [(6,10),(7,10),(8,10),(9,10),
              (5,11),(6,11),(7,11),(8,11),(9,11),(10,11),
              (4,12),(5,12),(6,12),(9,12),(10,12),(11,12),
              (4,13),(5,13),(6,13),(9,13),(10,13),(11,13)]
        for x,y in ov: s.set_at((x,y), PAL['brn'])
        shoes = [(3,14),(4,14),(5,14),(6,14),(9,14),(10,14),(11,14),(12,14),
                 (2,15),(3,15),(4,15),(5,15),(6,15),(9,15),(10,15),(11,15),(12,15),(13,15)]
        for x,y in shoes: s.set_at((x,y), PAL['brn'])
        return s

    elif name == 'mario_b':
        s = pygame.Surface((16, 32), pygame.SRCALPHA)
        hat = [(5,0),(6,0),(7,0),(8,0),(9,0),
               (4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),(11,1),
               (3,2),(4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),(12,2)]
        for x,y in hat: s.set_at((x,y), PAL['red'])
        hr = [(4,3),(5,3),(6,3),(7,3),(11,3),
              (3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(11,4),(12,4),
              (3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5)]
        for x,y in hr: s.set_at((x,y), PAL['brn'])
        fc = [(8,3),(9,3),(10,3),(12,3),(9,4),(10,4),(13,4),(12,5),(13,5)]
        for x,y in fc: s.set_at((x,y), PAL['skn'])
        s.set_at((10,5), PAL['blk'])
        lf = [(3,6),(4,6),(5,6),(9,6),(10,6),(11,6),(12,6),
              (4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),
              (5,8),(6,8),(7,8),(8,8),(9,8),(10,8),(11,8)]
        for x,y in lf: s.set_at((x,y), PAL['skn'])
        ms = [(6,6),(7,6),(8,6)]
        for x,y in ms: s.set_at((x,y), PAL['brn'])
        st = [(4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),
              (3,10),(4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(10,10),(11,10),(12,10),
              (2,11),(3,11),(4,11),(11,11),(12,11),(13,11),
              (2,12),(3,12),(12,12),(13,12)]
        for x,y in st: s.set_at((x,y), PAL['red'])
        ov = [(5,11),(6,11),(7,11),(8,11),(9,11),(10,11),
              (4,12),(5,12),(6,12),(7,12),(8,12),(9,12),(10,12),(11,12),
              (4,13),(5,13),(6,13),(7,13),(8,13),(9,13),(10,13),(11,13),
              (3,14),(4,14),(5,14),(6,14),(7,14),(8,14),(9,14),(10,14),(11,14),(12,14),
              (3,15),(4,15),(5,15),(6,15),(7,15),(8,15),(9,15),(10,15),(11,15),(12,15),
              (3,16),(4,16),(5,16),(6,16),(7,16),(8,16),(9,16),(10,16),(11,16),(12,16),
              (3,17),(4,17),(5,17),(6,17),(9,17),(10,17),(11,17),(12,17)]
        for x,y in ov: s.set_at((x,y), PAL['brn'])
        s.set_at((6,13), PAL['yel']); s.set_at((9,13), PAL['yel'])
        hnd = [(1,12),(1,13),(14,12),(14,13)]
        for x,y in hnd: s.set_at((x,y), PAL['skn'])
        lg = [(2,18),(3,18),(4,18),(5,18),(10,18),(11,18),(12,18),(13,18),
              (2,19),(3,19),(4,19),(5,19),(10,19),(11,19),(12,19),(13,19),
              (1,20),(2,20),(3,20),(4,20),(5,20),(10,20),(11,20),(12,20),(13,20),(14,20),
              (1,21),(2,21),(3,21),(4,21),(5,21),(6,21),(9,21),(10,21),(11,21),(12,21),(13,21),(14,21)]
        for x,y in lg: s.set_at((x,y), PAL['brn'])
        return s

    elif name == 'goomba':
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        bd = [(6,1),(7,1),(8,1),(9,1),
              (4,2),(5,2),(6,2),(7,2),(8,2),(9,2),(10,2),(11,2),
              (3,3),(4,3),(5,3),(6,3),(7,3),(8,3),(9,3),(10,3),(11,3),(12,3),
              (2,4),(3,4),(4,4),(5,4),(6,4),(7,4),(8,4),(9,4),(10,4),(11,4),(12,4),(13,4),
              (2,5),(3,5),(4,5),(5,5),(6,5),(7,5),(8,5),(9,5),(10,5),(11,5),(12,5),(13,5),
              (2,6),(3,6),(4,6),(5,6),(6,6),(7,6),(8,6),(9,6),(10,6),(11,6),(12,6),(13,6),
              (2,7),(3,7),(4,7),(5,7),(6,7),(7,7),(8,7),(9,7),(10,7),(11,7),(12,7),(13,7),
              (2,8),(3,8),(4,8),(5,8),(6,8),(7,8),(8,8),(9,8),(10,8),(11,8),(12,8),(13,8),
              (3,9),(4,9),(5,9),(6,9),(7,9),(8,9),(9,9),(10,9),(11,9),(12,9),
              (4,10),(5,10),(6,10),(7,10),(8,10),(9,10),(10,10),(11,10)]
        for x,y in bd: s.set_at((x,y), PAL['brn'])
        ew = [(4,4),(5,4),(6,4),(9,4),(10,4),(11,4),
              (4,5),(5,5),(6,5),(9,5),(10,5),(11,5),
              (5,6),(6,6),(9,6),(10,6)]
        for x,y in ew: s.set_at((x,y), PAL['wht'])
        s.set_at((5,5), PAL['blk']); s.set_at((6,5), PAL['blk'])
        s.set_at((9,5), PAL['blk']); s.set_at((10,5), PAL['blk'])
        ft = [(1,11),(2,11),(3,11),(4,11),(5,11),(10,11),(11,11),(12,11),(13,11),(14,11),
              (0,12),(1,12),(2,12),(3,12),(4,12),(5,12),(10,12),(11,12),(12,12),(13,12),(14,12),(15,12),
              (0,13),(1,13),(2,13),(3,13),(4,13),(11,13),(12,13),(13,13),(14,13),(15,13)]
        for x,y in ft: s.set_at((x,y), PAL['blk'])
        return s

    elif name == 'goomba_flat':
        s = pygame.Surface((16, 8), pygame.SRCALPHA)
        for x in range(2, 14):
            for y in range(4, 7): s.set_at((x, y), PAL['brn'])
        return s

    elif name == 'ground':
        s = pygame.Surface((16, 16))
        s.fill(PAL['grd2'])
        pygame.draw.line(s, PAL['blk'], (0, 0), (16, 0))
        pygame.draw.line(s, PAL['grd3'], (0, 1), (16, 1))
        for x in [0, 8]: pygame.draw.line(s, PAL['blk'], (x, 0), (x, 8))
        pygame.draw.line(s, PAL['blk'], (0, 8), (16, 8))
        for x in [4, 12]: pygame.draw.line(s, PAL['blk'], (x, 8), (x, 16))
        return s

    elif name == 'brick':
        s = pygame.Surface((16, 16))
        s.fill(PAL['brk2'])
        pygame.draw.rect(s, PAL['brk3'], (1, 1, 6, 6))
        pygame.draw.rect(s, PAL['brk3'], (9, 1, 6, 6))
        pygame.draw.rect(s, PAL['brk3'], (1, 9, 14, 6))
        pygame.draw.line(s, PAL['blk'], (0, 0), (15, 0))
        pygame.draw.line(s, PAL['blk'], (0, 8), (15, 8))
        pygame.draw.line(s, PAL['blk'], (0, 0), (0, 15))
        pygame.draw.line(s, PAL['blk'], (8, 0), (8, 8))
        pygame.draw.line(s, PAL['blk'], (4, 8), (4, 15))
        pygame.draw.line(s, PAL['blk'], (12, 8), (12, 15))
        return s

    elif name == 'question':
        s = pygame.Surface((16, 16))
        s.fill(PAL['org'])
        pygame.draw.rect(s, PAL['yel'], (1, 1, 14, 14))
        pygame.draw.rect(s, PAL['org'], (2, 2, 12, 12))
        br = 220 + int(math.sin(frame * 0.12) * 35)
        col = (br, br, 100)
        qm = [(6,4),(7,4),(8,4),(9,4),(5,5),(10,5),(9,6),(10,6),
              (8,7),(9,7),(7,8),(8,8),(7,9),(7,11),(8,11)]
        for x,y in qm: s.set_at((x,y), col)
        return s

    elif name == 'question_used':
        s = pygame.Surface((16, 16))
        s.fill(PAL['brn'])
        pygame.draw.rect(s, (100, 60, 20), (1, 1, 14, 14))
        return s

    elif name == 'pipe_top':
        s = pygame.Surface((32, 16))
        s.fill(PAL['pip1'])
        pygame.draw.rect(s, PAL['pip2'], (2, 0, 6, 16))
        pygame.draw.rect(s, PAL['pip3'], (24, 0, 6, 16))
        pygame.draw.rect(s, PAL['blk'], (0, 0, 32, 2))
        pygame.draw.rect(s, PAL['blk'], (0, 14, 32, 2))
        pygame.draw.line(s, PAL['blk'], (0, 0), (0, 16))
        pygame.draw.line(s, PAL['blk'], (31, 0), (31, 16))
        return s

    elif name == 'pipe_body':
        s = pygame.Surface((32, 16))
        pygame.draw.rect(s, PAL['pip3'], (0, 0, 4, 16))
        pygame.draw.rect(s, PAL['pip2'], (4, 0, 6, 16))
        pygame.draw.rect(s, PAL['pip1'], (10, 0, 12, 16))
        pygame.draw.rect(s, PAL['pip3'], (22, 0, 6, 16))
        pygame.draw.rect(s, PAL['blk'], (28, 0, 4, 16))
        pygame.draw.line(s, PAL['blk'], (0, 0), (0, 16))
        pygame.draw.line(s, PAL['blk'], (31, 0), (31, 16))
        return s

    elif name == 'coin':
        s = pygame.Surface((8, 14), pygame.SRCALPHA)
        c = [(3,0),(4,0),(2,1),(3,1),(4,1),(5,1),(1,2),(2,2),(3,2),(4,2),(5,2),(6,2)]
        for i in range(3, 11):
            c.extend([(1,i),(2,i),(5,i),(6,i),(3,i),(4,i)])
        c.extend([(1,11),(2,11),(3,11),(4,11),(5,11),(6,11),(2,12),(3,12),(4,12),(5,12),(3,13),(4,13)])
        for x,y in c: s.set_at((x,y), PAL['yel'])
        return s

    elif name == 'flag':
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(s, PAL['grn'], (7, 0, 2, 16))
        return s

    elif name == 'flagtop':
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(s, PAL['grn'], (7, 8, 2, 8))
        pygame.draw.circle(s, PAL['yel'], (8, 6), 5)
        return s

    elif name == 'flagbanner':
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(s, PAL['grn'], (7, 0, 2, 16))
        # Green flag banner
        pts = [(0, 2), (6, 2), (6, 10), (3, 8), (0, 10)]
        pygame.draw.polygon(s, PAL['grn'], pts)
        return s

    elif name == 'castle':
        s = pygame.Surface((80, 80), pygame.SRCALPHA)
        # Main body
        pygame.draw.rect(s, PAL['grd2'], (8, 32, 64, 48))
        # Towers
        pygame.draw.rect(s, PAL['grd2'], (8, 16, 16, 16))
        pygame.draw.rect(s, PAL['grd2'], (56, 16, 16, 16))
        pygame.draw.rect(s, PAL['grd2'], (32, 0, 16, 32))
        # Battlements
        for x in [8, 16, 56, 64]:
            pygame.draw.rect(s, PAL['grd2'], (x, 8, 8, 8))
        for x in [32, 40]:
            pygame.draw.rect(s, PAL['grd3'], (x, -8, 8, 8))
        # Door
        pygame.draw.rect(s, PAL['blk'], (32, 48, 16, 32))
        pygame.draw.rect(s, PAL['blk'], (36, 40, 8, 8))
        # Windows
        pygame.draw.rect(s, PAL['blk'], (16, 40, 8, 8))
        pygame.draw.rect(s, PAL['blk'], (56, 40, 8, 8))
        return s

    return pygame.Surface((16, 16))

# SOUND
class Sound:
    __slots__ = ['s']
    def __init__(self):
        self.s = {}
        self._gen()

    def _gen(self):
        def sq(f, d, v=0.2):
            n = int(44100 * d)
            b = array.array('h', [0] * n)
            p = 44100 / f if f > 0 else 1
            for i in range(n):
                w = 1 if (i % p) / p < 0.5 else -1
                b[i] = int(w * max(0, 1 - i / n) * v * 32767)
            return pygame.mixer.Sound(buffer=b)

        def win_fanfare():
            # Victory jingle
            n = int(44100 * 1.5)
            b = array.array('h', [0] * n)
            notes = [(523, 0, 0.15), (659, 0.15, 0.15), (784, 0.3, 0.15), 
                     (1047, 0.5, 0.5), (784, 1.0, 0.2), (1047, 1.2, 0.3)]
            for freq, start, dur in notes:
                st = int(start * 44100)
                ed = int((start + dur) * 44100)
                p = 44100 / freq
                for i in range(st, min(ed, n)):
                    w = 1 if ((i - st) % p) / p < 0.5 else -1
                    env = max(0, 1 - (i - st) / (dur * 44100) * 0.5)
                    b[i] = min(32767, max(-32768, b[i] + int(w * env * 0.2 * 32767)))
            return pygame.mixer.Sound(buffer=b)

        self.s = {
            'jump': sq(400, 0.12),
            'coin': sq(988, 0.06),
            'stomp': sq(150, 0.06),
            'bump': sq(100, 0.05),
            'powerup': sq(523, 0.3),
            'flagpole': sq(800, 0.5, 0.25),
            'win': win_fanfare(),
        }

    def play(self, n):
        if n in self.s: self.s[n].play()

SND = Sound()

# LEVEL
class Level:
    __slots__ = ['w', 'tiles', 'contents', 'used', 'pipes', 'flag_x']
    def __init__(self):
        self.w = 224
        self.tiles = [[0] * self.w for _ in range(15)]
        self.contents = {}
        self.used = set()
        self.pipes = []
        self.flag_x = 198  # Flag pole x position
        self._build()

    def _build(self):
        # Ground
        for x in range(self.w):
            if x not in range(69, 71) and x not in range(86, 89) and x not in range(153, 156):
                self.tiles[13][x] = self.tiles[14][x] = 1

        # Pipes
        pipe_data = [(28, 12, 1), (38, 11, 2), (46, 11, 2), (57, 11, 2), (163, 11, 2)]
        for px, py, ph in pipe_data:
            self.pipes.append((px, py, ph))
            for dy in range(ph + 1):
                self.tiles[py + dy][px] = 10
                self.tiles[py + dy][px + 1] = 10

        # Questions
        for qx, qy, c in [(16, 9, 'coin'), (21, 9, 'mush'), (23, 9, 'coin'), 
                          (22, 5, 'coin'), (78, 9, 'mush'), (106, 9, 'coin'), 
                          (109, 5, 'coin'), (112, 5, 'coin')]:
            self.tiles[qy][qx] = 2
            self.contents[(qx, qy)] = c

        # Bricks
        for bx, by in [(20, 9), (22, 9), (24, 9), (77, 9), (79, 9), (80, 9), 
                       (100, 9), (118, 9), (121, 5), (122, 5), (123, 5), 
                       (128, 5), (129, 5), (130, 5), (131, 5)]:
            self.tiles[by][bx] = 3

        # Stairs
        for i in range(4):
            for j in range(i + 1): self.tiles[12 - j][134 + i] = 1
        for i in range(4):
            for j in range(4 - i): self.tiles[12 - j][140 + i] = 1
        for i in range(5):
            for j in range(i + 1): self.tiles[12 - j][148 + i] = 1
        for i in range(9):
            for j in range(min(i + 1, 8)): self.tiles[12 - j][181 + i] = 1

        # Flagpole
        self.tiles[4][self.flag_x] = 6  # top
        for y in range(5, 13): self.tiles[y][self.flag_x] = 7

    def get(self, tx, ty):
        if 0 <= tx < self.w and 0 <= ty < 15: return self.tiles[ty][tx]
        return 0

    def solid(self, tx, ty):
        t = self.get(tx, ty)
        return t in (1, 2, 3, 10)

# ENTITIES
class Mario:
    __slots__ = ['x', 'y', 'vx', 'vy', 'w', 'h', 'big', 'grounded', 'jumping', 
                 'facing', 'coins', 'score', 'dead', 'inv', 'frame', 'won', 'flag_slide']
    def __init__(self):
        self.x, self.y = 40.0, 192.0
        self.vx, self.vy = 0.0, 0.0
        self.w, self.h = 12, 16
        self.big = False
        self.grounded = False
        self.jumping = False
        self.facing = 1
        self.coins = 0
        self.score = 0
        self.dead = False
        self.inv = 0
        self.frame = 0
        self.won = False
        self.flag_slide = 0  # 0 = not sliding, >0 = sliding down

class Enemy:
    __slots__ = ['x', 'y', 'vx', 'vy', 'alive', 'type', 'squash']
    def __init__(self, x, y, t='goomba'):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = -0.5, 0.0
        self.alive = True
        self.type = t
        self.squash = 0

# GAME
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H), pygame.SCALED)
        self.surf = pygame.Surface((NES_W, NES_H))
        pygame.display.set_caption("ULTRA MARIO 2D BROS")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.level = Level()
        self.mario = Mario()
        self.enemies = [
            Enemy(352, 192), Enemy(400, 192), Enemy(432, 192),
            Enemy(816, 192), Enemy(848, 192), Enemy(1280, 192)
        ]
        self.cam = 0.0
        self.frame = 0
        self.state = 'menu'
        self.flag_y = 80  # Banner position on pole
        self.win_timer = 0

    def run(self):
        while True:
            self.handle_events()
            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'play':
                self.update()
                self.draw()
            elif self.state == 'win':
                self.update_win()
                self.draw()
                self.draw_win_prompt()
            elif self.state == 'gameover':
                self.draw()
                self.draw_gameover_prompt()
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN:
                if self.state == 'menu' and e.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    self.state = 'play'
                    SND.play('coin')
                elif self.state == 'play' and e.key == pygame.K_r:
                    self.reset()
                    self.state = 'play'
                elif self.state == 'win':
                    if e.key == pygame.K_y:
                        self.reset()
                        self.state = 'play'
                    elif e.key == pygame.K_n:
                        pygame.quit()
                        sys.exit()
                elif self.state == 'gameover':
                    if e.key == pygame.K_y:
                        self.reset()
                        self.state = 'play'
                    elif e.key == pygame.K_n:
                        pygame.quit()
                        sys.exit()

    def update(self):
        self.frame += 1
        m = self.mario
        m.frame += 1

        # Check for flag win
        if not m.won and not m.dead:
            flag_px = self.level.flag_x * TILE
            if m.x + m.w >= flag_px and m.x <= flag_px + 16:
                m.won = True
                m.flag_slide = 1
                m.vx = 0
                m.vy = 0
                m.x = flag_px - 6
                SND.play('flagpole')
                self.win_timer = 0

        # Flag slide animation
        if m.flag_slide > 0:
            m.flag_slide += 1
            # Slide Mario down
            if m.y < 192:
                m.y += 2
                self.flag_y = min(self.flag_y + 2, 192)
            else:
                m.grounded = True
                if m.flag_slide > 60:
                    # Walk to castle
                    m.x += 1
                    m.facing = 1
                if m.flag_slide > 180:
                    self.state = 'win'
                    SND.play('win')
            return

        if m.dead:
            if self.win_timer == 0:
                self.win_timer = 1
            self.win_timer += 1
            if self.win_timer > 90:
                self.state = 'gameover'
            return

        if m.inv > 0: m.inv -= 1

        keys = pygame.key.get_pressed()
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        maxv = M_MAXR if run else M_MAXW

        if keys[pygame.K_LEFT]:
            m.vx = max(m.vx - M_ACCEL, -maxv)
            m.facing = -1
        elif keys[pygame.K_RIGHT]:
            m.vx = min(m.vx + M_ACCEL, maxv)
            m.facing = 1
        else:
            if abs(m.vx) < M_DECEL: m.vx = 0
            else: m.vx -= M_DECEL * (1 if m.vx > 0 else -1)

        jump_key = keys[pygame.K_z] or keys[pygame.K_SPACE]
        if jump_key and m.grounded and not m.jumping:
            m.vy = M_JUMP - (0.5 if run else 0)
            m.jumping = True
            m.grounded = False
            SND.play('jump')
        if m.jumping and jump_key and m.vy < 0:
            m.vy -= M_JUMP_HOLD
        if not jump_key:
            m.jumping = False
            if m.vy < -1: m.vy = -1

        m.vy = min(m.vy + GRAV, MAX_FALL)

        nx = m.x + m.vx
        if not self._collide_h(nx, m.y, m.w, m.h):
            m.x = nx
        else:
            m.vx = 0

        ny = m.y + m.vy
        m.grounded = False
        if self._collide_v(m.x, ny, m.w, m.h):
            if m.vy > 0:
                m.y = (int(ny + m.h) // TILE) * TILE - m.h
                m.grounded = True
            else:
                m.y = (int(ny) // TILE + 1) * TILE
                self._hit_block(int((m.x + m.w / 2) // TILE), int(ny // TILE))
            m.vy = 0
        else:
            m.y = ny

        target = max(0, min(m.x - NES_W / 3, self.level.w * TILE - NES_W))
        self.cam += (target - self.cam) * 0.1

        for e in self.enemies:
            if not e.alive:
                if e.squash > 0: e.squash -= 1
                continue
            e.vy = min(e.vy + GRAV, MAX_FALL)
            e.x += e.vx
            e.y += e.vy
            if self.level.solid(int(e.x + 8) // TILE, int(e.y + 16) // TILE):
                e.y = (int(e.y + 16) // TILE) * TILE - 16
                e.vy = 0
            if self.level.solid(int(e.x + e.vx * 16 + 8) // TILE, int(e.y + 8) // TILE):
                e.vx *= -1
            if m.inv == 0 and abs(e.x - m.x) < 12 and abs(e.y - m.y) < 14:
                if m.vy > 0 and m.y + m.h < e.y + 10:
                    e.alive = False
                    e.squash = 30
                    m.vy = -3
                    m.score += 100
                    SND.play('stomp')
                else:
                    self._hurt()

        if m.y > NES_H + 16:
            m.dead = True

    def update_win(self):
        self.frame += 1
        self.win_timer += 1

    def _collide_h(self, x, y, w, h):
        for dy in [2, h - 2]:
            tx = int((x + w) // TILE) if self.mario.vx > 0 else int(x // TILE)
            ty = int((y + dy) // TILE)
            if self.level.solid(tx, ty): return True
        return False

    def _collide_v(self, x, y, w, h):
        for dx in [2, w - 2]:
            tx = int((x + dx) // TILE)
            ty = int((y + h) // TILE) if self.mario.vy > 0 else int(y // TILE)
            if self.level.solid(tx, ty): return True
        return False

    def _hit_block(self, tx, ty):
        t = self.level.get(tx, ty)
        if t == 2 and (tx, ty) not in self.level.used:
            self.level.used.add((tx, ty))
            c = self.level.contents.get((tx, ty), 'coin')
            if c == 'coin':
                self.mario.coins += 1
                self.mario.score += 200
                SND.play('coin')
            elif c == 'mush':
                if not self.mario.big:
                    self.mario.big = True
                    self.mario.h = 24
                    self.mario.y -= 8
                    SND.play('powerup')
        elif t == 3:
            SND.play('bump')

    def _hurt(self):
        m = self.mario
        if m.big:
            m.big = False
            m.h = 16
            m.inv = 120
            SND.play('bump')
        else:
            m.dead = True

    def draw_menu(self):
        self.surf.fill(PAL['sky'])
        self.frame += 1
        for x in range(0, NES_W, 16):
            self.surf.blit(get_sprite('ground'), (x, 208))
            self.surf.blit(get_sprite('ground'), (x, 224))
        f = pygame.font.SysFont('arial', 16, bold=True)
        t1 = f.render("SUPER MARIO BROS.", True, PAL['wht'])
        t2 = f.render("PRESS START", True, PAL['yel'] if (self.frame // 30) % 2 else PAL['org'])
        self.surf.blit(t1, (NES_W // 2 - t1.get_width() // 2, 80))
        self.surf.blit(t2, (NES_W // 2 - t2.get_width() // 2, 150))
        self.surf.blit(get_sprite('mario_s'), (120, 192))
        self.screen.blit(pygame.transform.scale(self.surf, (W, H)), (0, 0))

    def draw(self):
        self.surf.fill(PAL['sky'])
        cx = int(self.cam)
        m = self.mario

        # Tiles
        for ty in range(15):
            for tx in range(cx // TILE - 1, (cx + NES_W) // TILE + 2):
                t = self.level.get(tx, ty)
                dx, dy = tx * TILE - cx, ty * TILE
                if t == 1:
                    self.surf.blit(get_sprite('ground'), (dx, dy))
                elif t == 2:
                    if (tx, ty) in self.level.used:
                        self.surf.blit(get_sprite('question_used'), (dx, dy))
                    else:
                        self.surf.blit(_create_sprite('question', self.frame), (dx, dy))
                elif t == 3:
                    self.surf.blit(get_sprite('brick'), (dx, dy))
                elif t == 6:
                    self.surf.blit(get_sprite('flagtop'), (dx, dy))
                elif t == 7:
                    # Draw flag with banner at correct position
                    flag_screen_x = self.level.flag_x * TILE - cx
                    if ty * TILE >= self.flag_y and ty * TILE < self.flag_y + 16:
                        self.surf.blit(get_sprite('flagbanner'), (dx, dy))
                    else:
                        self.surf.blit(get_sprite('flag'), (dx, dy))

        # Castle at end
        castle_x = 202 * TILE - cx
        if castle_x < NES_W + 80:
            self.surf.blit(get_sprite('castle'), (castle_x, 128))

        # Pipes
        for px, py, ph in self.level.pipes:
            dx = px * TILE - cx
            self.surf.blit(get_sprite('pipe_top'), (dx, py * TILE))
            for i in range(1, ph + 1):
                self.surf.blit(get_sprite('pipe_body'), (dx, (py + i) * TILE))

        # Enemies
        for e in self.enemies:
            ex = int(e.x - cx)
            if -20 < ex < NES_W + 20:
                if e.alive:
                    self.surf.blit(get_sprite('goomba'), (ex, int(e.y)))
                elif e.squash > 0:
                    self.surf.blit(get_sprite('goomba_flat'), (ex, int(e.y) + 8))

        # Mario
        mx, my = int(m.x - cx), int(m.y)
        if not m.dead and (m.inv == 0 or self.frame % 4 < 2):
            spr = get_sprite('mario_b' if m.big else 'mario_s')
            if m.facing < 0:
                spr = pygame.transform.flip(spr, True, False)
            self.surf.blit(spr, (mx, my))

        # HUD
        f = pygame.font.SysFont('arial', 8)
        self.surf.blit(f.render("MARIO", True, PAL['wht']), (24, 8))
        self.surf.blit(f.render(f"{m.score:06d}", True, PAL['wht']), (24, 16))
        self.surf.blit(f.render(f"x{m.coins:02d}", True, PAL['wht']), (100, 16))
        self.surf.blit(get_sprite('coin'), (90, 14))
        self.surf.blit(f.render("WORLD", True, PAL['wht']), (145, 8))
        self.surf.blit(f.render("1-1", True, PAL['wht']), (152, 16))
        self.surf.blit(f.render("TIME", True, PAL['wht']), (200, 8))
        time_left = max(0, 400 - self.frame // 60)
        self.surf.blit(f.render(f"{time_left:03d}", True, PAL['wht']), (204, 16))

        self.screen.blit(pygame.transform.scale(self.surf, (W, H)), (0, 0))

    def draw_win_prompt(self):
        # Draw win overlay
        overlay = pygame.Surface((NES_W, NES_H), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 180), (40, 80, 176, 80))
        pygame.draw.rect(overlay, PAL['yel'], (40, 80, 176, 80), 3)
        
        f_big = pygame.font.SysFont('arial', 14, bold=True)
        f_small = pygame.font.SysFont('arial', 10)
        
        # "YOU WIN!" text with animation
        if (self.frame // 15) % 2:
            col = PAL['yel']
        else:
            col = PAL['wht']
        
        t1 = f_big.render("YOU WIN!", True, col)
        t2 = f_small.render(f"SCORE: {self.mario.score}", True, PAL['wht'])
        t3 = f_small.render("PLAY AGAIN?", True, PAL['wht'])
        t4 = f_small.render("Y = YES    N = NO", True, PAL['grn'])
        
        overlay.blit(t1, (NES_W // 2 - t1.get_width() // 2, 88))
        overlay.blit(t2, (NES_W // 2 - t2.get_width() // 2, 108))
        overlay.blit(t3, (NES_W // 2 - t3.get_width() // 2, 125))
        overlay.blit(t4, (NES_W // 2 - t4.get_width() // 2, 140))
        
        self.surf.blit(overlay, (0, 0))
        self.screen.blit(pygame.transform.scale(self.surf, (W, H)), (0, 0))

    def draw_gameover_prompt(self):
        overlay = pygame.Surface((NES_W, NES_H), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 200), (40, 80, 176, 80))
        pygame.draw.rect(overlay, PAL['red'], (40, 80, 176, 80), 3)
        
        f_big = pygame.font.SysFont('arial', 14, bold=True)
        f_small = pygame.font.SysFont('arial', 10)
        
        t1 = f_big.render("GAME OVER", True, PAL['red'])
        t2 = f_small.render(f"SCORE: {self.mario.score}", True, PAL['wht'])
        t3 = f_small.render("CONTINUE?", True, PAL['wht'])
        t4 = f_small.render("Y = YES    N = NO", True, PAL['grn'])
        
        overlay.blit(t1, (NES_W // 2 - t1.get_width() // 2, 88))
        overlay.blit(t2, (NES_W // 2 - t2.get_width() // 2, 108))
        overlay.blit(t3, (NES_W // 2 - t3.get_width() // 2, 125))
        overlay.blit(t4, (NES_W // 2 - t4.get_width() // 2, 140))
        
        self.surf.blit(overlay, (0, 0))
        self.screen.blit(pygame.transform.scale(self.surf, (W, H)), (0, 0))

if __name__ == "__main__":
    Game().run()
