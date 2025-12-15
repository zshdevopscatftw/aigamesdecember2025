# ══════════════════════════════════════════════════════════════════════════════
# CAT'S BOTW M4 PYTHON PORT 1.0
# ══════════════════════════════════════════════════════════════════════════════
# PURE GRAYSCALE | NO TEXTURES | UNLIT FLAT SHADING | NOIR AESTHETIC
# Run: pip install ursina noise && python botw_m4_port.py

# ─────────────────────────────────────────────────────────────────────────────
# 🔧 PANDA3D CONFIG - SILENCE + COMPATIBILITY
# ─────────────────────────────────────────────────────────────────────────────
from panda3d.core import loadPrcFileData
loadPrcFileData('', '''
gl-version 2 1
basic-shaders-only #t
hardware-animated-vertices #f
framebuffer-multisample #f
multisamples 0
notify-level fatal
notify-level-glgsg fatal
notify-level-display fatal
notify-level-pnmimage fatal
notify-level-text fatal
win-size 800 600
''')

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import uniform, seed, randint
from math import sin
import noise

Entity.default_shader = None
Mesh.default_shader = None

# ─────────────────────────────────────────────────────────────────────────────
# 🎨 GRAYSCALE PALETTE (NO COLORS - PURE B&W)
# ─────────────────────────────────────────────────────────────────────────────
def gray(v): return color.rgb(v, v, v)

BLACK = gray(0)
NEAR_BLACK = gray(20)
DARK = gray(40)
SHADOW = gray(60)
MID_DARK = gray(80)
MID = gray(100)
MID_LIGHT = gray(120)
LIGHT = gray(150)
BRIGHT = gray(180)
OFF_WHITE = gray(210)
NEAR_WHITE = gray(235)
WHITE = gray(255)

# Semantic assignments (all grayscale)
C_SKY = gray(45)           # Dark gray sky
C_GRASS_LOW = gray(70)     # Dark grass
C_GRASS = gray(90)         # Medium grass
C_STONE = gray(110)        # Stone
C_MOUNTAIN = gray(140)     # Mountain
C_SNOW = gray(230)         # Snow peaks
C_WATER = color.rgba(30, 30, 30, 180)  # Dark water
C_TREE_TRUNK = gray(50)    # Dark trunk
C_TREE_LEAVES = gray(75)   # Dark foliage
C_ROCK = gray(100)         # Rocks
C_CLOUD = color.rgba(200, 200, 200, 150)  # Light clouds
C_ENEMY = gray(25)         # Near-black enemies
C_RUPEE = gray(220)        # Bright rupees (stand out)
C_HEART = gray(255)        # White hearts
C_STAMINA = gray(200)      # Light stamina
C_UI_BG = gray(20)         # UI background
C_UI_TEXT = gray(240)      # UI text
C_GLIDER = gray(180)       # Paraglider
C_KOROK = gray(255)        # Bright white korok

# ─────────────────────────────────────────────────────────────────────────────
# 🪟 APP INIT
# ─────────────────────────────────────────────────────────────────────────────
app = Ursina(
    title="Cat's BOTW M4 PYTHON PORT 1.0",
    borderless=False,
    fullscreen=False,
    development_mode=False,
    editor_ui_enabled=False
)

window.exit_button.visible = False
window.fps_counter.enabled = True
window.color = C_SKY  # Gray sky
camera.clip_plane_far = 600

# ─────────────────────────────────────────────────────────────────────────────
# ⛰️ TERRAIN GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def build_terrain(size=80, amplitude=35):
    print("[*] Generating terrain...")
    verts, tris, cols = [], [], []
    half = size // 2
    
    for z in range(size):
        for x in range(size):
            nx, nz = x * 0.03, z * 0.03
            h = noise.pnoise2(nx, nz, octaves=4, persistence=0.5, lacunarity=2.0)
            h += noise.pnoise2(nx * 2, nz * 2, octaves=2) * 0.3
            h = (h + 1) * 0.5
            
            y = (h ** 1.4) * amplitude
            
            # Grayscale by height
            if h > 0.72:
                c = C_SNOW
            elif h > 0.55:
                c = C_MOUNTAIN
            elif h > 0.35:
                c = C_STONE
            elif h > 0.2:
                c = C_GRASS
            else:
                c = C_GRASS_LOW
            
            verts.append(Vec3(x - half, y, z - half))
            cols.append(c)
    
    for z in range(size - 1):
        for x in range(size - 1):
            i = z * size + x
            tris.append((i, i + size, i + 1))
            tris.append((i + 1, i + size, i + size + 1))
    
    mesh = Mesh(vertices=verts, triangles=tris, colors=cols)
    mesh.generate_normals()
    print("[+] Terrain ready!")
    return mesh

