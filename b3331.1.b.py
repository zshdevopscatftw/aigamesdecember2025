import math
import pygame

# =========================
# Minimal "SM64-ish" 3D + Physics demo (single-file, no external assets)
# =========================

# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SAMSOFT ! B3313 ! 1.0 - SM64-ish Physics + Tiny 3D Engine")
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont(None, 48)
SMALL_FONT = pygame.font.SysFont(None, 24)

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
PINK  = (255, 105, 180)
YELLOW= (255, 255, 0)
BLUE  = (0, 0, 255)

# =========================
# Math helpers
# =========================
class Vec3:
    __slots__ = ("x", "y", "z")
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x); self.y = float(y); self.z = float(z)

    def __add__(self, o): return Vec3(self.x + o.x, self.y + o.y, self.z + o.z)
    def __sub__(self, o): return Vec3(self.x - o.x, self.y - o.y, self.z - o.z)
    def __mul__(self, s): return Vec3(self.x * s, self.y * s, self.z * s)
    __rmul__ = __mul__
    def __truediv__(self, s): return Vec3(self.x / s, self.y / s, self.z / s)

    def dot(self, o): return self.x * o.x + self.y * o.y + self.z * o.z
    def cross(self, o):
        return Vec3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x,
        )

    def length(self): return math.sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
    def normalized(self):
        l = self.length()
        return self if l == 0 else self / l

    def copy(self): return Vec3(self.x, self.y, self.z)

def approach(cur, target, step):
    if cur < target: return min(cur + step, target)
    if cur > target: return max(cur - step, target)
    return cur

def rotate_x(v: Vec3, a: float) -> Vec3:
    ca, sa = math.cos(a), math.sin(a)
    return Vec3(v.x, v.y * ca - v.z * sa, v.y * sa + v.z * ca)

def rotate_y(v: Vec3, a: float) -> Vec3:
    ca, sa = math.cos(a), math.sin(a)
    return Vec3(v.x * ca + v.z * sa, v.y, -v.x * sa + v.z * ca)

def rotate_z(v: Vec3, a: float) -> Vec3:
    ca, sa = math.cos(a), math.sin(a)
    return Vec3(v.x * ca - v.y * sa, v.x * sa + v.y * ca, v.z)

# =========================
# Tiny software 3D engine
# =========================
class Camera:
    def __init__(self, fov_deg=70.0, near=1.0):
        self.pos = Vec3(0, 0, -200)
        self.yaw = 0.0
        self.pitch = 0.0
        self.near = near
        self.fov = math.radians(fov_deg)
        self.f = (WIDTH * 0.5) / math.tan(self.fov * 0.5)

    def look_at(self, pos: Vec3, target: Vec3):
        self.pos = pos.copy()
        d = target - pos
        # yaw: 0 means looking along +Z
        self.yaw = math.atan2(d.x, d.z)
        horiz = math.sqrt(d.x*d.x + d.z*d.z)
        self.pitch = -math.atan2(d.y, horiz if horiz > 1e-6 else 1e-6)

    def world_to_camera(self, p: Vec3) -> Vec3:
        # translate
        v = p - self.pos
        # rotate around Y by -yaw
        cy, sy = math.cos(-self.yaw), math.sin(-self.yaw)
        x1 = v.x * cy + v.z * sy
        z1 = -v.x * sy + v.z * cy
        # rotate around X by -pitch
        cp, sp = math.cos(-self.pitch), math.sin(-self.pitch)
        y2 = v.y * cp - z1 * sp
        z2 = v.y * sp + z1 * cp
        return Vec3(x1, y2, z2)

    def project(self, p_world: Vec3):
        p = self.world_to_camera(p_world)
        if p.z <= self.near:
            return None, None
        x = (p.x / p.z) * self.f + WIDTH * 0.5
        y = (-p.y / p.z) * self.f + HEIGHT * 0.5
        return (x, y), p.z

