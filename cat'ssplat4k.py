#!/usr/bin/env python3
"""
Ultra!Splatoon 0.1 — Ursina 3D Engine
Full 3D Splatoon-style ink shooter with RPG elements
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random
import math

# ============================================================================
# GAME CONSTANTS
# ============================================================================
ARENA_SIZE = 64
INK_RESOLUTION = 128  # Texture resolution for ink
TEAM_NONE = 0
TEAM_PLAYER = 1
TEAM_ENEMY = 2

# Color palettes
PALETTES = [
    {'ink': color.rgb(65, 163, 255), 'dark': color.rgb(30, 80, 140), 'roller': color.rgb(160, 210, 255)},
    {'ink': color.rgb(255, 61, 110), 'dark': color.rgb(140, 30, 55), 'roller': color.rgb(255, 150, 180)},
    {'ink': color.rgb(118, 255, 65), 'dark': color.rgb(55, 140, 30), 'roller': color.rgb(180, 255, 150)},
    {'ink': color.rgb(255, 212, 65), 'dark': color.rgb(140, 100, 30), 'roller': color.rgb(255, 230, 150)},
    {'ink': color.rgb(195, 65, 255), 'dark': color.rgb(100, 30, 140), 'roller': color.rgb(220, 150, 255)},
    {'ink': color.rgb(255, 140, 65), 'dark': color.rgb(140, 70, 30), 'roller': color.rgb(255, 190, 150)},
]
ENEMY_COLOR = color.rgb(255, 107, 138)
ENEMY_COLOR_DARK = color.rgb(140, 50, 70)


# ============================================================================
# GAME CLASS
# ============================================================================
class UltraSplatoon:
    def __init__(self):
        self.state = 'boot_nintendo'
        self.state_timer = 0
        self.palette_index = 0
        
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
        
        # Ink map (2D array for ground painting)
        self.ink_owner = [[TEAM_NONE] * INK_RESOLUTION for _ in range(INK_RESOLUTION)]
        self.ink_alpha = [[0.0] * INK_RESOLUTION for _ in range(INK_RESOLUTION)]
        
        # Entity lists
        self.enemies = []
        self.bombs = []
        self.ink_splats = []
        self.walls = []
        
        # Toast
        self.toast_text = ""
        self.toast_timer = 0
        
        # UI elements (created later)
        self.boot_text = None
        self.boot_sub = None
        self.menu_title = None
        self.menu_items = []
        self.hud_elements = {}
        self.result_panel = None
        
        # 3D elements
        self.ground = None
        self.ground_texture = None
        self.player = None
        self.weapon_model = None
        self.crosshair = None
        self.skybox = None
        
        # Input
        self.shooting = False
        self.rolling = False
    
    def setup(self):
        """Initialize the game after Ursina app is created"""
        # Sky
        self.skybox = Sky(color=color.rgb(40, 50, 80))
        
        # Create boot screen
        self.create_boot_screen()
        
        # Ambient light
        ambient = AmbientLight(color=color.rgba(100, 100, 100, 100))
        
        # Directional light
        sun = DirectionalLight(y=10, rotation=(45, 45, 0))
        sun.color = color.white
    
    def create_boot_screen(self):
        """Create boot sequence UI"""
        self.boot_text = Text(
            text='Nintendo',
            scale=3,
            origin=(0, 0),
            color=color.white
        )
        self.boot_sub = Text(
            text='presents',
            scale=1.5,
            origin=(0, 0),
            y=-0.1,
            color=color.gray
        )
    
    def create_menu(self):
        """Create main menu"""
        self.menu_title = Text(
            text='Ultra!Splatoon',
            scale=4,
            origin=(0, 0),
            y=0.3,
            color=PALETTES[0]['ink']
        )
        
        self.menu_version = Text(
            text='v0.1 Tech Demo',
            scale=1.5,
            origin=(0, 0),
            y=0.18,
            color=color.gray
        )
        
        instructions = [
            'WASD - Move',
            'Mouse - Look',
            'LMB - Spray • RMB - Roller',
            'Q - Bomb • E - Perk • R - Palette',
            'SPACE - Dash',
            '',
            'Paint the arena to win!'
        ]
        
        self.menu_items = []
        for i, line in enumerate(instructions):
            t = Text(
                text=line,
                scale=1,
                origin=(0, 0),
                y=-0.05 - i * 0.06,
                color=color.light_gray
            )
            self.menu_items.append(t)
        
        self.menu_start = Text(
            text='[ Press ENTER or CLICK to Start ]',
            scale=1.5,
            origin=(0, 0),
            y=-0.35,
            color=color.white
        )
        self.menu_items.append(self.menu_start)
    
    def destroy_menu(self):
        """Remove menu elements"""
        if self.menu_title:
            destroy(self.menu_title)
            self.menu_title = None
        if hasattr(self, 'menu_version') and self.menu_version:
            destroy(self.menu_version)
            self.menu_version = None
        if hasattr(self, 'menu_start') and self.menu_start:
            destroy(self.menu_start)
            self.menu_start = None
        for item in self.menu_items:
            destroy(item)
        self.menu_items = []
    
    def create_hud(self):
        """Create in-game HUD"""
        # HP bar background
        self.hud_elements['hp_bg'] = Entity(
            parent=camera.ui,
            model='quad',
            color=color.dark_gray,
            scale=(0.3, 0.02),
            position=(-0.55, 0.45)
        )
        # HP bar fill
        self.hud_elements['hp_fill'] = Entity(
            parent=camera.ui,
            model='quad',
            color=color.rgb(255, 100, 120),
            scale=(0.3, 0.02),
            position=(-0.55, 0.45),
            origin=(-0.5, 0)
        )
        
        # Ink bar background
        self.hud_elements['ink_bg'] = Entity(
            parent=camera.ui,
            model='quad',
            color=color.dark_gray,
            scale=(0.3, 0.015),
            position=(-0.55, 0.42)
        )
        # Ink bar fill
        self.hud_elements['ink_fill'] = Entity(
            parent=camera.ui,
            model='quad',
            color=PALETTES[self.palette_index]['ink'],
            scale=(0.3, 0.015),
            position=(-0.55, 0.42),
            origin=(-0.5, 0)
        )
        
        # Stats text
        self.hud_elements['stats'] = Text(
            text='Lvl 1 • XP 0/100',
            scale=1,
            position=(-0.7, 0.48),
            color=color.white
        )
        
        self.hud_elements['gear'] = Text(
            text='Gear: Common',
            scale=0.8,
            position=(-0.7, 0.38),
            color=color.light_gray
        )
        
        # Map title
        self.hud_elements['map_title'] = Text(
            text='Tech Demo Arena',
            scale=1.5,
            origin=(0, 0),
            y=0.45,
            color=color.white
        )
        
        # Timer
        self.hud_elements['timer'] = Text(
            text='3:00',
            scale=1.2,
            origin=(0, 0),
            y=0.40,
            color=color.light_gray
        )
        
        # Territory bars
        self.hud_elements['terr_bg'] = Entity(
            parent=camera.ui,
            model='quad',
            color=color.dark_gray,
            scale=(0.5, 0.025),
            position=(0, -0.45)
        )
        self.hud_elements['terr_player'] = Entity(
            parent=camera.ui,
            model='quad',
            color=PALETTES[self.palette_index]['ink'],
            scale=(0.01, 0.025),
            position=(-0.245, -0.45),
            origin=(-0.5, 0)
        )
        self.hud_elements['terr_enemy'] = Entity(
            parent=camera.ui,
            model='quad',
            color=ENEMY_COLOR,
            scale=(0.01, 0.025),
            position=(0.245, -0.45),
            origin=(0.5, 0)
        )
        
        self.hud_elements['terr_p_pct'] = Text(
            text='0%',
            scale=0.8,
            position=(-0.32, -0.46),
            color=color.white
        )
        self.hud_elements['terr_e_pct'] = Text(
            text='0%',
            scale=0.8,
            position=(0.27, -0.46),
            color=color.white
        )
        
        # Ink percentage
        self.hud_elements['ink_pct'] = Text(
            text='Ink: 100%',
            scale=0.8,
            position=(-0.7, 0.35),
            color=color.light_gray
        )
        
        # Crosshair
        self.crosshair = Entity(
            parent=camera.ui,
            model='quad',
            color=color.white,
            scale=0.01,
            position=(0, 0)
        )
        
        # Toast (hidden initially)
        self.hud_elements['toast'] = Text(
            text='',
            scale=1.5,
            origin=(0, 0),
            y=-0.3,
            color=color.white,
            visible=False
        )
    
    def destroy_hud(self):
        """Remove HUD elements"""
        for key, element in self.hud_elements.items():
            destroy(element)
        self.hud_elements = {}
        if self.crosshair:
            destroy(self.crosshair)
            self.crosshair = None
    
    def create_arena(self):
        """Create the 3D arena"""
        # Ground plane with ink texture
        self.ground_texture = self.create_ink_texture()
        
        self.ground = Entity(
            model='plane',
            scale=(ARENA_SIZE, 1, ARENA_SIZE),
            texture=self.ground_texture,
            texture_scale=(1, 1),
            collider='box',
            color=color.white,
            y=0
        )
        
        # Border walls
        wall_height = 4
        wall_color = color.rgb(50, 55, 65)
        
        # North wall
        self.walls.append(Entity(
            model='cube',
            scale=(ARENA_SIZE, wall_height, 1),
            position=(0, wall_height/2, ARENA_SIZE/2),
            color=wall_color,
            collider='box'
        ))
        # South wall
        self.walls.append(Entity(
            model='cube',
            scale=(ARENA_SIZE, wall_height, 1),
            position=(0, wall_height/2, -ARENA_SIZE/2),
            color=wall_color,
            collider='box'
        ))
        # East wall
        self.walls.append(Entity(
            model='cube',
            scale=(1, wall_height, ARENA_SIZE),
            position=(ARENA_SIZE/2, wall_height/2, 0),
            color=wall_color,
            collider='box'
        ))
        # West wall
        self.walls.append(Entity(
            model='cube',
            scale=(1, wall_height, ARENA_SIZE),
            position=(-ARENA_SIZE/2, wall_height/2, 0),
            color=wall_color,
            collider='box'
        ))
        
        # Central structure
        self.walls.append(Entity(
            model='cube',
            scale=(12, 2, 8),
            position=(0, 1, 0),
            color=wall_color,
            collider='box'
        ))
        
        # Corner pillars
        corners = [
            (ARENA_SIZE/4, ARENA_SIZE/4),
            (-ARENA_SIZE/4, ARENA_SIZE/4),
            (ARENA_SIZE/4, -ARENA_SIZE/4),
            (-ARENA_SIZE/4, -ARENA_SIZE/4)
        ]
        for cx, cz in corners:
            self.walls.append(Entity(
                model='cylinder',
                scale=(3, 3, 3),
                position=(cx, 1.5, cz),
                color=wall_color,
                collider='box'
            ))
        
        # Side barriers
        for side in [-1, 1]:
            for z_side in [-1, 1]:
                self.walls.append(Entity(
                    model='cube',
                    scale=(8, 1.5, 1),
                    position=(side * ARENA_SIZE/3, 0.75, z_side * ARENA_SIZE/4),
                    color=wall_color,
                    collider='box'
                ))
    
    def create_ink_texture(self):
        """Create a texture for the ground ink"""
        # Create a simple colored texture
        tex = Texture(Image.new('RGBA', (INK_RESOLUTION, INK_RESOLUTION), (40, 45, 55, 255)))
        return tex
    
    def update_ink_texture(self):
        """Update the ground texture based on ink data"""
        if not self.ground_texture:
            return
        
        palette = PALETTES[self.palette_index]
        player_color = (int(palette['ink'].r * 255), int(palette['ink'].g * 255), int(palette['ink'].b * 255), 255)
        enemy_color = (int(ENEMY_COLOR.r * 255), int(ENEMY_COLOR.g * 255), int(ENEMY_COLOR.b * 255), 255)
        base_color = (40, 45, 55, 255)
        
        # Update pixels
        img = Image.new('RGBA', (INK_RESOLUTION, INK_RESOLUTION), base_color)
        pixels = img.load()
        
        for x in range(INK_RESOLUTION):
            for y in range(INK_RESOLUTION):
                owner = self.ink_owner[x][y]
                alpha = self.ink_alpha[x][y]
                
                if owner == TEAM_PLAYER and alpha > 0.1:
                    t = min(1, alpha)
                    r = int(base_color[0] + (player_color[0] - base_color[0]) * t)
                    g = int(base_color[1] + (player_color[1] - base_color[1]) * t)
                    b = int(base_color[2] + (player_color[2] - base_color[2]) * t)
                    pixels[x, y] = (r, g, b, 255)
                elif owner == TEAM_ENEMY and alpha > 0.1:
                    t = min(1, alpha)
                    r = int(base_color[0] + (enemy_color[0] - base_color[0]) * t)
                    g = int(base_color[1] + (enemy_color[1] - base_color[1]) * t)
                    b = int(base_color[2] + (enemy_color[2] - base_color[2]) * t)
                    pixels[x, y] = (r, g, b, 255)
                else:
                    # Checkerboard
                    checker = ((x // 8) + (y // 8)) % 2
                    val = 40 + checker * 8
                    pixels[x, y] = (val, val + 5, val + 15, 255)
        
        # Apply new texture
        self.ground_texture = Texture(img)
        if self.ground:
            self.ground.texture = self.ground_texture
    
    def create_player(self):
        """Create the player controller"""
        self.player = FirstPersonController(
            position=(0, 2, -ARENA_SIZE/3),
            speed=8,
            mouse_sensitivity=Vec2(50, 50)
        )
        self.player.gravity = 0.5
        self.player.jump_height = 2
        self.player.cursor.visible = False
        
        # Weapon model (simple representation)
        self.weapon_model = Entity(
            parent=camera,
            model='cube',
            scale=(0.1, 0.1, 0.4),
            position=(0.3, -0.2, 0.5),
            color=PALETTES[self.palette_index]['dark'],
            rotation=(0, 0, 0)
        )
        
        # Weapon nozzle
        self.weapon_nozzle = Entity(
            parent=self.weapon_model,
            model='cube',
            scale=(0.8, 0.8, 0.3),
            position=(0, 0, 0.6),
            color=PALETTES[self.palette_index]['ink']
        )
        
        # Ink tank
        self.ink_tank = Entity(
            parent=camera,
            model='cube',
            scale=(0.15, 0.25, 0.1),
            position=(0.45, -0.15, 0.3),
            color=PALETTES[self.palette_index]['ink']
        )
    
    def destroy_arena(self):
        """Remove arena elements"""
        if self.ground:
            destroy(self.ground)
            self.ground = None
        for wall in self.walls:
            destroy(wall)
        self.walls = []
        if self.player:
            destroy(self.player)
            self.player = None
        if self.weapon_model:
            destroy(self.weapon_model)
            self.weapon_model = None
        if hasattr(self, 'weapon_nozzle') and self.weapon_nozzle:
            destroy(self.weapon_nozzle)
        if hasattr(self, 'ink_tank') and self.ink_tank:
            destroy(self.ink_tank)
        for enemy in self.enemies:
            destroy(enemy)
        self.enemies = []
        for bomb in self.bombs:
            destroy(bomb)
        self.bombs = []
        for splat in self.ink_splats:
            destroy(splat)
        self.ink_splats = []
    
    def world_to_ink(self, x, z):
        """Convert world coordinates to ink texture coordinates"""
        ix = int((x + ARENA_SIZE/2) / ARENA_SIZE * INK_RESOLUTION)
        iy = int((z + ARENA_SIZE/2) / ARENA_SIZE * INK_RESOLUTION)
        return max(0, min(INK_RESOLUTION-1, ix)), max(0, min(INK_RESOLUTION-1, iy))
    
    def paint_circle(self, wx, wz, radius, team, alpha=0.8):
        """Paint a circle of ink at world position"""
        cx, cy = self.world_to_ink(wx, wz)
        r = int(radius / ARENA_SIZE * INK_RESOLUTION)
        r = max(1, r)
        
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                ix, iy = cx + dx, cy + dy
                if 0 <= ix < INK_RESOLUTION and 0 <= iy < INK_RESOLUTION:
                    if dx*dx + dy*dy <= r*r:
                        self.ink_owner[ix][iy] = team
                        self.ink_alpha[ix][iy] = min(1, self.ink_alpha[ix][iy] + alpha)
    
    def get_ink_at(self, wx, wz):
        """Get ink info at world position"""
        ix, iy = self.world_to_ink(wx, wz)
        if 0 <= ix < INK_RESOLUTION and 0 <= iy < INK_RESOLUTION:
            return self.ink_owner[ix][iy], self.ink_alpha[ix][iy]
        return TEAM_NONE, 0
    
    def territory_ratio(self, team):
        """Calculate territory percentage for a team"""
        owned = 0
        total = 0
        for x in range(INK_RESOLUTION):
            for y in range(INK_RESOLUTION):
                total += 1
                if self.ink_owner[x][y] == team and self.ink_alpha[x][y] > 0.1:
                    owned += 1
        return owned / total if total > 0 else 0
    
    def spawn_enemy(self):
        """Spawn an enemy at arena edge"""
        side = random.randint(0, 3)
        if side == 0:
            pos = Vec3(random.uniform(-ARENA_SIZE/3, ARENA_SIZE/3), 1, ARENA_SIZE/3)
        elif side == 1:
            pos = Vec3(random.uniform(-ARENA_SIZE/3, ARENA_SIZE/3), 1, -ARENA_SIZE/3)
        elif side == 2:
            pos = Vec3(ARENA_SIZE/3, 1, random.uniform(-ARENA_SIZE/3, ARENA_SIZE/3))
        else:
            pos = Vec3(-ARENA_SIZE/3, 1, random.uniform(-ARENA_SIZE/3, ARENA_SIZE/3))
        
        enemy = Entity(
            model='sphere',
            scale=1.5,
            position=pos,
            color=ENEMY_COLOR,
            collider='sphere'
        )
        enemy.hp = 40
        enemy.cooldown = 0
        enemy.target = Vec3(0, 1, 0)
        enemy.bob_phase = random.random() * math.pi * 2
        
        # Eye
        eye = Entity(
            parent=enemy,
            model='sphere',
            scale=0.3,
            position=(0, 0.2, 0.4),
            color=color.black
        )
        enemy.eye = eye
        
        self.enemies.append(enemy)
    
    def throw_bomb(self):
        """Throw an ink bomb"""
        if self.ink < 15:
            return
        
        self.ink -= 15
        
        # Get throw direction from camera
        direction = camera.forward
        
        bomb = Entity(
            model='sphere',
            scale=0.4,
            position=self.player.position + Vec3(0, 1.5, 0) + direction * 1.5,
            color=PALETTES[self.palette_index]['ink']
        )
        bomb.velocity = direction * 20 + Vec3(0, 8, 0)
        bomb.timer = 0
        bomb.power = 5 + self.perks['bomb_power'] * 2
        bomb.team = TEAM_PLAYER
        
        self.bombs.append(bomb)
    
    def spawn_ink_splat(self, pos, team, count=5):
        """Spawn visual ink splat particles"""
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(3, 8)
            
            splat = Entity(
                model='sphere',
                scale=0.2,
                position=pos + Vec3(0, 0.5, 0),
                color=PALETTES[self.palette_index]['ink'] if team == TEAM_PLAYER else ENEMY_COLOR
            )
            splat.velocity = Vec3(
                math.cos(angle) * speed,
                random.uniform(2, 6),
                math.sin(angle) * speed
            )
            splat.timer = 0
            splat.team = team
            
            self.ink_splats.append(splat)
    
    def show_toast(self, text):
        """Show a toast message"""
        self.toast_text = text
        self.toast_timer = 2.0
    
    def reset_match(self):
        """Reset for a new match"""
        # Clear ink
        for x in range(INK_RESOLUTION):
            for y in range(INK_RESOLUTION):
                self.ink_owner[x][y] = TEAM_NONE
                self.ink_alpha[x][y] = 0
        
        # Reset stats
        self.hp = self.hp_max
        self.ink = 100
        self.match_time = 0
        self.splat_count = 0
        self.spawn_timer = 2
        self.perk_choices = []
        
        # Initial ink around spawn
        self.paint_circle(0, -ARENA_SIZE/3, 5, TEAM_PLAYER, 1.0)
        
        # Clear entities
        for enemy in self.enemies:
            destroy(enemy)
        self.enemies = []
        for bomb in self.bombs:
            destroy(bomb)
        self.bombs = []
        for splat in self.ink_splats:
            destroy(splat)
        self.ink_splats = []
        
        # Spawn initial enemies
        for _ in range(4):
            self.spawn_enemy()
        
        self.update_ink_texture()
    
    def start_game(self):
        """Start the game"""
        self.destroy_menu()
        self.create_arena()
        self.create_player()
        self.create_hud()
        self.reset_match()
        self.state = 'playing'
        mouse.locked = True
        self.show_toast("Paint the arena to win!")
    
    def end_game(self, won):
        """End the current match"""
        self.state = 'win' if won else 'lose'
        mouse.locked = False
        
        # Create result panel
        p_terr = int(self.territory_ratio(TEAM_PLAYER) * 100)
        
        bg_color = PALETTES[self.palette_index]['ink'] if won else ENEMY_COLOR
        
        self.result_panel = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.8, 0.5),
            color=bg_color,
            z=1
        )
        
        self.result_title = Text(
            text='VICTORY!' if won else 'SPLATTED!',
            scale=4,
            origin=(0, 0),
            y=0.1,
            color=color.white
        )
        
        self.result_stats = Text(
            text=f'Territory: {p_terr}% • Splats: {self.splat_count}',
            scale=1.5,
            origin=(0, 0),
            y=-0.05,
            color=color.white
        )
        
        self.result_prompt = Text(
            text='Press ENTER to continue',
            scale=1.2,
            origin=(0, 0),
            y=-0.15,
            color=color.white
        )
    
    def return_to_menu(self):
        """Return to main menu"""
        # Destroy game elements
        self.destroy_hud()
        self.destroy_arena()
        
        # Destroy result panel
        if self.result_panel:
            destroy(self.result_panel)
            self.result_panel = None
        if hasattr(self, 'result_title') and self.result_title:
            destroy(self.result_title)
        if hasattr(self, 'result_stats') and self.result_stats:
            destroy(self.result_stats)
        if hasattr(self, 'result_prompt') and self.result_prompt:
            destroy(self.result_prompt)
        
        self.create_menu()
        self.state = 'menu'
        mouse.locked = False
    
    def update(self):
        """Main update loop"""
        dt = time.dt
        self.state_timer += dt
        self.toast_timer = max(0, self.toast_timer - dt)
        
        if self.state == 'boot_nintendo':
            self.update_boot(dt)
        elif self.state == 'boot_samsoft':
            self.update_boot(dt)
        elif self.state == 'menu':
            self.update_menu(dt)
        elif self.state == 'playing':
            self.update_game(dt)
        elif self.state in ('win', 'lose'):
            pass  # Wait for input
    
    def update_boot(self, dt):
        """Update boot sequence"""
        # Fade effect
        alpha = min(1, self.state_timer / 0.5)
        if self.state_timer > 1.5:
            alpha = max(0, 1 - (self.state_timer - 1.5) / 0.5)
        
        if self.boot_text:
            self.boot_text.color = color.rgba(255, 255, 255, int(alpha * 255))
        if self.boot_sub:
            self.boot_sub.color = color.rgba(150, 150, 150, int(alpha * 255))
        
        if self.state_timer > 2.0:
            if self.state == 'boot_nintendo':
                if self.boot_text:
                    self.boot_text.text = 'SAMSOFT'
                self.state = 'boot_samsoft'
                self.state_timer = 0
            elif self.state == 'boot_samsoft':
                # Destroy boot screen
                if self.boot_text:
                    destroy(self.boot_text)
                    self.boot_text = None
                if self.boot_sub:
                    destroy(self.boot_sub)
                    self.boot_sub = None
                
                self.create_menu()
                self.state = 'menu'
                self.state_timer = 0
    
    def update_menu(self, dt):
        """Update menu"""
        # Animate title color
        idx = int(self.state_timer * 2) % len(PALETTES)
        if self.menu_title:
            self.menu_title.color = PALETTES[idx]['ink']
        
        # Blink start prompt
        if hasattr(self, 'menu_start') and self.menu_start:
            self.menu_start.visible = int(self.state_timer * 2) % 2 == 0
    
    def update_game(self, dt):
        """Update gameplay"""
        self.match_time += dt
        self.dash_cooldown = max(0, self.dash_cooldown - dt)
        
        # Check win/lose
        if self.match_time >= self.match_duration:
            p_terr = self.territory_ratio(TEAM_PLAYER)
            e_terr = self.territory_ratio(TEAM_ENEMY)
            self.end_game(p_terr > e_terr)
            return
        
        if self.territory_ratio(TEAM_PLAYER) > 0.75:
            self.end_game(True)
            return
        
        if self.hp <= 0:
            self.end_game(False)
            return
        
        # Player ink status
        owner, alpha = self.get_ink_at(self.player.x, self.player.z)
        in_own_ink = owner == TEAM_PLAYER and alpha > 0.2
        in_enemy_ink = owner == TEAM_ENEMY and alpha > 0.2
        
        # Speed modification
        base_speed = 8
        if in_own_ink:
            self.player.speed = base_speed * (1.3 + self.perks['swim_speed'] * 0.2)
        elif in_enemy_ink:
            self.player.speed = base_speed * 0.5
        else:
            self.player.speed = base_speed
        
        # Shooting
        if held_keys['left mouse'] and self.ink > 0:
            self.shooting = True
            eff = 1 + self.perks['ink_eff'] * 0.3
            
            # Paint in front of player
            forward = camera.forward
            spray_pos = self.player.position + forward * 4
            self.paint_circle(spray_pos.x, spray_pos.z, 2 * eff, TEAM_PLAYER, 0.3)
            
            self.ink = max(0, self.ink - 0.4 / eff)
            
            # Spawn splat particles occasionally
            if random.random() < 0.2:
                self.spawn_ink_splat(spray_pos, TEAM_PLAYER, 2)
            
            # Weapon recoil
            if self.weapon_model:
                self.weapon_model.z = 0.45 + random.uniform(-0.02, 0.02)
        else:
            self.shooting = False
            if self.weapon_model:
                self.weapon_model.z = 0.5
        
        # Rolling
        if held_keys['right mouse'] and self.ink > 0:
            self.rolling = True
            eff = 1 + self.perks['ink_eff'] * 0.2
            r = 3 + self.perks['swim_speed']
            self.paint_circle(self.player.x, self.player.z, r, TEAM_PLAYER, 0.5)
            self.ink = max(0, self.ink - 0.3 / eff)
        else:
            self.rolling = False
        
        # Dash
        if held_keys['space'] and self.ink > 10 and self.dash_cooldown <= 0 and in_own_ink:
            self.ink -= 10
            self.dash_cooldown = 0.5
            # Boost forward
            forward = camera.forward
            self.player.position += forward * 5
            self.show_toast("Dash!")
        
        # Ink regeneration
        if in_own_ink:
            self.ink = min(100, self.ink + 20 * dt)
        else:
            self.ink = min(100, self.ink + 5 * dt)
        
        # Update enemies
        for enemy in self.enemies[:]:
            self.update_enemy(enemy, dt)
        
        # Update bombs
        for bomb in self.bombs[:]:
            self.update_bomb(bomb, dt)
        
        # Update splats
        for splat in self.ink_splats[:]:
            self.update_splat(splat, dt)
        
        # Spawn enemies
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_enemy()
            self.spawn_timer = 2.5 - self.territory_ratio(TEAM_PLAYER) * 1.5
        
        # Update ink texture periodically
        if int(self.match_time * 10) % 5 == 0:
            self.update_ink_texture()
        
        # Update HUD
        self.update_hud()
    
    def update_enemy(self, enemy, dt):
        """Update an enemy"""
        enemy.cooldown = max(0, enemy.cooldown - dt)
        enemy.bob_phase += dt * 5
        
        # Bob animation
        enemy.y = 1 + math.sin(enemy.bob_phase) * 0.2
        
        # Retarget occasionally
        if random.random() < 0.02:
            enemy.target = Vec3(
                self.player.x + random.uniform(-15, 15),
                1,
                self.player.z + random.uniform(-15, 15)
            )
        
        # Move toward target
        direction = (enemy.target - enemy.position).normalized()
        speed = 4
        enemy.position += direction * speed * dt
        
        # Keep in bounds
        enemy.x = max(-ARENA_SIZE/2 + 2, min(ARENA_SIZE/2 - 2, enemy.x))
        enemy.z = max(-ARENA_SIZE/2 + 2, min(ARENA_SIZE/2 - 2, enemy.z))
        
        # Paint trail
        self.paint_circle(enemy.x, enemy.z, 1.5, TEAM_ENEMY, 0.5)
        
        # Attack player
        dist = (enemy.position - self.player.position).length()
        if dist < 3 and enemy.cooldown <= 0:
            owner, alpha = self.get_ink_at(enemy.x, enemy.z)
            if owner == TEAM_ENEMY and alpha > 0.2:
                self.hp -= 10
                enemy.cooldown = 1.0
                self.show_toast("Ouch!")
        
        # Check death
        if enemy.hp <= 0:
            self.enemies.remove(enemy)
            destroy(enemy)
            self.splat_count += 1
            self.spawn_ink_splat(enemy.position, TEAM_PLAYER, 10)
            
            # XP
            self.xp += 25
            if self.xp >= self.xp_to:
                self.level += 1
                self.xp = 0
                self.xp_to = int(self.xp_to * 1.35)
                self.perk_choices = self.roll_perks()
                self.show_toast("Level up! Press E for perk")
            
            # Gear drop
            if random.random() < 0.15:
                tiers = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
                r = random.random()
                new_tier = 4 if r > 0.985 else 3 if r > 0.94 else 2 if r > 0.75 else 1 if r > 0.45 else 0
                if new_tier > self.gear_tier:
                    self.gear_tier = new_tier
                    self.show_toast(f"Gear: {tiers[new_tier]}")
    
    def update_bomb(self, bomb, dt):
        """Update a bomb"""
        bomb.timer += dt
        
        # Physics
        bomb.velocity += Vec3(0, -20, 0) * dt  # Gravity
        bomb.position += bomb.velocity * dt
        
        # Hit ground or timeout
        if bomb.y <= 0.5 or bomb.timer > 2:
            # Explode
            self.paint_circle(bomb.x, bomb.z, bomb.power, bomb.team, 1.0)
            self.spawn_ink_splat(bomb.position, bomb.team, 15)
            
            # Damage enemies
            for enemy in self.enemies:
                dist = (enemy.position - bomb.position).length()
                if dist < bomb.power:
                    enemy.hp -= 30
            
            self.bombs.remove(bomb)
            destroy(bomb)
    
    def update_splat(self, splat, dt):
        """Update an ink splat particle"""
        splat.timer += dt
        splat.velocity += Vec3(0, -15, 0) * dt  # Gravity
        splat.position += splat.velocity * dt
        
        # Hit ground
        if splat.y <= 0.1:
            self.paint_circle(splat.x, splat.z, 0.5, splat.team, 0.3)
            self.ink_splats.remove(splat)
            destroy(splat)
        elif splat.timer > 2:
            self.ink_splats.remove(splat)
            destroy(splat)
    
    def update_hud(self):
        """Update HUD elements"""
        if 'hp_fill' in self.hud_elements:
            self.hud_elements['hp_fill'].scale_x = 0.3 * (self.hp / self.hp_max)
        
        if 'ink_fill' in self.hud_elements:
            self.hud_elements['ink_fill'].scale_x = 0.3 * (self.ink / 100)
            self.hud_elements['ink_fill'].color = PALETTES[self.palette_index]['ink']
        
        if 'stats' in self.hud_elements:
            self.hud_elements['stats'].text = f'Lvl {self.level} • XP {self.xp}/{self.xp_to}'
        
        if 'gear' in self.hud_elements:
            tiers = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
            self.hud_elements['gear'].text = f'Gear: {tiers[self.gear_tier]}'
        
        if 'timer' in self.hud_elements:
            time_left = max(0, self.match_duration - self.match_time)
            mins = int(time_left // 60)
            secs = int(time_left % 60)
            self.hud_elements['timer'].text = f'{mins}:{secs:02d}'
        
        if 'ink_pct' in self.hud_elements:
            self.hud_elements['ink_pct'].text = f'Ink: {int(self.ink)}%'
        
        # Territory
        p_terr = self.territory_ratio(TEAM_PLAYER)
        e_terr = self.territory_ratio(TEAM_ENEMY)
        
        if 'terr_player' in self.hud_elements:
            self.hud_elements['terr_player'].scale_x = 0.5 * p_terr
            self.hud_elements['terr_player'].color = PALETTES[self.palette_index]['ink']
        
        if 'terr_enemy' in self.hud_elements:
            self.hud_elements['terr_enemy'].scale_x = 0.5 * e_terr
        
        if 'terr_p_pct' in self.hud_elements:
            self.hud_elements['terr_p_pct'].text = f'{int(p_terr * 100)}%'
        
        if 'terr_e_pct' in self.hud_elements:
            self.hud_elements['terr_e_pct'].text = f'{int(e_terr * 100)}%'
        
        # Toast
        if 'toast' in self.hud_elements:
            if self.toast_timer > 0:
                self.hud_elements['toast'].text = self.toast_text
                self.hud_elements['toast'].visible = True
            else:
                self.hud_elements['toast'].visible = False
    
    def roll_perks(self):
        """Roll perk choices"""
        pool = [
            {'key': 'ink_eff', 'name': 'Ink Efficiency +1'},
            {'key': 'swim_speed', 'name': 'Swim Speed +1'},
            {'key': 'bomb_power', 'name': 'Bomb Power +1'},
        ]
        random.shuffle(pool)
        return pool[:2]
    
    def apply_perk(self, perk):
        """Apply a perk"""
        self.perks[perk['key']] += 1
        self.show_toast(f"Perk: {perk['name']}")
    
    def input(self, key):
        """Handle input"""
        if self.state == 'boot_nintendo' or self.state == 'boot_samsoft':
            self.state_timer = 999  # Skip
        
        elif self.state == 'menu':
            if key == 'enter' or key == 'left mouse down':
                self.start_game()
        
        elif self.state == 'playing':
            if key == 'escape':
                self.return_to_menu()
            elif key == 'q':
                self.throw_bomb()
            elif key == 'e' and self.perk_choices:
                self.apply_perk(self.perk_choices.pop(0))
            elif key == 'r':
                self.palette_index = (self.palette_index + 1) % len(PALETTES)
                self.show_toast("Palette swapped!")
                # Update weapon colors
                if self.weapon_model:
                    self.weapon_model.color = PALETTES[self.palette_index]['dark']
                if hasattr(self, 'weapon_nozzle') and self.weapon_nozzle:
                    self.weapon_nozzle.color = PALETTES[self.palette_index]['ink']
                if hasattr(self, 'ink_tank') and self.ink_tank:
                    self.ink_tank.color = PALETTES[self.palette_index]['ink']
        
        elif self.state in ('win', 'lose'):
            if key == 'enter' or key == 'left mouse down':
                self.return_to_menu()


# ============================================================================
# MAIN
# ============================================================================
app = Ursina(
    title='Ultra!Splatoon 0.1',
    borderless=False,
    fullscreen=False,
    size=(800, 600),
    vsync=True
)

# Try to import Image from PIL for texture generation
try:
    from PIL import Image
except ImportError:
    # Create a simple fallback
    class Image:
        @staticmethod
        def new(mode, size, color):
            class FakeImage:
                def __init__(self, mode, size, color):
                    self.mode = mode
                    self.size = size
                    self._pixels = [[color for _ in range(size[0])] for _ in range(size[1])]
                def load(self):
                    return self._pixels
            return FakeImage(mode, size, color)

game = UltraSplatoon()
game.setup()

def update():
    game.update()

def input(key):
    game.input(key)

app.run()
