# ─────────────────────────────────────────────────────────────────────────────
# Cat's PVZ "Sleep Garden" — single-file Pygame prototype
# 600x400 @ 60 FPS | FILES=OFF | dreamy night palette + fog-of-yawn overlay
# Lullaby pacing (gentle waves), sleep-sun economy, doze-combo bonuses
# Replanted-style seed bank & 5 lanes | Soft reboot: press R
# Run: pip install pygame && python sleep_garden.py
# ─────────────────────────────────────────────────────────────────────────────

import pygame, random, math, sys, time

# ====== TWEAKABLE CONSTANTS ===================================================
CONSTANTS = dict(
    WIDTH=600, HEIGHT=400, FPS=60, LANES=5, COLS=9,
    TILE_W=56, TILE_H=60, GRID_X=20, GRID_Y=60,
    SUN_TICK=90,                 # frames per passive "sleep-sun" drip
    SUN_PER_TICK=10,             # amount per drip
    PLANT_COST=50,               # cost of a calm-shooter
    SHOOT_COOLDOWN=75,           # frames between shots
    BULLET_SPEED=4.0,
    BULLET_DMG=12,
    Z_SPAWN_GAP_BASE=240,        # base frames between shambler spawns
    Z_SPAWN_GAP_JITTER=160,      # added random jitter
    Z_BASE_HP=95,
    Z_SPEED=0.35,
    WAVES=[(0, 0), (20, 1), (40, 2), (70, 3), (110, 4)],  # (sec, wave level)
    FOG_INTENSITY=0.45,          # 0..1
    DOZE_DECAY=0.997,            # per frame decay of calm meter
    DOZE_HIT_PENALTY=0.25,
    DOZE_BONUS_THRESHOLDS=[0.25, 0.5, 0.75, 0.9],  # tiers increase sun gain
    DOZE_BONUS=[0, 1, 2, 3, 5],  # extra sun per tick by tier
    NIGHT_COLORS={
        "bg": (10, 14, 22),
        "grid": (24, 32, 48),
        "lane": (18, 24, 38),
        "seed_bank": (22, 28, 44),
        "white": (230, 240, 255),
        "soft": (180, 200, 230),
        "plant": (140, 200, 180),
        "bullet": (220, 240, 255),
        "zombie": (140, 150, 160),
        "danger": (255, 120, 120),
        "sun": (245, 230, 110),
    }
)
# ============================================================================

W, H = CONSTANTS["WIDTH"], CONSTANTS["HEIGHT"]

class CalmRNG(random.Random): pass
rng = CalmRNG(42)

# --- Game State ---------------------------------------------------------------
class GameState:
    def __init__(self):
        self.reset()
    def reset(self):
        self.grid = [[None for _ in range(CONSTANTS["COLS"])] for _ in range(CONSTANTS["LANES"])]
        self.plants = []
        self.bullets = []
        self.zombies = []
        self.sun = 75
        self.frame = 0
        self.last_z_spawn = 0
        self.next_gap = self._calc_spawn_gap()
        self.running = True
        self.doze = 0.5  # calm meter 0..1
        self.health = 3
        self.wave_level = 0
        self.start_time = time.time()
        self.shoot_cooldown_map = {}  # (lane,col) -> next_frame
    def _calc_spawn_gap(self):
        base = CONSTANTS["Z_SPAWN_GAP_BASE"]
        jit = rng.randint(0, CONSTANTS["Z_SPAWN_GAP_JITTER"])
        lullaby = max(0, (4 - self.wave_level)) * 90  # earlier waves slower
        return base + jit + lullaby

GS = GameState()

# --- Utility ------------------------------------------------------------------
def grid_to_xy(lane, col):
    x = CONSTANTS["GRID_X"] + col * CONSTANTS["TILE_W"]
    y = CONSTANTS["GRID_Y"] + lane * CONSTANTS["TILE_H"]
    return x, y