terrain = Entity(
    model=build_terrain(),
    scale=5,
    collider='mesh',
    shader=None,
    unlit=True
)

# ─────────────────────────────────────────────────────────────────────────────
# 💧 WATER
# ─────────────────────────────────────────────────────────────────────────────
water = Entity(
    model='plane',
    scale=500,
    y=8,
    color=C_WATER,
    shader=None,
    unlit=True,
    double_sided=True
)

# ─────────────────────────────────────────────────────────────────────────────
# 🌳 TREES
# ─────────────────────────────────────────────────────────────────────────────
print("[*] Planting trees...")

def spawn_tree(pos):
    Entity(
        model='cube',
        scale=(0.6, 4, 0.6),
        position=pos + Vec3(0, 2, 0),
        color=C_TREE_TRUNK,
        shader=None,
        unlit=True
    )
    Entity(
        model='sphere',
        scale=3.5,
        position=pos + Vec3(0, 5.5, 0),
        color=C_TREE_LEAVES,
        shader=None,
        unlit=True
    )

tree_count = 0
seed(42)
for _ in range(100):
    x, z = uniform(-180, 180), uniform(-180, 180)
    hit = raycast(Vec3(x, 200, z), Vec3(0, -1, 0), distance=400)
    if hit.hit and hit.entity == terrain:
        if 12 < hit.point.y < 45:
            spawn_tree(hit.point)
            tree_count += 1

print(f"[+] {tree_count} trees planted!")

# ─────────────────────────────────────────────────────────────────────────────
# 🪨 ROCKS
# ─────────────────────────────────────────────────────────────────────────────
print("[*] Placing rocks...")

class Rock(Entity):
    def __init__(self, pos, has_korok=False):
        super().__init__(
            model='sphere',
            scale=(uniform(1, 2), uniform(0.8, 1.2), uniform(1, 2)),
            position=pos,
            color=C_ROCK,
            collider='box',
            shader=None,
            unlit=True
        )
        self.has_korok = has_korok
        self.grabbed = False
        self.original_pos = pos

rocks = []
for _ in range(50):
    x, z = uniform(-150, 150), uniform(-150, 150)
    hit = raycast(Vec3(x, 200, z), Vec3(0, -1, 0), distance=400)
    if hit.hit and hit.entity == terrain and hit.point.y > 10:
        has_korok = randint(0, 100) < 15
        rocks.append(Rock(hit.point + Vec3(0, 0.5, 0), has_korok))

print(f"[+] {len(rocks)} rocks placed!")

# ─────────────────────────────────────────────────────────────────────────────
# 💎 RUPEES (bright white - stand out in grayscale)
# ─────────────────────────────────────────────────────────────────────────────
print("[*] Scattering rupees...")

class Rupee(Entity):
    def __init__(self, pos, value):
        # Different brightness for different values
        shades = {1: gray(180), 5: gray(210), 20: gray(255)}
        super().__init__(
            model='diamond',
            scale=0.5,
            position=pos + Vec3(0, 1, 0),
            color=shades.get(value, gray(200)),
            shader=None,
            unlit=True
        )
        self.value = value
        self.bob_offset = uniform(0, 6.28)
        self.base_y = pos.y + 1
    
    def update(self):
        self.rotation_y += 90 * time.dt
        self.y = self.base_y + sin(time.time() * 2 + self.bob_offset) * 0.3

rupees = []
for _ in range(40):
    x, z = uniform(-150, 150), uniform(-150, 150)
    hit = raycast(Vec3(x, 200, z), Vec3(0, -1, 0), distance=400)
    if hit.hit and hit.entity == terrain and hit.point.y > 10:
        value = [1, 1, 1, 5, 5, 20][randint(0, 5)]
        rupees.append(Rupee(hit.point, value))

print(f"[+] {len(rupees)} rupees scattered!")

