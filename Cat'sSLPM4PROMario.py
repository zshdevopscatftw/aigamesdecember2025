# platformer_onefile.py
# Single-file Pygame platformer engine with:
# - String/CSV tilemaps
# - AABB collisions + optional slopes
# - Sub-pixel physics (float pos, rects for broad-phase)
# - Camera with dead-zone + tile/object culling
# - dt-capped fixedish main loop
# - Sprite batching via pre-converted surfaces
# - Tiny on-screen profiler readout
#
# Python 3.9+ / Pygame 2.x
# Run:  python3 platformer_onefile.py

import sys, math, time, csv, io, random
import pygame

# --------------------------- Config ---------------------------
W, H       = 960, 540
SCALE      = 1
FPS        = 60
DT_CAP     = 1/30  # clamp dt spikes (e.g., window drag) to keep physics stable
TILE       = 32
GRAVITY    = 2100.0
AIR_DRAG   = 0.04
GROUND_DRAG= 0.16
RUN_ACCEL  = 2200.0
RUN_DECEL  = 2800.0
MAX_VX     = 360.0
JUMP_V     = 780.0
TERM_V     = 1800.0
SLOPE_MAX_DEG = 46

# Camera dead-zone (rectangle centered on player)
DEAD_W, DEAD_H = 220, 140

# Colors
BG  = (21, 22, 30)
INK = (230, 240, 255)
GR1 = (70, 90, 120)
GR2 = (40, 55, 80)
ACCENT = (255, 185, 85)

pygame.init()
pygame.display.set_caption("Onefile Platformer (dt-capped, slopes, camera DZ, profiler)")
screen = pygame.display.set_mode((W, H))
clock  = pygame.time.Clock()

# --------------------- Tiny profiler helper -------------------
class Prof:
    def __init__(self, n=60):
        self.samples = []
        self.n = n
        self.font = pygame.font.SysFont("consolas", 14)
        self.enabled = True
    def push(self, dt):
        self.samples.append(dt)
        if len(self.samples) > self.n:
            self.samples.pop(0)
    def draw(self, surf):
        if not self.enabled or not self.samples: return
        avg = sum(self.samples) / len(self.samples)
        ms  = avg * 1000
        fps = 1.0 / avg if avg > 0 else 0
        txt = f"{ms:5.1f} ms  {fps:5.1f} fps"
        img = self.font.render(txt, True, ACCENT)
        surf.blit(img, (8, 8))

prof = Prof()

# -------------------------- Assets ----------------------------
def make_tile_surface(color_a, color_b):
    s = pygame.Surface((TILE, TILE)).convert()
    s.fill(color_a)
    pygame.draw.rect(s, color_b, (0, 0, TILE, TILE), 2)
    return s

TILE_SOLID = make_tile_surface(GR2, GR1)
TILE_SLOPE = make_tile_surface((80, 110, 160), (120, 160, 210))
TILE_DECO  = make_tile_surface((35, 40, 60), (60, 70, 100))

PLAYER_IMG = pygame.Surface((26, 30), pygame.SRCALPHA).convert_alpha()
pygame.draw.rect(PLAYER_IMG, (255,255,255,220), (0,0,26,30), border_radius=6)
pygame.draw.rect(PLAYER_IMG, (60,130,255,255), (3,10,20,14), border_radius=4)

# --------------------- Map / Tile defs ------------------------
# Map legend:
#   '#' = solid block
#   '/' = slope up-left (ascending as x decreases)
#   '\' = slope up-right
#   '.' = empty
#   'd' = decorative (non-colliding)
LEVEL_STR = """
................................................
................................................
................................................
.....................d.....d...................
..............####.................../.........
.............######.................###........
......../...##########.............#####.......
.......###..###########...........#######......
......#####.###########..........#########.....
.....######################################....
.....######################################....
.....######################################....
.....######################################....
.....######################################....
"""

def parse_string_map(s):
    rows = [list(r) for r in s.strip("\n").split("\n")]
    h = len(rows); w = max(len(r) for r in rows)
    # pad uneven rows
    for r in rows:
        if len(r) < w:
            r += ['.']*(w-len(r))
    return rows, w, h

TILES, MAP_W, MAP_H = parse_string_map(LEVEL_STR)

# Optional: also accept CSV-style tilemaps; demonstrating parser:
CSV_SAMPLE = """.,.,.,.,.
#,.,\.,#,.
#,/,#,\,#,
#,.,.,.,#
#,.,.,.,#
"""
def parse_csv(cs):
    rdr = csv.reader(io.StringIO(cs))
    rows = [row for row in rdr if row]
    h = len(rows); w = max(len(r) for r in rows) if rows else 0
    # normalize empties
    out = []
    for r in rows:
        pad = r + ['.']*(w - len(r))
        out.append([c.strip() if c.strip() else '.' for c in pad])
    return out, w, h
# _csv_tiles, _csv_w, _csv_h = parse_csv(CSV_SAMPLE)