def xy_to_grid(mx, my):
    gx = mx - CONSTANTS["GRID_X"]
    gy = my - CONSTANTS["GRID_Y"]
    if gx < 0 or gy < 0: return None
    col = gx // CONSTANTS["TILE_W"]
    lane = gy // CONSTANTS["TILE_H"]
    if 0 <= lane < CONSTANTS["LANES"] and 0 <= col < CONSTANTS["COLS"]:
        return int(lane), int(col)
    return None

# --- Entities -----------------------------------------------------------------
class Plant:
    def __init__(self, lane, col):
        self.lane, self.col = lane, col
        self.hp = 80
    def can_shoot(self):
        key = (self.lane, self.col)
        return GS.frame >= GS.shoot_cooldown_map.get(key, 0)
    def shoot(self):
        x, y = grid_to_xy(self.lane, self.col)
        bx = x + CONSTANTS["TILE_W"] - 8
        by = y + CONSTANTS["TILE_H"] // 2
        GS.bullets.append(Bullet(bx, by, self.lane))
        GS.shoot_cooldown_map[(self.lane, self.col)] = GS.frame + CONSTANTS["SHOOT_COOLDOWN"]

class Bullet:
    def __init__(self, x, y, lane):
        self.x, self.y, self.lane = x, y, lane
        self.dmg = CONSTANTS["BULLET_DMG"]
        self.dead = False
    def update(self):
        self.x += CONSTANTS["BULLET_SPEED"]
        if self.x > W - 10:
            self.dead = True