class Mesh:
    def __init__(self, vertices, edges=None, faces=None, color=WHITE):
        self.vertices = [Vec3(*v) for v in vertices]
        self.edges = edges or []
        self.faces = faces or []   # optional triangles
        self.color = color
        self.rotation = Vec3(0.0, 0.0, 0.0)
        self.position = Vec3(0.0, 0.0, 0.0)

    def rotate(self, axis: int, angle: float):
        if axis == 0: self.rotation.x += angle
        elif axis == 1: self.rotation.y += angle
        elif axis == 2: self.rotation.z += angle

    def world_vertices(self):
        out = []
        for v in self.vertices:
            r = rotate_x(v, self.rotation.x)
            r = rotate_y(r, self.rotation.y)
            r = rotate_z(r, self.rotation.z)
            out.append(r + self.position)
        return out

    def draw_wireframe(self, surf, cam: Camera, width_px=2):
        wv = self.world_vertices()
        proj = [cam.project(p)[0] for p in wv]
        for a, b in self.edges:
            pa = proj[a]; pb = proj[b]
            if pa and pb:
                pygame.draw.line(surf, self.color, pa, pb, width_px)

# =========================
# Collision surfaces (SM64-inspired: floor triangles + simple bounds walls)
# =========================
class Triangle:
    __slots__ = ("a", "b", "c", "n")
    def __init__(self, a: Vec3, b: Vec3, c: Vec3):
        self.a = a; self.b = b; self.c = c
        self.n = (b - a).cross(c - a).normalized()

def point_in_tri_2d(px, pz, ax, az, bx, bz, cx, cz):
    # barycentric in XZ plane
    v0x, v0z = cx - ax, cz - az
    v1x, v1z = bx - ax, bz - az
    v2x, v2z = px - ax, pz - az

    dot00 = v0x*v0x + v0z*v0z
    dot01 = v0x*v1x + v0z*v1z
    dot02 = v0x*v2x + v0z*v2z
    dot11 = v1x*v1x + v1z*v1z
    dot12 = v1x*v2x + v1z*v2z

    denom = (dot00 * dot11 - dot01 * dot01)
    if abs(denom) < 1e-9:
        return False
    inv = 1.0 / denom
    u = (dot11 * dot02 - dot01 * dot12) * inv
    v = (dot00 * dot12 - dot01 * dot02) * inv
    return (u >= 0.0) and (v >= 0.0) and (u + v <= 1.0)

class Level:
    def __init__(self, meshes, floor_tris=None, bounds=None):
        self.meshes = meshes
        self.floor_tris = floor_tris or []
        # bounds = (minx, maxx, minz, maxz) for simple "wall" collisions
        self.bounds = bounds

    def find_floor(self, x, z, y_probe, step_up=60.0, max_drop=2000.0):
        # SM64-ish 'find floor' scan:
        # - vertical line at (x,z)
        # - find highest floor triangle under y_probe+step_up
        best_y = -1e9
        best_n = Vec3(0, 1, 0)
        for t in self.floor_tris:
            if t.n.y <= 0.01:
                continue
            if not point_in_tri_2d(x, z, t.a.x, t.a.z, t.b.x, t.b.z, t.c.x, t.c.z):
                continue
            if abs(t.n.y) < 1e-6:
                continue
            y = t.a.y - (t.n.x * (x - t.a.x) + t.n.z * (z - t.a.z)) / t.n.y
            if y > y_probe + step_up:
                continue
            if y < y_probe - max_drop:
                continue
            if y > best_y:
                best_y = y
                best_n = t.n
        return best_y, best_n

    def collide_bounds(self, pos: Vec3, vel: Vec3, radius: float):
        if not self.bounds:
            return
        minx, maxx, minz, maxz = self.bounds
        if pos.x < minx + radius:
            pos.x = minx + radius
            vel.x = 0
        elif pos.x > maxx - radius:
            pos.x = maxx - radius
            vel.x = 0
        if pos.z < minz + radius:
            pos.z = minz + radius
            vel.z = 0
        elif pos.z > maxz - radius:
            pos.z = maxz - radius
            vel.z = 0