def tile_rect(tx, ty):
    return pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)

def is_solid(tok):
    return tok == '#'

def is_slope(tok):
    return tok in ('/', '\\')

def is_deco(tok):
    return tok == 'd'

# For slopes, we define line endpoints in tile-local coords (0..TILE)
def slope_line(tok):
    if tok == '/':   # up-left: low on right, high on left
        return (TILE, TILE, 0, 0)
    if tok == '\\':  # up-right: low on left, high on right
        return (0, TILE, TILE, 0)
    return None

# ------------------------ Camera ------------------------------
class Camera:
    def __init__(self):
        self.x = 0.0; self.y = 0.0
    def world_to_screen(self, rect):
        return pygame.Rect(int(rect.x - self.x), int(rect.y - self.y), rect.w, rect.h)
    def pos_to_screen(self, x, y):
        return (int(x - self.x), int(y - self.y))
    def update(self, target_rect):
        # dead-zone centered
        center_x = self.x + W*0.5
        center_y = self.y + H*0.5
        dz = pygame.Rect(int(center_x - DEAD_W*0.5), int(center_y - DEAD_H*0.5), DEAD_W, DEAD_H)
        if target_rect.centerx < dz.left:
            self.x = target_rect.centerx - DEAD_W*0.5 - (W*0.5 - DEAD_W*0.5)
        elif target_rect.centerx > dz.right:
            self.x = target_rect.centerx + DEAD_W*0.5 - (W*0.5 + DEAD_W*0.5)
        if target_rect.centery < dz.top:
            self.y = target_rect.centery - DEAD_H*0.5 - (H*0.5 - DEAD_H*0.5)
        elif target_rect.centery > dz.bottom:
            self.y = target_rect.centery + DEAD_H*0.5 - (H*0.5 + DEAD_H*0.5)
        # Clamp to map bounds (leave little margin)
        max_x = MAP_W*TILE - W
        max_y = MAP_H*TILE - H
        self.x = max(0, min(self.x, max(0, max_x)))
        self.y = max(0, min(self.y, max(0, max_y)))

camera = Camera()

# ----------------------- Player -------------------------------
class Player:
    def __init__(self, x, y):
        self.w, self.h = 26, 30
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.img = PLAYER_IMG
        self.flip = False
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def handle_input(self, dt, keys):
        ax = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= RUN_ACCEL
            self.flip = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += RUN_ACCEL
            self.flip = False

        # Horizontal accel/decel
        if ax == 0:
            # decel
            if abs(self.vx) < 1:
                self.vx = 0.0
            else:
                dec = RUN_DECEL * dt
                self.vx -= math.copysign(dec, self.vx)
        else:
            self.vx += ax * dt

        # Drag
        drag = GROUND_DRAG if self.on_ground else AIR_DRAG
        self.vx *= (1.0 - drag)

        # Clamp ground speed
        if self.on_ground:
            self.vx = max(-MAX_VX, min(MAX_VX, self.vx))

        # Jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_UP]) and self.on_ground:
            self.vy = -JUMP_V
            self.on_ground = False

    def integrate(self, dt):
        # Gravity
        self.vy += GRAVITY * dt
        if self.vy > TERM_V: self.vy = TERM_V
        # Apply sub-pixel integration
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, surf, cam):
        img = pygame.transform.flip(self.img, self.flip, False)
        surf.blit(img, cam.world_to_screen(self.rect))

player = Player(120, 0)