# ─────────────────────────────────────────────────────────────────────────────
# 👾 ENEMIES (near-black silhouettes)
# ─────────────────────────────────────────────────────────────────────────────
print("[*] Spawning enemies...")

class Bokoblin(Entity):
    def __init__(self, pos):
        super().__init__(
            model='sphere',
            scale=1.8,
            position=pos + Vec3(0, 1, 0),
            color=C_ENEMY,
            collider='sphere',
            shader=None,
            unlit=True
        )
        self.speed = 5
        self.home = pos
        self.hp = 3
    
    def update(self):
        if not hasattr(self, 'target') or not self.target:
            return
        
        dist = distance_xz(self, self.target)
        
        if dist < 40:
            self.look_at_2d(self.target.position, 'y')
            if dist > 3:
                self.position += self.forward * self.speed * time.dt
            self.y = self.home.y + 1 + sin(time.time() * 8) * 0.15
        
        hit = raycast(self.position + Vec3(0, 5, 0), Vec3(0, -1, 0), distance=20)
        if hit.hit:
            self.y = max(self.y, hit.point.y + 1)

enemies = []
for _ in range(12):
    x, z = uniform(-100, 100), uniform(-100, 100)
    hit = raycast(Vec3(x, 200, z), Vec3(0, -1, 0), distance=400)
    if hit.hit and hit.entity == terrain and hit.point.y > 12:
        enemies.append(Bokoblin(hit.point))

print(f"[+] {len(enemies)} enemies spawned!")

# ─────────────────────────────────────────────────────────────────────────────
# ☁️ CLOUDS
# ─────────────────────────────────────────────────────────────────────────────
print("[*] Adding clouds...")

for _ in range(25):
    Entity(
        model='sphere',
        scale=(uniform(15, 40), uniform(8, 15), uniform(15, 30)),
        position=(uniform(-250, 250), uniform(90, 130), uniform(-250, 250)),
        color=C_CLOUD,
        shader=None,
        unlit=True
    )

print("[+] Clouds added!")

