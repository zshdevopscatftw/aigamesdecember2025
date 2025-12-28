# program.py — ULTRA MARIO 2D BROS (NES-Inspired Procedural Pixel Art)
# Single-file | No external assets | Pygame only
#
# What this does:
# - Renders gameplay at an NES-like base resolution (256×240) and scales up with integer scaling
#   to keep pixels crisp.
# - Uses original, NES-inspired procedural pixel art (no Nintendo sprite sheets or ripped assets).
#
# Controls:
# - Left / Right: move
# - Z or Space: jump
# - X: run (faster)

import sys
import pygame

pygame.init()

# ───────────────── VIDEO SETUP ─────────────────
WINDOW_W, WINDOW_H = 800, 600

# NES maximum display resolution is commonly given as 256×240. (We render at that base size.)
BASE_W, BASE_H = 256, 240

SCREEN = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("ULTRA MARIO 2D BROS — NES-INSPIRED")
CLOCK = pygame.time.Clock()

BASE = pygame.Surface((BASE_W, BASE_H))  # render target

SCALE = max(1, min(WINDOW_W // BASE_W, WINDOW_H // BASE_H))  # integer scale for crisp pixels
SCALED_W, SCALED_H = BASE_W * SCALE, BASE_H * SCALE
OFFSET_X = (WINDOW_W - SCALED_W) // 2
OFFSET_Y = (WINDOW_H - SCALED_H) // 2

# ───────────────── PALETTE (NES-ish) ─────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Sky/ground colors in a classic SMB-like vibe (still original art)
SKY = (92, 148, 252)
GROUND_DARK = (148, 60, 12)
GROUND_LIGHT = (200, 76, 12)
BRICK_DARK = (156, 40, 0)
BRICK_LIGHT = (208, 96, 40)
QUESTION_GOLD = (252, 152, 56)
QUESTION_LIGHT = (252, 216, 168)
PIPE_DARK = (0, 168, 0)
PIPE_LIGHT = (88, 216, 84)

HERO_RED = (216, 40, 0)
HERO_BLUE = (0, 80, 200)
HERO_SKIN = (252, 152, 56)
HERO_BROWN = (100, 50, 20)

GOOMBA_BROWN = (200, 108, 44)
GOOMBA_DARK = (120, 60, 20)

HUD_COLOR = WHITE
HILL_GREEN = (0, 168, 68)

TILE = 16

# ───────────────── PIXEL ART HELPERS ─────────────────
def surf(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)

def draw_pixels(target, pattern, palette, px=1, ox=0, oy=0):
    """
    Draw a pixel-art pattern (list[str]) onto target.
    - pattern: list of strings (rows). Each char maps to palette. '.' means transparent.
    - px: pixel size multiplier.
    """
    for y, row in enumerate(pattern):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            color = palette.get(ch)
            if color is None:
                continue
            target.fill(color, pygame.Rect(ox + x * px, oy + y * px, px, px))

def make_sprite(pattern, palette, px=1):
    h = len(pattern)
    w = len(pattern[0]) if h else 0
    s = surf(w * px, h * px)
    draw_pixels(s, pattern, palette, px=px)
    return s

def pad16(rows):
    """Force each row to 16 chars (centered) for tile-aligned sprites."""
    out = []
    for r in rows:
        if len(r) > 16:
            out.append(r[:16])
            continue
        pad = 16 - len(r)
        left = pad // 2
        right = pad - left
        out.append("." * left + r + "." * right)
    return out

# ───────────────── SPRITES (ORIGINAL, NES-INSPIRED) ─────────────────
SPRITE_PAL = {
    "R": HERO_RED,
    "B": HERO_BLUE,
    "S": HERO_SKIN,
    "K": BLACK,
    "W": WHITE,
    "H": HERO_BROWN,
    "g": GOOMBA_BROWN,
    "d": GOOMBA_DARK,
    "q": QUESTION_GOLD,
    "Q": QUESTION_LIGHT,
    "a": BRICK_DARK,
    "A": BRICK_LIGHT,
    "m": GROUND_DARK,
    "M": GROUND_LIGHT,
}

# Small hero (16×16)
SMALL_HERO = pad16([
    "....RRRRRR....",
    "...RRRRRRRR...",
    "..RRRKKKRRRR..",
    "..RRSSSSSSRR..",
    "..RRSSKSSKRR..",
    "..RRSSSSSSRR..",
    "...RRSSSSRR...",
    "....RRRRRR....",
    ".....BBBB.....",
    "....BBBBBB....",
    "...BBBWBBBB...",
    "...BBBWBBBB...",
    "....BB..BB....",
    "...HH....HH...",
    "..HHH....HHH..",
    "..............",
])

# Big hero (16×32) — two tiles tall
BIG_HERO = pad16([
    "....RRRRRR....",
    "...RRRRRRRR...",
    "..RRRKKKRRRR..",
    "..RRSSSSSSRR..",
    "..RRSSKSSKRR..",
    "..RRSSSSSSRR..",
    "...RRSSSSRR...",
    "....RRRRRR....",
    ".....BBBB.....",
    "....BBBBBB....",
    "...BBBWBBBB...",
    "...BBBWBBBB...",
    "....BB..BB....",
    "...HH....HH...",
    "..HHH....HHH..",
    "..............",
    ".....RRRR.....",
    "....RRRRRR....",
    "...RRBBBBRR...",
    "...RRBBBBRR...",
    "...RRBBBBRR...",
    "....BBBBBB....",
    "....BBBBBB....",
    "....BB..BB....",
    "...HH....HH...",
    "..HHH....HHH..",
    "..HH......HH..",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
])

GOOMBA = pad16([
    "....gggggg....",
    "...gggggggg...",
    "..gggddddggg..",
    "..ggdggggdgg..",
    "..ggdggggdgg..",
    "..gggddddggg..",
    "...gggggggg...",
    "....gggggg....",
    "....d....d....",
    "...dd....dd...",
    "..ddd....ddd..",
    "..d........d..",
    "..............",
    "..............",
    "..............",
    "..............",
])

# 16×16 brick tile
BRICK = [
    "aaaaaaaaaaaaaaaa",
    "aAAAAaAAAAaAAAAa",
    "aAAAAaAAAAaAAAAa",
    "aaaaaaaaaaaaaaaa",
    "aAAAAaAAAAaAAAAa",
    "aAAAAaAAAAaAAAAa",
    "aaaaaaaaaaaaaaaa",
    "aAAAAaAAAAaAAAAa",
    "aAAAAaAAAAaAAAAa",
    "aaaaaaaaaaaaaaaa",
    "aAAAAaAAAAaAAAAa",
    "aAAAAaAAAAaAAAAa",
    "aaaaaaaaaaaaaaaa",
    "aAAAAaAAAAaAAAAa",
    "aAAAAaAAAAaAAAAa",
    "aaaaaaaaaaaaaaaa",
]

QUESTION = [
    "qqqqqqqqqqqqqqqq",
    "qQQQQQQQQQQQQQQq",
    "qQQqqQQQQqqQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qQQqqqqqqqqQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qQQQQqqqqQQQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qQQQQqqQQqqQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qQQqqqqqqqqQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qQQQQQQQQQQQQQQq",
    "qqqqqqqqqqqqqqqq",
]

USED = [
    "MMMMMMMMMMMMMMMM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MmmmmmmmmmmmmmmM",
    "MMMMMMMMMMMMMMMM",
]

GROUND = [
    "MMMMMMMMMMMMMMMM",
    "MMMMMMMMMMMMMMMM",
    "MMmmmmMMmmmmMMmm",
    "MmmmmMmmmmMmmmmM",
    "MMmmmmMMmmmmMMmm",
    "MmmmmMmmmmMmmmmM",
    "MMmmmmMMmmmmMMmm",
    "MmmmmMmmmmMmmmmM",
    "MMmmmmMMmmmmMMmm",
    "MmmmmMmmmmMmmmmM",
    "MMmmmmMMmmmmMMmm",
    "MmmmmMmmmmMmmmmM",
    "MMmmmmMMmmmmMMmm",
    "MmmmmMmmmmMmmmmM",
    "MMMMMMMMMMMMMMMM",
    "MMMMMMMMMMMMMMMM",
]

COIN = pad16([
    ".....QQQQQ.....",
    "....QQqqqQQ....",
    "...QQqqqqqQQ...",
    "...QqqQQQqqQ...",
    "..QQqQ...QqQQ..",
    "..QqqQ...QqqQ..",
    "..QqqQ...QqqQ..",
    "..QQqQ...QqQQ..",
    "...QqqQQQqqQ...",
    "...QQqqqqqQQ...",
    "....QQqqqQQ....",
    ".....QQQQQ.....",
    "...............",
    "...............",
    "...............",
    "...............",
])

MUSHROOM = pad16([
    "....RRRRRR....",
    "...RRRRRRRR...",
    "..RRWWRRWWRR..",
    "..RWWWWWWWWR..",
    ".RRWWWWWWWWRR.",
    ".RRWWWWWWWWRR.",
    ".RRRWWWWWWRRR.",
    "..RRRRRRRRRR..",
    "..SSSSSSSSSS..",
    ".SSSKSSSSKSSS.",
    ".SSSSSSSSSSSS.",
    ".SSSSSSSSSSSS.",
    "..SSSS..SSSS..",
    "..HHHH..HHHH..",
    "..............",
    "..............",
])

# Prebuild surfaces
SPR_HERO_SMALL = make_sprite(SMALL_HERO, SPRITE_PAL, px=1)
SPR_HERO_BIG = make_sprite(BIG_HERO, SPRITE_PAL, px=1)
SPR_GOOMBA = make_sprite(GOOMBA, SPRITE_PAL, px=1)
SPR_BRICK = make_sprite(BRICK, SPRITE_PAL, px=1)
SPR_QUESTION = make_sprite(QUESTION, SPRITE_PAL, px=1)
SPR_USED = make_sprite(USED, SPRITE_PAL, px=1)
SPR_GROUND = make_sprite(GROUND, SPRITE_PAL, px=1)
SPR_COIN = make_sprite(COIN, SPRITE_PAL, px=1)
SPR_MUSHROOM = make_sprite(MUSHROOM, SPRITE_PAL, px=1)

# ───────────────── BASIC GAME OBJECTS ─────────────────
class Solid:
    """Solid collision object with a rect (for collision). Drawing is handled per-kind."""
    __slots__ = ("rect", "kind")
    def __init__(self, x, y, w, h, kind="solid"):
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind

    def draw(self, target, cam_x):
        pass

    def hit_from_below(self, mario, level):
        pass

class BrickBlock(Solid):
    def __init__(self, tx, ty):
        super().__init__(tx*TILE, ty*TILE, TILE, TILE, kind="brick")

    def draw(self, target, cam_x):
        target.blit(SPR_BRICK, (self.rect.x - cam_x, self.rect.y))

class QuestionBlock(Solid):
    __slots__ = ("used", "item")
    def __init__(self, tx, ty, item="coin"):
        super().__init__(tx*TILE, ty*TILE, TILE, TILE, kind="question")
        self.used = False
        self.item = item

    def draw(self, target, cam_x):
        target.blit(SPR_USED if self.used else SPR_QUESTION, (self.rect.x - cam_x, self.rect.y))

    def hit_from_below(self, mario, level):
        if self.used:
            return
        self.used = True
        if self.item == "coin":
            level.spawn_coin_pop(self.rect.centerx, self.rect.y)
            level.coins += 1
            level.score += 200
        elif self.item == "mushroom":
            level.spawn_mushroom(self.rect.x, self.rect.y - TILE)
        else:
            level.score += 50

class Pipe(Solid):
    __slots__ = ("image",)
    def __init__(self, tx, ground_ty, height_tiles=2):
        w = TILE * 2
        h = TILE * height_tiles
        x = tx * TILE
        y = (ground_ty - height_tiles) * TILE
        super().__init__(x, y, w, h, kind="pipe")
        self.image = self._make_image(w, h)

    @staticmethod
    def _make_image(w, h):
        s = surf(w, h)
        s.fill(PIPE_DARK)
        stripe = pygame.Rect(w//2 - 3, 0, 6, h)
        s.fill(PIPE_LIGHT, stripe)
        s.fill((0, 120, 0), pygame.Rect(0, 0, w, 6))
        s.fill((0, 200, 0), pygame.Rect(0, 6, w, 2))
        pygame.draw.rect(s, BLACK, s.get_rect(), 1)
        return s

    def draw(self, target, cam_x):
        target.blit(self.image, (self.rect.x - cam_x, self.rect.y))

class CoinPop:
    __slots__ = ("x","y","timer")
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 18

    def update(self):
        self.timer -= 1
        self.y -= 1

    def draw(self, target, cam_x):
        target.blit(SPR_COIN, (self.x - cam_x - SPR_COIN.get_width()//2, self.y))

    @property
    def alive(self):
        return self.timer > 0

class MushroomPower:
    __slots__ = ("rect","vx","vy","emerging")
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.vx = 0.8
        self.vy = 0.0
        self.emerging = 16

    def update(self, level):
        if self.emerging > 0:
            self.rect.y -= 1
            self.emerging -= 1
            return

        self.vy = min(self.vy + 0.5, 6)

        self.rect.x += int(self.vx)
        for s in level.solids:
            if self.rect.colliderect(s.rect):
                if self.vx > 0:
                    self.rect.right = s.rect.left
                else:
                    self.rect.left = s.rect.right
                self.vx *= -1

        self.rect.y += int(self.vy)
        for s in level.solids:
            if self.rect.colliderect(s.rect):
                if self.vy > 0:
                    self.rect.bottom = s.rect.top
                else:
                    self.rect.top = s.rect.bottom
                self.vy = 0

        if self.rect.colliderect(level.mario.rect):
            level.mario.power_up()
            level.score += 1000
            level._powerup_sfx_flash = 8
            return "picked"

    def draw(self, target, cam_x):
        target.blit(SPR_MUSHROOM, (self.rect.x - cam_x, self.rect.y))

class GoombaEnemy:
    __slots__ = ("rect","vx","vy","alive")
    def __init__(self, tx, ty):
        self.rect = pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)
        self.vx = -0.6
        self.vy = 0.0
        self.alive = True

    def update(self, level):
        if not self.alive:
            return

        self.vy = min(self.vy + 0.5, 6)

        self.rect.x += int(self.vx)
        for s in level.solids:
            if self.rect.colliderect(s.rect):
                if self.vx > 0:
                    self.rect.right = s.rect.left
                else:
                    self.rect.left = s.rect.right
                self.vx *= -1

        self.rect.y += int(self.vy)
        for s in level.solids:
            if self.rect.colliderect(s.rect):
                if self.vy > 0:
                    self.rect.bottom = s.rect.top
                else:
                    self.rect.top = s.rect.bottom
                self.vy = 0

        if self.rect.colliderect(level.mario.rect):
            m = level.mario
            stomp = (m.vy > 0) and (m.rect.bottom - self.rect.top <= 8)
            if stomp:
                self.alive = False
                m.vy = -6
                level.score += 100
            else:
                m.hurt_or_die(level)

    def draw(self, target, cam_x):
        if self.alive:
            target.blit(SPR_GOOMBA, (self.rect.x - cam_x, self.rect.y))

class MarioPlayer:
    __slots__ = ("rect","x","y","vx","vy","on_ground","facing","state","dead","jump_held","invuln")
    def __init__(self, x, y):
        self.state = "small"
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.dead = False
        self.jump_held = False
        self.invuln = 0

    def power_up(self):
        if self.state == "big":
            return
        bottom = self.rect.bottom
        self.state = "big"
        self.rect.height = TILE * 2
        self.rect.bottom = bottom
        self.y = float(self.rect.y)
        self.invuln = 30

    def shrink(self):
        if self.state == "small":
            return
        bottom = self.rect.bottom
        self.state = "small"
        self.rect.height = TILE
        self.rect.bottom = bottom
        self.y = float(self.rect.y)
        self.invuln = 45

    def hurt_or_die(self, level):
        if self.invuln > 0:
            return
        if self.state == "big":
            self.shrink()
            level.score = max(0, level.score - 200)
        else:
            self.dead = True

    def update(self, keys, level):
        if self.dead:
            return

        if self.invuln > 0:
            self.invuln -= 1

        left = keys[pygame.K_LEFT]
        right = keys[pygame.K_RIGHT]
        run = keys[pygame.K_x]
        jump = keys[pygame.K_z] or keys[pygame.K_SPACE]

        accel = 0.15 if not run else 0.22
        max_speed = 1.4 if not run else 2.2
        friction = 0.12

        if left:
            self.vx -= accel
            self.facing = -1
        if right:
            self.vx += accel
            self.facing = 1

        if not (left or right):
            if self.vx > 0:
                self.vx = max(0, self.vx - friction)
            elif self.vx < 0:
                self.vx = min(0, self.vx + friction)

        self.vx = max(-max_speed, min(max_speed, self.vx))

        if jump and self.on_ground and not self.jump_held:
            self.vy = -5.5
            self.on_ground = False
            self.jump_held = True

        if not jump:
            self.jump_held = False

        self.vy = min(self.vy + 0.35, 6)

        self._move_and_collide(level)

        if self.rect.top > BASE_H + 48:
            self.dead = True

    def _move_and_collide(self, level):
        self.on_ground = False

        self.x += self.vx
        self.rect.x = int(self.x)
        for s in level.solids:
            if self.rect.colliderect(s.rect):
                if self.vx > 0:
                    self.rect.right = s.rect.left
                elif self.vx < 0:
                    self.rect.left = s.rect.right
                self.x = float(self.rect.x)
                self.vx = 0

        self.y += self.vy
        self.rect.y = int(self.y)
        for s in level.solids:
            if self.rect.colliderect(s.rect):
                if self.vy > 0:
                    self.rect.bottom = s.rect.top
                    self.on_ground = True
                    self.vy = 0
                elif self.vy < 0:
                    self.rect.top = s.rect.bottom
                    self.vy = 0
                    s.hit_from_below(self, level)
                self.y = float(self.rect.y)

    def draw(self, target, cam_x):
        img = SPR_HERO_BIG if self.state == "big" else SPR_HERO_SMALL
        if self.facing == -1:
            img = pygame.transform.flip(img, True, False)

        if self.invuln > 0 and (self.invuln // 3) % 2 == 0:
            return

        target.blit(img, (self.rect.x - cam_x, self.rect.y))

# ───────────────── LEVEL ─────────────────
class Level:
    def __init__(self):
        self.world_w = 240 * TILE
        self.ground_y = 13
        self.solids = []
        self.blocks = []
        self.enemies = []
        self.effects = []
        self.powerups = []

        self.score = 0
        self.coins = 0

        self.mario = MarioPlayer(2 * TILE, 8 * TILE)

        self._powerup_sfx_flash = 0
        self._build_level()

    def _build_level(self):
        # Inspired by a "World 1-1" feel, NOT a 1:1 copy.
        segments = [
            (0, 60),
            (62, 120),
            (122, 180),
            (182, 220),
        ]
        for a, b in segments:
            x = a * TILE
            w = (b - a + 1) * TILE
            y = self.ground_y * TILE
            h = (15 - self.ground_y) * TILE
            self.solids.append(Solid(x, y, w, h, kind="ground"))

        self.blocks.append(QuestionBlock(10, 9, item="coin"))
        self.blocks.append(QuestionBlock(12, 9, item="mushroom"))
        self.blocks.append(BrickBlock(14, 9))

        for i in range(4):
            self.blocks.append(BrickBlock(30 + i, 12 - i))

        self.blocks.append(Pipe(18, ground_ty=self.ground_y, height_tiles=3))

        self.enemies.append(GoombaEnemy(16, 12))
        self.enemies.append(GoombaEnemy(40, 12))
        self.enemies.append(GoombaEnemy(90, 12))

        for b in self.blocks:
            self.solids.append(b)

    def spawn_coin_pop(self, x, y):
        self.effects.append(CoinPop(x, y - 12))

    def spawn_mushroom(self, x, y):
        self.powerups.append(MushroomPower(x, y))

    def update(self, keys):
        self.mario.update(keys, self)

        for e in self.enemies:
            e.update(self)

        for fx in self.effects:
            fx.update()
        self.effects = [fx for fx in self.effects if fx.alive]

        new_powerups = []
        for p in self.powerups:
            res = p.update(self)
            if res != "picked":
                new_powerups.append(p)
        self.powerups = new_powerups

        if self._powerup_sfx_flash > 0:
            self._powerup_sfx_flash -= 1

        if self.mario.dead:
            self.__init__()

    def camera_x(self):
        target = int(self.mario.rect.x - BASE_W * 0.4)
        return max(0, min(target, self.world_w - BASE_W))

    def _draw_background(self, target, cam_x):
        target.fill(SKY)

        for hx in (40, 140, 220, 340, 520, 700):
            x = int((hx - cam_x // 2) % (self.world_w // 2 + BASE_W))
            pygame.draw.circle(target, HILL_GREEN, (x, BASE_H - 48), 36)
            pygame.draw.circle(target, HILL_GREEN, (x + 24, BASE_H - 42), 28)

        for cx in (60, 180, 300, 440, 620):
            x = int((cx - cam_x // 3) % (self.world_w // 3 + BASE_W))
            pygame.draw.circle(target, WHITE, (x, 50), 10)
            pygame.draw.circle(target, WHITE, (x + 12, 46), 12)
            pygame.draw.circle(target, WHITE, (x + 26, 50), 10)
            pygame.draw.rect(target, WHITE, pygame.Rect(x - 10, 50, 46, 10))

    def _draw_ground(self, target, cam_x):
        for s in self.solids:
            if s.kind != "ground":
                continue
            if s.rect.right < cam_x or s.rect.left > cam_x + BASE_W:
                continue

            visible_left = max(s.rect.left, cam_x)
            visible_right = min(s.rect.right, cam_x + BASE_W)

            y = s.rect.y
            tx0 = visible_left // TILE
            tx1 = (visible_right // TILE) + 1

            for tx in range(tx0, tx1):
                target.blit(SPR_GROUND, (tx * TILE - cam_x, y))

            fill_rect = pygame.Rect(visible_left - cam_x, y + TILE, visible_right - visible_left, BASE_H - (y + TILE))
            pygame.draw.rect(target, GROUND_DARK, fill_rect)

    def draw(self, target):
        cam_x = self.camera_x()

        self._draw_background(target, cam_x)
        self._draw_ground(target, cam_x)

        for b in self.blocks:
            if b.rect.right < cam_x or b.rect.left > cam_x + BASE_W:
                continue
            b.draw(target, cam_x)

        for p in self.powerups:
            if p.rect.right < cam_x or p.rect.left > cam_x + BASE_W:
                continue
            p.draw(target, cam_x)

        for e in self.enemies:
            if e.rect.right < cam_x or e.rect.left > cam_x + BASE_W:
                continue
            e.draw(target, cam_x)

        self.mario.draw(target, cam_x)

        font = pygame.font.SysFont("arial", 10, bold=True)
        hud = font.render(f"MARIO {self.score:06d}   COIN x{self.coins:02d}   WORLD 1-1", False, HUD_COLOR)
        target.blit(hud, (8, 8))

        if self._powerup_sfx_flash > 0:
            pygame.draw.rect(target, WHITE, target.get_rect(), 1)

# ───────────────── MAIN LOOP ─────────────────
def main():
    level = Level()

    while True:
        CLOCK.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        level.update(keys)

        level.draw(BASE)

        scaled = pygame.transform.scale(BASE, (SCALED_W, SCALED_H))
        SCREEN.fill(BLACK)
        SCREEN.blit(scaled, (OFFSET_X, OFFSET_Y))
        pygame.display.flip()

if __name__ == "__main__":
    main()
