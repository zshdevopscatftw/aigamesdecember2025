#!/usr/bin/env python3
# ============================================================
# ULTRA MARIO 2D BROS.
# NES-STYLE MAIN MENU — TKINTER
# Pure SMB1 vibe • No parody • No extras • One file
# Extended to SMB3 engine with basic World 1-1
# ============================================================

import tkinter as tk
import math  # for sign

def sign(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)

# ============================================================
# CONFIG
# ============================================================
WIDTH, HEIGHT = 512, 448   # NES 256x224 ×2
BG = "black"
WHITE = "#f8f8f8"
RED = "#d82800"
SKY_BLUE = "#5c94fc"  # SMB3 sky
GROUND_GREEN = "#00a800"
BLOCK_BROWN = "#c84c0c"
GOOMBA_BROWN = "#a80020"
KOOPA_GREEN = "#00d800"

# Physics constants from research (approximated and scaled x2 for canvas)
WALK_MAX = 36  # 18 * 2
RUN_MAX = 56   # 28 * 2
FLIGHT_MAX = 76  # 38 * 2 (not implemented)
ACCEL = 2      # Scaled 1 per frame
FRICTION = 2
JUMP_BASE = -80
JUMP_OFFSET = 4  # Scaled offsets [0,4,8,16]
GRAV_LOW = 2   # 1 * 2 when holding jump
GRAV_HIGH = 10 # 5 * 2 normal
MAX_FALL = 90  # 45 * 2

