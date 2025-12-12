from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader, basic_lighting_shader
import random

app = Ursina(borderless=False, fullscreen=True, title='Ultra Mario 3D Bros - Peach\'s Castle N64DD Demo')

# ʕ•́ᴥ•̀ʔっ♡ CUDDLY GAMEPLAY CONSTANTS
PLAYER_SPEED = 10
SPRINT_SPEED = 15
JUMP_HEIGHT = 8
GRAVITY = 2
MOUSE_SENSITIVITY = 100
COIN_TOTAL = 100
STAR_TOTAL = 7
ENEMY_COUNT = 5

# ୧( ˵ ° ~ ° ˵ )୨ WHOLESOME PARTICLES
particles = []
coins = []
stars = []
enemies = []

# ʕ´• ᴥ•̥`ʔ BLOOM & LIGHTING MAGIC
window.color = color.rgb(135, 206, 235)  # Sky blue
Application.visual_quality = 2
scene.fog_color = color.rgb(135, 206, 235)
scene.fog_density = 0.01

# ฅ^•ﻌ•^ฅ SUNSET SKYBOX
Sky(texture='sky_default', color=color.linear_gradient(
    (0, color.rgb(255, 223, 186)),
    (0.5, color.rgb(255, 183, 197)),
    (1, color.rgb(179, 136, 235))
))

# ✨🐰🍰 SUN LIGHT WITH SHADOWS
sun = DirectionalLight(shadows=True, rotation=(45, -45, 0))
sun._light.color = color.rgb(255, 244, 229)
AmbientLight(color=color.rgb(100, 100, 150, a=0.3))

# (◕‿◕✿) CASTLE PARENT
castle_parent = Entity()

# ₊˚ʚ ᗢ₊˚✧ ﾟ. GRASSY GROUND
ground = Entity(
    model='plane',
    texture='white_cube',
    color=color.rgb(34, 139, 34),
    scale=200,
    collider='mesh',
    rotation_x=-90,
    y=-1,
    shader=lit_with_shadows_shader
)
ground.texture_scale = (50, 50)

# 🌊💙 MOAT
moat = Entity(
    model='cylinder',
    color=color.rgba(64, 164, 223, 180),
    scale=(52, 0.5, 52),
    y=-0.8,
    collider='mesh'
)

# 🏰💕 MAIN CASTLE BODY
castle_base = Entity(
    parent=castle_parent,
    model='cube',
    color=color.rgb(255, 182, 193),
    scale=(20, 1, 30),
    y=0,
    texture='white_cube',
    collider='box',
    shader=lit_with_shadows_shader
)

# WALLS
wall_front = Entity(
    parent=castle_parent,
    model='cube',
    color=color.rgb(255, 192, 203),
    scale=(20, 15, 1),
    y=7.5,
    z=14.5,
    texture='white_cube',
    shader=lit_with_shadows_shader
)

wall_back = duplicate(wall_front, z=-14.5)
wall_left = Entity(
    parent=castle_parent,
    model='cube',
    color=color.rgb(255, 192, 203),
    scale=(1, 15, 28),
    y=7.5,
    x=-9.5,
    texture='white_cube',
    shader=lit_with_shadows_shader
)
wall_right = duplicate(wall_left, x=9.5)

# 🎀 BATTLEMENTS
for x in [-8, -4, 0, 4, 8]:
    for z in [-13, 13]:
        battlement = Entity(
            parent=castle_parent,
            model='cube',
            color=color.rgb(255, 105, 180),
            scale=(2, 2, 2),
            y=16,
            x=x,
            z=z,
            texture='white_cube',
            shader=lit_with_shadows_shader
        )

# 🏰✨ CORNER TOWERS
for x, z in [(-12, 20), (12, 20), (-12, -20), (12, -20)]:
    tower = Entity(
        parent=castle_parent,
        model='cylinder',
        color=color.rgb(255, 182, 193),
        scale=(3, 20, 3),
        x=x,
        y=10,
        z=z,
        segments=16,
        texture='white_cube',
        collider='mesh',
        shader=lit_with_shadows_shader
    )
    
    # CONICAL ROOFS
    roof = Entity(
        parent=tower,
        model='cone',
        color=color.rgb(220, 20, 60),
        scale=(4, 5, 4),
        rotation_x=180,
        y=12,
        shader=lit_with_shadows_shader
    )