# =========================
# SM64-ish player controller (simplified)
# =========================
class Player:
    def __init__(self, start_pos: Vec3):
        self.pos = start_pos.copy()
        self.vel = Vec3(0, 0, 0)
        self.yaw = 0.0  # facing angle; 0 means +Z
        self.on_ground = False
        self.floor_n = Vec3(0, 1, 0)

        # tunables (rough SM64 vibe, not exact)
        self.radius = 12.0
        self.walk_speed = 7.0
        self.run_speed = 12.0
        self.ground_accel = 0.9
        self.air_accel = 0.35
        self.friction = 0.82

        self.jump_vel = 12.0
        self.gravity = 0.55
        self.term_vel = -24.0

    def update(self, move_world: Vec3, jump_pressed: bool, running: bool, level: Level):
        # desired direction
        move_mag = math.sqrt(move_world.x*move_world.x + move_world.z*move_world.z)
        if move_mag > 1e-6:
            move_dir = Vec3(move_world.x / move_mag, 0.0, move_world.z / move_mag)
            self.yaw = math.atan2(move_dir.x, move_dir.z)
        else:
            move_dir = Vec3(0, 0, 0)

        # floor probe (SM64 does this every frame)
        floor_y, floor_n = level.find_floor(self.pos.x, self.pos.z, self.pos.y)
        self.floor_n = floor_n
        self.on_ground = (floor_y > -1e8) and (abs(self.pos.y - floor_y) <= 0.5)

        # jump
        if jump_pressed and self.on_ground:
            self.vel.y = self.jump_vel
            self.on_ground = False

        target_speed = self.run_speed if running else self.walk_speed

        # horizontal accel / friction
        if self.on_ground:
            if move_mag <= 1e-6:
                self.vel.x *= self.friction
                self.vel.z *= self.friction
            else:
                desired_vx = move_dir.x * target_speed
                desired_vz = move_dir.z * target_speed
                self.vel.x = approach(self.vel.x, desired_vx, self.ground_accel)
                self.vel.z = approach(self.vel.z, desired_vz, self.ground_accel)
        else:
            if move_mag > 1e-6:
                desired_vx = move_dir.x * target_speed
                desired_vz = move_dir.z * target_speed
                self.vel.x = approach(self.vel.x, desired_vx, self.air_accel)
                self.vel.z = approach(self.vel.z, desired_vz, self.air_accel)

        # gravity
        self.vel.y = max(self.vel.y - self.gravity, self.term_vel)

        # integrate
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y
        self.pos.z += self.vel.z

        # wall bounds
        level.collide_bounds(self.pos, self.vel, self.radius)

        # resolve floor after move
        floor_y2, floor_n2 = level.find_floor(self.pos.x, self.pos.z, self.pos.y)
        if floor_y2 > -1e8 and self.pos.y < floor_y2:
            self.pos.y = floor_y2
            self.vel.y = 0.0
            self.on_ground = True
            self.floor_n = floor_n2
        else:
            self.on_ground = False

# =========================
# HUD (kept from your original vibe)
# =========================
lives = 3
coins = 0
stars = 0
health = 8

def draw_beta_hud(screen):
    pygame.draw.circle(screen, RED, (40, 40), 20, 2)
    screen.blit(SMALL_FONT.render(f"x {lives}", True, WHITE), (70, 30))

    pygame.draw.circle(screen, YELLOW, (40, 80), 10, 2)
    screen.blit(SMALL_FONT.render(f"x {coins}", True, WHITE), (70, 70))

    star_points = [(40, 120), (50, 100), (60, 120), (50, 140)]
    pygame.draw.lines(screen, YELLOW, True, star_points, 2)
    screen.blit(SMALL_FONT.render(f"x {stars}", True, WHITE), (70, 110))

    pygame.draw.circle(screen, BLUE, (WIDTH - 50, 50), 30, 0)
    angle = (8 - health) / 8 * 2 * math.pi
    pygame.draw.arc(screen, BLACK, (WIDTH - 80, 20, 60, 60), 0, angle, 30)
    screen.blit(SMALL_FONT.render("POWER", True, WHITE), (WIDTH - 80, 80))

# =========================
# Meshes (your original wireframes)
# =========================
castle_vertices = [
    [-100, -50, -100], [100, -50, -100], [100, -50, 100], [-100, -50, 100],
    [-100, 50, -100], [100, 50, -100], [100, 50, 100], [-100, 50, 100],
    [0, 50, 0], [0, 100, 0], [-20, 50, -20], [20, 50, -20], [20, 50, 20], [-20, 50, 20],
    [-20, 100, -20], [20, 100, -20], [20, 100, 20], [-20, 100, 20],
    [0, 150, 0]
]
castle_edges = [
    [0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4],
    [0,4], [1,5], [2,6], [3,7],
    [10,11], [11,12], [12,13], [13,10],
    [14,15], [15,16], [16,17], [17,14],
    [10,14], [11,15], [12,16], [13,17],
    [8,4], [8,5], [8,6], [8,7],
    [14,18], [15,18], [16,18], [17,18]
]
castle = Mesh(castle_vertices, edges=castle_edges, color=WHITE)