class Zombie:
    def __init__(self, lane, hp, speed):
        self.lane = lane
        self.x = W + rng.randint(0, 60)
        _, y = grid_to_xy(lane, 0)
        self.y = y + CONSTANTS["TILE_H"] // 6
        self.hp = hp
        self.speed = speed
        self.bite_cool = 0
        self.dead = False
    def update(self):
        # Check plant collision
        col = int((self.x - CONSTANTS["GRID_X"]) // CONSTANTS["TILE_W"])
        if 0 <= col < CONSTANTS["COLS"]:
            p = GS.grid[self.lane][col]
            if p:
                # Bite
                if self.bite_cool <= 0:
                    p.hp -= 8
                    self.bite_cool = 35
                    GS.doze = max(0.0, GS.doze - CONSTANTS["DOZE_HIT_PENALTY"])
                else:
                    self.bite_cool -= 1
                return
        self.x -= self.speed
        if self.x < 0:
            self.dead = True
            GS.health -= 1
            GS.doze = max(0.0, GS.doze - CONSTANTS["DOZE_HIT_PENALTY"])

# --- Drawing Helpers -----------------------------------------------------------
def draw_text(surf, text, x, y, size=16, color=(255,255,255), center=False):
    font = pygame.font.SysFont("arial", size, bold=False)
    img = font.render(text, True, color)
    r = img.get_rect()
    if center:
        r.center = (x, y)
    else:
        r.topleft = (x, y)
    surf.blit(img, r)

def draw_ui(screen):
    c = CONSTANTS["NIGHT_COLORS"]
    # Seed bank
    pygame.draw.rect(screen, c["seed_bank"], (0, 0, W, 50))
    draw_text(screen, "Sleep Garden", 10, 10, 20, c["white"])
    # Sun counter with doze bonus info
    tier = doze_tier()
    bonus = CONSTANTS["DOZE_BONUS"][tier]
    draw_text(screen, f"Sun: {GS.sun}  (+{bonus} on drip)", 220, 12, 18, c["sun"])
    # Health hearts
    hearts = "♥" * max(0, GS.health)
    draw_text(screen, f"Health: {hearts}", 470, 12, 18, c["soft"])
    # Plant card
    pygame.draw.rect(screen, c["plant"], (10, 8, 36, 36), border_radius=6)
    draw_text(screen, f"{CONSTANTS['PLANT_COST']}", 28, 40, 14, c["white"], center=True)

def draw_grid(screen):
    c = CONSTANTS["NIGHT_COLORS"]
    pygame.draw.rect(screen, c["grid"], (0, 50, W, H-50))
    # lanes
    for l in range(CONSTANTS["LANES"]):
        y = CONSTANTS["GRID_Y"] + l * CONSTANTS["TILE_H"]
        pygame.draw.rect(screen, c["lane"], (CONSTANTS["GRID_X"], y, CONSTANTS["TILE_W"]*CONSTANTS["COLS"], CONSTANTS["TILE_H"]), border_radius=6)
    # columns
    for col in range(CONSTANTS["COLS"]+1):
        x = CONSTANTS["GRID_X"] + col * CONSTANTS["TILE_W"]
        pygame.draw.line(screen, (30,40,60), (x, CONSTANTS["GRID_Y"]), (x, CONSTANTS["GRID_Y"]+CONSTANTS["LANES"]*CONSTANTS["TILE_H"]), 1)

def draw_plants(screen):
    c = CONSTANTS["NIGHT_COLORS"]
    for p in GS.plants:
        x, y = grid_to_xy(p.lane, p.col)
        body = pygame.Rect(x+6, y+8, CONSTANTS["TILE_W"]-12, CONSTANTS["TILE_H"]-16)
        pygame.draw.rect(screen, c["plant"], body, border_radius=8)
        # sleepy face
        draw_text(screen, "(-‿-)", body.centerx, body.centery, 14, c["white"], center=True)

def draw_bullets(screen):
    c = CONSTANTS["NIGHT_COLORS"]
    for b in GS.bullets:
        pygame.draw.circle(screen, c["bullet"], (int(b.x), int(b.y)), 4)

def draw_zombies(screen):
    c = CONSTANTS["NIGHT_COLORS"]
    for z in GS.zombies:
        r = pygame.Rect(int(z.x)-10, int(z.y)-6, 20, 28)
        pygame.draw.rect(screen, c["zombie"], r, border_radius=6)
        # tiny eyes
        pygame.draw.circle(screen, c["white"], (r.centerx-4, r.y+9), 2)
        pygame.draw.circle(screen, c["white"], (r.centerx+4, r.y+9), 2)

def draw_fog(screen):
    # fog-of-yawn overlay: radial alpha falloff around cursor + plant area
    fog = pygame.Surface((W, H), pygame.SRCALPHA)
    base = int(255 * CONSTANTS["FOG_INTENSITY"])
    fog.fill((8,12,20, base))
    mx, my = pygame.mouse.get_pos()
    for (cx, cy, rad) in [(mx, my, 80), (W*0.35, H*0.62, 110), (W*0.7, H*0.62, 110)]:
        for r in range(0, int(rad), 8):
            alpha = max(0, base - int((r / rad) * base))
            pygame.draw.circle(fog, (0,0,0, max(0, alpha-40)), (int(cx), int(cy)), r)
    screen.blit(fog, (0,0))

def draw_doze_meter(screen):
    c = CONSTANTS["NIGHT_COLORS"]
    x, y, w, h = 10, H-18, 180, 8
    pygame.draw.rect(screen, (30,40,60), (x,y,w,h), border_radius=4)
    fill = int(w * GS.doze)
    pygame.draw.rect(screen, (70,160,200), (x,y,fill,h), border_radius=4)
    tier = doze_tier()
    draw_text(screen, f"Doze {tier}", x+w+8, y-4, 14, c["soft"])

# --- Mechanics ----------------------------------------------------------------
def doze_tier():
    th = CONSTANTS["DOZE_BONUS_THRESHOLDS"]
    v = GS.doze
    t = 0
    for i, cut in enumerate(th, start=1):
        if v >= cut: t = i
    return t

def passive_sun_tick():
    if GS.frame % CONSTANTS["SUN_TICK"] == 0:
        tier = doze_tier()
        bonus = CONSTANTS["DOZE_BONUS"][tier]
        GS.sun += CONSTANTS["SUN_PER_TICK"] + bonus

def maybe_advance_wave():
    elapsed = time.time() - GS.start_time
    while GS.wave_level + 1 < len(CONSTANTS["WAVES"]) and elapsed >= CONSTANTS["WAVES"][GS.wave_level+1][0]:
        GS.wave_level += 1

def spawn_zombie_if_needed():
    if GS.frame - GS.last_z_spawn >= GS.next_gap:
        # burst count depends on wave_level (gentle bursts)
        burst = 1 + GS.wave_level
        for _ in range(burst):
            lane = rng.randrange(CONSTANTS["LANES"])
            hp = CONSTANTS["Z_BASE_HP"] + 12*GS.wave_level
            sp = CONSTANTS["Z_SPEED"] * (1 + 0.05*GS.wave_level)
            GS.zombies.append(Zombie(lane, hp, sp))
        GS.last_z_spawn = GS.frame
        GS.next_gap = GS._calc_spawn_gap()

def update_bullets():
    for b in GS.bullets:
        b.update()
        # collision on lane
        for z in GS.zombies:
            if z.lane != b.lane: continue
            if abs(z.x - b.x) < 10 and abs(z.y - b.y) < 14:
                z.hp -= b.dmg
                b.dead = True
                GS.doze = min(1.0, GS.doze + 0.01)  # calm confidence grows on good timing
                break
    GS.bullets[:] = [b for b in GS.bullets if not b.dead]

def update_zombies():
    for z in GS.zombies:
        z.update()
        if z.hp <= 0:
            z.dead = True
            GS.doze = min(1.0, GS.doze + 0.02)
    GS.zombies[:] = [z for z in GS.zombies if not z.dead]

def plants_act():
    # each plant shoots if zombie present in front in same lane (simple LOS)
    for p in GS.plants:
        lane_z = [z for z in GS.zombies if z.lane == p.lane and z.x > CONSTANTS["GRID_X"] + p.col*CONSTANTS["TILE_W"]]
        if lane_z and p.can_shoot():
            p.shoot()
    # remove dead plants
    alive = []
    for p in GS.plants:
        if p.hp > 0:
            alive.append(p)
        else:
            GS.grid[p.lane][p.col] = None
            GS.doze = max(0.0, GS.doze - 0.1)
    GS.plants[:] = alive

def place_plant(pos):
    g = xy_to_grid(*pos)
    if not g: return
    lane, col = g
    if GS.grid[lane][col] is not None: return
    if GS.sun < CONSTANTS["PLANT_COST"]: return
    GS.sun -= CONSTANTS["PLANT_COST"]
    p = Plant(lane, col)
    GS.grid[lane][col] = p
    GS.plants.append(p)

# --- Main ---------------------------------------------------------------------
def main():
    pygame.init()
    pygame.display.set_caption("Sleep Garden — Doze not Click")
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    c = CONSTANTS["NIGHT_COLORS"]

    while True:
        # Input
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit(0)
                if e.key == pygame.K_r:
                    # soft reboot
                    GS.reset()
                    continue
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and GS.running:
                # click in bank? (optional future seeds); for now any click on grid places calm-shooter
                if e.pos[1] >= CONSTANTS["GRID_Y"]:
                    place_plant(e.pos)

        # Update game state
        if GS.health <= 0:
            GS.running = False

        if GS.running:
            GS.frame += 1
            GS.doze = max(0.0, min(1.0, GS.doze * CONSTANTS["DOZE_DECAY"] + 0.0008))  # slow drift to calm
            passive_sun_tick()
            maybe_advance_wave()
            spawn_zombie_if_needed()
            plants_act()
            update_bullets()
            update_zombies()

        # Draw
        screen.fill(c["bg"])
        draw_ui(screen)
        draw_grid(screen)
        draw_plants(screen)
        draw_bullets(screen)
        draw_zombies(screen)
        draw_fog(screen)
        draw_doze_meter(screen)

        if not GS.running:
            draw_text(screen, "Soft‑Reboot with R", W//2, H//2+26, 18, c["soft"], center=True)
            draw_text(screen, "Sweet dreams…", W//2, H//2-6, 22, c["white"], center=True)

        # Footer hint
        draw_text(screen, "Place plants with L‑Click • Calm > Speed • ESC quits", 10, H-34, 14, c["soft"])

        pygame.display.flip()
        clock.tick(CONSTANTS["FPS"])

if __name__ == "__main__":
    main()