# 🌸 DRAWBRIDGE
drawbridge = Entity(
    parent=castle_parent,
    model='cube',
    color=color.rgb(139, 69, 19),
    scale=(6, 1, 8),
    y=0.5,
    z=15,
    rotation_z=-45,
    collider='box',
    texture='white_cube',
    shader=lit_with_shadows_shader
)

# 🚪 ENTRANCE GATE
gate = Entity(
    parent=castle_parent,
    model='quad',
    color=color.rgb(160, 120, 80),
    scale=(5, 8, 1),
    y=4,
    z=14.6,
    collider='box',
    shader=basic_lighting_shader
)

# 🎆 STAINED GLASS WINDOWS
for x in [-6, 0, 6]:
    window_glass = Entity(
        parent=castle_parent,
        model='quad',
        color=color.rgba(255, 105, 180, 150),
        scale=(2, 3, 1),
        y=8,
        x=x,
        z=14.7,
        shader=basic_lighting_shader
    )

# 👑 PEACH STATUE
statue_base = Entity(
    parent=castle_parent,
    model='cylinder',
    color=color.rgb(255, 182, 193),
    scale=(2, 1, 2),
    y=17,
    shader=lit_with_shadows_shader
)
statue_body = Entity(
    parent=statue_base,
    model='cylinder',
    color=color.rgb(255, 192, 203),
    scale=(1.5, 3, 1.5),
    y=2,
    shader=lit_with_shadows_shader
)
statue_head = Entity(
    parent=statue_body,
    model='sphere',
    color=color.rgb(255, 228, 196),
    scale=1.5,
    y=3,
    shader=lit_with_shadows_shader
)

# 💛 ?-BLOCKS
for i in range(10):
    qblock = Entity(
        model='cube',
        color=color.yellow,
        scale=2,
        position=(random.uniform(-40, 40), 2, random.uniform(-40, 40)),
        texture='white_cube',
        collider='box',
        shader=lit_with_shadows_shader
    )
    qblock.animate_y(qblock.y + 0.5, duration=1, loop=True, curve=curve.in_out_sine)
    qblock.animate_rotation_y(360, duration=3, loop=True)

# 🟢 WARP PIPES
for i in range(5):
    pipe = Entity(
        model='cylinder',
        color=color.green,
        scale=(2, 4, 2),
        position=(random.uniform(-30, 30), 2, random.uniform(-30, 30)),
        collider='mesh',
        shader=lit_with_shadows_shader
    )
    pipe_top = Entity(
        parent=pipe,
        model='cylinder',
        color=color.dark_green,
        scale=(2.2, 0.5, 2.2),
        y=2.5
    )

# 🎀 INSIDE CASTLE GLOW
castle_glow = PointLight(
    parent=castle_parent,
    color=color.rgb(255, 182, 193, a=0.5),
    position=(0, 10, 0),
    shadows=True
)

# 💫 N64DD LOGO HOLOGRAM
logo_disk = Entity(
    model='cylinder',
    color=color.silver,
    scale=(5, 0.1, 5),
    y=30,
    texture='white_cube',
    shader=basic_lighting_shader
)
logo_text = Text(
    text='N64DD',
    scale=3,
    y=30.5,
    origin=(-0.5, 0),
    color=color.cyan,
    background=True
)
logo_light = PointLight(
    color=color.cyan,
    position=(0, 30, 0),
    shadows=False
)

