# ══════════════════════════════════════════════════════════════════════════════
# WHOLSOME POWNEY COUNCIL 0.2 - BOTW ENGINE ULTRA-FLUFFY EDITION
# ══════════════════════════════════════════════════════════════════════════════
# 100% GORE-FREE | 1000% KITTEN ENERGY | PURE UNLIT | FILES = OFF
# Run: pip install ursina noise && python botw_ultra.py

# ─────────────────────────────────────────────────────────────────────────────
# 🔥 HARD SHADER / LOG NUKE (ABSOLUTE SILENCE)
# ─────────────────────────────────────────────────────────────────────────────
from panda3d.core import loadPrcFileData
loadPrcFileData('', 'basic-shaders-only #t')
loadPrcFileData('', 'hardware-animated-vertices #f')
loadPrcFileData('', 'notify-level-glgsg fatal')
loadPrcFileData('', 'notify-level-display fatal')
loadPrcFileData('', 'notify-level-pnmimage fatal')
loadPrcFileData('', 'win-size 600 400')

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from random import uniform, seed
from math import sin
import noise

Entity.default_shader = None  # FINAL SHADER KILL

# ─────────────────────────────────────────────────────────────────────────────
# 🪟 APP SETUP
# ─────────────────────────────────────────────────────────────────────────────
app = Ursina()
window.title = "Cat's BOTW: Tears of the Kibble"
window.size = (600, 400)
window.borderless = False
window.exit_button.visible = False
window.fps_counter.enabled = True
window.color = color.rgb(110, 190, 255)
camera.clip_plane_far = 800

# ─────────────────────────────────────────────────────────────────────────────
# 🎨 COLORS
# ─────────────────────────────────────────────────────────────────────────────
def gray(v): return color.rgb(v, v, v)

C_WHITE = gray(250)
C_STONE = gray(120)
C_DARK = gray(50)
C_GRASS = color.rgb(100, 220, 100)
C_MOUNTAIN_TOP = color.rgb(240, 240, 255)
C_STAMINA = color.rgb(50, 255, 100)
C_HEART = color.rgb(255, 80, 80)
C_MENU = color.rgb(255, 250, 240)

# ─────────────────────────────────────────────────────────────────────────────
# ⛰️ TERRAIN
# ─────────────────────────────────────────────────────────────────────────────
def generate_terrain(size=100, scale=40, detail=0.02):
    verts, tris, cols = [], [], []
    seed(1337)
    off = size / 2

    for z in range(size):
        for x in range(size):
            nx, nz = x * detail, z * detail
            y = noise.pnoise2(nx, nz, octaves=4, persistence=0.5)
            y += noise.pnoise2(nx*4, nz*4, octaves=2) * 0.1
            h = (y + 1) / 2

            if h > 0.75: c = C_MOUNTAIN_TOP
            elif h > 0.45: c = C_STONE
            else: c = C_GRASS

            verts.append(Vec3(x - off, (h ** 1.5) * scale, z - off))
            cols.append(c)

    for z in range(size - 1):
        for x in range(size - 1):
            i = z * size + x
            tris += [(i, i+size, i+1), (i+1, i+size, i+size+1)]

    m = Mesh(vertices=verts, triangles=tris, colors=cols)
    m.generate_normals()
    return m

print("✨ Baking the world...")
terrain = Entity(
    model=generate_terrain(),
    scale=4,
    collider='mesh',
    unlit=True
)
print("🥞 World served!")

# ─────────────────────────────────────────────────────────────────────────────
# 🎮 MENU
# ─────────────────────────────────────────────────────────────────────────────
game_started = False
player = None

menu_pivot = Entity(y=20)
camera.parent = menu_pivot
camera.position = (0, 30, -80)
camera.rotation_x = 20

menu_ui = Entity(parent=camera.ui)
Entity(parent=menu_ui, model='quad', scale=(2, 1),
       color=color.rgba(0, 0, 0, 120), z=1)

Text("CAT'S BOTW", scale=3, y=0.2, parent=menu_ui, color=C_MENU)
Text("Tears of the Kibble", scale=1.5, y=0.1, parent=menu_ui, color=color.gold)

def start_game():
    global game_started, player
    if game_started: return
    game_started = True
    menu_ui.enabled = False
    camera.parent = scene
    player = FluffyLink(position=(0, 60, 0))
    print("⚔️ Backyard unlocked!")

