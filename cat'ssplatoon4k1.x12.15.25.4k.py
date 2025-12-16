#!/usr/bin/env python3
"""
Ultra!Splatoon 0.2 — SGI Texture Edition
Procedural textures for that crunchy 90s workstation aesthetic.
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL import Image, ImageDraw, ImageFilter
import random
import math
import sys

# FIX FOR MACOS OPENGL SHADER ERRORS
# macOS defaults to legacy OpenGL 2.1 which doesn't support the shaders Ursina uses (GLSL 1.30+)
# We must force OpenGL 3.2+ Core Profile to unlock modern shader support.
from panda3d.core import loadPrcFileData
if sys.platform == 'darwin':
    loadPrcFileData('', 'gl-version 3 2')

# ============================================================================
# TEXTURE GENERATOR (The SGI Bakery)
# ============================================================================
class TextureBakery:
    @staticmethod
    def bake_grid():
        """Generates a retro SGI-style neon grid texture"""
        size = 512
        # Deep Indigo Background (Not Black!)
        img = Image.new('RGB', (size, size), (20, 15, 50)) 
        draw = ImageDraw.Draw(img)
        
        # Draw Neon Grid Lines
        step = 64
        for i in range(0, size, step):
            # Horizontal
            draw.line([(0, i), (size, i)], fill=(0, 200, 255), width=2)
            # Vertical
            draw.line([(i, 0), (i, size)], fill=(0, 200, 255), width=2)
            
        # Add subtle digital noise
        pixels = img.load()
        for _ in range(2000):
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            pixels[x, y] = (50, 50, 100) # Sparkles

        return Texture(img)

    @staticmethod
    def bake_plasma_noise():
        """Generates a smooth plasma cloud for ink"""
        size = 128
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        pixels = img.load()
        
        for x in range(size):
            for y in range(size):
                # Smooth sine waves for plasma look
                nx = x * 0.1
                ny = y * 0.1
                v = math.sin(nx) + math.cos(ny) + math.sin((x+y)*0.05)
                
                # Soft alpha gradient
                alpha = int(((v + 3) / 6) * 255)
                # Clamp alpha to avoid invisibility
                alpha = max(100, min(240, alpha))
                
                pixels[x, y] = (255, 255, 255, alpha)
        
        return Texture(img)

    @staticmethod
    def bake_brushed_metal():
        """Generates a lighter brushed metal texture"""
        size = 256
        # Light Grey Base
        img = Image.new('RGB', (size, size), (150, 155, 160))
        draw = ImageDraw.Draw(img)
        
        # Draw horizontal streaks
        for _ in range(500):
            y = random.randint(0, size-1)
            l = random.randint(10, 50)
            x = random.randint(0, size-l)
            c = random.randint(130, 180)
            draw.line([(x, y), (x+l, y)], fill=(c, c, c+10), width=1)
            
        # Panel border
        draw.rectangle([0,0,size-1,size-1], outline=(100,100,110), width=3)
            
        return Texture(img)

# ============================================================================
# GAME CONSTANTS
# ============================================================================
ARENA_SIZE = 64
INK_RESOLUTION = 64
TEAM_NONE = 0
TEAM_PLAYER = 1
TEAM_ENEMY = 2

# Adjusted palettes for SGI aesthetic (More neon against dark textures)
PALETTES = [
    {'ink': color.rgb(0, 255, 255), 'dark': color.rgb(0, 100, 100)},   # Cyan (SGI Teal)
    {'ink': color.rgb(255, 50, 255), 'dark': color.rgb(100, 20, 100)}, # Magenta
    {'ink': color.rgb(50, 255, 50), 'dark': color.rgb(20, 100, 20)},   # Alien Green
    {'ink': color.rgb(255, 180, 0), 'dark': color.rgb(100, 70, 0)},    # Amber
]
ENEMY_COLOR = color.rgb(255, 50, 80) # Hot Red

# ============================================================================
# GAME CLASS
# ============================================================================
class UltraSplatoon:
    def __init__(self):
        self.state = 'menu' # Skip fake boot for faster testing
        self.palette_index = 0
        
        # Textures
        print("Baking textures... (this might take a second)")
        self.tex_grid = TextureBakery.bake_grid()
        self.tex_ink = TextureBakery.bake_plasma_noise()
        self.tex_wall = TextureBakery.bake_brushed_metal()
        print("Textures baked! 🥞")

        # Player stats
        self.hp = 100
        self.hp_max = 100
        self.ink = 100
        self.xp = 0
        self.xp_to = 100
        self.level = 1
        self.gear_tier = 0
        self.perks = {'ink_eff': 0, 'swim_speed': 0, 'bomb_power': 0}
        self.dash_cooldown = 0
        self.perk_choices = []
        
        # Match
        self.match_time = 0
        self.match_duration = 180
        self.splat_count = 0
        self.spawn_timer = 2
        
        # Ink map
        self.ink_owner = [[TEAM_NONE] * INK_RESOLUTION for _ in range(INK_RESOLUTION)]
        self.ink_alpha = [[0.0] * INK_RESOLUTION for _ in range(INK_RESOLUTION)]
        
        # Entity lists
        self.enemies = []
        self.bombs = []
        self.ink_splats = []
        self.walls = []
        self.ink_decals = []
        
        # UI & 3D
        self.hud_elements = {}
        self.menu_items = []
        self.ground = None
        self.player = None
        self.weapon_model = None
        
        # Input
        self.shooting = False
        self.rolling = False
    
    def setup(self):
        """Initialize the game"""
        camera.clip_plane_far = 200
        self.create_menu()
    
    def create_menu(self):
        """Create main menu"""
        self.menu_title = Text(
            text='ULTRA!SPLATOON\nNEON GRID EDITION',
            scale=3,
            origin=(0, 0),
            y=0.3,
            color=PALETTES[0]['ink'],
            font='font/pixel_font.ttf' if os.path.exists('font/pixel_font.ttf') else 'default_font'
        )
        
        self.menu_start = Text(
            text='[ CLICK TO INITIALIZE ]',
            scale=1.5,
            origin=(0, 0),
            y=-0.2,
            color=color.white
        )

    def destroy_menu(self):
        destroy(self.menu_title)
        destroy(self.menu_start)
        self.menu_title = None
        self.menu_start = None

    def create_hud(self):
        """Create in-game HUD"""
        # HP Bar
        self.hud_elements['hp_bg'] = Entity(parent=camera.ui, model='quad', color=color.black66, scale=(0.3, 0.02), position=(-0.55, 0.45))
        self.hud_elements['hp_fill'] = Entity(parent=camera.ui, model='quad', color=color.red, scale=(0.3, 0.02), position=(-0.55, 0.45), origin=(-0.5, 0))
        
        # Ink Bar
        self.hud_elements['ink_bg'] = Entity(parent=camera.ui, model='quad', color=color.black66, scale=(0.3, 0.015), position=(-0.55, 0.42))
        self.hud_elements['ink_fill'] = Entity(parent=camera.ui, model='quad', color=PALETTES[self.palette_index]['ink'], scale=(0.3, 0.015), position=(-0.55, 0.42), origin=(-0.5, 0))
        
        # Crosshair
        self.crosshair = Entity(parent=camera.ui, model='quad', color=color.white, scale=0.005)
        
        # Toast
        self.hud_elements['toast'] = Text(text='', scale=1.5, origin=(0,0), y=-0.3, color=color.white, visible=False)

    def destroy_hud(self):
        for key, element in self.hud_elements.items():
            destroy(element)
        self.hud_elements = {}
        if self.crosshair: destroy(self.crosshair)

    def create_arena(self):
        """Create the 3D arena with TEXTURES"""
        # Ground plane with NEON GRID Texture
        self.ground = Entity(
            model='plane',
            scale=(ARENA_SIZE, 1, ARENA_SIZE),
            texture=self.tex_grid, # APPLY GRID
            texture_scale=(8, 8),  # Tile the texture
            color=color.white,     # Keep white so texture shows true colors
            collider='box',
            y=0
        )
        
        wall_height = 5
        
        # Walls with BRUSHED METAL Texture
        wall_configs = [
            ((ARENA_SIZE, wall_height, 1), (0, wall_height/2, ARENA_SIZE/2)),
            ((ARENA_SIZE, wall_height, 1), (0, wall_height/2, -ARENA_SIZE/2)),
            ((1, wall_height, ARENA_SIZE), (ARENA_SIZE/2, wall_height/2, 0)),
            ((1, wall_height, ARENA_SIZE), (-ARENA_SIZE/2, wall_height/2, 0)),
            # Central Block
            ((12, 3, 12), (0, 1.5, 0))
        ]
        
        for scale, pos in wall_configs:
            self.walls.append(Entity(
                model='cube',
                scale=scale,
                position=pos,
                texture=self.tex_wall, # APPLY METAL
                texture_scale=(scale[0]/4, scale[1]/4),
                color=color.rgb(200, 200, 220), # Slight blue tint
                collider='box'
            ))

    def spawn_ink_decal(self, x, z, team, size=2):
        """Spawn a textured ink decal"""
        if len(self.ink_decals) > 400: # Limit for performance
            old = self.ink_decals.pop(0)
            destroy(old)
        
        col = PALETTES[self.palette_index]['ink'] if team == TEAM_PLAYER else ENEMY_COLOR
        
        decal = Entity(
            model='quad',
            scale=(size, size),
            position=(x, 0.02, z),
            rotation=(90, 0, random.uniform(0, 360)),
            color=col,
            texture=self.tex_ink, # APPLY PLASMA INK
            alpha=0.9
        )
        decal.team = team
        self.ink_decals.append(decal)

    def create_player(self):
        self.player = FirstPersonController(
            position=(0, 2, -ARENA_SIZE/3),
            speed=10,
            mouse_sensitivity=Vec2(50, 50)
        )
        self.player.cursor.visible = False
        self.player.gravity = 0.6
        
        # Gun
        self.weapon_model = Entity(
            parent=camera,
            model='cube',
            scale=(0.1, 0.1, 0.4),
            position=(0.3, -0.2, 0.5),
            color=color.dark_gray,
            texture=self.tex_wall # Gun gets metal texture
        )

    def destroy_arena(self):
        if self.ground: destroy(self.ground)
        for w in self.walls: destroy(w)
        self.walls = []
        for d in self.ink_decals: destroy(d)
        self.ink_decals = []
        if self.player: destroy(self.player)
        if self.weapon_model: destroy(self.weapon_model)
        for e in self.enemies: destroy(e)
        self.enemies = []

    # --- Gameplay Logic (Simplified for brevity) ---
    
    def world_to_ink(self, x, z):
        ix = int((x + ARENA_SIZE/2) / ARENA_SIZE * INK_RESOLUTION)
        iy = int((z + ARENA_SIZE/2) / ARENA_SIZE * INK_RESOLUTION)
        return max(0, min(INK_RESOLUTION-1, ix)), max(0, min(INK_RESOLUTION-1, iy))
    
    def paint_circle(self, wx, wz, radius, team, alpha=0.8):
        # Logical paint (gameplay)
        cx, cy = self.world_to_ink(wx, wz)
        r = int(radius / ARENA_SIZE * INK_RESOLUTION)
        r = max(1, r)
        painted = False
        
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                if dx*dx + dy*dy <= r*r:
                    ix, iy = cx + dx, cy + dy
                    if 0 <= ix < INK_RESOLUTION and 0 <= iy < INK_RESOLUTION:
                        if self.ink_owner[ix][iy] != team: painted = True
                        self.ink_owner[ix][iy] = team
                        self.ink_alpha[ix][iy] = 1.0
        
        # Visual paint
        if painted and random.random() < 0.4:
            self.spawn_ink_decal(wx, wz, team, radius * 0.9)

    def spawn_enemy(self):
        pos = Vec3(random.uniform(-20, 20), 1, random.uniform(-20, 20))
        enemy = Entity(model='sphere', scale=1.5, position=pos, color=ENEMY_COLOR, collider='box')
        enemy.hp = 30
        enemy.dir = Vec3(0,0,0)
        self.enemies.append(enemy)

    def start_game(self):
        self.destroy_menu()
        self.create_arena()
        self.create_player()
        self.create_hud()
        self.state = 'playing'
        mouse.locked = True
        self.show_toast("NEON SYSTEMS ONLINE: GO!")

    def show_toast(self, t):
        self.hud_elements['toast'].text = t
        self.hud_elements['toast'].visible = True
        invoke(setattr, self.hud_elements['toast'], 'visible', False, delay=2)

    def update(self):
        if self.state == 'playing':
            # Shooting
            if held_keys['left mouse'] and self.ink > 0:
                self.ink -= 0.5
                hit = raycast(camera.world_position, camera.forward, distance=100, ignore=(self.player,))
                if hit.hit:
                    self.paint_circle(hit.point.x, hit.point.z, 2.5, TEAM_PLAYER)
                
                # Gun recoil anim
                self.weapon_model.z = 0.4 + random.uniform(-0.02, 0.02)
            else:
                self.weapon_model.z = 0.5
                self.ink = min(100, self.ink + 0.2)
            
            self.hud_elements['ink_fill'].scale_x = 0.3 * (self.ink / 100)
            
            # Simple enemy logic
            for e in self.enemies:
                e.position += (self.player.position - e.position).normalized() * time.dt * 4
                e.y = 1
                if distance(e, self.player) < 2:
                    self.hp -= 1
                    self.hud_elements['hp_fill'].scale_x = 0.3 * (self.hp/100)

    def input(self, key):
        if self.state == 'menu':
            if key == 'left mouse down': self.start_game()
        elif self.state == 'playing':
            if key == 'q': quit()
            if key == 'r': 
                self.palette_index = (self.palette_index + 1) % len(PALETTES)
                self.hud_elements['ink_fill'].color = PALETTES[self.palette_index]['ink']

# ============================================================================
# MAIN
# ============================================================================
if __name__ == '__main__':
    app = Ursina(title='Splatoon SGI', vsync=False)
    
    # Retro Window Settings
    window.color = color.rgb(10, 10, 25) # Deep blue background
    
    game = UltraSplatoon()
    game.setup()
    
    def update(): game.update()
    def input(key): game.input(key)
    
    app.run()