# 🐾 MARIO PLAYER
class UltraMario(Entity):
    def __init__(self):
        super().__init__()
        self.model = 'cube'
        self.color = color.blue
        self.scale_y = 1.5
        self.scale_x = 0.8
        self.scale_z = 0.8
        self.position = (0, 5, -50)
        self.rotation_y = 180
        self.collider = 'box'
        self.speed = PLAYER_SPEED
        self.velocity_y = 0
        self.grounded = False
        self.jumps = 0
        self.max_jumps = 2
        self.lives = 3
        self.coins = 0
        self.stars = 0
        self.hurt_timer = 0
        
        # 🎩 MARIO PARTS
        self.head = Entity(
            parent=self,
            model='sphere',
            color=color.rgb(255, 228, 196),
            scale=0.5,
            y=1,
            z=-0.1
        )
        self.hat = Entity(
            parent=self.head,
            model='cone',
            color=color.red,
            scale=(1, 1, 1.5),
            y=0.3,
            rotation_x=-90
        )
        self.mustache = Entity(
            parent=self.head,
            model='quad',
            color=color.black,
            scale=(0.6, 0.1, 1),
            y=-0.1,
            z=0.3,
            rotation_x=10
        )
        
        # 👕 OVERALLS
        self.overalls = []
        for x in [-0.3, 0.3]:
            strap = Entity(
                parent=self,
                model='cube',
                color=color.dark_blue,
                scale=(0.1, 0.8, 0.1),
                x=x,
                y=0.3
            )
            self.overalls.append(strap)
        
        # 🎥 CAMERA PIVOT
        self.camera_pivot = Entity(parent=self, position=(0, 5, -10))
        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        
    def update(self):
        # 🎮 CONTROLS
        move_dir = Vec3(
            (held_keys['d'] - held_keys['a']) * self.speed * time.dt,
            self.velocity_y,
            (held_keys['w'] - held_keys['s']) * self.speed * time.dt
        )
        
        # 🏃‍♂️ SPRINT
        if held_keys['shift']:
            self.speed = SPRINT_SPEED
            move_dir *= 1.5
        else:
            self.speed = PLAYER_SPEED
            
        # 🐭 MOUSE LOOK
        if mouse.locked:
            self.camera_pivot.rotation_x -= mouse.velocity[1] * MOUSE_SENSITIVITY
            self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)
            self.rotation_y += mouse.velocity[0] * MOUSE_SENSITIVITY
            
        # 🦘 JUMP
        if held_keys['space'] and self.jumps < self.max_jumps:
            self.velocity_y = JUMP_HEIGHT
            self.jumps += 1
            self.grounded = False
            self.animate_scale_y(0.8, duration=0.1)
            self.animate_scale_y(1.5, duration=0.3, delay=0.1)
            
        # 🌌 GRAVITY
        self.velocity_y -= GRAVITY * time.dt
        move_dir.y = self.velocity_y
        
        # 🧱 COLLISION
        hit_info = self.intersects()
        if hit_info.hit:
            if hit_info.normal.y > 0.5:  # Ground
                self.grounded = True
                self.jumps = 0
                self.velocity_y = 0
                self.y = hit_info.world_point.y + 0.5
            else:  # Wall
                move_dir.x = 0
                move_dir.z = 0
                
        self.position += move_dir
        
        # 🥾 GROUND POUND
        if held_keys['c'] and not self.grounded:
            self.velocity_y = -20
            
        # 🎈 BOBBING ANIMATION
        if held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']:
            self.head.y = lerp(self.head.y, 1 + sin(time.time() * 10) * 0.1, 6 * time.dt)
        else:
            self.head.y = lerp(self.head.y, 1, 6 * time.dt)
            
        # 💔 HURT TIMER
        if self.hurt_timer > 0:
            self.hurt_timer -= time.dt
            self.color = color.red if int(self.hurt_timer * 10) % 2 == 0 else color.blue
        else:
            self.color = color.blue
            
        # 🎯 KEEP IN BOUNDS
        if self.y < -20:
            self.take_damage()
            self.position = (0, 10, -50)
            
    def take_damage(self):
        if self.hurt_timer <= 0:
            self.lives -= 1
            self.hurt_timer = 2
            if self.lives <= 0:
                self.game_over()
                
    def game_over(self):
        self.position = (0, 10, -50)
        self.lives = 3
        self.coins = 0
        self.stars = 0
        
    def collect_coin(self):
        self.coins += 1
        if self.coins >= COIN_TOTAL:
            self.coins = COIN_TOTAL
            
    def collect_star(self):
        self.stars += 1