# ============================================================
# APP
# ============================================================
class SMB3Game:
    def __init__(self, root):
        self.root = root
        self.root.title("ULTRA MARIO 2D BROS.")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.pack()

        self.state = "menu"
        self.selection = 0
        self.options = ["1 PLAYER GAME", "2 PLAYER GAME"]

        self.keys = set()
        self.jump_pressed = False
        self.was_jump = False
        self.run_pressed = False

        self.bind()
        self.draw()
        self.update()  # Start game loop

    # ========================================================
    # DRAW
    # ========================================================
    def draw(self):
        self.canvas.delete("all")

        if self.state == "menu":
            # --- TITLE ---
            self.canvas.create_text(
                WIDTH // 2, 120,
                text="ULTRA MARIO 2D BROS.",
                fill=WHITE,
                font=("Courier", 28, "bold")
            )

            # --- MENU OPTIONS ---
            y_start = 220
            for i, text in enumerate(self.options):
                y = y_start + i * 32

                # Selector (like SMB1 arrow)
                if self.selection == i:
                    self.canvas.create_text(
                        WIDTH // 2 - 120, y,
                        text="▶",
                        fill=WHITE,
                        font=("Courier", 18, "bold")
                    )

                self.canvas.create_text(
                    WIDTH // 2, y,
                    text=text,
                    fill=WHITE,
                    font=("Courier", 18, "bold")
                )

            # --- FOOTER (TOP SCORE STYLE) ---
            self.canvas.create_text(
                WIDTH // 2, HEIGHT - 64,
                text="TOP-000000",
                fill=WHITE,
                font=("Courier", 14)
            )

            self.canvas.create_text(
                WIDTH // 2, HEIGHT - 36,
                text="© 1985 SAMSOFT",
                fill=RED,
                font=("Courier", 12)
            )

        elif self.state == "playing":
            self.draw_game()

    def draw_game(self):
        # Background
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=SKY_BLUE)

        # Platforms / ground
        for plat in self.platforms:
            px, py, pw, ph = plat
            self.canvas.create_rectangle(px - self.scroll_x, py, px + pw - self.scroll_x, py + ph, fill=GROUND_GREEN)

        # Blocks
        for block in self.blocks:
            bx, by = block['x'], block['y']
            self.canvas.create_rectangle(bx - self.scroll_x, by, bx + 32 - self.scroll_x, by + 32, fill=BLOCK_BROWN)

        # Pipes
        for pipe in self.pipes:
            px, py, pw, ph = pipe['x'], pipe['y'], pipe['width'], pipe['height']
            self.canvas.create_rectangle(px - self.scroll_x, py, px + pw - self.scroll_x, py + ph, fill="green")

            # Piranha if present
            if 'enemy' in pipe and pipe['enemy'] == 'piranha':
                pir_y = py - 32 + (math.sin(pipe['timer'] / 10) * 16)  # Oscillate
                self.canvas.create_rectangle(px + 16 - self.scroll_x, pir_y, px + 48 - self.scroll_x, pir_y + 32, fill="red")
                pipe['timer'] += 1

        # Enemies
        for enemy in self.enemies:
            ex, ey = enemy['x'], enemy['y']
            color = GOOMBA_BROWN if enemy['type'] == 'goomba' else KOOPA_GREEN
            self.canvas.create_rectangle(ex - self.scroll_x, ey, ex + 32 - self.scroll_x, ey + 32, fill=color)

        # Player
        self.canvas.create_rectangle(self.player_x - self.scroll_x, self.player_y, self.player_x + 32 - self.scroll_x, self.player_y + 32, fill=RED)

    # ========================================================
    # INPUT
    # ========================================================
    def bind(self):
        self.root.bind("<Up>", self.up)
        self.root.bind("<Down>", self.down)
        self.root.bind("<Return>", self.select)
        self.root.bind("<z>", self.select)      # NES A
        self.root.bind("<space>", self.select)  # NES A alt
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)

    def up(self, event=None):
        if self.state == "menu":
            self.selection = (self.selection - 1) % len(self.options)
            self.draw()

    def down(self, event=None):
        if self.state == "menu":
            self.selection = (self.selection + 1) % len(self.options)
            self.draw()

    def select(self, event=None):
        if self.state == "menu":
            choice = self.options[self.selection]
            print("SELECTED:", choice)
            if choice == "1 PLAYER GAME":
                self.start_game(1)
            elif choice == "2 PLAYER GAME":
                self.start_game(2)

    def key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == 'z':
            self.jump_pressed = True
            self.was_jump = False  # Reset for detection

    def key_release(self, event):
        key = event.keysym.lower()
        self.keys.discard(key)
        if key == 'z':
            self.jump_pressed = False
            self.was_jump = False

    # ========================================================
    # GAME LOGIC
    # ========================================================
    def start_game(self, players):
        self.state = "playing"
        self.players = players
        self.current_player = 0
        self.lives = [3] * players
        self.world = 1
        self.level = 1
        self.load_level(self.world, self.level)

    def load_level(self, world, level):
        # Level data for World 1-1 (extended for scrolling, positions scaled)
        if world == 1 and level == 1:
            level_width = WIDTH * 4  # Extended level
            self.platforms = [
                (0, HEIGHT - 64, level_width, 64),  # Main ground
                (800, HEIGHT - 128, 256, 32),       # Elevated platform
                (1200, HEIGHT - 160, 128, 32),      # Another platform
                # Add more for full map
            ]
            self.enemies = [
                {'type': 'goomba', 'x': 400, 'y': HEIGHT - 64 - 32, 'vel_x': -4, 'dir': -1},  # Initial Goomba
                {'type': 'goomba', 'x': 600, 'y': HEIGHT - 64 - 32, 'vel_x': -4, 'dir': -1},  # More Goombas
                {'type': 'koopa', 'x': 900, 'y': HEIGHT - 128 - 32, 'vel_x': -4, 'dir': -1},  # Koopa on platform
                # Add Para-Goomba, etc.
            ]
            self.blocks = [
                {'type': '?', 'x': 300, 'y': HEIGHT - 200, 'item': 'mushroom'},  # Super Mushroom
                {'type': '?', 'x': 350, 'y': HEIGHT - 200, 'item': 'leaf'},      # Super Leaf
                # Brick stack at 1000, HEIGHT-200, add multiple
            ]
            self.pipes = [
                {'x': 500, 'y': HEIGHT - 128, 'width': 64, 'height': 64, 'enemy': 'piranha', 'timer': 0},  # With Venus Fire Trap
                # Tall pipe for bonus at 1400, etc.
            ]
            self.goal_x = level_width - 100  # Goal position

        # Player init
        self.player_x = 100
        self.player_y = HEIGHT - 64 - 32
        self.player_vel_x = 0
        self.player_vel_y = 0
        self.on_ground = True
        self.scroll_x = 0
        self.power = 'small'  # //todo: implement power-ups
        self.p_meter = 0      # //todo: for flight

        # //todo: add more levels, e.g. if world==1 and level==2: ...

    def update(self):
        if self.state == "playing":
            # Horizontal movement
            max_speed = RUN_MAX if 'x' in self.keys else WALK_MAX
            accel = ACCEL
            if 'left' in self.keys:
                if self.player_vel_x > 0:
                    self.player_vel_x -= accel * 2  # Skid
                else:
                    self.player_vel_x -= accel
                if self.player_vel_x < -max_speed:
                    self.player_vel_x = -max_speed
            if 'right' in self.keys:
                if self.player_vel_x < 0:
                    self.player_vel_x += accel * 2
                else:
                    self.player_vel_x += accel
                if self.player_vel_x > max_speed:
                    self.player_vel_x = max_speed
            if 'left' not in self.keys and 'right' not in self.keys:
                if self.player_vel_x > 0:
                    self.player_vel_x -= FRICTION
                elif self.player_vel_x < 0:
                    self.player_vel_x += FRICTION
                if abs(self.player_vel_x) < FRICTION:
                    self.player_vel_x = 0

            # Jump
            if 'z' in self.keys and self.on_ground and not self.was_jump:
                speed_index = abs(self.player_vel_x) // 16
                jump_vel = JUMP_BASE - (speed_index * JUMP_OFFSET)  # Higher speed = higher jump
                self.player_vel_y = jump_vel
                self.on_ground = False
                self.was_jump = True

            # Gravity
            grav = GRAV_LOW if self.jump_pressed and self.player_vel_y < 0 else GRAV_HIGH
            self.player_vel_y += grav
            if self.player_vel_y > MAX_FALL:
                self.player_vel_y = MAX_FALL

            # Apply velocity
            self.player_x += self.player_vel_x
            self.player_y += self.player_vel_y

            # Collisions with platforms
            self.on_ground = False
            for plat in self.platforms:
                px, py, pw, ph = plat
                if (self.player_x + 32 > px and self.player_x < px + pw and
                    self.player_y + 32 > py and self.player_y + 32 - self.player_vel_y <= py and
                    self.player_vel_y >= 0):
                    self.player_y = py - 32
                    self.player_vel_y = 0
                    self.on_ground = True
                    break

            # Enemy updates and collisions
            for enemy in self.enemies[:]:
                enemy['x'] += enemy['vel_x']
                # Reverse dir at "edges" (simplified)
                if enemy['x'] < 0 or enemy['x'] > self.goal_x:
                    enemy['vel_x'] = -enemy['vel_x']
                    enemy['dir'] = -enemy['dir']

                ex, ey = enemy['x'], enemy['y']
                # Player-enemy collision
                if (self.player_x + 32 > ex and self.player_x < ex + 32 and
                    self.player_y + 32 > ey and self.player_y < ey + 32):
                    if self.player_y + 32 - self.player_vel_y <= ey and self.player_vel_y > 0:  # Stomp
                        self.enemies.remove(enemy)
                        self.player_vel_y = -40  # Bounce
                    else:  # Hurt
                        print("Hurt!")  # //todo: lose power/life

            # Scrolling
            if self.player_x - self.scroll_x > WIDTH * 0.6:
                self.scroll_x = self.player_x - WIDTH * 0.6
            if self.player_x - self.scroll_x < WIDTH * 0.4:
                self.scroll_x = self.player_x - WIDTH * 0.4
            if self.scroll_x < 0:
                self.scroll_x = 0
            if self.scroll_x > self.goal_x - WIDTH:
                self.scroll_x = self.goal_x - WIDTH

            # Goal check
            if self.player_x > self.goal_x:
                print("Level complete!")  # //todo: next level

            # //todo: block hits, item spawns, power-ups, flight, more enemies/behaviors

        self.draw()
        self.root.after(16, self.update)  # ~60 FPS

# ============================================================
# BOOT
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    SMB3Game(root)
    root.mainloop()
