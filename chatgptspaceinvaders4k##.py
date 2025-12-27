import pygame
import sys
import math
import random
import numpy as np

# ================== INIT ==================
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

SAMPLE_RATE, _, _ = pygame.mixer.get_init()

W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Space Invaders — Famicom Pure")
clock = pygame.time.Clock()
FPS = 60

BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,80,80)
GRAY = (120,120,120)

# ================== AUDIO ==================
def make_sound(mono):
    stereo = np.repeat(mono[:, None], 2, axis=1)
    return pygame.sndarray.make_sound(stereo)

def pulse(freq, dur, vol=0.4):
    t = np.linspace(0, dur, int(SAMPLE_RATE * dur), False)
    wave = np.sign(np.sin(2 * math.pi * freq * t))
    return make_sound((wave * vol * 32767).astype(np.int16))

def noise(dur, vol=0.4):
    mono = (np.random.uniform(-1, 1, int(SAMPLE_RATE * dur)) * vol * 32767).astype(np.int16)
    return make_sound(mono.astype(np.int16))

SND_SHOOT   = pulse(880, 0.07)
SND_HIT     = pulse(220, 0.12)
SND_EXPLODE = noise(0.15)

# ================== SPRITES ==================
INVADER_FRAMES = [
    ["00111100","01111110","11011011","11111111","01111110","00100100","01000010","10000001"],
    ["00111100","01111110","11011011","11111111","01111110","01000010","10000001","01000010"],
]

PLAYER_SPRITE = [
    "00011000",
    "00111100",
    "01111110",
    "11111111",
]

def draw_sprite(sprite, x, y, scale, color):
    for r, row in enumerate(sprite):
        for c, bit in enumerate(row):
            if bit == "1":
                pygame.draw.rect(screen, color,
                    (x + c*scale, y + r*scale, scale, scale))

# ================== GAME ENTITIES ==================
class Player:
    def __init__(self):
        self.x = W//2
        self.y = H - 60
        self.cooldown = 0
        self.score = 0
        self.lives = 3

    def update(self):
        mx, _ = pygame.mouse.get_pos()
        self.x = max(20, min(mx, W-60))
        if self.cooldown > 0:
            self.cooldown -= 1

    def draw(self):
        draw_sprite(PLAYER_SPRITE, self.x, self.y, 4, GREEN)

class Invader:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.dir = 1

    def update(self, speed):
        self.x += self.dir * speed
        self.frame ^= 1

    def draw(self):
        draw_sprite(INVADER_FRAMES[self.frame], self.x, self.y, 4, GREEN)

class Bullet:
    def __init__(self, x, y, dy):
        self.x = x
        self.y = y
        self.dy = dy

    def update(self):
        self.y += self.dy

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 4, 12))

# ================== GAME STATE ==================
STATE_MENU = 0
STATE_GAME = 1
STATE_HELP = 2
STATE_CREDITS = 3
state = STATE_MENU
menu_index = 0

player = None
invaders = []
direction = 1
player_bullet = None

def spawn_invaders():
    invaders.clear()
    for r in range(5):
        for c in range(11):
            invaders.append(Invader(100 + c*50, 60 + r*40))

def start_game():
    global player, direction, player_bullet
    player = Player()
    direction = 1
    player_bullet = None
    spawn_invaders()

def invader_speed():
    return 0.6 + (55 - len(invaders)) * 0.035

# ================== DRAW HELPERS ==================
font_big = pygame.font.SysFont(None, 64)
font = pygame.font.SysFont(None, 32)

def draw_center(text, y, color=WHITE):
    surf = font.render(text, True, color)
    screen.blit(surf, (W//2 - surf.get_width()//2, y))

# ================== MAIN LOOP ==================
while True:
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN:
            if state == STATE_MENU:
                if e.key == pygame.K_UP:
                    menu_index = (menu_index - 1) % 4
                if e.key == pygame.K_DOWN:
                    menu_index = (menu_index + 1) % 4
                if e.key == pygame.K_RETURN:
                    if menu_index == 0:
                        start_game()
                        state = STATE_GAME
                    elif menu_index == 1:
                        state = STATE_HELP
                    elif menu_index == 2:
                        state = STATE_CREDITS
                    elif menu_index == 3:
                        pygame.quit()
                        sys.exit()

            else:
                if e.key == pygame.K_ESCAPE:
                    state = STATE_MENU

        if state == STATE_GAME and e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if not player_bullet and player.cooldown == 0:
                SND_SHOOT.play()
                player_bullet = Bullet(player.x+16, player.y, -8)
                player.cooldown = 15

    # ================== UPDATE ==================
    if state == STATE_GAME:
        player.update()
        speed = invader_speed()
        edge = False

        for inv in invaders:
            inv.dir = direction
            inv.update(speed)
            if inv.x < 20 or inv.x > W-80:
                edge = True

        if edge:
            direction *= -1
            for inv in invaders:
                inv.y += 20

        if player_bullet:
            player_bullet.update()
            if player_bullet.y < 0:
                player_bullet = None
            else:
                for inv in invaders[:]:
                    if abs(player_bullet.x - inv.x) < 20 and abs(player_bullet.y - inv.y) < 20:
                        invaders.remove(inv)
                        player.score += 10
                        SND_HIT.play()
                        player_bullet = None
                        break

        if not invaders:
            SND_EXPLODE.play()
            spawn_invaders()

    # ================== DRAW ==================
    screen.fill(BLACK)

    if state == STATE_MENU:
        screen.blit(font_big.render("SPACE INVADERS", True, GREEN), (180, 80))
        items = ["Start Game", "How To Play", "Credits", "Exit"]
        for i, item in enumerate(items):
            color = GREEN if i == menu_index else GRAY
            draw_center(item, 220 + i*40, color)

    elif state == STATE_HELP:
        draw_center("HOW TO PLAY", 80, GREEN)
        draw_center("Mouse: Move Ship", 200)
        draw_center("Left Click: Shoot", 240)
        draw_center("ESC: Back", 300)

    elif state == STATE_CREDITS:
        draw_center("CREDITS", 80, GREEN)
        draw_center("Code & Design:", 220)
        draw_center("Catsan / Team Flames", 260)
        draw_center("ESC: Back", 320)

    elif state == STATE_GAME:
        player.draw()
        for inv in invaders:
            inv.draw()
        if player_bullet:
            player_bullet.draw()

        screen.blit(font.render(f"SCORE {player.score:04d}", True, WHITE), (10,10))
        screen.blit(font.render(f"LIVES {player.lives}", True, WHITE), (W-140,10))

    pygame.display.flip()