# 🍄 GOOMBA ENEMIES
class Goomba(Entity):
    def __init__(self, position):
        super().__init__()
        self.model = 'sphere'
        self.color = color.brown
        self.scale = 1
        self.position = position
        self.collider = 'sphere'
        self.speed = 2
        self.direction = 1
        self.alive = True
        self.walk_timer = 0
        
        self.legs = []
        for i in range(4):
            leg = Entity(
                parent=self,
                model='cylinder',
                color=color.dark_brown,
                scale=(0.2, 0.5, 0.2),
                position=(0.3 if i % 2 == 0 else -0.3, -0.5, 0.3 if i < 2 else -0.3)
            )
            self.legs.append(leg)
            
        enemies.append(self)
        
    def update(self):
        if not self.alive:
            self.scale_y = lerp(self.scale_y, 0.2, 10 * time.dt)
            if self.scale_y < 0.3:
                destroy(self)
                enemies.remove(self)
            return
            
        # 🚶‍♂️ PATROL
        self.walk_timer += time.dt
        self.x += self.direction * self.speed * time.dt
        
        # 🦵 LEG ANIMATION
        for i, leg in enumerate(self.legs):
            leg.y = -0.5 + sin(self.walk_timer * 10 + i) * 0.2
            
        # 🔄 DIRECTION CHANGE
        if random.random() < 0.01 * time.dt:
            self.direction *= -1
            
        # 🎯 COLLISION WITH MARIO
        if distance(self.position, player.position) < 1.5:
            if player.velocity_y < -5:  # JUMP ON HEAD
                self.squash()
                player.velocity_y = JUMP_HEIGHT * 0.8
            elif player.hurt_timer <= 0:
                player.take_damage()
                
    def squash(self):
        self.alive = False
        for leg in self.legs:
            destroy(leg)
        self.collider = None

# ✨ COINS
def create_coins():
    for i in range(COIN_TOTAL):
        coin = Entity(
            model='sphere',
            color=color.gold,
            scale=0.5,
            position=(random.uniform(-40, 40), 5, random.uniform(-40, 40)),
            collider='sphere'
        )
        coins.append(coin)

# ⭐ STARS
def create_stars():
    for i in range(STAR_TOTAL):
        star = Entity(
            model='icosahedron',
            color=color.yellow,
            scale=2,
            position=(random.uniform(-40, 40), 10, random.uniform(-40, 40)),
            collider='mesh'
        )
        star.animate_rotation_y(360, duration=3, loop=True)
        star.animate_y(star.y + 2, duration=1, loop=True, curve=curve.in_out_sine)
        stars.append(star)

# 🎮 HUD
class GameHUD(Entity):
    def __init__(self):
        super().__init__()
        self.lives_text = Text(
            text='Lives: 3',
            position=(-0.85, 0.45),
            scale=2,
            color=color.red,
            background=True
        )
        self.coins_text = Text(
            text='Coins: 0/100',
            position=(-0.85, 0.4),
            scale=2,
            color=color.yellow,
            background=True
        )
        self.stars_text = Text(
            text='Stars: 0/7',
            position=(-0.85, 0.35),
            scale=2,
            color=color.cyan,
            background=True
        )
        
    def update(self):
        self.lives_text.text = f'Lives: {player.lives}'
        self.coins_text.text = f'Coins: {player.coins}/{COIN_TOTAL}'
        self.stars_text.text = f'Stars: {player.stars}/{STAR_TOTAL}'

# 🎆 PARTICLES
def create_particle(pos, color=color.yellow):
    p = Entity(
        model='sphere',
        color=color,
        scale=0.2,
        position=pos,
        shader=basic_lighting_shader
    )
    p.animate_scale(0, duration=0.5)
    particles.append(p)
    invoke(destroy, p, delay=0.5)
    if len(particles) > 100:
        destroy(particles.pop(0))

# 🎀 CASTLE INTERIOR
class CastleInterior(Entity):
    def __init__(self):
        super().__init__()
        self.active = False
        self.model = 'cube'
        self.color = color.rgb(255, 228, 225)
        self.scale = (15, 10, 15)
        self.position = (0, 5, 0)
        self.visible = False
        self.collider = 'box'
        
        # 🕯️ INTERIOR LIGHTS
        self.lights = []
        for x in [-5, 0, 5]:
            for z in [-5, 0, 5]:
                light = PointLight(
                    color=color.rgb(255, 255, 200),
                    position=(x, 3, z),
                    shadows=False
                )
                self.lights.append(light)
                light.enabled = False