spaceworld_vertices = [
    [-200, -50, -200], [200, -50, -200], [200, -50, 200], [-200, -50, 200],
    [-100, -50, -100], [-50, -50, -100], [-50, -50, -50], [-100, -50, -50],
    [-75, 20, -75],
    [50, -50, 50], [100, -50, 50], [100, -50, 100], [50, -50, 100],
    [75, 30, 75]
]
spaceworld_edges = [
    [0,1], [1,2], [2,3], [3,0],
    [4,5], [5,6], [6,7], [7,4], [4,8], [5,8], [6,8], [7,8],
    [9,10], [10,11], [11,12], [12,9], [9,13], [10,13], [11,13], [12,13]
]
spaceworld = Mesh(spaceworld_vertices, edges=spaceworld_edges, color=WHITE)

wireframe_vertices = [
    [0, 40, 0], [10, 50, 0], [-10, 50, 0], [0, 60, 0],
    [0, 20, 0], [15, 20, 0], [-15, 20, 0], [0, 0, 0],
    [15, 20, 0], [30, 10, 0], [-15, 20, 0], [-30, 10, 0],
    [10, 0, 0], [10, -30, 0], [-10, 0, 0], [-10, -30, 0]
]
wireframe_edges = [
    [0,1], [1,3], [3,2], [2,0],
    [4,5], [5,7], [7,6], [6,4],
    [0,4],
    [5,9], [6,11],
    [7,13], [7,15]
]
wireframe_fighter = Mesh(wireframe_vertices, edges=wireframe_edges, color=PINK)
wireframe_fighter.position = Vec3(80, -50, 120)

courtyard_vertices = [
    [-200, -50, -200], [200, -50, -200], [200, -50, 200], [-200, -50, 200],
    [-200, -50, -200], [-200, 20, -200], [200, 20, -200], [200, -50, -200],
    [-200, -50, 200], [-200, 20, 200], [200, 20, 200], [200, -50, 200],
    [-200, -50, -200], [-200, 20, -200], [-200, 20, 200], [-200, -50, 200],
    [200, -50, -200], [200, 20, -200], [200, 20, 200], [200, -50, 200],
    [0, -50, 0], [20, -50, 0], [14, -50, 14], [0, -50, 20], [-14, -50, 14], [-20, -50, 0], [-14, -50, -14], [0, -50, -20], [14, -50, -14],
    [0, -30, 0], [15, -30, 0], [10, -30, 10], [0, -30, 15], [-10, -30, 10], [-15, -30, 0], [-10, -30, -10], [0, -30, -15], [10, -30, -10],
    [-100, -50, -100], [-50, -50, -100], [-50, 0, -100], [-100, 0, -100],
    [-100, -50, -50], [-50, -50, -50], [-50, 0, -50], [-100, 0, -50],
    [50, -50, 50], [100, -50, 50], [100, 0, 50], [50, 0, 50],
    [50, -50, 100], [100, -50, 100], [100, 0, 100], [50, 0, 100]
]
courtyard_edges = [
    [0,1], [1,2], [2,3], [3,0],
    [4,5], [5,6], [6,7], [7,4],
    [8,9], [9,10], [10,11], [11,8],
    [12,13], [13,14], [14,15], [15,12],
    [16,17], [17,18], [18,19], [19,16],
    [20,21], [21,22], [22,23], [23,24], [24,25], [25,26], [26,27], [27,28], [28,20],
    [29,30], [30,31], [31,32], [32,33], [33,34], [34,35], [35,36], [36,37], [37,29],
    [20,29], [21,30], [22,31], [23,32], [24,33], [25,34], [26,35], [27,36], [28,37],
    [38,39], [39,40], [40,41], [41,38], [38,42], [39,43], [40,44], [41,45], [42,43], [43,44], [44,45], [45,42],
    [46,47], [47,48], [48,49], [49,46], [46,50], [47,51], [48,52], [49,53], [50,51], [51,52], [52,53], [53,50]
]
courtyard = Mesh(courtyard_vertices, edges=courtyard_edges, color=WHITE)