Button("Play Game", scale=(0.25, 0.08), y=-0.2,
       parent=menu_ui, color=color.azure,
       on_click=start_game)

def update():
    if not game_started:
        menu_pivot.rotation_y += 5 * time.dt

# ─────────────────────────────────────────────────────────────────────────────
# 🏃 PLAYER
# ─────────────────────────────────────────────────────────────────────────────
class FluffyLink(FirstPersonController):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.speed = 8
        self.run_speed = 15
        self.jump_height = 3
        self.gravity = 1
        self.max_stamina = 100
        self.stamina = 100
        self.is_gliding = False
        self.glider = None
        self._ui()

    def _ui(self):
        self.stam_bg = Entity(parent=camera.ui, model='quad',
                              scale=(0.3, 0.02),
                              position=(-0.6, 0.4),
                              color=color.rgba(0,0,0,150))
        self.stam = Entity(parent=camera.ui, model='quad',
                           scale=(0.3, 0.02),
                           position=(-0.6, 0.4),
                           color=C_STAMINA)
        for i in range(3):
            Entity(parent=camera.ui, model='sphere',
                   scale=0.04, color=C_HEART,
                   position=(-0.8 + i*0.05, 0.45),
                   unlit=True)

        Text("WASD Move | SHIFT Sprint | SPACE Glide",
             position=(0, -0.45), scale=0.8)

    def update(self):
        if held_keys['shift'] and self.stamina > 0:
            self.speed = self.run_speed
            self.stamina -= 30 * time.dt
        else:
            self.speed = 8
            self.stamina += 20 * time.dt

        self.stamina = clamp(self.stamina, 0, self.max_stamina)
        self.stam.scale_x = 0.3 * (self.stamina / self.max_stamina)
        super().update()

    def input(self, key):
        super().input(key)
        if key == 'space' and not self.grounded and self.stamina > 10:
            self.start_glide()

    def start_glide(self):
        if self.is_gliding: return
        self.is_gliding = True
        self.gravity = 0.2
        self.glider = Entity(parent=self, model='quad',
                             scale=(4,2), y=2.5,
                             rotation_x=90,
                             color=color.light_gray,
                             double_sided=True,
                             unlit=True)

# ─────────────────────────────────────────────────────────────────────────────
# 🌳 TREES
# ─────────────────────────────────────────────────────────────────────────────
tree = Entity(enabled=False)
Entity(parent=tree, model='cube', scale=(0.5,4,0.5),
       y=2, color=color.brown, unlit=True)
Entity(parent=tree, model='sphere', scale=3,
       y=4, color=color.green, unlit=True)

for _ in range(100):
    x,z = uniform(-180,180), uniform(-180,180)
    hit = raycast(Vec3(x,200,z), Vec3(0,-1,0))
    if hit.hit and hit.entity == terrain and hit.point.y < 50:
        duplicate(tree, position=hit.point,
                  rotation_y=uniform(0,360),
                  enabled=True)

# ─────────────────────────────────────────────────────────────────────────────
# 👾 ENEMIES
# ─────────────────────────────────────────────────────────────────────────────
class BlobMob(Entity):
    def __init__(self, pos):
        super().__init__(model='sphere', color=color.red,
                         scale=1.5, position=pos,
                         collider='sphere', unlit=True)

    def update(self):
        if not game_started or not player: return
        if distance(self, player) < 30:
            self.look_at_2d(player, 'y')
            self.position += self.forward * 4 * time.dt
            self.y += sin(time.time()*10)*0.02

for _ in range(15):
    x,z = uniform(-80,80), uniform(-80,80)
    hit = raycast(Vec3(x,200,z), Vec3(0,-1,0))
    if hit.hit:
        BlobMob(hit.point + Vec3(0,1,0))

# ─────────────────────────────────────────────────────────────────────────────
# ☁️ CLOUDS
# ─────────────────────────────────────────────────────────────────────────────
for _ in range(20):
    Entity(model='sphere',
           scale=(uniform(10,30),uniform(5,10),uniform(10,20)),
           position=(uniform(-200,200),uniform(80,120),uniform(-200,200)),
           color=color.white,
           alpha=0.8,
           unlit=True)

# ─────────────────────────────────────────────────────────────────────────────
app.run()
