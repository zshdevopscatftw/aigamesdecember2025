import sys
import math
import random
import pygame

# ============================================================
# Smash Lite (No-files) — Title + Menu + Options + VS Mode
# ============================================================

# ------------------ SETUP ------------------
pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smash Lite - Pygame (Menu + Intro)")
clock = pygame.time.Clock()

# Fonts (no external files)
FONT_TINY = pygame.font.Font(None, 22)
FONT_UI = pygame.font.Font(None, 26)
FONT_MED = pygame.font.Font(None, 36)
FONT_BIG = pygame.font.Font(None, 84)

GRAVITY = 0.60
FLOOR_Y = 420

# ------------------ PLATFORM ------------------
platforms = [
    pygame.Rect(200, 330, 200, 15),
    pygame.Rect(500, 280, 200, 15),
    pygame.Rect(350, 200, 200, 15),
]


# ------------------ BACKGROUND FX ------------------
class Star:
    def __init__(self):
        self.reset(True)

    def reset(self, random_y=False):
        self.x = random.randrange(0, WIDTH)
        self.y = random.randrange(0, HEIGHT) if random_y else -random.randrange(10, 120)
        self.speed = random.uniform(20, 90)
        self.r = random.randint(1, 2)

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > HEIGHT + 5:
            self.reset(False)

    def draw(self, surf):
        pygame.draw.circle(surf, (200, 200, 220), (int(self.x), int(self.y)), self.r)


stars = [Star() for _ in range(90)]
ring_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)


def draw_background(t_seconds: float):
    # Dark base
    screen.fill((18, 18, 30))

    # Starfield
    for s in stars:
        s.draw(screen)

    # Soft animated rings behind menu/title
    ring_surface.fill((0, 0, 0, 0))
    cx, cy = WIDTH // 2, HEIGHT // 2 - 40
    wobble = math.sin(t_seconds * 0.7) * 14

    for i in range(6):
        r = 70 + i * 42 + wobble
        a = 26 - i * 3
        pygame.draw.circle(ring_surface, (140, 140, 170, max(0, a)), (cx, cy), int(r), width=2)

    screen.blit(ring_surface, (0, 0))

    # Ground strip
    pygame.draw.rect(screen, (70, 120, 80), (0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y))


def draw_platforms():
    for p in platforms:
        pygame.draw.rect(screen, (165, 165, 175), p)