# Player visible cube
player_cube = Mesh(
    vertices=[
        [-8, 0, -8], [8, 0, -8], [8, 0, 8], [-8, 0, 8],
        [-8, 24, -8], [8, 24, -8], [8, 24, 8], [-8, 24, 8],
    ],
    edges=[
        [0,1],[1,2],[2,3],[3,0],
        [4,5],[5,6],[6,7],[7,4],
        [0,4],[1,5],[2,6],[3,7]
    ],
    color=YELLOW
)

# =========================
# Floors
# =========================
def floor_from_quad(v0, v1, v2, v3):
    a = Vec3(*v0); b = Vec3(*v1); c = Vec3(*v2); d = Vec3(*v3)
    return [Triangle(a,b,c), Triangle(a,c,d)]

overworld_floor = floor_from_quad([-300,-50,-300],[300,-50,-300],[300,-50,300],[-300,-50,300])

sw = [Vec3(*p) for p in spaceworld_vertices]
spaceworld_floor = [
    Triangle(sw[0], sw[1], sw[2]), Triangle(sw[0], sw[2], sw[3]),
    Triangle(sw[4], sw[5], sw[8]), Triangle(sw[5], sw[6], sw[8]),
    Triangle(sw[6], sw[7], sw[8]), Triangle(sw[7], sw[4], sw[8]),
    Triangle(sw[9], sw[10], sw[13]), Triangle(sw[10], sw[11], sw[13]),
    Triangle(sw[11], sw[12], sw[13]), Triangle(sw[12], sw[9], sw[13]),
]

cv = [Vec3(*p) for p in courtyard_vertices]
courtyard_floor = [Triangle(cv[0], cv[1], cv[2]), Triangle(cv[0], cv[2], cv[3])]

LEVEL_OVERWORLD = Level(meshes=[castle], floor_tris=overworld_floor, bounds=(-260, 260, -260, 260))
LEVEL_TECHDEMO  = Level(meshes=[castle, wireframe_fighter], floor_tris=overworld_floor, bounds=(-260, 260, -260, 260))
LEVEL_SPACEWORLD= Level(meshes=[spaceworld], floor_tris=spaceworld_floor, bounds=(-220, 220, -220, 220))
LEVEL_COURTYARD = Level(meshes=[courtyard], floor_tris=courtyard_floor, bounds=(-190, 190, -190, 190))

# =========================
# States
# =========================
STATE_INTRO = -1
STATE_MENU = 0
STATE_OVERWORLD = 1
STATE_TECHDEMO = 2
STATE_SPACEWORLD = 3
STATE_COURTYARD = 4

state = STATE_INTRO
start_time_ms = pygame.time.get_ticks()

player = Player(start_pos=Vec3(0, -50, 0))
camera = Camera(fov_deg=70.0, near=5.0)
cam_yaw = 0.0
cam_dist = 240.0
cam_height = 140.0

def reset_player():
    player.pos = Vec3(0, -50, 0)
    player.vel = Vec3(0, 0, 0)
    player.yaw = 0.0

def current_level():
    if state == STATE_OVERWORLD: return LEVEL_OVERWORLD
    if state == STATE_TECHDEMO: return LEVEL_TECHDEMO
    if state == STATE_SPACEWORLD: return LEVEL_SPACEWORLD
    if state == STATE_COURTYARD: return LEVEL_COURTYARD
    return LEVEL_OVERWORLD