# 🎵 SOUNDS
def play_sound(pitch=1, volume=0.5):
    Audio('synth', pitch=pitch, volume=volume, loop=False)

# 🎯 INITIALIZE EVERYTHING
player = UltraMario()
hud = GameHUD()
castle_interior = CastleInterior()
create_coins()
create_stars()

# 🍄 SPAWN GOOMBAS
for i in range(ENEMY_COUNT):
    Goomba(position=(random.uniform(-30, 30), 1, random.uniform(-30, 30)))

# 🎀 UPDATE LOOP
def update():
    # 🎪 LOGO ANIMATION
    logo_disk.rotation_y += 45 * time.dt
    logo_disk.scale = 5 + sin(time.time() * 5) * 0.5
    logo_text.rotation_y = logo_disk.rotation_y
    logo_light.color = color.hsv(time.time() * 50 % 360, 1, 1)
    
    # 💛 COIN COLLECTION
    for coin in coins[:]:
        if distance(coin.position, player.position) < 1.5:
            player.collect_coin()
            create_particle(coin.position, color.yellow)
            play_sound(pitch=2)
            coins.remove(coin)
            destroy(coin)
        else:
            coin.rotation_y += 100 * time.dt
            coin.y = 5 + sin(time.time() * 3 + coin.x) * 2
            
    # ⭐ STAR COLLECTION
    for star in stars[:]:
        if distance(star.position, player.position) < 2:
            player.collect_star()
            for i in range(20):
                create_particle(star.position, color.random_color())
            play_sound(pitch=1.5, volume=1)
            stars.remove(star)
            destroy(star)
            
    # 🏰 CASTLE ENTRANCE
    if distance(player.position, gate.position) < 5 and not castle_interior.active:
        castle_interior.active = True
        castle_interior.visible = True
        for light in castle_interior.lights:
            light.enabled = True
        player.position = (0, 5, 0)
        player.rotation_y = 180
        
    # 🎆 WIN CONDITION
    if player.stars >= STAR_TOTAL:
        for i in range(5):
            pos = (random.uniform(-10, 10), random.uniform(0, 20), random.uniform(-10, 10))
            create_particle(pos, color.random_color())
            
    # ✨ AUTO-ORBIT CAMERA IDLE
    if mouse.moved and mouse.locked:
        player.camera_pivot.idle_timer = 0
    elif hasattr(player.camera_pivot, 'idle_timer'):
        player.camera_pivot.idle_timer += time.dt
        if player.camera_pivot.idle_timer > 3:
            player.camera_pivot.rotation_y += 10 * time.dt
            
# 🎮 INPUT
def input(key):
    # 🖱️ MOUSE LOCK
    if key == 'left mouse down' and not mouse.locked:
        mouse.locked = True
        mouse.visible = False
    elif key == 'escape':
        mouse.locked = False
        mouse.visible = True
        
    # 🦘 TRIPLE JUMP
    if key == 'space' and player.grounded:
        player.max_jumps = 3
        invoke(setattr, player, 'max_jumps', 2, delay=1)
        
    # 📸 SCREENSHOT
    if key == 'p':
        application.screenshot()

# 🎀 START SCREEN TEXT
start_text = Text(
    text='Ultra Mario 3D Bros - Peach\'s Castle N64DD Demo\nClick to Start • WASD: Move • Space: Jump • Shift: Sprint\nC: Ground Pound • Collect 100 Coins & 7 Stars',
    position=(0, 0.2),
    scale=1.5,
    color=color.cyan,
    background=True
)

def start_game():
    destroy(start_text)
    mouse.locked = True
    mouse.visible = False

# ✨ FINAL INIT
if __name__ == '__main__':
    window.fullscreen = True
    window.borderless = False
    mouse.traverse_target = scene
    
    # 🎨 POST-PROCESSING
    camera.post_processing = True
    camera.set_shader_input('bloom_intensity', 1.0)
    camera.set_shader_input('bloom_threshold', 0.8)
    
    # 🎪 FINAL MESSAGE
    print('🎮✨ NYAAA~ Ultra Mario 3D Bros N64DD Demo Ready!')
    print('🐾 Collect all stars for a cuddly surprise!')
    print('🔥🐰🍰 WHOLESOME PWNIUS MAXIMUS ACTIVATED ♡')
    
    app.run()
