
"""
Ultra Platformer (Mario-like) - 600x400 prototype

- Main menu + level select (World 1-1 through 8-4)
- Side-scrolling tile platformer core
- HUD (score, coins, world, time, lives)
- Placeholder art only (colored rectangles/circles) — bring your own original assets.

Install:
  pip install pygame

Run:
  python ultra_platformer.py
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

import pygame


# -----------------------------
# Config
# -----------------------------
WIDTH, HEIGHT = 600, 400
FPS = 60
TILE = 16  # pixels per tile
HUD_H = 32  # reserved for HUD drawing (visual only)

GRAVITY = 1400.0
MAX_WALK = 150.0
MAX_RUN = 235.0
ACCEL = 1050.0
FRICTION = 1450.0
JUMP_V = 520.0
MAX_FALL = 900.0

COYOTE_TIME = 0.08
JUMP_BUFFER = 0.10

START_TIME = 400.0  # seconds per level (SMB-style)
LIVES_START = 3


# -----------------------------
# Helpers
# -----------------------------
def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def parse_level_id(level_id: str) -> Tuple[int, int]:
    # Accept formats like "1-1"
    w, l = level_id.split("-")
    return int(w), int(l)


def level_id(world: int, level: int) -> str:
    return f"{world}-{level}"


# -----------------------------
# Level generation & storage
# -----------------------------
TileType = str  # one-character code


@dataclass
class LevelData:
    world: int
    level: int
    width_tiles: int
    height_tiles: int
    tiles: Dict[Tuple[int, int], TileType]         # solid / interactive tiles
    coins: Set[Tuple[int, int]]                    # collectible coins
    enemies: List[Tuple[int, int]]                 # enemy spawn tile coords
    player_start: Tuple[int, int]                  # tile coords
    goal_pos: Tuple[int, int]                      # tile coords


def _put_rect_tiles(tiles: Dict[Tuple[int, int], TileType], x0: int, y0: int, w: int, h: int, t: TileType) -> None:
    for x in range(x0, x0 + w):
        for y in range(y0, y0 + h):
            tiles[(x, y)] = t


def generate_level(world: int, level: int) -> LevelData:
    """
    Generates an original platformer level (NOT Nintendo's layouts).
    Uses deterministic RNG based on world/level.
    """
    rng = random.Random(world * 1000 + level * 17 + 42)

    height_tiles = HEIGHT // TILE
    width_tiles = 220  # ~3520px, gives good scrolling length

    tiles: Dict[Tuple[int, int], TileType] = {}
    coins: Set[Tuple[int, int]] = set()
    enemies: List[Tuple[int, int]] = []

    # Difficulty scaling
    diff = (world - 1) * 0.18 + (level - 1) * 0.06  # 0.. roughly 1.5
    gap_chance = clamp(0.05 + diff * 0.03, 0.05, 0.15)
    enemy_chance = clamp(0.02 + diff * 0.03, 0.02, 0.12)
    block_chance = clamp(0.04 + diff * 0.02, 0.04, 0.10)
    coin_chance = clamp(0.06 + diff * 0.03, 0.06, 0.18)

    ground_y = height_tiles - 2  # two-tile thick ground

    # Base ground with occasional gaps
    x = 0
    while x < width_tiles:
        if x > 10 and x < width_tiles - 10 and rng.random() < gap_chance:
            gap_w = rng.randint(2, 5 if world < 5 else 7)
            x += gap_w
            continue
        tiles[(x, ground_y)] = "#"
        tiles[(x, ground_y + 1)] = "#"
        x += 1

    # Ensure spawn/goal areas are safe ground
    for gx in range(0, 18):
        tiles[(gx, ground_y)] = "#"
        tiles[(gx, ground_y + 1)] = "#"
    for gx in range(width_tiles - 20, width_tiles):
        tiles[(gx, ground_y)] = "#"
        tiles[(gx, ground_y + 1)] = "#"

    # Platforms, blocks, coins, enemies
    for x in range(8, width_tiles - 10):
        # Elevated platforms
        if rng.random() < 0.035 + diff * 0.01:
            plat_y = rng.randint(ground_y - 8, ground_y - 4)
            plat_w = rng.randint(3, 9)
            for px in range(x, min(width_tiles - 1, x + plat_w)):
                tiles[(px, plat_y)] = "B"  # brick/platform
            # Sprinkle coins above platform
            if rng.random() < 0.7:
                for px in range(x, min(width_tiles - 1, x + plat_w)):
                    if rng.random() < 0.35:
                        coins.add((px, plat_y - 1))

        # Floating blocks (bricks and "?" blocks)
        if rng.random() < block_chance:
            by = rng.randint(ground_y - 10, ground_y - 5)
            if rng.random() < 0.35:
                tiles[(x, by)] = "?"
            else:
                tiles[(x, by)] = "B"
            if rng.random() < coin_chance:
                coins.add((x, by - 1))

        # Enemies on the ground (avoid gaps by checking ground tile)
        if x > 12 and rng.random() < enemy_chance and (x, ground_y) in tiles:
            enemies.append((x, ground_y - 1))

        # Occasional coin arcs
        if rng.random() < 0.010 + diff * 0.004:
            arc_len = rng.randint(4, 10)
            base_y = rng.randint(ground_y - 10, ground_y - 6)
            for i in range(arc_len):
                ax = x + i
                if ax >= width_tiles - 5:
                    break
                ay = base_y - int(2.5 * math.sin(i / max(1, arc_len - 1) * math.pi))
                coins.add((ax, ay))

    # Hand-tune "1-1" to be especially friendly
    if world == 1 and level == 1:
        # Clear early section, add a few blocks and coins
        for x in range(0, 35):
            for y in range(0, height_tiles):
                # Remove stray blocks near start
                if tiles.get((x, y)) in {"B", "?"} and y < ground_y - 2:
                    tiles.pop((x, y), None)
        for x in range(18, 28):
            tiles[(x, ground_y - 6)] = "B"
            coins.add((x, ground_y - 7))
        tiles[(30, ground_y - 8)] = "?"
        coins.add((30, ground_y - 9))
        enemies = [e for e in enemies if e[0] > 40]

    # Hand-tune "8-4" to be harder (more vertical variety + enemy density)
    if world == 8 and level == 4:
        for x in range(60, width_tiles - 40, 22):
            # Tall stairs
            step_h = rng.randint(2, 6)
            for i in range(step_h):
                _put_rect_tiles(tiles, x + i, ground_y - i, 1, i + 2, "#")
        # Add extra enemies
        extra = []
        for x in range(30, width_tiles - 30):
            if rng.random() < 0.06 and (x, ground_y) in tiles:
                extra.append((x, ground_y - 1))
        enemies.extend(extra)

    player_start = (3, ground_y - 2)
    goal_pos = (width_tiles - 6, ground_y - 6)

    # Goal tower
    for y in range(goal_pos[1], ground_y + 1):
        tiles[(goal_pos[0], y)] = "#"

    return LevelData(
        world=world,
        level=level,
        width_tiles=width_tiles,
        height_tiles=height_tiles,
        tiles=tiles,
        coins=coins,
        enemies=enemies,
        player_start=player_start,
        goal_pos=goal_pos,
    )


# -----------------------------
# Game objects
# -----------------------------
@dataclass
class Enemy:
    rect: pygame.Rect
    vx: float = -60.0
    alive: bool = True

    def update(self, dt: float, level: "Level") -> None:
        if not self.alive:
            return
        # Move
        self.rect.x += int(self.vx * dt)
        # Wall collision
        for tile_rect, _ in level.iter_near_solid_tiles(self.rect):
            if self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.rect.right = tile_rect.left
                else:
                    self.rect.left = tile_rect.right
                self.vx *= -1
                break

        # Gravity
        self.rect.y += int(level.enemy_gravity * dt)
        # Floor collision
        for tile_rect, _ in level.iter_near_solid_tiles(self.rect):
            if self.rect.colliderect(tile_rect):
                self.rect.bottom = tile_rect.top
                break

        # Edge detection: if no tile ahead, turn around
        foot_y = self.rect.bottom + 1
        ahead_x = self.rect.centerx + (8 if self.vx > 0 else -8)
        tx = ahead_x // TILE
        ty = foot_y // TILE
        if (tx, ty) not in level.tiles:
            self.vx *= -1

    def draw(self, surf: pygame.Surface, cam_x: int) -> None:
        if not self.alive:
            return
        pygame.draw.rect(surf, (200, 60, 60), self.rect.move(-cam_x, 0))


class Player:
    def __init__(self, x: int, y: int):
        self.is_big = False
        self.rect = pygame.Rect(x, y, 12, 14)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.coyote = 0.0
        self.jump_buf = 0.0
        self.facing = 1
        self.invuln = 0.0  # seconds
        self._jump_held_prev = False

    def set_big(self, big: bool) -> None:
        if big == self.is_big:
            return
        # Adjust rect height while keeping feet planted
        bottom = self.rect.bottom
        self.is_big = big
        if self.is_big:
            self.rect.height = 24
        else:
            self.rect.height = 14
        self.rect.bottom = bottom

    def hurt(self) -> bool:
        """
        Returns True if player died, False if survived.
        """
        if self.invuln > 0:
            return False
        if self.is_big:
            self.set_big(False)
            self.invuln = 1.2
            return False
        return True

    def update(self, dt: float, keys: pygame.key.ScancodeWrapper, level: "Level") -> None:
        # Timers
        if self.invuln > 0:
            self.invuln = max(0.0, self.invuln - dt)

        # Input
        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1

        run = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        max_speed = MAX_RUN if run else MAX_WALK

        if move != 0:
            self.facing = move
            self.vx += move * ACCEL * dt
        else:
            # Friction
            if self.vx > 0:
                self.vx = max(0.0, self.vx - FRICTION * dt)
            elif self.vx < 0:
                self.vx = min(0.0, self.vx + FRICTION * dt)

        self.vx = clamp(self.vx, -max_speed, max_speed)

        # Jump buffering / coyote time
        jump_held = keys[pygame.K_SPACE] or keys[pygame.K_z]
        jump_pressed = jump_held and not self._jump_held_prev
        jump_released = (not jump_held) and self._jump_held_prev
        self._jump_held_prev = jump_held

        if jump_pressed:
            self.jump_buf = JUMP_BUFFER
        else:
            self.jump_buf = max(0.0, self.jump_buf - dt)

        if self.on_ground:
            self.coyote = COYOTE_TIME
        else:
            self.coyote = max(0.0, self.coyote - dt)

        if self.jump_buf > 0 and self.coyote > 0:
            self.vy = -JUMP_V
            self.on_ground = False
            self.coyote = 0.0
            self.jump_buf = 0.0

        # Variable jump height
        if jump_released and self.vy < -160:
            self.vy = -160

        # Gravity
        self.vy = min(MAX_FALL, self.vy + GRAVITY * dt)

        # --- Movement & collision (X) ---
        self.rect.x += int(self.vx * dt)
        for tile_rect, tile_type in level.iter_near_solid_tiles(self.rect):
            if self.rect.colliderect(tile_rect):
                if self.vx > 0:
                    self.rect.right = tile_rect.left
                elif self.vx < 0:
                    self.rect.left = tile_rect.right
                self.vx = 0.0

        # --- Movement & collision (Y) ---
        self.rect.y += int(self.vy * dt)
        self.on_ground = False

        # We'll track if we hit a tile from below this frame
        hit_from_below: Optional[Tuple[int, int]] = None
        for tile_rect, tile_type in level.iter_near_solid_tiles(self.rect):
            if self.rect.colliderect(tile_rect):
                if self.vy > 0:
                    self.rect.bottom = tile_rect.top
                    self.vy = 0.0
                    self.on_ground = True
                elif self.vy < 0:
                    self.rect.top = tile_rect.bottom
                    self.vy = 0.0
                    # Identify tile coord hit
                    tx = tile_rect.x // TILE
                    ty = tile_rect.y // TILE
                    hit_from_below = (tx, ty)

        if hit_from_below is not None:
            level.bump_tile(*hit_from_below, player=self)

        # Collect coins

    def draw(self, surf: pygame.Surface, cam_x: int) -> None:
        # Blink when invulnerable
        if self.invuln > 0:
            if int(self.invuln * 10) % 2 == 0:
                return
        pygame.draw.rect(surf, (70, 70, 220), self.rect.move(-cam_x, 0))


class Level:
    def __init__(self, data: LevelData):
        self.data = data
        self.tiles = data.tiles  # solid & interactive tile dict
        self.coins = set(data.coins)  # mutable copy
        self.width_tiles = data.width_tiles
        self.height_tiles = data.height_tiles
        self.enemy_gravity = 700.0

        # Spawn
        psx, psy = data.player_start
        self.player_spawn_px = (psx * TILE + 2, psy * TILE)
        self.goal_rect = pygame.Rect(data.goal_pos[0] * TILE, data.goal_pos[1] * TILE, TILE, (HEIGHT // TILE - data.goal_pos[1]) * TILE)

        # Create enemies
        self.enemies: List[Enemy] = []
        for ex, ey in data.enemies:
            r = pygame.Rect(ex * TILE, ey * TILE, 14, 14)
            self.enemies.append(Enemy(r))

    def world_size_px(self) -> int:
        return self.width_tiles * TILE

    def iter_near_solid_tiles(self, rect: pygame.Rect):
        # Check tiles in the neighborhood of rect to keep collision fast
        left = (rect.left // TILE) - 1
        right = (rect.right // TILE) + 1
        top = (rect.top // TILE) - 1
        bottom = (rect.bottom // TILE) + 1
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                t = self.tiles.get((tx, ty))
                if t is None:
                    continue
                # Solid types (spent '?' becomes 'b' but still solid)
                if t in {"#", "B", "?", "b"}:
                    yield pygame.Rect(tx * TILE, ty * TILE, TILE, TILE), t

    def bump_tile(self, tx: int, ty: int, player: Player) -> None:
        t = self.tiles.get((tx, ty))
        if t is None:
            return
        if t == "?":
            # Spawn a coin (one-time) and mark as spent
            self.tiles[(tx, ty)] = "b"
            self.coins.add((tx, ty - 1))
        elif t == "B":
            # Break brick if big; otherwise just bonk
            if player.is_big:
                self.tiles.pop((tx, ty), None)

    def collect_coins(self, player: Player) -> int:
        collected = 0
        # Only check coins near player
        left = (player.rect.left // TILE) - 1
        right = (player.rect.right // TILE) + 1
        top = (player.rect.top // TILE) - 2
        bottom = (player.rect.bottom // TILE) + 2
        to_remove = []
        for (cx, cy) in self.coins:
            if cx < left or cx > right or cy < top or cy > bottom:
                continue
            coin_rect = pygame.Rect(cx * TILE + 4, cy * TILE + 4, TILE - 8, TILE - 8)
            if player.rect.colliderect(coin_rect):
                to_remove.append((cx, cy))
                collected += 1
        for c in to_remove:
            self.coins.discard(c)
        return collected

    def update_enemies(self, dt: float) -> None:
        for e in self.enemies:
            e.update(dt, self)

    def draw(self, surf: pygame.Surface, cam_x: int) -> None:
        # Tiles
        start_tx = max(0, cam_x // TILE - 2)
        end_tx = min(self.width_tiles, (cam_x + WIDTH) // TILE + 3)
        for ty in range(0, self.height_tiles):
            for tx in range(start_tx, end_tx):
                t = self.tiles.get((tx, ty))
                if t is None:
                    continue
                r = pygame.Rect(tx * TILE - cam_x, ty * TILE, TILE, TILE)
                if t == "#":
                    pygame.draw.rect(surf, (120, 70, 20), r)
                elif t == "B":
                    pygame.draw.rect(surf, (170, 110, 50), r)
                    pygame.draw.rect(surf, (140, 80, 30), r, 1)
                elif t == "?":
                    pygame.draw.rect(surf, (220, 190, 40), r)
                    pygame.draw.rect(surf, (120, 90, 10), r, 1)
                elif t == "b":
                    pygame.draw.rect(surf, (130, 130, 130), r)
                    pygame.draw.rect(surf, (90, 90, 90), r, 1)

        # Coins
        for (cx, cy) in self.coins:
            x = cx * TILE - cam_x + TILE // 2
            y = cy * TILE + TILE // 2
            pygame.draw.circle(surf, (240, 220, 90), (x, y), 5)

        # Goal (flag pole / tower placeholder)
        pygame.draw.rect(surf, (60, 200, 80), self.goal_rect.move(-cam_x, 0), 2)

        # Enemies
        for e in self.enemies:
            e.draw(surf, cam_x)


# -----------------------------
# Game state machine
# -----------------------------
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Ultra Platformer (Original Template)")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 22)
        self.font_big = pygame.font.Font(None, 44)

        self.state = "menu"  # menu, select, play, gameover, pause
        self.menu_idx = 0
        self.menu_items = ["Start", "Level Select", "Quit"]

        self.sel_world = 1
        self.sel_level = 1

        self.level: Optional[Level] = None
        self.player: Optional[Player] = None
        self.cam_x = 0

        self.score = 0
        self.coin_count = 0
        self.lives = LIVES_START
        self.time_left = START_TIME

        # For coin collection tracking each frame
        self._prev_coin_count = 0

    # ---------- Flow ----------
    def reset_run(self) -> None:
        self.score = 0
        self.coin_count = 0
        self.lives = LIVES_START
        self.load_level(self.sel_world, self.sel_level)

    def load_level(self, world: int, level: int) -> None:
        data = generate_level(world, level)
        self.level = Level(data)
        self.player = Player(*self.level.player_spawn_px)
        self.cam_x = 0
        self.time_left = START_TIME

    def next_level(self) -> None:
        w, l = self.sel_world, self.sel_level
        l += 1
        if l > 4:
            w += 1
            l = 1
        if w > 8:
            # Finished all levels
            self.state = "gameover"
            return
        self.sel_world, self.sel_level = w, l
        self.load_level(w, l)

    def respawn_or_gameover(self) -> None:
        self.lives -= 1
        if self.lives <= 0:
            self.state = "gameover"
            return
        # Respawn on same level
        self.load_level(self.sel_world, self.sel_level)

    # ---------- Update ----------
    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()

        if self.state == "menu":
            self.update_menu()
        elif self.state == "select":
            self.update_select()
        elif self.state == "play":
            if keys[pygame.K_ESCAPE]:
                self.state = "pause"
                return
            self.update_play(dt, keys)
        elif self.state == "pause":
            if keys[pygame.K_ESCAPE]:
                self.state = "play"
            # no gameplay update
        elif self.state == "gameover":
            self.update_gameover()

    def update_menu(self) -> None:
        for event in pygame.event.get([pygame.KEYDOWN, pygame.QUIT]):
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.menu_idx = (self.menu_idx - 1) % len(self.menu_items)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.menu_idx = (self.menu_idx + 1) % len(self.menu_items)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = self.menu_items[self.menu_idx]
                    if choice == "Start":
                        self.reset_run()
                        self.state = "play"
                    elif choice == "Level Select":
                        self.state = "select"
                    elif choice == "Quit":
                        raise SystemExit

    def update_select(self) -> None:
        for event in pygame.event.get([pygame.KEYDOWN, pygame.QUIT]):
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    self.state = "menu"
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.sel_level = 4 if self.sel_level == 1 else self.sel_level - 1
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.sel_level = 1 if self.sel_level == 4 else self.sel_level + 1
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.sel_world = 8 if self.sel_world == 1 else self.sel_world - 1
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel_world = 1 if self.sel_world == 8 else self.sel_world + 1
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset_run()
                    self.state = "play"

    def update_play(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        assert self.level is not None and self.player is not None

        # Consume QUIT / KEYDOWN events we didn't handle via get_pressed
        for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    # quick return to menu
                    self.state = "menu"

        # Timer
        self.time_left = max(0.0, self.time_left - dt)
        if self.time_left <= 0.0:
            self.respawn_or_gameover()
            return

        # Player update
        self.player.update(dt, keys, self.level)

        # Enemy update
        self.level.update_enemies(dt)

        # Coin collection accounting (based on delta)
        collected_now = 0
        # Use collect_coins return only for deltas? We already collect in player.update,
        # so infer by scanning near and comparing is hard. We'll do this: detect coins by overlap each frame in Level.collect_coins
        # and update counts inside that function is not stored. To keep simple: rerun collect_coins and rely on it removing coins.
        collected_now = self.level.collect_coins(self.player)
        if collected_now:
            self.coin_count += collected_now
            self.score += collected_now * 100

        # Enemy interactions
        for e in self.level.enemies:
            if not e.alive:
                continue
            if self.player.rect.colliderect(e.rect):
                # Determine if stomp (coming from above)
                if self.player.vy > 0 and (self.player.rect.bottom - e.rect.top) <= 10:
                    e.alive = False
                    self.player.vy = -JUMP_V * 0.55
                    self.score += 200
                else:
                    died = self.player.hurt()
                    if died:
                        self.respawn_or_gameover()
                        return

        # Goal reached
        if self.player.rect.colliderect(self.level.goal_rect):
            self.score += int(self.time_left) * 10
            self.next_level()
            return

        # Fall off world
        if self.player.rect.top > HEIGHT + 120:
            self.respawn_or_gameover()
            return

        # Camera follows
        target = self.player.rect.centerx - WIDTH // 2
        self.cam_x = int(clamp(target, 0, self.level.world_size_px() - WIDTH))

    def update_gameover(self) -> None:
        for event in pygame.event.get([pygame.KEYDOWN, pygame.QUIT]):
            if event.type == pygame.QUIT:
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                self.state = "menu"

    # ---------- Draw ----------
    def draw(self) -> None:
        self.screen.fill((105, 170, 255))  # sky

        if self.state in {"play", "pause"}:
            assert self.level is not None and self.player is not None
            self.level.draw(self.screen, self.cam_x)
            self.player.draw(self.screen, self.cam_x)
            self.draw_hud()

            if self.state == "pause":
                self.draw_center_text("PAUSED", self.font_big, y=HEIGHT // 2 - 20)
                self.draw_center_text("Press ESC to resume", self.font, y=HEIGHT // 2 + 20)

        elif self.state == "menu":
            self.draw_center_text("ULTRA PLATFORMER", self.font_big, y=90)
            self.draw_center_text("(original template)", self.font, y=125)

            for i, item in enumerate(self.menu_items):
                prefix = "> " if i == self.menu_idx else "  "
                text = self.font.render(prefix + item, True, (15, 15, 25))
                self.screen.blit(text, (WIDTH // 2 - 90, 190 + i * 28))

            hint = self.font.render("Arrows/WASD + Enter", True, (15, 15, 25))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 320))

        elif self.state == "select":
            self.draw_center_text("LEVEL SELECT", self.font_big, y=70)
            sel = f"World {self.sel_world}  Level {self.sel_level}   ({self.sel_world}-{self.sel_level})"
            self.draw_center_text(sel, self.font, y=125)
            self.draw_center_text("←/→ change level  •  ↑/↓ change world", self.font, y=190)
            self.draw_center_text("Enter to start  •  Esc to go back", self.font, y=220)

        elif self.state == "gameover":
            self.draw_center_text("GAME OVER", self.font_big, y=140)
            msg = f"Score: {self.score}   Coins: {self.coin_count}"
            self.draw_center_text(msg, self.font, y=190)
            self.draw_center_text("Press any key to return to menu", self.font, y=235)

        pygame.display.flip()

    def draw_hud(self) -> None:
        # Simple SMB-like HUD layout
        w, l = self.sel_world, self.sel_level
        world_txt = f"WORLD {w}-{l}"
        time_txt = f"TIME {int(self.time_left):03d}"
        score_txt = f"SCORE {self.score:06d}"
        coin_txt = f"COINS {self.coin_count:03d}"
        lives_txt = f"LIVES {self.lives}"

        texts = [score_txt, coin_txt, world_txt, time_txt, lives_txt]
        x = 8
        y = 6
        for t in texts:
            s = self.font.render(t, True, (15, 15, 25))
            self.screen.blit(s, (x, y))
            x += s.get_width() + 14

    def draw_center_text(self, txt: str, font: pygame.font.Font, y: int) -> None:
        s = font.render(txt, True, (15, 15, 25))
        self.screen.blit(s, (WIDTH // 2 - s.get_width() // 2, y))

    # ---------- Run ----------
    def run(self) -> None:
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