# =========================
# Main loop
# =========================
running = True
while running:
    SCREEN.fill(BLACK)

    jump_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and state not in (STATE_INTRO, STATE_MENU):
                state = STATE_MENU
            if event.key == pygame.K_SPACE:
                jump_pressed = True
            if event.key == pygame.K_r and state not in (STATE_INTRO, STATE_MENU):
                reset_player()

        if event.type == pygame.MOUSEBUTTONDOWN and state == STATE_MENU:
            mx, my = pygame.mouse.get_pos()
            if 200 < mx < 600 and 150 < my < 200:
                state = STATE_OVERWORLD; reset_player()
            if 200 < mx < 600 and 250 < my < 300:
                state = STATE_TECHDEMO; reset_player()
            if 200 < mx < 600 and 350 < my < 400:
                state = STATE_SPACEWORLD; reset_player()
            if 200 < mx < 600 and 450 < my < 500:
                state = STATE_COURTYARD; reset_player()

    keys = pygame.key.get_pressed()

    if state == STATE_INTRO:
        SCREEN.blit(FONT.render("SAMSOFT ! B3313 ! 1.0", True, RED), (150, 250))
        SCREEN.blit(SMALL_FONT.render("Intro auto-continues...", True, WHITE), (290, 310))
        if pygame.time.get_ticks() - start_time_ms > 2500:
            state = STATE_MENU

    elif state == STATE_MENU:
        SCREEN.blit(FONT.render("B3313 Pygame Edition", True, RED), (150, 50))
        pygame.draw.rect(SCREEN, WHITE, (200, 150, 400, 50), 2)
        SCREEN.blit(FONT.render("Overworld", True, WHITE), (300, 160))
        pygame.draw.rect(SCREEN, WHITE, (200, 250, 400, 50), 2)
        SCREEN.blit(FONT.render("Tech Demo", True, WHITE), (300, 260))
        pygame.draw.rect(SCREEN, WHITE, (200, 350, 400, 50), 2)
        SCREEN.blit(FONT.render("Debug Space World", True, WHITE), (240, 360))
        pygame.draw.rect(SCREEN, WHITE, (200, 450, 400, 50), 2)
        SCREEN.blit(FONT.render("Peach's Courtyard", True, WHITE), (240, 460))

        help_lines = [
            "Controls:",
            "WASD move (camera-relative), SHIFT run, SPACE jump",
            "Q/E orbit camera, R to respawn, ESC to menu",
        ]
        y = 530
        for line in help_lines:
            SCREEN.blit(SMALL_FONT.render(line, True, WHITE), (20, y))
            y += 18

    else:
        # camera orbit control
        if keys[pygame.K_q]:
            cam_yaw -= 0.04
        if keys[pygame.K_e]:
            cam_yaw += 0.04

        # build move vector in camera space
        local_x = 0.0
        local_z = 0.0
        if keys[pygame.K_w]: local_z += 1.0
        if keys[pygame.K_s]: local_z -= 1.0
        if keys[pygame.K_d]: local_x += 1.0
        if keys[pygame.K_a]: local_x -= 1.0

        # camera-relative to world (SM64-style)
        cy, sy = math.cos(cam_yaw), math.sin(cam_yaw)
        move_world = Vec3(
            local_x * cy + local_z * sy,
            0.0,
            -local_x * sy + local_z * cy
        )

        running_fast = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        lvl = current_level()

        if state == STATE_TECHDEMO:
            castle.rotate(1, 0.02)

        player.update(move_world=move_world, jump_pressed=jump_pressed, running=running_fast, level=lvl)

        # camera look-at
        target = player.pos + Vec3(0, 55, 0)
        orbit = Vec3(math.sin(cam_yaw), 0.0, math.cos(cam_yaw)) * cam_dist
        cam_pos = target - orbit + Vec3(0, cam_height, 0)
        camera.look_at(cam_pos, target)

        # draw world
        for m in lvl.meshes:
            m.draw_wireframe(SCREEN, camera, width_px=2)

        # draw player cube
        player_cube.position = player.pos
        player_cube.draw_wireframe(SCREEN, camera, width_px=2)

        # title
        if state == STATE_OVERWORLD:
            SCREEN.blit(FONT.render("Peach's Castle Overworld", True, WHITE), (160, 50))
        elif state == STATE_TECHDEMO:
            SCREEN.blit(FONT.render("Tech Demo (SM64-ish physics)", True, RED), (150, 50))
        elif state == STATE_SPACEWORLD:
            SCREEN.blit(FONT.render("Debug Space World Beta", True, WHITE), (185, 50))
            pygame.draw.rect(SCREEN, WHITE, (WIDTH - 110, 10, 100, 100), 1)
            SCREEN.blit(SMALL_FONT.render("Minimap", True, WHITE), (WIDTH - 95, 50))
        elif state == STATE_COURTYARD:
            SCREEN.blit(FONT.render("Peach's Castle Courtyard", True, WHITE), (150, 50))

        # debug
        dbg = f"pos=({player.pos.x:.1f},{player.pos.y:.1f},{player.pos.z:.1f}) vel=({player.vel.x:.1f},{player.vel.y:.1f},{player.vel.z:.1f}) ground={player.on_ground}"
        SCREEN.blit(SMALL_FONT.render(dbg, True, WHITE), (10, HEIGHT - 24))

        draw_beta_hud(SCREEN)

    pygame.display.flip()
    CLOCK.tick(60)

pygame.quit()
