#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS - Optimized NES Clone (2025 Flames Co.)
60 FPS locked, cached sprites, accurate NES physics
"""

import pygame, sys, random, math, array
from functools import lru_cache

pygame.init()
pygame.mixer.init(44100, -16, 2, 512)

# CONSTANTS - NES accurate
NES_W, NES_H = 256, 240
SCALE = 3
W, H = NES_W * SCALE, NES_H * SCALE
FPS = 60
TILE = 16

# NES physics (subpixel accurate)
GRAV = 0.5
MAX_FALL = 4.5
M_ACCEL = 0.09375
M_DECEL = 0.0625
M_MAXW = 1.5625
M_MAXR = 2.5
M_JUMP = -4.0
M_JUMP_HOLD = 0.25

# PALETTE (NES 2C02)
PAL = {
    'sky': (92, 148, 252),
    'grd': (200, 76, 12),
    'brk': (228, 92, 16),
    'pip': (0, 168, 0),
    'pip2': (0, 128, 0),
    'red': (228, 0, 88),
    'skn': (252, 188, 116),
    'brn': (172, 80, 24),
    'yel': (252, 188, 60),
    'blk': (0, 0, 0),
    'wht': (252, 252, 252),
}

# CACHED SPRITE SURFACES
_sprite_cache = {}

def get_sprite(name, frame=0):
    key = (name, frame)
    if key not in _sprite_cache:
        _sprite_cache[key] = _create_sprite(name, frame)
    return _sprite_cache[key]

def _create_sprite(name, frame):
    if name == 'mario_s':
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(s, PAL['red'], (4, 0, 8, 4))
        pygame.draw.rect(s, PAL['skn'], (3, 4, 10, 4))
        pygame.draw.rect(s, PAL['blk'], (5, 5, 2, 2))
        pygame.draw.rect(s, PAL['brn'], (4, 7, 6, 2))
        pygame.draw.rect(s, PAL['red'], (2, 9, 12, 4))
        pygame.draw.rect(s, PAL['brn'], (3, 11, 10, 2))
        pygame.draw.rect(s, PAL['skn'], (1, 9, 2, 3))
        pygame.draw.rect(s, PAL['skn'], (13, 9, 2, 3))
        pygame.draw.rect(s, PAL['brn'], (2, 13, 4, 3))
        pygame.draw.rect(s, PAL['brn'], (10, 13, 4, 3))
        return s
    elif name == 'mario_b':
        s = pygame.Surface((16, 32), pygame.SRCALPHA)
        pygame.draw.rect(s, PAL['red'], (3, 0, 10, 5))
        pygame.draw.rect(s, PAL['skn'], (2, 5, 12, 7))
        pygame.draw.rect(s, PAL['blk'], (4, 7, 2, 3))
        pygame.draw.rect(s, PAL['brn'], (4, 10, 8, 2))
        pygame.draw.rect(s, PAL['red'], (1, 12, 14, 8))
        pygame.draw.rect(s, PAL['brn'], (2, 16, 12, 8))
        pygame.draw.rect(s, PAL['skn'], (0, 13, 2, 5))
        pygame.draw.rect(s, PAL['skn'], (14, 13, 2, 5))
        pygame.draw.rect(s, PAL['brn'], (2, 24, 5, 8))
        pygame.draw.rect(s, PAL['brn'], (9, 24, 5, 8))
        return s
    elif name == 'goomba':
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(s, PAL['brn'], (1, 2, 14, 10))
        pygame.draw.ellipse(s, PAL['yel'], (3, 3, 4, 5))
        pygame.draw.ellipse(s, PAL['yel'], (9, 3, 4, 5))
        pygame.draw.ellipse(s, PAL['blk'], (4, 5, 2, 3))
        pygame.draw.ellipse(s, PAL['blk'], (10, 5, 2, 3))
        pygame.draw.ellipse(s, PAL['brn'], (2, 11, 5, 5))
        pygame.draw.ellipse(s, PAL['brn'], (9, 11, 5, 5))
        return s
    elif name == 'ground':
        s = pygame.Surface((16, 16))
        s.fill(PAL['grd'])
        pygame.draw.rect(s, (160, 60, 8), (0, 0, 16, 2))
        return s
    elif name == 'brick':
        s = pygame.Surface((16, 16))
        s.fill(PAL['brk'])
        pygame.draw.line(s, PAL['blk'], (0, 7), (16, 7))
        pygame.draw.line(s, PAL['blk'], (4, 0), (4, 7))
        pygame.draw.line(s, PAL['blk'], (12, 0), (12, 7))
        pygame.draw.line(s, PAL['blk'], (8, 8), (8, 16))
        return s
    elif name == 'question':
        s = pygame.Surface((16, 16))
        s.fill(PAL['yel'])
        pygame.draw.rect(s, PAL['brk'], (1, 1, 14, 14))
        br = 200 + int(math.sin(frame * 0.15) * 55)
        pygame.draw.rect(s, (br, br, 100), (5, 3, 6, 2))
        pygame.draw.rect(s, (br, br, 100), (9, 4, 2, 4))
        pygame.draw.rect(s, (br, br, 100), (5, 7, 6, 2))
        pygame.draw.rect(s, (br, br, 100), (5, 10, 2, 2))
        pygame.draw.rect(s, (br, br, 100), (6, 13, 4, 2))
        return s
    elif name == 'question_used':
        s = pygame.Surface((16, 16))
        s.fill((100, 60, 8))
        pygame.draw.rect(s, PAL['brn'], (1, 1, 14, 14))
        return s
    elif name == 'pipe_top':
        s = pygame.Surface((32, 16))
        s.fill(PAL['pip'])
        pygame.draw.rect(s, PAL['pip2'], (0, 0, 4, 16))
        pygame.draw.rect(s, (0, 200, 0), (4, 0, 4, 16))
        pygame.draw.rect(s, PAL['pip2'], (24, 0, 8, 16))
        return s
    elif name == 'pipe_body':
        s = pygame.Surface((32, 16))
        pygame.draw.rect(s, PAL['pip2'], (0, 0, 4, 16))
        pygame.draw.rect(s, PAL['pip'], (4, 0, 24, 16))
        pygame.draw.rect(s, PAL['pip2'], (28, 0, 4, 16))
        return s
    elif name == 'coin':
        s = pygame.Surface((8, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(s, PAL['yel'], (0, 0, 8, 14))
        pygame.draw.ellipse(s, (200, 160, 40), (2, 2, 4, 10))
        return s
    return pygame.Surface((16, 16))

# SOUND - optimized buffer gen
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

        self.s = {
            'jump': sq(400, 0.12),
            'coin': sq(988, 0.06),
            'stomp': sq(150, 0.06),
            'bump': sq(100, 0.05),
            'powerup': sq(523, 0.3),
        }

    def play(self, n):
        if n in self.s: self.s[n].play()

SND = Sound()

# LEVEL
class Level:
    __slots__ = ['w', 'tiles', 'contents', 'used']
    def __init__(self):
        self.w = 224
        self.tiles = [[0] * self.w for _ in range(15)]
        self.contents = {}
        self.used = set()
        self._build()

    def _build(self):
        # Ground
        for x in range(self.w):
            if x not in range(69, 71) and x not in range(86, 89) and x not in range(153, 156):
                self.tiles[13][x] = self.tiles[14][x] = 1
        # Pipes
        for px, py, ph in [(28, 11, 2), (38, 10, 3), (46, 9, 4), (57, 9, 4), (163, 9, 4)]:
            self.tiles[py][px] = 4
            for i in range(1, ph): self.tiles[py + i][px] = 5
        # Questions
        for qx, qy, c in [(16, 9, 'coin'), (21, 9, 'mush'), (23, 9, 'coin'), (22, 5, 'star'), (78, 9, 'mush'), (106, 9, 'coin'), (109, 5, 'coin'), (112, 5, 'coin')]:
            self.tiles[qy][qx] = 2
            self.contents[(qx, qy)] = c
        # Bricks
        for bx, by in [(20, 9), (22, 9), (24, 9), (77, 9), (79, 9), (80, 9), (100, 9), (118, 9), (121, 5), (122, 5), (123, 5), (128, 5), (129, 5), (130, 5), (131, 5)]:
            self.tiles[by][bx] = 3
        # Stairs
        for i in range(8):
            for j in range(i + 1): self.tiles[12 - j][134 + i] = 1
        for i in range(4):
            for j in range(4 - i): self.tiles[12 - j][144 + i] = 1
        for i in range(8):
            for j in range(i + 1): self.tiles[12 - j][155 + i] = 1
        # Flagpole
        self.tiles[4][198] = 6
        for y in range(5, 13): self.tiles[y][198] = 7

    def get(self, tx, ty):
        if 0 <= tx < self.w and 0 <= ty < 15: return self.tiles[ty][tx]
        return 0

    def solid(self, tx, ty):
        t = self.get(tx, ty)
        return t in (1, 2, 3, 4, 5)

# ENTITIES
class Mario:
    __slots__ = ['x', 'y', 'vx', 'vy', 'w', 'h', 'big', 'grounded', 'jumping', 'facing', 'coins', 'score', 'dead', 'inv']
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
        pygame.display.set_caption("ULTRA MARIO 2D")
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        self.level = Level()
        self.mario = Mario()
        self.enemies = [Enemy(352, 192), Enemy(400, 192), Enemy(432, 192), Enemy(816, 192), Enemy(848, 192), Enemy(1280, 192), Enemy(1520, 192)]
        self.cam = 0.0
        self.frame = 0
        self.state = 'menu'

    def run(self):
        while True:
            self.handle_events()
            if self.state == 'menu':
                self.draw_menu()
            elif self.state == 'play':
                self.update()
                self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT: sys.exit()
            if e.type == pygame.KEYDOWN:
                if self.state == 'menu' and e.key in (pygame.K_RETURN, pygame.K_z, pygame.K_SPACE):
                    self.state = 'play'
                    SND.play('coin')
                if self.state == 'play' and e.key == pygame.K_r:
                    self.reset()
                    self.state = 'play'

    def update(self):
        self.frame += 1
        m = self.mario
        if m.dead: return
        if m.inv > 0: m.inv -= 1

        keys = pygame.key.get_pressed()
        run = keys[pygame.K_LSHIFT] or keys[pygame.K_x]
        maxv = M_MAXR if run else M_MAXW

        # Horizontal
        if keys[pygame.K_LEFT]:
            m.vx = max(m.vx - M_ACCEL, -maxv)
            m.facing = -1
        elif keys[pygame.K_RIGHT]:
            m.vx = min(m.vx + M_ACCEL, maxv)
            m.facing = 1
        else:
            if abs(m.vx) < M_DECEL: m.vx = 0
            else: m.vx -= M_DECEL * (1 if m.vx > 0 else -1)

        # Jump (NES variable height)
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

        # Gravity
        m.vy = min(m.vy + GRAV, MAX_FALL)

        # Move X with collision
        nx = m.x + m.vx
        if not self._collide_h(nx, m.y, m.w, m.h):
            m.x = nx
        else:
            m.vx = 0

        # Move Y with collision
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

        # Camera (smooth)
        target = max(0, min(m.x - NES_W / 3, self.level.w * TILE - NES_W))
        self.cam += (target - self.cam) * 0.1

        # Enemies
        for e in self.enemies:
            if not e.alive:
                if e.squash > 0: e.squash -= 1
                continue
            e.vy = min(e.vy + GRAV, MAX_FALL)
            e.x += e.vx
            e.y += e.vy
            # Ground
            if self.level.solid(int(e.x + 8) // TILE, int(e.y + 16) // TILE):
                e.y = (int(e.y + 16) // TILE) * TILE - 16
                e.vy = 0
            # Wall
            if self.level.solid(int(e.x + e.vx * 16 + 8) // TILE, int(e.y + 8) // TILE):
                e.vx *= -1
            # Mario collision
            if m.inv == 0 and abs(e.x - m.x) < 12 and abs(e.y - m.y) < 14:
                if m.vy > 0 and m.y + m.h < e.y + 10:
                    e.alive = False
                    e.squash = 30
                    m.vy = -3
                    m.score += 100
                    SND.play('stomp')
                else:
                    self._hurt()

        # Pit death
        if m.y > NES_H + 16:
            m.dead = True

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
                    self.mario.h = 28
                    self.mario.y -= 12
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
        f = pygame.font.SysFont('arial', 16, bold=True)
        t1 = f.render("ULTRA MARIO 2D BROS", True, PAL['wht'])
        t2 = f.render("PRESS Z OR ENTER", True, PAL['yel'])
        self.surf.blit(t1, (NES_W // 2 - t1.get_width() // 2, 80))
        self.surf.blit(t2, (NES_W // 2 - t2.get_width() // 2, 140))
        self.screen.blit(pygame.transform.scale(self.surf, (W, H)), (0, 0))

    def draw(self):
        self.surf.fill(PAL['sky'])
        cx = int(self.cam)
        m = self.mario

        # Tiles (only visible)
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
                elif t == 4:
                    self.surf.blit(get_sprite('pipe_top'), (dx, dy))
                elif t == 5:
                    self.surf.blit(get_sprite('pipe_body'), (dx, dy))
                elif t in (6, 7):
                    pygame.draw.rect(self.surf, PAL['pip'], (dx + 6, dy, 4, 16))

        # Enemies
        for e in self.enemies:
            ex = int(e.x - cx)
            if -20 < ex < NES_W + 20:
                if e.alive:
                    self.surf.blit(get_sprite('goomba'), (ex, int(e.y)))
                elif e.squash > 0:
                    pygame.draw.rect(self.surf, PAL['brn'], (ex + 2, int(e.y) + 12, 12, 4))

        # Mario
        mx, my = int(m.x - cx), int(m.y)
        if m.inv == 0 or self.frame % 4 < 2:
            spr = get_sprite('mario_b' if m.big else 'mario_s')
            if m.facing < 0:
                spr = pygame.transform.flip(spr, True, False)
            self.surf.blit(spr, (mx, my))

        # HUD
        f = pygame.font.SysFont('arial', 10)
        self.surf.blit(f.render(f"SCORE {m.score:06d}", True, PAL['wht']), (8, 8))
        self.surf.blit(f.render(f"COINS {m.coins:02d}", True, PAL['yel']), (120, 8))
        self.surf.blit(f.render(f"WORLD 1-1", True, PAL['wht']), (200, 8))

        # Death screen
        if m.dead:
            self.surf.fill((0, 0, 0))
            t = f.render("GAME OVER - PRESS R", True, PAL['wht'])
            self.surf.blit(t, (NES_W // 2 - t.get_width() // 2, NES_H // 2))

        self.screen.blit(pygame.transform.scale(self.surf, (W, H)), (0, 0))

if __name__ == "__main__":
    Game().run()