def draw_center_text(text, font, y, color=(245, 245, 245), shadow=True):
    if shadow:
        s = font.render(text, True, (10, 10, 15))
        rect = s.get_rect(center=(WIDTH // 2 + 2, y + 2))
        screen.blit(s, rect)

    r = font.render(text, True, color)
    rect = r.get_rect(center=(WIDTH // 2, y))
    screen.blit(r, rect)


def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


# ------------------ PLAYER ------------------
class Player:
    def __init__(self, spawn_xy, color, controls, stocks=3):
        self.spawn_xy = spawn_xy
        self.rect = pygame.Rect(spawn_xy[0], spawn_xy[1], 40, 50)
        self.prev_rect = self.rect.copy()

        self.vel = pygame.Vector2(0, 0)
        self.color = color
        self.on_ground = False

        self.percent = 0
        self.stocks = stocks
        self.controls = controls
        self.facing = 1

        self.attack_cooldown = 0
        self.hitstun = 0

        # tiny visual cue for attacks (no assets)
        self.swing_timer = 0

    def reset_position(self):
        self.rect.topleft = self.spawn_xy
        self.prev_rect = self.rect.copy()
        self.vel.update(0, 0)
        self.on_ground = False
        self.attack_cooldown = 0
        self.hitstun = 0
        self.swing_timer = 0

    def lose_stock(self):
        self.stocks -= 1
        self.percent = 0
        self.vel.update(0, 0)
        self.hitstun = 0
        self.attack_cooldown = 0
        self.swing_timer = 0

        if self.stocks > 0:
            self.reset_position()
        else:
            # put offscreen so it doesn't interfere
            self.rect.topleft = (-9999, -9999)

    def move(self, keys, keys_down):
        if self.stocks <= 0:
            return

        # hitstun: can't control movement for a bit
        if self.hitstun > 0:
            return

        speed = 4
        if keys[self.controls["left"]]:
            self.vel.x = -speed
            self.facing = -1
        elif keys[self.controls["right"]]:
            self.vel.x = speed
            self.facing = 1
        else:
            self.vel.x = 0

        # jump only on press (not hold)
        if self.controls["jump"] in keys_down and self.on_ground:
            self.vel.y = -12
            self.on_ground = False

    def apply_gravity_and_move(self):
        if self.stocks <= 0:
            return

        self.prev_rect = self.rect.copy()
        self.vel.y += GRAVITY
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)

    def collide_platforms(self):
        if self.stocks <= 0:
            return

        self.on_ground = False

        # floor
        if self.rect.bottom >= FLOOR_Y:
            self.rect.bottom = FLOOR_Y
            self.vel.y = 0
            self.on_ground = True

        # platforms: land only if falling AND you were above last frame
        if self.vel.y >= 0:
            for p in platforms:
                if self.rect.colliderect(p) and self.prev_rect.bottom <= p.top + 2:
                    self.rect.bottom = p.top
                    self.vel.y = 0
                    self.on_ground = True

    def attack(self, other):
        if self.stocks <= 0:
            return
        if self.attack_cooldown > 0:
            return

        # start attack
        self.attack_cooldown = 18
        self.swing_timer = 8

        # simple forward hitbox
        hitbox = self.rect.copy()
        hitbox.width += 18
        hitbox.height -= 10
        hitbox.y += 6
        hitbox.x += (14 * self.facing)

        if hitbox.colliderect(other.rect) and other.stocks > 0:
            other.percent += 8
            knockback = (other.percent / 10.0) + 3.0
            other.vel.x = knockback * self.facing
            other.vel.y = -knockback
            other.hitstun = int(10 + other.percent / 12)

    def check_ringout(self):
        if self.stocks <= 0:
            return False

        out = (
            self.rect.top > HEIGHT + 50 or
            self.rect.right < -50 or
            self.rect.left > WIDTH + 50
        )
        if out:
            self.lose_stock()
            return True
        return False

    def tick_timers(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.hitstun > 0:
            self.hitstun -= 1
        if self.swing_timer > 0:
            self.swing_timer -= 1

    def draw(self):
        if self.stocks <= 0:
            return

        pygame.draw.rect(screen, self.color, self.rect)

        # tiny "swing" effect (no files)
        if self.swing_timer > 0:
            fx = pygame.Rect(0, 0, 16, 10)
            fx.centery = self.rect.centery
            fx.centerx = self.rect.centerx + (28 * self.facing)
            pygame.draw.rect(screen, (240, 240, 240), fx, border_radius=3)


# ------------------ GAME HELPERS ------------------
def make_players(stocks: int):
    # spawn positions
    p1_spawn = (240, FLOOR_Y - 50)
    p2_spawn = (620, FLOOR_Y - 50)

    p1 = Player(p1_spawn, (255, 120, 0), {
        "left": pygame.K_a,
        "right": pygame.K_d,
        "jump": pygame.K_w,
        "attack": pygame.K_f
    }, stocks=stocks)

    p2 = Player(p2_spawn, (80, 160, 255), {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "jump": pygame.K_UP,
        "attack": pygame.K_SLASH  # change if you want (e.g. pygame.K_RSHIFT)
    }, stocks=stocks)

    return p1, p2


def draw_hud(p1: Player, p2: Player):
    ui1 = FONT_UI.render(f"P1  {p1.percent}%   Stocks: {p1.stocks}", True, (245, 245, 245))
    ui2 = FONT_UI.render(f"P2  {p2.percent}%   Stocks: {p2.stocks}", True, (245, 245, 245))
    screen.blit(ui1, (20, 16))
    screen.blit(ui2, (WIDTH - ui2.get_width() - 20, 16))


# ------------------ STATES ------------------
STATE_INTRO = "INTRO"
STATE_TITLE = "TITLE"
STATE_MENU = "MENU"
STATE_OPTIONS = "OPTIONS"
STATE_GAME = "GAME"
STATE_PAUSE = "PAUSE"
STATE_RESULTS = "RESULTS"


def main():
    settings = {
        "stocks": 3
    }

    # state variables
    state = STATE_INTRO
    intro_start_ms = pygame.time.get_ticks()

    menu_items = ["VS MODE", "OPTIONS", "QUIT"]
    menu_idx = 0

    opt_items = ["STOCKS", "BACK"]
    opt_idx = 0

    pause_items = ["RESUME", "RESTART", "MAIN MENU"]
    pause_idx = 0

    p1, p2 = make_players(settings["stocks"])
    winner_text = ""

    while True:
        dt = clock.tick(60) / 1000.0
        now_ms = pygame.time.get_ticks()
        t = now_ms / 1000.0

        # update background fx
        for s in stars:
            s.update(dt)

        keys_down = set()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                keys_down.add(event.key)

        keys = pygame.key.get_pressed()

        # ============================================================
        # INTRO (fade splash)
        # ============================================================
        if state == STATE_INTRO:
            draw_background(t)

            elapsed = now_ms - intro_start_ms

            # You can skip after a brief moment
            if elapsed > 400 and len(keys_down) > 0:
                state = STATE_TITLE

            # Simple 3-phase fade: in -> hold -> out
            # total ~ 2800ms
            if elapsed < 800:
                alpha = int((elapsed / 800) * 255)
            elif elapsed < 1800:
                alpha = 255
            elif elapsed < 2600:
                alpha = int((1 - (elapsed - 1800) / 800) * 255)
            else:
                state = STATE_TITLE
                alpha = 0

            # Splash box
            box = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            box.fill((0, 0, 0, 0))
            splash = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            splash.fill((0, 0, 0, 0))

            # Splash text
            text1 = FONT_BIG.render("PYGAME", True, (245, 245, 245))
            text2 = FONT_MED.render("presents", True, (200, 200, 210))
            r1 = text1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            r2 = text2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 36))

            splash.blit(text1, r1)
            splash.blit(text2, r2)
            splash.set_alpha(alpha)

            screen.blit(splash, (0, 0))
            pygame.display.flip()
            continue

        # ============================================================
        # TITLE (logo + press start)
        # ============================================================
        if state == STATE_TITLE:
            draw_background(t)
            draw_platforms()

            # "Logo" with a chunky shadow
            draw_center_text("SMASH", FONT_BIG, 170, color=(250, 250, 250), shadow=True)
            draw_center_text("L I T E", FONT_MED, 232, color=(210, 210, 225), shadow=True)

            blink = (math.sin(t * 4.0) > 0.0)
            if blink:
                draw_center_text("PRESS START", FONT_MED, 320, color=(250, 250, 250), shadow=True)

            # Start = any key
            if len(keys_down) > 0:
                state = STATE_MENU

            # quick quit
            if pygame.K_ESCAPE in keys_down:
                pygame.quit()
                sys.exit()

            pygame.display.flip()
            continue

        # ============================================================
        # MENU
        # ============================================================
        if state == STATE_MENU:
            draw_background(t)
            draw_platforms()

            # Title small
            draw_center_text("SMASH LITE", FONT_MED, 90, color=(245, 245, 245), shadow=True)

            # Menu navigation
            if pygame.K_UP in keys_down or pygame.K_w in keys_down:
                menu_idx = (menu_idx - 1) % len(menu_items)
            if pygame.K_DOWN in keys_down or pygame.K_s in keys_down:
                menu_idx = (menu_idx + 1) % len(menu_items)

            # Activate
            if pygame.K_RETURN in keys_down or pygame.K_SPACE in keys_down:
                choice = menu_items[menu_idx]
                if choice == "VS MODE":
                    p1, p2 = make_players(settings["stocks"])
                    state = STATE_GAME
                elif choice == "OPTIONS":
                    state = STATE_OPTIONS
                elif choice == "QUIT":
                    pygame.quit()
                    sys.exit()

            if pygame.K_ESCAPE in keys_down:
                state = STATE_TITLE

            # Draw items
            base_y = 200
            for i, item in enumerate(menu_items):
                y = base_y + i * 54
                selected = (i == menu_idx)

                if selected:
                    draw_center_text(f"> {item} <", FONT_MED, y, color=(255, 255, 255), shadow=True)
                else:
                    draw_center_text(item, FONT_MED, y, color=(190, 190, 205), shadow=False)

            hint = FONT_TINY.render("ENTER/SPACE = Select   UP/DOWN = Move   ESC = Back", True, (200, 200, 210))
            screen.blit(hint, (20, HEIGHT - 28))

            pygame.display.flip()
            continue

        # ============================================================
        # OPTIONS
        # ============================================================
        if state == STATE_OPTIONS:
            draw_background(t)
            draw_platforms()

            draw_center_text("OPTIONS", FONT_MED, 90, color=(245, 245, 245), shadow=True)

            if pygame.K_UP in keys_down or pygame.K_w in keys_down:
                opt_idx = (opt_idx - 1) % len(opt_items)
            if pygame.K_DOWN in keys_down or pygame.K_s in keys_down:
                opt_idx = (opt_idx + 1) % len(opt_items)

            # Change stocks when STOCKS selected
            if opt_items[opt_idx] == "STOCKS":
                if pygame.K_LEFT in keys_down or pygame.K_a in keys_down:
                    settings["stocks"] = clamp(settings["stocks"] - 1, 1, 9)
                if pygame.K_RIGHT in keys_down or pygame.K_d in keys_down:
                    settings["stocks"] = clamp(settings["stocks"] + 1, 1, 9)

            if pygame.K_RETURN in keys_down or pygame.K_SPACE in keys_down:
                if opt_items[opt_idx] == "BACK":
                    state = STATE_MENU

            if pygame.K_ESCAPE in keys_down:
                state = STATE_MENU

            # Draw options
            y0 = 210
            for i, item in enumerate(opt_items):
                y = y0 + i * 60
                selected = (i == opt_idx)

                if item == "STOCKS":
                    label = f"STOCKS: {settings['stocks']}"
                else:
                    label = item

                if selected:
                    draw_center_text(f"> {label} <", FONT_MED, y, color=(255, 255, 255), shadow=True)
                else:
                    draw_center_text(label, FONT_MED, y, color=(190, 190, 205), shadow=False)

            hint = FONT_TINY.render("LEFT/RIGHT = Change Stocks (when selected)   ESC = Back", True, (200, 200, 210))
            screen.blit(hint, (20, HEIGHT - 28))

            pygame.display.flip()
            continue

        # ============================================================
        # PAUSE
        # ============================================================
        if state == STATE_PAUSE:
            # Draw game scene behind pause overlay
            draw_background(t)
            draw_platforms()
            p1.draw()
            p2.draw()
            draw_hud(p1, p2)

            # Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            draw_center_text("PAUSE", FONT_MED, 120, color=(255, 255, 255), shadow=True)

            if pygame.K_UP in keys_down or pygame.K_w in keys_down:
                pause_idx = (pause_idx - 1) % len(pause_items)
            if pygame.K_DOWN in keys_down or pygame.K_s in keys_down:
                pause_idx = (pause_idx + 1) % len(pause_items)

            if pygame.K_RETURN in keys_down or pygame.K_SPACE in keys_down:
                choice = pause_items[pause_idx]
                if choice == "RESUME":
                    state = STATE_GAME
                elif choice == "RESTART":
                    p1, p2 = make_players(settings["stocks"])
                    state = STATE_GAME
                elif choice == "MAIN MENU":
                    state = STATE_MENU

            if pygame.K_ESCAPE in keys_down:
                state = STATE_GAME

            y0 = 220
            for i, item in enumerate(pause_items):
                y = y0 + i * 52
                selected = (i == pause_idx)
                if selected:
                    draw_center_text(f"> {item} <", FONT_MED, y, color=(255, 255, 255), shadow=True)
                else:
                    draw_center_text(item, FONT_MED, y, color=(210, 210, 225), shadow=False)

            pygame.display.flip()
            continue

        # ============================================================
        # GAME
        # ============================================================
        if state == STATE_GAME:
            # Pause
            if pygame.K_ESCAPE in keys_down:
                state = STATE_PAUSE
                pygame.display.flip()
                continue

            # Inputs
            p1.move(keys, keys_down)
            p2.move(keys, keys_down)

            # Attacks (on press, not hold)
            if p1.controls["attack"] in keys_down:
                p1.attack(p2)
            if p2.controls["attack"] in keys_down:
                p2.attack(p1)

            # Physics
            for p in (p1, p2):
                p.tick_timers()
                p.apply_gravity_and_move()
                p.collide_platforms()

            # Ringout check
            p1.check_ringout()
            p2.check_ringout()

            # Win condition
            if p1.stocks <= 0 or p2.stocks <= 0:
                if p1.stocks <= 0 and p2.stocks <= 0:
                    winner_text = "DRAW!"
                elif p2.stocks <= 0:
                    winner_text = "P1 WINS!"
                else:
                    winner_text = "P2 WINS!"
                state = STATE_RESULTS

            # Draw
            draw_background(t)
            draw_platforms()

            p1.draw()
            p2.draw()
            draw_hud(p1, p2)

            pygame.display.flip()
            continue

        # ============================================================
        # RESULTS
        # ============================================================
        if state == STATE_RESULTS:
            draw_background(t)
            draw_platforms()

            # show players frozen for a moment (optional)
            p1.draw()
            p2.draw()

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            draw_center_text(winner_text, FONT_BIG, 200, color=(255, 255, 255), shadow=True)
            draw_center_text("ENTER = Main Menu    R = Rematch", FONT_MED, 290, color=(230, 230, 240), shadow=True)

            if pygame.K_RETURN in keys_down or pygame.K_SPACE in keys_down:
                state = STATE_MENU
            if pygame.K_r in keys_down:
                p1, p2 = make_players(settings["stocks"])
                state = STATE_GAME
            if pygame.K_ESCAPE in keys_down:
                state = STATE_MENU

            pygame.display.flip()
            continue


if __name__ == "__main__":
    main()