# ------------------- Collision / Queries ----------------------
def tiles_in_aabb(px, py, pw, ph):
    # cull queries to nearby tiles
    x0 = max(0, int((px)//TILE) - 2)
    y0 = max(0, int((py)//TILE) - 2)
    x1 = min(MAP_W-1, int((px+pw)//TILE) + 2)
    y1 = min(MAP_H-1, int((py+ph)//TILE) + 2)
    out = []
    for ty in range(y0, y1+1):
        row = TILES[ty]
        for tx in range(x0, x1+1):
            tok = row[tx]
            if tok != '.':
                out.append((tx, ty, tok))
    return out

def resolve_aabb_horizontal(p: Player):
    pr = p.rect
    hits = []
    for tx, ty, tok in tiles_in_aabb(pr.x, pr.y, pr.w, pr.h):
        if is_solid(tok) or is_slope(tok):
            tr = tile_rect(tx, ty)
            if pr.colliderect(tr):
                if p.vx > 0:
                    pr.right = tr.left
                    p.x = pr.x
                    p.vx = 0
                elif p.vx < 0:
                    pr.left = tr.right
                    p.x = pr.x
                    p.vx = 0
                hits.append((tx,ty,tok))
    return hits

def resolve_aabb_vertical(p: Player):
    pr = p.rect
    p.on_ground = False
    hits = []
    for tx, ty, tok in tiles_in_aabb(pr.x, pr.y, pr.w, pr.h):
        tr = tile_rect(tx, ty)
        if not pr.colliderect(tr):
            continue

        if is_solid(tok):
            if p.vy > 0:
                pr.bottom = tr.top
                p.y = pr.y
                p.vy = 0
                p.on_ground = True
            elif p.vy < 0:
                pr.top = tr.bottom
                p.y = pr.y
                p.vy = 0
            hits.append((tx,ty,tok))

        elif is_slope(tok):
            # Handle as ground if we're descending into the tile
            # Sample slope height at player's foot x
            x0, y0, x1, y1 = slope_line(tok)
            # line y(x) = y0 + (y1 - y0) * t, where t = (x - x0)/(x1 - x0)
            # Convert player foot world-x into tile-local
            foot_x = pr.centerx - tr.x
            foot_x = max(0, min(TILE, foot_x))
            if x1 != x0:
                t = (foot_x - x0) / (x1 - x0)
                y_at = y0 + (y1 - y0) * t
            else:
                y_at = min(y0, y1)
            ground_y_world = tr.y + y_at

            # Only push up if feet are below slope surface
            feet = pr.bottom
            if feet > ground_y_world - 0.5 and p.vy >= -60:
                pr.bottom = int(ground_y_world)
                p.y = pr.y
                p.vy = 0
                p.on_ground = True
                hits.append((tx,ty,tok))
    return hits

def update_player_with_collisions(p: Player, dt, keys):
    # Input first (affects velocity), then integrate, then collide separately on axes
    p.handle_input(dt, keys)

    # Horizontal integrate + collide
    p.x += p.vx * dt
    resolve_aabb_horizontal(p)

    # Vertical integrate + collide (includes slope response)
    p.y += p.vy * dt
    resolve_aabb_vertical(p)

# ------------------------ Rendering ---------------------------
def visible_tile_span(cam_x, cam_y):
    x0 = max(0, int(cam_x // TILE) - 1)
    y0 = max(0, int(cam_y // TILE) - 1)
    x1 = min(MAP_W-1, int((cam_x + W) // TILE) + 1)
    y1 = min(MAP_H-1, int((cam_y + H) // TILE) + 1)
    return x0, y0, x1, y1

def draw_map(surf, cam):
    x0, y0, x1, y1 = visible_tile_span(cam.x, cam.y)
    blit = surf.blit
    for ty in range(y0, y1+1):
        row = TILES[ty]
        for tx in range(x0, x1+1):
            tok = row[tx]
            if tok == '.': continue
            dst = (tx*TILE - cam.x, ty*TILE - cam.y)
            if tok == '#':
                blit(TILE_SOLID, dst)
            elif tok in ('/', '\\'):
                blit(TILE_SLOPE, dst)
                # draw slope line for debug
                x0l, y0l, x1l, y1l = slope_line(tok)
                pygame.draw.line(surf, ACCENT,
                                 (dst[0]+x0l, dst[1]+y0l),
                                 (dst[0]+x1l, dst[1]+y1l), 2)
            elif tok == 'd':
                blit(TILE_DECO, dst)

def draw_hud(surf):
    # Dead-zone outline for debug
    cx = int(camera.x + W*0.5 - DEAD_W*0.5)
    cy = int(camera.y + H*0.5 - DEAD_H*0.5)
    pygame.draw.rect(surf, (255,255,255,40), pygame.Rect(
        cx - camera.x, cy - camera.y, DEAD_W, DEAD_H), 1)

# --------------------------- Main -----------------------------
def main():
    running = True
    t_prev = time.perf_counter()

    # Simple “overworld/level” states (no assets) demo:
    state = "level"  # or "overworld"
    level_spawn = (120, 0)

    while running:
        # dt with clamp
        t_now = time.perf_counter()
        dt = t_now - t_prev
        t_prev = t_now
        if dt > DT_CAP: dt = DT_CAP

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_TAB:
                    # toggle state (no external assets needed)
                    nonlocal_state = None  # placeholder for closure clarity
                    # revive a minimal overworld swap
                    if state == "level":
                        state = "overworld"
                    else:
                        state = "level"
                if e.key == pygame.K_r:
                    # quick reset
                    player.x, player.y = level_spawn
                    player.vx = player.vy = 0.0

        keys = pygame.key.get_pressed()

        # Update
        if state == "level":
            update_player_with_collisions(player, dt, keys)
        else:
            # overworld: gentle float to show state separation
            player.vx = math.sin(pygame.time.get_ticks()*0.001)*40
            player.vy = math.cos(pygame.time.get_ticks()*0.001)*40
            player.x += player.vx * dt
            player.y += player.vy * dt

        # Camera follows player with dead-zone
        camera.update(player.rect)

        # Draw (batched by pre-converted surfaces)
        screen.fill(BG)
        draw_map(screen, camera)
        player.draw(screen, camera)
        draw_hud(screen)

        # Profiler
        prof.push(dt)
        prof.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        pass