# ─────────────────────────────────────────────────────────────────────────────
# 🎮 PLAYER
# ─────────────────────────────────────────────────────────────────────────────
class Link(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = 8
        self.run_speed = 16
        self.jump_height = 3
        self.gravity = 1.0
        
        self.max_stamina = 100
        self.stamina = 100
        self.max_health = 100
        self.health = 100
        self.rupee_count = 0
        self.korok_count = 0
        
        self.is_gliding = False
        self.glider = None
        self.held_rock = None
        self.invincible = 0
        
        self._build_ui()
        
        for e in enemies:
            e.target = self
    
    def _build_ui(self):
        # Hearts (white squares)
        self.hearts = []
        for i in range(5):
            h = Entity(
                parent=camera.ui,
                model='quad',
                scale=0.035,
                position=(-0.85 + i * 0.05, 0.45),
                color=C_HEART,
                shader=None,
                unlit=True
            )
            self.hearts.append(h)
        
        # Stamina bar
        self.stam_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.25, 0.012),
            position=(-0.72, 0.4),
            color=DARK,
            shader=None
        )
        self.stam_bar = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.25, 0.012),
            position=(-0.72, 0.4),
            color=C_STAMINA,
            shader=None
        )
        
        # Counters
        self.rupee_text = Text(
            text='RUPEES: 0',
            position=(-0.85, 0.35),
            scale=1,
            color=C_UI_TEXT
        )
        
        self.korok_text = Text(
            text='KOROKS: 0',
            position=(-0.85, 0.31),
            scale=1,
            color=C_UI_TEXT
        )
        
        # Title
        Text(
            text="CAT'S BOTW M4 PYTHON PORT 1.0",
            position=(0, 0.47),
            origin=(0, 0),
            scale=1.2,
            color=C_UI_TEXT
        )
        
        # Controls
        Text(
            text='WASD: Move | SHIFT: Run | SPACE: Jump/Glide | E: Grab/Throw',
            position=(0, -0.45),
            origin=(0, 0),
            scale=0.8,
            color=gray(160)
        )
    
    def update(self):
        if held_keys['shift'] and self.stamina > 0 and self.grounded:
            self.speed = self.run_speed
            self.stamina -= 25 * time.dt
        else:
            self.speed = 8
            if self.grounded:
                self.stamina = min(self.stamina + 15 * time.dt, self.max_stamina)
        
        if self.is_gliding:
            self.stamina -= 20 * time.dt
            if self.stamina <= 0:
                self.stop_glide()
        
        ratio = self.stamina / self.max_stamina
        self.stam_bar.scale_x = 0.25 * ratio
        self.stam_bar.x = -0.72 - (0.25 * (1 - ratio)) / 2
        
        if self.grounded and self.is_gliding:
            self.stop_glide()
        
        if self.invincible > 0:
            self.invincible -= time.dt
        
        self._check_rupees()
        self._check_enemies()
        
        if self.held_rock:
            self.held_rock.position = self.position + self.forward * 2 + Vec3(0, 2, 0)
        
        super().update()
    
    def _check_rupees(self):
        for r in rupees[:]:
            if distance(self, r) < 2:
                self.rupee_count += r.value
                self.rupee_text.text = f'RUPEES: {self.rupee_count}'
                rupees.remove(r)
                destroy(r)
    
    def _check_enemies(self):
        if self.invincible > 0:
            return
        for e in enemies:
            if distance(self, e) < 2.5:
                self.health -= 20
                self.invincible = 1.0
                self._update_hearts()
                print(f"[!] Hit! Health: {self.health}")
                if self.health <= 0:
                    print("[X] Game Over!")
    
    def _update_hearts(self):
        filled = int((self.health / self.max_health) * 5)
        for i, h in enumerate(self.hearts):
            h.color = C_HEART if i < filled else DARK
    
    def input(self, key):
        super().input(key)
        
        if key == 'space' and not self.grounded and self.stamina > 10:
            if self.is_gliding:
                self.stop_glide()
            else:
                self.start_glide()
        
        if key == 'e':
            if self.held_rock:
                self.throw_rock()
            else:
                self.grab_rock()
    
    def start_glide(self):
        if self.is_gliding:
            return
        self.is_gliding = True
        self.gravity = 0.15
        self.glider = Entity(
            parent=self,
            model='quad',
            scale=(5, 3),
            y=2.5,
            rotation_x=90,
            color=C_GLIDER,
            double_sided=True,
            shader=None,
            unlit=True
        )
    
    def stop_glide(self):
        if not self.is_gliding:
            return
        self.is_gliding = False
        self.gravity = 1.0
        if self.glider:
            destroy(self.glider)
            self.glider = None
    
    def grab_rock(self):
        for r in rocks:
            if distance(self, r) < 3 and not r.grabbed:
                r.grabbed = True
                r.collider = None
                self.held_rock = r
                return
    
    def throw_rock(self):
        if not self.held_rock:
            return
        rock = self.held_rock
        rock.grabbed = False
        self.held_rock = None
        
        if rock.has_korok:
            self.korok_count += 1
            self.korok_text.text = f'KOROKS: {self.korok_count}'
            rock.has_korok = False
            print("[*] YAHAHA! Korok found!")
            korok = Entity(
                model='sphere',
                scale=0.8,
                position=rock.position + Vec3(0, 1, 0),
                color=C_KOROK,
                shader=None,
                unlit=True
            )
            destroy(korok, delay=2)
        
        rock.animate_position(
            rock.position + self.forward * 15 + Vec3(0, 5, 0),
            duration=0.3,
            curve=curve.out_expo
        )
        
        for e in enemies[:]:
            if distance(rock, e) < 4:
                e.hp -= 1
                if e.hp <= 0:
                    enemies.remove(e)
                    destroy(e)
                    print("[!] Enemy defeated!")
        
        invoke(lambda: setattr(rock, 'collider', 'box'), delay=0.5)

# ─────────────────────────────────────────────────────────────────────────────
# 🎬 START
# ─────────────────────────────────────────────────────────────────────────────
print("""
================================================================
  CAT'S BOTW M4 PYTHON PORT 1.0
================================================================
  GRAYSCALE NOIR EDITION
  No textures | Pure geometry | Flat unlit shading
----------------------------------------------------------------
  WASD       - Move
  SHIFT      - Sprint
  SPACE      - Jump / Glide
  E          - Grab / Throw rocks
  Mouse      - Look
----------------------------------------------------------------
  * Lift rocks for Koroks (bright white flash)
  * Collect rupees (bright objects)
  * Dark silhouettes are enemies!
================================================================
""")

player = Link(position=(0, 80, 0))

app.run()
