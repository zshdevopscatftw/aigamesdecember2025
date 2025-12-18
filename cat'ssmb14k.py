#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS
© Samsoft 2025
A retro-style platformer built with Tkinter
"""

import tkinter as tk
import math
import random
import time

# === CONSTANTS ===
WIDTH, HEIGHT = 800, 600
TILE = 32
FPS = 60
GRAVITY = 0.6
JUMP_FORCE = -12
MOVE_SPEED = 4
RUN_SPEED = 7

# Colors (NES-style palette)
COL_SKY = "#5C94FC"
COL_GROUND = "#C84C0C"
COL_BRICK = "#D07030"
COL_BLOCK = "#FAC000"
COL_PIPE = "#00A800"
COL_PLAYER = "#E44040"
COL_PLAYER2 = "#00A800"
COL_ENEMY = "#D8A068"
COL_COIN = "#FAC000"
COL_CLOUD = "#FCFCFC"
COL_BUSH = "#00A800"
COL_BLACK = "#000000"
COL_WHITE = "#FCFCFC"

# === GAME STATE ===
class GameState:
    TITLE = 0
    PLAYING = 1
    GAMEOVER = 2
    WIN = 3
    PAUSED = 4

# === PLAYER CLASS ===
class Player:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.w, self.h = 24, 32
        self.on_ground = False
        self.facing = 1
        self.big = False
        self.fire = False
        self.invincible = 0
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.dead = False
        self.death_timer = 0
        self.frame = 0

    def update(self, keys, level):
        if self.dead:
            self.death_timer += 1
            self.vy += 0.3
            self.y += self.vy
            return

        # Horizontal movement
        speed = RUN_SPEED if keys.get('shift') else MOVE_SPEED
        if keys.get('left'):
            self.vx = -speed
            self.facing = -1
        elif keys.get('right'):
            self.vx = speed
            self.facing = 1
        else:
            self.vx *= 0.8
            if abs(self.vx) < 0.5: self.vx = 0

        # Jump
        if keys.get('space') and self.on_ground:
            self.vy = JUMP_FORCE - (2 if keys.get('shift') else 0)
            self.on_ground = False

        # Gravity
        self.vy += GRAVITY
        if self.vy > 12: self.vy = 12

        # Move X
        self.x += self.vx
        self.resolve_collision_x(level)

        # Move Y
        self.y += self.vy
        self.on_ground = False
        self.resolve_collision_y(level)

        # Screen bounds
        if self.x < 0: self.x = 0
        if self.y > HEIGHT + 100:
            self.die()

        # Animation
        self.frame += 0.2 if abs(self.vx) > 1 else 0
        if self.invincible > 0: self.invincible -= 1

    def resolve_collision_x(self, level):
        for tile in level.get_solid_tiles():
            if self.collides(tile):
                if self.vx > 0: self.x = tile[0] - self.w
                elif self.vx < 0: self.x = tile[0] + TILE
                self.vx = 0

    def resolve_collision_y(self, level):
        for tile in level.get_solid_tiles():
            if self.collides(tile):
                if self.vy > 0:
                    self.y = tile[1] - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.y = tile[1] + TILE
                    self.vy = 0
                    level.hit_block(tile[0]//TILE, tile[1]//TILE, self)

    def collides(self, tile):
        return (self.x < tile[0] + TILE and self.x + self.w > tile[0] and
                self.y < tile[1] + TILE and self.y + self.h > tile[1])

    def die(self):
        if self.invincible > 0: return
        if self.big:
            self.big = False
            self.fire = False
            self.h = 32
            self.invincible = 120
        else:
            self.dead = True
            self.vy = -10
            self.lives -= 1

    def draw(self, canvas, cam_x):
        if self.invincible > 0 and self.invincible % 10 < 5: return
        x = self.x - cam_x
        y = self.y
        h = 48 if self.big else 32
        # Body
        color = COL_PLAYER
        canvas.create_rectangle(x+4, y+h-24, x+20, y+h, fill=color, outline="")
        # Head
        canvas.create_oval(x+2, y, x+22, y+20, fill="#FFB8A0", outline="")
        # Cap
        canvas.create_rectangle(x, y+2, x+24, y+10, fill=color, outline="")
        # Eye
        ex = x + 16 if self.facing > 0 else x + 6
        canvas.create_oval(ex, y+8, ex+4, y+14, fill=COL_BLACK, outline="")
        # Mustache
        canvas.create_rectangle(x+8, y+14, x+18, y+17, fill="#4C2800", outline="")

# === ENEMY CLASS ===
class Enemy:
    def __init__(self, x, y, etype="goomba"):
        self.x, self.y = x, y
        self.vx = -1
        self.vy = 0
        self.w, self.h = 28, 28
        self.etype = etype
        self.active = True
        self.stomped = False
        self.stomp_timer = 0
        self.frame = 0

    def update(self, level):
        if not self.active: return
        if self.stomped:
            self.stomp_timer += 1
            if self.stomp_timer > 30: self.active = False
            return

        self.vy += GRAVITY * 0.5
        self.y += self.vy
        self.x += self.vx

        # Simple ground collision
        for tile in level.get_solid_tiles():
            if (self.x < tile[0] + TILE and self.x + self.w > tile[0] and
                self.y < tile[1] + TILE and self.y + self.h > tile[1]):
                if self.vy > 0:
                    self.y = tile[1] - self.h
                    self.vy = 0
                elif self.vx != 0:
                    self.vx *= -1

        self.frame += 0.1
        if self.y > HEIGHT + 50: self.active = False

    def draw(self, canvas, cam_x):
        if not self.active: return
        x = self.x - cam_x
        if x < -50 or x > WIDTH + 50: return
        y = self.y
        if self.stomped:
            canvas.create_oval(x, y+20, x+28, y+28, fill=COL_ENEMY, outline="#4C2800")
        else:
            # Body
            canvas.create_oval(x, y+8, x+28, y+28, fill=COL_ENEMY, outline="#4C2800")
            # Feet animation
            f = int(self.frame) % 2
            canvas.create_oval(x+2+f*4, y+22, x+12+f*4, y+30, fill="#4C2800", outline="")
            canvas.create_oval(x+14-f*4, y+22, x+24-f*4, y+30, fill="#4C2800", outline="")
            # Eyes
            canvas.create_oval(x+6, y+10, x+12, y+18, fill=COL_WHITE, outline="")
            canvas.create_oval(x+16, y+10, x+22, y+18, fill=COL_WHITE, outline="")
            canvas.create_oval(x+8, y+12, x+11, y+17, fill=COL_BLACK, outline="")
            canvas.create_oval(x+18, y+12, x+21, y+17, fill=COL_BLACK, outline="")

# === COIN CLASS ===
class Coin:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.collected = False
        self.frame = 0

    def draw(self, canvas, cam_x):
        if self.collected: return
        x = self.x - cam_x
        if x < -20 or x > WIDTH + 20: return
        f = abs(math.sin(self.frame * 0.15)) * 8
        canvas.create_oval(x+8-f/2, self.y+4, x+24+f/2, self.y+28, fill=COL_COIN, outline="#D08000")
        self.frame += 1

# === LEVEL CLASS ===
class Level:
    def __init__(self, world, stage):
        self.world = world
        self.stage = stage
        self.width = 200
        self.tiles = {}
        self.enemies = []
        self.coins = []
        self.generate()

    def generate(self):
        # Ground
        for x in range(self.width):
            if random.random() > 0.05 or x < 10:
                self.tiles[(x, 17)] = 'G'
                self.tiles[(x, 18)] = 'G'

        # Platforms and blocks
        for i in range(self.width // 15):
            px = 10 + i * 15 + random.randint(-3, 3)
            py = random.randint(10, 14)
            plen = random.randint(3, 7)
            for j in range(plen):
                t = random.choice(['B', 'Q', 'B', 'B'])
                self.tiles[(px+j, py)] = t
                if t == 'Q': self.coins.append(Coin((px+j)*TILE+2, py*TILE-28))

        # Pipes
        for i in range(self.width // 25):
            px = 20 + i * 25 + random.randint(0, 10)
            ph = random.randint(2, 4)
            for py in range(17-ph, 17):
                self.tiles[(px, py)] = 'P'
                self.tiles[(px+1, py)] = 'P'

        # Enemies
        for i in range(self.width // 12):
            ex = 15 + i * 12 + random.randint(0, 5)
            self.enemies.append(Enemy(ex * TILE, 15 * TILE))

        # Coins in air
        for i in range(self.width // 8):
            cx = 8 + i * 8 + random.randint(0, 4)
            cy = random.randint(8, 14)
            self.coins.append(Coin(cx * TILE, cy * TILE))

        # Flag at end
        self.flag_x = (self.width - 5) * TILE

    def get_solid_tiles(self):
        result = []
        for (tx, ty), t in self.tiles.items():
            if t in ['G', 'B', 'Q', 'P', 'S']:
                result.append((tx * TILE, ty * TILE))
        return result

    def hit_block(self, tx, ty, player):
        t = self.tiles.get((tx, ty))
        if t == 'Q':
            self.tiles[(tx, ty)] = 'S'
            player.coins += 1
            player.score += 200

    def draw(self, canvas, cam_x):
        # Sky
        canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=COL_SKY, outline="")

        # Clouds
        for i in range(10):
            cx = (i * 200 - cam_x * 0.3) % (WIDTH + 200) - 100
            canvas.create_oval(cx, 50 + i*20%80, cx+80, 90 + i*20%80, fill=COL_CLOUD, outline="")

        # Bushes
        for i in range(15):
            bx = (i * 150 - cam_x * 0.8) % (WIDTH + 200) - 100
            canvas.create_oval(bx, HEIGHT-100, bx+100, HEIGHT-40, fill=COL_BUSH, outline="")

        # Tiles
        for (tx, ty), t in self.tiles.items():
            x = tx * TILE - cam_x
            y = ty * TILE
            if x < -TILE or x > WIDTH + TILE: continue

            if t == 'G':
                canvas.create_rectangle(x, y, x+TILE, y+TILE, fill=COL_GROUND, outline="#802800")
            elif t == 'B':
                canvas.create_rectangle(x, y, x+TILE, y+TILE, fill=COL_BRICK, outline="#802800")
                canvas.create_line(x, y+TILE//2, x+TILE, y+TILE//2, fill="#802800")
                canvas.create_line(x+TILE//2, y, x+TILE//2, y+TILE, fill="#802800")
            elif t == 'Q':
                canvas.create_rectangle(x, y, x+TILE, y+TILE, fill=COL_BLOCK, outline="#806000")
                canvas.create_text(x+TILE//2, y+TILE//2, text="?", fill=COL_WHITE, font=("Arial", 16, "bold"))
            elif t == 'S':
                canvas.create_rectangle(x, y, x+TILE, y+TILE, fill="#808080", outline="#404040")
            elif t == 'P':
                canvas.create_rectangle(x, y, x+TILE, y+TILE, fill=COL_PIPE, outline="#006000")

        # Flag
        fx = self.flag_x - cam_x
        canvas.create_rectangle(fx+14, 100, fx+18, HEIGHT-64, fill="#808080", outline="")
        canvas.create_polygon(fx+18, 100, fx+18, 150, fx+60, 125, fill="#00C000", outline="")

        # Coins
        for c in self.coins: c.draw(canvas, cam_x)

        # Enemies
        for e in self.enemies: e.draw(canvas, cam_x)

# === MAIN GAME CLASS ===
class UltraMario2DBros:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ULTRA MARIO 2D BROS - © Samsoft 2025")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=COL_SKY, highlightthickness=0)
        self.canvas.pack()

        self.state = GameState.TITLE
        self.world, self.stage = 1, 1
        self.player = None
        self.level = None
        self.cam_x = 0
        self.timer = 400
        self.keys = {}

        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

        self.title_frame = 0
        self.game_loop()
        self.root.mainloop()

    def key_down(self, e):
        k = e.keysym.lower()
        if k in ['left', 'right', 'up', 'down']: self.keys[k] = True
        if k == 'space': self.keys['space'] = True
        if k in ['shift_l', 'shift_r', 'shift']: self.keys['shift'] = True
        if k == 'return':
            if self.state == GameState.TITLE:
                self.start_game()
            elif self.state == GameState.GAMEOVER:
                self.state = GameState.TITLE

    def key_up(self, e):
        k = e.keysym.lower()
        if k in ['left', 'right', 'up', 'down']: self.keys[k] = False
        if k == 'space': self.keys['space'] = False
        if k in ['shift_l', 'shift_r', 'shift']: self.keys['shift'] = False

    def start_game(self):
        self.state = GameState.PLAYING
        self.world, self.stage = 1, 1
        self.player = Player(100, 400)
        self.level = Level(self.world, self.stage)
        self.cam_x = 0
        self.timer = 400

    def next_level(self):
        self.stage += 1
        if self.stage > 4:
            self.stage = 1
            self.world += 1
        if self.world > 8:
            self.state = GameState.WIN
            return
        self.level = Level(self.world, self.stage)
        self.player.x, self.player.y = 100, 400
        self.cam_x = 0
        self.timer = 400

    def update(self):
        if self.state != GameState.PLAYING: return

        self.player.update(self.keys, self.level)

        # Camera
        target_cam = self.player.x - WIDTH // 3
        self.cam_x += (target_cam - self.cam_x) * 0.1
        if self.cam_x < 0: self.cam_x = 0

        # Enemies
        for e in self.level.enemies:
            e.update(self.level)
            if e.active and not e.stomped and not self.player.dead:
                if (self.player.x < e.x + e.w and self.player.x + self.player.w > e.x and
                    self.player.y < e.y + e.h and self.player.y + self.player.h > e.y):
                    if self.player.vy > 0 and self.player.y + self.player.h < e.y + e.h//2:
                        e.stomped = True
                        self.player.vy = -8
                        self.player.score += 100
                    else:
                        self.player.die()

        # Coins
        for c in self.level.coins:
            if not c.collected:
                if (self.player.x < c.x + 20 and self.player.x + self.player.w > c.x and
                    self.player.y < c.y + 24 and self.player.y + self.player.h > c.y):
                    c.collected = True
                    self.player.coins += 1
                    self.player.score += 100

        # Flag
        if self.player.x > self.level.flag_x:
            self.player.score += self.timer * 50
            self.next_level()

        # Timer
        self.timer -= 1/FPS
        if self.timer <= 0:
            self.player.die()

        # Death
        if self.player.dead and self.player.death_timer > 120:
            if self.player.lives <= 0:
                self.state = GameState.GAMEOVER
            else:
                self.player = Player(100, 400)
                self.cam_x = 0
                self.timer = 400

    def draw(self):
        self.canvas.delete("all")

        if self.state == GameState.TITLE:
            self.draw_title()
        elif self.state == GameState.PLAYING:
            self.level.draw(self.canvas, self.cam_x)
            self.player.draw(self.canvas, self.cam_x)
            self.draw_hud()
        elif self.state == GameState.GAMEOVER:
            self.draw_gameover()
        elif self.state == GameState.WIN:
            self.draw_win()

    def draw_title(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=COL_BLACK, outline="")
        self.title_frame += 1

        # Title with animation
        y_off = math.sin(self.title_frame * 0.05) * 10
        self.canvas.create_text(WIDTH//2, 150 + y_off, text="ULTRA MARIO 2D BROS",
                                fill=COL_WHITE, font=("Arial", 48, "bold"))
        self.canvas.create_text(WIDTH//2, 220, text="© Samsoft 2025",
                                fill="#808080", font=("Arial", 18))

        # Animated ground
        for i in range(WIDTH//TILE + 1):
            self.canvas.create_rectangle(i*TILE, HEIGHT-64, i*TILE+TILE, HEIGHT,
                                         fill=COL_GROUND, outline="#802800")

        # Player preview
        px = WIDTH//2 - 12
        py = HEIGHT - 96
        self.canvas.create_rectangle(px+4, py+8, px+20, py+32, fill=COL_PLAYER, outline="")
        self.canvas.create_oval(px+2, py, px+22, py+20, fill="#FFB8A0", outline="")
        self.canvas.create_rectangle(px, py+2, px+24, py+10, fill=COL_PLAYER, outline="")

        # Press start
        if self.title_frame % 60 < 40:
            self.canvas.create_text(WIDTH//2, 400, text="PRESS ENTER TO START",
                                    fill=COL_WHITE, font=("Arial", 24))

        # Controls
        self.canvas.create_text(WIDTH//2, 500, text="ARROWS: Move  |  SPACE: Jump  |  SHIFT: Run",
                                fill="#606060", font=("Arial", 14))

    def draw_hud(self):
        # Score
        self.canvas.create_text(80, 30, text=f"SCORE\n{self.player.score:06d}",
                                fill=COL_WHITE, font=("Arial", 14, "bold"))
        # Coins
        self.canvas.create_text(250, 30, text=f"COINS\n×{self.player.coins:02d}",
                                fill=COL_WHITE, font=("Arial", 14, "bold"))
        # World
        self.canvas.create_text(450, 30, text=f"WORLD\n{self.world}-{self.stage}",
                                fill=COL_WHITE, font=("Arial", 14, "bold"))
        # Time
        self.canvas.create_text(650, 30, text=f"TIME\n{int(self.timer):03d}",
                                fill=COL_WHITE, font=("Arial", 14, "bold"))
        # Lives
        self.canvas.create_text(750, 30, text=f"LIVES\n×{self.player.lives}",
                                fill=COL_WHITE, font=("Arial", 14, "bold"))

    def draw_gameover(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=COL_BLACK, outline="")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 - 50, text="GAME OVER",
                                fill=COL_WHITE, font=("Arial", 48, "bold"))
        self.canvas.create_text(WIDTH//2, HEIGHT//2 + 50, text="PRESS ENTER",
                                fill="#808080", font=("Arial", 24))

    def draw_win(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=COL_BLACK, outline="")
        self.canvas.create_text(WIDTH//2, HEIGHT//2 - 50, text="CONGRATULATIONS!",
                                fill=COL_COIN, font=("Arial", 48, "bold"))
        self.canvas.create_text(WIDTH//2, HEIGHT//2 + 20, text="YOU SAVED THE KINGDOM!",
                                fill=COL_WHITE, font=("Arial", 24))
        self.canvas.create_text(WIDTH//2, HEIGHT//2 + 80, text=f"FINAL SCORE: {self.player.score}",
                                fill=COL_WHITE, font=("Arial", 20))

    def game_loop(self):
        self.update()
        self.draw()
        self.root.after(1000 // FPS, self.game_loop)

if __name__ == "__main__":
    UltraMario2DBros()

