# filename: pvz_replanted.py
# PvZ Replanted-Style Engine with Full Main Menu
# Team Flames / Samsoft

import pygame, sys, random, math
from enum import Enum, auto

# --- Constants ---
W, H = 800, 600
UI_HEIGHT = 60
ROWS, COLS = 5, 9
CW, CH = (W - 100) // COLS, (H - UI_HEIGHT - 80) // ROWS
LAWN_OFFSET_X, LAWN_OFFSET_Y = 50, UI_HEIGHT + 40

# --- Colors (PvZ Replanted palette) ---
class Colors:
    GRASS_LIGHT = (124, 204, 25)
    GRASS_DARK = (86, 176, 0)
    SKY_DAY = (135, 206, 235)
    SKY_NIGHT = (25, 25, 60)
    SOIL = (139, 90, 43)
    MENU_BG = (78, 53, 36)
    MENU_WOOD = (101, 67, 33)
    BUTTON_NORMAL = (76, 153, 0)
    BUTTON_HOVER = (102, 187, 23)
    BUTTON_PRESSED = (50, 120, 0)
    BUTTON_DISABLED = (100, 100, 100)
    TEXT_WHITE = (255, 255, 255)
    TEXT_YELLOW = (255, 230, 0)
    TEXT_BROWN = (80, 50, 20)
    SUN_YELLOW = (255, 220, 50)
    ZOMBIE_SKIN = (170, 200, 130)
    ZOMBIE_CLOTHES = (80, 80, 80)
    PEA = (80, 200, 60)
    PEASHOOTER = (28, 180, 28)

# --- Game States ---
class GameState(Enum):
    MAIN_MENU = auto()
    ADVENTURE_SELECT = auto()
    MINIGAMES_MENU = auto()
    PUZZLE_MENU = auto()
    SURVIVAL_MENU = auto()
    ZEN_GARDEN = auto()
    ALMANAC = auto()
    ALMANAC_PLANTS = auto()
    ALMANAC_ZOMBIES = auto()
    OPTIONS = auto()
    CREDITS = auto()
    HELP = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    STORE = auto()

# --- Initialize Pygame ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Cat's PvZ Replanted 0.2")
clock = pygame.time.Clock()

# --- Fonts ---
try:
    font_title = pygame.font.SysFont("impact", 48)
    font_large = pygame.font.SysFont("arial", 32, bold=True)
    font_medium = pygame.font.SysFont("arial", 24)
    font_small = pygame.font.SysFont("arial", 18)
    font_tiny = pygame.font.SysFont("arial", 14)
except:
    font_title = pygame.font.SysFont(None, 48)
    font_large = pygame.font.SysFont(None, 32)
    font_medium = pygame.font.SysFont(None, 24)
    font_small = pygame.font.SysFont(None, 18)
    font_tiny = pygame.font.SysFont(None, 14)

# --- Plant Types ---
class PlantType(Enum):
    PEASHOOTER = {"name": "Peashooter", "cost": 100, "hp": 100, "cooldown": 1.35, "recharge": 7.5, "damage": 20, "color": Colors.PEASHOOTER}
    SUNFLOWER = {"name": "Sunflower", "cost": 50, "hp": 100, "cooldown": 24.0, "recharge": 7.5, "sun_prod": 25, "color": (255, 200, 0)}
    WALLNUT = {"name": "Wall-nut", "cost": 50, "hp": 400, "cooldown": 0, "recharge": 30.0, "color": (180, 120, 60)}
    CHERRYBOMB = {"name": "Cherry Bomb", "cost": 150, "hp": 100, "cooldown": 0, "recharge": 50.0, "damage": 1800, "color": (220, 30, 30)}
    POTATOMINE = {"name": "Potato Mine", "cost": 25, "hp": 100, "cooldown": 0, "recharge": 30.0, "damage": 1800, "arm_time": 15.0, "color": (139, 90, 43)}
    SNOWPEA = {"name": "Snow Pea", "cost": 175, "hp": 100, "cooldown": 1.35, "recharge": 7.5, "damage": 20, "slow": 0.5, "color": (150, 200, 255)}
    CHOMPER = {"name": "Chomper", "cost": 150, "hp": 100, "cooldown": 42.0, "recharge": 7.5, "damage": 9999, "color": (200, 100, 200)}
    REPEATER = {"name": "Repeater", "cost": 200, "hp": 100, "cooldown": 1.35, "recharge": 7.5, "damage": 20, "shots": 2, "color": (20, 150, 20)}

# --- Zombie Types ---
class ZombieType(Enum):
    BASIC = {"name": "Zombie", "hp": 200, "speed": 18, "damage": 100, "color": Colors.ZOMBIE_SKIN}
    CONEHEAD = {"name": "Conehead Zombie", "hp": 560, "speed": 18, "damage": 100, "color": (255, 140, 0)}
    BUCKETHEAD = {"name": "Buckethead Zombie", "hp": 1300, "speed": 18, "damage": 100, "color": (150, 150, 150)}
    FLAG = {"name": "Flag Zombie", "hp": 200, "speed": 23, "damage": 100, "color": (200, 50, 50)}
    POLE_VAULTER = {"name": "Pole Vaulting Zombie", "hp": 340, "speed": 40, "damage": 100, "vaults": True, "color": (100, 100, 200)}
    NEWSPAPER = {"name": "Newspaper Zombie", "hp": 340, "speed": 18, "damage": 100, "enrage_speed": 50, "color": (200, 200, 200)}

# --- Level Definitions ---
ADVENTURE_LEVELS = [
    {"name": "Day 1-1", "world": "day", "waves": 2, "zombies": [ZombieType.BASIC], "sun_start": 150},
    {"name": "Day 1-2", "world": "day", "waves": 3, "zombies": [ZombieType.BASIC], "sun_start": 100},
    {"name": "Day 1-3", "world": "day", "waves": 4, "zombies": [ZombieType.BASIC, ZombieType.CONEHEAD], "sun_start": 100},
    {"name": "Day 1-4", "world": "day", "waves": 5, "zombies": [ZombieType.BASIC, ZombieType.CONEHEAD], "sun_start": 50},
    {"name": "Day 1-5", "world": "day", "waves": 6, "zombies": [ZombieType.BASIC, ZombieType.CONEHEAD, ZombieType.FLAG], "sun_start": 50, "flag_wave": True},
    {"name": "Night 2-1", "world": "night", "waves": 3, "zombies": [ZombieType.BASIC], "sun_start": 50, "no_sun_sky": True},
    {"name": "Night 2-2", "world": "night", "waves": 4, "zombies": [ZombieType.BASIC, ZombieType.CONEHEAD], "sun_start": 50, "no_sun_sky": True},
    {"name": "Night 2-3", "world": "night", "waves": 5, "zombies": [ZombieType.BASIC, ZombieType.NEWSPAPER], "sun_start": 50, "no_sun_sky": True},
    {"name": "Pool 3-1", "world": "pool", "waves": 4, "zombies": [ZombieType.BASIC, ZombieType.CONEHEAD], "sun_start": 100, "pool_lanes": [2, 3]},
    {"name": "Fog 4-1", "world": "fog", "waves": 5, "zombies": [ZombieType.BASIC, ZombieType.CONEHEAD, ZombieType.POLE_VAULTER], "sun_start": 50, "fog": True},
    {"name": "Roof 5-1", "world": "roof", "waves": 6, "zombies": [ZombieType.BASIC, ZombieType.CONEHEAD, ZombieType.BUCKETHEAD], "sun_start": 100, "sloped": True},
]

MINIGAMES = [
    {"name": "ZomBotany", "desc": "Zombies with plant heads!", "unlocked": True},
    {"name": "Wall-nut Bowling", "desc": "Bowl over the zombies!", "unlocked": True},
    {"name": "Slot Machine", "desc": "Spin for plants!", "unlocked": True},
    {"name": "It's Raining Seeds", "desc": "Plants fall from sky!", "unlocked": False},
    {"name": "Beghouled", "desc": "Match-3 plants!", "unlocked": False},
    {"name": "Invisighoul", "desc": "Invisible zombies!", "unlocked": False},
    {"name": "Seeing Stars", "desc": "Plant in star pattern!", "unlocked": False},
    {"name": "Zombiquarium", "desc": "Feed the zombies!", "unlocked": False},
    {"name": "Portal Combat", "desc": "Portals everywhere!", "unlocked": False},
    {"name": "Column Like You See 'Em", "desc": "Pre-placed plants!", "unlocked": False},
    {"name": "Bobsled Bonanza", "desc": "Zomboni attack!", "unlocked": False},
    {"name": "Zombie Nimble Zombie Quick", "desc": "Speed run!", "unlocked": False},
    {"name": "Whack a Zombie", "desc": "Whack 'em good!", "unlocked": False},
    {"name": "Last Stand", "desc": "5000 sun, survive!", "unlocked": False},
    {"name": "Pogo Party", "desc": "Pogo zombies!", "unlocked": False},
    {"name": "Dr. Zomboss's Revenge", "desc": "The final battle!", "unlocked": False},
]

SURVIVAL_MODES = [
    {"name": "Survival: Day", "desc": "Survive 5 flags", "unlocked": True},
    {"name": "Survival: Night", "desc": "Survive 5 flags", "unlocked": True},
    {"name": "Survival: Pool", "desc": "Survive 5 flags", "unlocked": False},
    {"name": "Survival: Fog", "desc": "Survive 5 flags", "unlocked": False},
    {"name": "Survival: Roof", "desc": "Survive 5 flags", "unlocked": False},
    {"name": "Survival: Day (Hard)", "desc": "Survive 10 flags", "unlocked": False},
    {"name": "Survival: Night (Hard)", "desc": "Survive 10 flags", "unlocked": False},
    {"name": "Survival: Pool (Hard)", "desc": "Survive 10 flags", "unlocked": False},
    {"name": "Survival: Fog (Hard)", "desc": "Survive 10 flags", "unlocked": False},
    {"name": "Survival: Roof (Hard)", "desc": "Survive 10 flags", "unlocked": False},
    {"name": "Survival: Endless", "desc": "How long can you last?", "unlocked": False},
]

PUZZLE_MODES = [
    {"name": "Vasebreaker", "desc": "Break the vases!", "unlocked": True},
    {"name": "I, Zombie", "desc": "Play as zombies!", "unlocked": True},
    {"name": "Vasebreaker Endless", "desc": "Endless vases!", "unlocked": False},
    {"name": "I, Zombie Endless", "desc": "Endless zombie planting!", "unlocked": False},
]

# --- Button Class ---
class Button:
    def __init__(self, x, y, w, h, text, font=None, enabled=True, style="normal"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font or font_medium
        self.enabled = enabled
        self.style = style
        self.hovered = False
        self.pressed = False
    
    def update(self, mouse_pos, mouse_pressed):
        self.hovered = self.rect.collidepoint(mouse_pos) and self.enabled
        self.pressed = self.hovered and mouse_pressed
    
    def draw(self, surface):
        if not self.enabled:
            color = Colors.BUTTON_DISABLED
        elif self.pressed:
            color = Colors.BUTTON_PRESSED
        elif self.hovered:
            color = Colors.BUTTON_HOVER
        else:
            color = Colors.BUTTON_NORMAL
        
        # Draw button with border
        if self.style == "wood":
            pygame.draw.rect(surface, Colors.MENU_WOOD, self.rect, border_radius=8)
            pygame.draw.rect(surface, (60, 40, 20), self.rect, 3, border_radius=8)
        else:
            pygame.draw.rect(surface, color, self.rect, border_radius=8)
            pygame.draw.rect(surface, (0, 80, 0) if self.enabled else (60, 60, 60), self.rect, 3, border_radius=8)
        
        # Draw text
        text_color = Colors.TEXT_WHITE if self.enabled else (150, 150, 150)
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.rect.collidepoint(event.pos) and 
                self.enabled)

# --- Animated Background Elements ---
class FloatingSun:
    def __init__(self):
        self.x = random.randint(0, W)
        self.y = random.randint(-100, -20)
        self.speed = random.uniform(30, 60)
        self.size = random.randint(15, 25)
        self.wobble = random.uniform(0, math.pi * 2)
    
    def update(self, dt):
        self.y += self.speed * dt
        self.wobble += 2 * dt
        return self.y < H + 50
    
    def draw(self, surface):
        x = self.x + math.sin(self.wobble) * 15
        pygame.draw.circle(surface, Colors.SUN_YELLOW, (int(x), int(self.y)), self.size)
        # Rays
        for i in range(8):
            angle = i * math.pi / 4 + self.wobble * 0.5
            dx = math.cos(angle) * (self.size + 8)
            dy = math.sin(angle) * (self.size + 8)
            pygame.draw.line(surface, Colors.SUN_YELLOW, (int(x), int(self.y)), 
                           (int(x + dx), int(self.y + dy)), 2)

class MenuZombie:
    def __init__(self):
        self.x = W + 50
        self.y = H - 120 + random.randint(-20, 20)
        self.speed = random.uniform(15, 30)
        self.arm_phase = random.uniform(0, math.pi * 2)
    
    def update(self, dt):
        self.x -= self.speed * dt
        self.arm_phase += 3 * dt
        return self.x > -50
    
    def draw(self, surface):
        # Body
        pygame.draw.rect(surface, Colors.ZOMBIE_CLOTHES, (int(self.x) - 10, int(self.y), 20, 40))
        # Head
        pygame.draw.circle(surface, Colors.ZOMBIE_SKIN, (int(self.x), int(self.y) - 10), 15)
        # Eyes
        pygame.draw.circle(surface, (255, 50, 50), (int(self.x) - 5, int(self.y) - 12), 3)
        pygame.draw.circle(surface, (255, 50, 50), (int(self.x) + 5, int(self.y) - 12), 3)
        # Arms (animated)
        arm_offset = math.sin(self.arm_phase) * 5
        pygame.draw.line(surface, Colors.ZOMBIE_SKIN, (int(self.x) - 10, int(self.y) + 10),
                        (int(self.x) - 25, int(self.y) + arm_offset), 4)
        pygame.draw.line(surface, Colors.ZOMBIE_SKIN, (int(self.x) + 10, int(self.y) + 10),
                        (int(self.x) + 25, int(self.y) - arm_offset), 4)

# --- Game Manager ---
class GameManager:
    def __init__(self):
        self.state = GameState.MAIN_MENU
        self.prev_state = None
        self.transition_alpha = 0
        self.floating_suns = []
        self.menu_zombies = []
        self.sun_spawn_timer = 0
        self.zombie_spawn_timer = 0
        self.scroll_offset = 0
        self.selected_level = 0
        self.current_level = None
        
        # Player progress
        self.player_progress = {
            "adventure_level": 1,
            "coins": 0,
            "plants_unlocked": [PlantType.PEASHOOTER, PlantType.SUNFLOWER],
            "achievements": [],
        }
        
        # Options
        self.options = {
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "fullscreen": False,
            "show_tips": True,
            "difficulty": "Normal",
        }
        
        # Game state (when playing)
        self.reset_game_state()
        
        # Create main menu buttons
        self.create_main_menu_buttons()
    
    def reset_game_state(self):
        self.sun = 150
        self.plants = {}  # (r,c) -> plant dict
        self.peas = []
        self.zombies = []
        self.falling_suns = []
        self.wave_num = 0
        self.total_waves = 10
        self.spawn_cd = 3.0
        self.sun_tick = 0.0
        self.game_over_reason = None
        self.selected_plant = None
        self.plant_recharges = {pt: 0.0 for pt in PlantType}
    
    def create_main_menu_buttons(self):
        btn_w, btn_h = 280, 50
        center_x = W // 2 - btn_w // 2
        start_y = 200
        gap = 60
        
        self.main_menu_buttons = [
            Button(center_x, start_y, btn_w, btn_h, "Adventure Mode"),
            Button(center_x, start_y + gap, btn_w, btn_h, "Mini-Games"),
            Button(center_x, start_y + gap * 2, btn_w, btn_h, "Puzzle"),
            Button(center_x, start_y + gap * 3, btn_w, btn_h, "Survival"),
            Button(center_x - 150, start_y + gap * 4, 130, 45, "Zen Garden", font_small),
            Button(center_x + 150, start_y + gap * 4, 130, 45, "Almanac", font_small),
            Button(center_x - 150, start_y + gap * 5, 130, 45, "Options", font_small),
            Button(center_x + 150, start_y + gap * 5, 130, 45, "Help", font_small),
            Button(center_x, start_y + gap * 6, btn_w, btn_h, "Credits"),
            Button(W - 100, H - 50, 80, 35, "Quit", font_small),
        ]
        
        # Back button for sub-menus
        self.back_button = Button(20, H - 50, 100, 35, "← Back", font_small)
    
    def change_state(self, new_state):
        self.prev_state = self.state
        self.state = new_state
        self.scroll_offset = 0
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # Update animated elements
        self.sun_spawn_timer += dt
        self.zombie_spawn_timer += dt
        
        if self.sun_spawn_timer > 1.5:
            self.floating_suns.append(FloatingSun())
            self.sun_spawn_timer = 0
        
        if self.zombie_spawn_timer > 4.0:
            self.menu_zombies.append(MenuZombie())
            self.zombie_spawn_timer = 0
        
        self.floating_suns = [s for s in self.floating_suns if s.update(dt)]
        self.menu_zombies = [z for z in self.menu_zombies if z.update(dt)]
        
        # State-specific updates
        if self.state == GameState.MAIN_MENU:
            for btn in self.main_menu_buttons:
                btn.update(mouse_pos, mouse_pressed)
        elif self.state == GameState.PLAYING:
            self.update_gameplay(dt)
        elif self.state in [GameState.ADVENTURE_SELECT, GameState.MINIGAMES_MENU, 
                           GameState.SURVIVAL_MENU, GameState.PUZZLE_MENU,
                           GameState.ALMANAC, GameState.ALMANAC_PLANTS, GameState.ALMANAC_ZOMBIES,
                           GameState.OPTIONS, GameState.CREDITS, GameState.HELP,
                           GameState.ZEN_GARDEN, GameState.STORE]:
            self.back_button.update(mouse_pos, mouse_pressed)
    
    def update_gameplay(self, dt):
        if self.state != GameState.PLAYING:
            return
        
        level = ADVENTURE_LEVELS[self.selected_level] if self.selected_level < len(ADVENTURE_LEVELS) else ADVENTURE_LEVELS[0]
        
        # Sun economy
        if not level.get("no_sun_sky", False):
            self.sun_tick += dt
            if self.sun_tick >= 6.0:
                # Spawn falling sun
                self.falling_suns.append({
                    "x": random.randint(LAWN_OFFSET_X + 20, W - LAWN_OFFSET_X - 20),
                    "y": -30,
                    "target_y": random.randint(100, H - 150),
                    "collected": False,
                    "timer": 8.0
                })
                self.sun_tick = 0
        
        # Update falling suns
        for sun in list(self.falling_suns):
            if sun["y"] < sun["target_y"]:
                sun["y"] += 60 * dt
            else:
                sun["timer"] -= dt
                if sun["timer"] <= 0:
                    self.falling_suns.remove(sun)
        
        # Update plant recharges
        for pt in self.plant_recharges:
            if self.plant_recharges[pt] > 0:
                self.plant_recharges[pt] -= dt
        
        # Plant actions
        for (r, c), plant in list(self.plants.items()):
            plant["cd"] = max(0.0, plant["cd"] - dt)
            ptype = plant["type"]
            
            if ptype == PlantType.PEASHOOTER:
                if plant["cd"] <= 0:
                    if any(z["r"] == r and z["x"] > c * CW + LAWN_OFFSET_X for z in self.zombies):
                        x, y = self.get_cell_center(r, c)
                        self.peas.append({"x": x + 20, "y": y, "vx": 300, "dmg": 20, "lane": r, "type": "normal"})
                        plant["cd"] = 1.35
            
            elif ptype == PlantType.SUNFLOWER:
                if plant["cd"] <= 0:
                    x, y = self.get_cell_center(r, c)
                    self.falling_suns.append({
                        "x": x,
                        "y": y,
                        "target_y": y + 20,
                        "collected": False,
                        "timer": 8.0
                    })
                    plant["cd"] = 24.0
            
            elif ptype == PlantType.SNOWPEA:
                if plant["cd"] <= 0:
                    if any(z["r"] == r and z["x"] > c * CW + LAWN_OFFSET_X for z in self.zombies):
                        x, y = self.get_cell_center(r, c)
                        self.peas.append({"x": x + 20, "y": y, "vx": 300, "dmg": 20, "lane": r, "type": "frozen"})
                        plant["cd"] = 1.35
            
            elif ptype == PlantType.REPEATER:
                if plant["cd"] <= 0:
                    if any(z["r"] == r and z["x"] > c * CW + LAWN_OFFSET_X for z in self.zombies):
                        x, y = self.get_cell_center(r, c)
                        self.peas.append({"x": x + 20, "y": y, "vx": 300, "dmg": 20, "lane": r, "type": "normal"})
                        self.peas.append({"x": x + 10, "y": y, "vx": 300, "dmg": 20, "lane": r, "type": "normal"})
                        plant["cd"] = 1.35
        
        # Update peas
        for pea in list(self.peas):
            pea["x"] += pea["vx"] * dt
            if pea["x"] > W:
                self.peas.remove(pea)
                continue
            
            # Hit detection
            for z in list(self.zombies):
                if z["r"] == pea["lane"] and abs(z["x"] - pea["x"]) < 20:
                    z["hp"] -= pea["dmg"]
                    if pea["type"] == "frozen":
                        z["slowed"] = 2.0  # Slow for 2 seconds
                    if pea in self.peas:
                        self.peas.remove(pea)
                    if z["hp"] <= 0:
                        self.zombies.remove(z)
                    break
        
        # Spawn zombies
        self.spawn_cd -= dt
        if self.spawn_cd <= 0 and self.wave_num < self.total_waves:
            zombie_types = level.get("zombies", [ZombieType.BASIC])
            ztype = random.choice(zombie_types)
            r = random.randrange(ROWS)
            self.zombies.append({
                "r": r,
                "x": W + 30,
                "hp": ztype.value["hp"],
                "max_hp": ztype.value["hp"],
                "speed": ztype.value["speed"],
                "type": ztype,
                "eat_cd": 0,
                "slowed": 0
            })
            self.wave_num += 1
            self.spawn_cd = random.uniform(1.5, 3.5)
        
        # Update zombies
        for z in list(self.zombies):
            # Update slow effect
            if z.get("slowed", 0) > 0:
                z["slowed"] -= dt
                speed = z["speed"] * 0.5
            else:
                speed = z["speed"]
            
            # Check for plant collision
            c = int((z["x"] - LAWN_OFFSET_X) // CW)
            r = z["r"]
            target = self.plants.get((r, c))
            
            if target and (c * CW + LAWN_OFFSET_X) <= z["x"] < ((c + 1) * CW + LAWN_OFFSET_X):
                z["eat_cd"] += dt
                if z["eat_cd"] > 0.5:
                    target["hp"] -= 20
                    z["eat_cd"] = 0
                    if target["hp"] <= 0:
                        del self.plants[(r, c)]
            else:
                z["x"] -= speed * dt
            
            if z["x"] < LAWN_OFFSET_X - 20:
                self.game_over_reason = "Zombies ate your brains!"
                self.state = GameState.GAME_OVER
        
        # Check win condition
        if self.wave_num >= self.total_waves and not self.zombies:
            self.state = GameState.LEVEL_COMPLETE
    
    def get_cell_center(self, r, c):
        return (LAWN_OFFSET_X + c * CW + CW // 2, LAWN_OFFSET_Y + r * CH + CH // 2)
    
    def handle_event(self, event):
        if self.state == GameState.MAIN_MENU:
            self.handle_main_menu_event(event)
        elif self.state == GameState.ADVENTURE_SELECT:
            self.handle_adventure_select_event(event)
        elif self.state == GameState.MINIGAMES_MENU:
            self.handle_minigames_event(event)
        elif self.state == GameState.SURVIVAL_MENU:
            self.handle_survival_event(event)
        elif self.state == GameState.PUZZLE_MENU:
            self.handle_puzzle_event(event)
        elif self.state == GameState.ALMANAC:
            self.handle_almanac_event(event)
        elif self.state == GameState.ALMANAC_PLANTS:
            self.handle_almanac_plants_event(event)
        elif self.state == GameState.ALMANAC_ZOMBIES:
            self.handle_almanac_zombies_event(event)
        elif self.state == GameState.OPTIONS:
            self.handle_options_event(event)
        elif self.state == GameState.CREDITS:
            self.handle_credits_event(event)
        elif self.state == GameState.HELP:
            self.handle_help_event(event)
        elif self.state == GameState.ZEN_GARDEN:
            self.handle_zen_garden_event(event)
        elif self.state == GameState.PLAYING:
            self.handle_gameplay_event(event)
        elif self.state == GameState.PAUSED:
            self.handle_paused_event(event)
        elif self.state == GameState.GAME_OVER:
            self.handle_game_over_event(event)
        elif self.state == GameState.LEVEL_COMPLETE:
            self.handle_level_complete_event(event)
    
    def handle_main_menu_event(self, event):
        buttons = self.main_menu_buttons
        if buttons[0].clicked(event):  # Adventure
            self.change_state(GameState.ADVENTURE_SELECT)
        elif buttons[1].clicked(event):  # Mini-Games
            self.change_state(GameState.MINIGAMES_MENU)
        elif buttons[2].clicked(event):  # Puzzle
            self.change_state(GameState.PUZZLE_MENU)
        elif buttons[3].clicked(event):  # Survival
            self.change_state(GameState.SURVIVAL_MENU)
        elif buttons[4].clicked(event):  # Zen Garden
            self.change_state(GameState.ZEN_GARDEN)
        elif buttons[5].clicked(event):  # Almanac
            self.change_state(GameState.ALMANAC)
        elif buttons[6].clicked(event):  # Options
            self.change_state(GameState.OPTIONS)
        elif buttons[7].clicked(event):  # Help
            self.change_state(GameState.HELP)
        elif buttons[8].clicked(event):  # Credits
            self.change_state(GameState.CREDITS)
        elif buttons[9].clicked(event):  # Quit
            pygame.quit()
            sys.exit()
    
    def handle_adventure_select_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check level clicks
            for i, level in enumerate(ADVENTURE_LEVELS):
                x = 100 + (i % 5) * 130
                y = 150 + (i // 5) * 100
                rect = pygame.Rect(x, y, 120, 80)
                if rect.collidepoint(event.pos) and i < self.player_progress["adventure_level"]:
                    self.selected_level = i
                    self.reset_game_state()
                    self.sun = level["sun_start"]
                    self.total_waves = level["waves"] * 3
                    self.change_state(GameState.PLAYING)
        
        # Scroll
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(-200, min(0, self.scroll_offset + event.y * 30))
    
    def handle_minigames_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(-400, min(0, self.scroll_offset + event.y * 30))
    
    def handle_survival_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(-200, min(0, self.scroll_offset + event.y * 30))
    
    def handle_puzzle_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
    
    def handle_almanac_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            plants_rect = pygame.Rect(W//2 - 200, 200, 180, 150)
            zombies_rect = pygame.Rect(W//2 + 20, 200, 180, 150)
            if plants_rect.collidepoint(event.pos):
                self.change_state(GameState.ALMANAC_PLANTS)
            elif zombies_rect.collidepoint(event.pos):
                self.change_state(GameState.ALMANAC_ZOMBIES)
    
    def handle_almanac_plants_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.ALMANAC)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(-200, min(0, self.scroll_offset + event.y * 30))
    
    def handle_almanac_zombies_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.ALMANAC)
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset = max(-200, min(0, self.scroll_offset + event.y * 30))
    
    def handle_options_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Volume sliders
            music_rect = pygame.Rect(300, 180, 200, 20)
            sfx_rect = pygame.Rect(300, 250, 200, 20)
            if music_rect.collidepoint(event.pos):
                self.options["music_volume"] = (event.pos[0] - 300) / 200
            elif sfx_rect.collidepoint(event.pos):
                self.options["sfx_volume"] = (event.pos[0] - 300) / 200
            
            # Difficulty toggle
            diff_rect = pygame.Rect(300, 320, 200, 40)
            if diff_rect.collidepoint(event.pos):
                diffs = ["Easy", "Normal", "Hard"]
                idx = diffs.index(self.options["difficulty"])
                self.options["difficulty"] = diffs[(idx + 1) % 3]
    
    def handle_credits_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
    
    def handle_help_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
    
    def handle_zen_garden_event(self, event):
        if self.back_button.clicked(event):
            self.change_state(GameState.MAIN_MENU)
    
    def handle_gameplay_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]:
                idx = event.key - pygame.K_1
                plant_types = list(PlantType)
                if idx < len(plant_types):
                    self.selected_plant = plant_types[idx]
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            
            # Check sun collection
            if event.button == 1:
                for sun in list(self.falling_suns):
                    sun_rect = pygame.Rect(sun["x"] - 20, sun["y"] - 20, 40, 40)
                    if sun_rect.collidepoint(mx, my) and not sun["collected"]:
                        self.sun += 25
                        self.falling_suns.remove(sun)
                        break
            
            # Plant placement
            if event.button == 1 and my >= LAWN_OFFSET_Y and self.selected_plant:
                c = (mx - LAWN_OFFSET_X) // CW
                r = (my - LAWN_OFFSET_Y) // CH
                if 0 <= r < ROWS and 0 <= c < COLS:
                    ptype = self.selected_plant
                    cost = ptype.value["cost"]
                    if (r, c) not in self.plants and self.sun >= cost and self.plant_recharges[ptype] <= 0:
                        self.plants[(r, c)] = {
                            "type": ptype,
                            "hp": ptype.value["hp"],
                            "cd": 0.0
                        }
                        self.sun -= cost
                        self.plant_recharges[ptype] = ptype.value["recharge"]
            
            # Remove plant
            if event.button == 3 and my >= LAWN_OFFSET_Y:
                c = (mx - LAWN_OFFSET_X) // CW
                r = (my - LAWN_OFFSET_Y) // CH
                if (r, c) in self.plants:
                    del self.plants[(r, c)]
            
            # Plant selection from seed tray
            if event.button == 1 and 50 <= my <= 100:
                for i, ptype in enumerate(PlantType):
                    seed_x = 80 + i * 70
                    if seed_x <= mx <= seed_x + 60:
                        if self.sun >= ptype.value["cost"] and self.plant_recharges[ptype] <= 0:
                            self.selected_plant = ptype
    
    def handle_paused_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = GameState.PLAYING
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Resume button
            resume_rect = pygame.Rect(W//2 - 100, 250, 200, 50)
            menu_rect = pygame.Rect(W//2 - 100, 320, 200, 50)
            if resume_rect.collidepoint(event.pos):
                self.state = GameState.PLAYING
            elif menu_rect.collidepoint(event.pos):
                self.change_state(GameState.MAIN_MENU)
    
    def handle_game_over_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            self.change_state(GameState.MAIN_MENU)
    
    def handle_level_complete_event(self, event):
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            # Unlock next level
            if self.selected_level + 1 < len(ADVENTURE_LEVELS):
                self.player_progress["adventure_level"] = max(
                    self.player_progress["adventure_level"], 
                    self.selected_level + 2
                )
            self.change_state(GameState.ADVENTURE_SELECT)
    
    def draw(self):
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.ADVENTURE_SELECT:
            self.draw_adventure_select()
        elif self.state == GameState.MINIGAMES_MENU:
            self.draw_minigames_menu()
        elif self.state == GameState.SURVIVAL_MENU:
            self.draw_survival_menu()
        elif self.state == GameState.PUZZLE_MENU:
            self.draw_puzzle_menu()
        elif self.state == GameState.ALMANAC:
            self.draw_almanac()
        elif self.state == GameState.ALMANAC_PLANTS:
            self.draw_almanac_plants()
        elif self.state == GameState.ALMANAC_ZOMBIES:
            self.draw_almanac_zombies()
        elif self.state == GameState.OPTIONS:
            self.draw_options()
        elif self.state == GameState.CREDITS:
            self.draw_credits()
        elif self.state == GameState.HELP:
            self.draw_help()
        elif self.state == GameState.ZEN_GARDEN:
            self.draw_zen_garden()
        elif self.state == GameState.PLAYING:
            self.draw_gameplay()
        elif self.state == GameState.PAUSED:
            self.draw_gameplay()
            self.draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self.draw_gameplay()
            self.draw_game_over()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_gameplay()
            self.draw_level_complete()
    
    def draw_menu_background(self):
        # Sky gradient
        for y in range(H):
            ratio = y / H
            r = int(135 * (1 - ratio) + 50 * ratio)
            g = int(206 * (1 - ratio) + 150 * ratio)
            b = int(235 * (1 - ratio) + 50 * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (W, y))
        
        # Grass
        pygame.draw.rect(screen, Colors.GRASS_LIGHT, (0, H - 100, W, 100))
        for x in range(0, W, 40):
            pygame.draw.ellipse(screen, Colors.GRASS_DARK, (x, H - 110, 50, 30))
        
        # Draw animated elements
        for sun in self.floating_suns:
            sun.draw(screen)
        for zombie in self.menu_zombies:
            zombie.draw(screen)
        
        # House silhouette
        pygame.draw.rect(screen, (60, 40, 30), (20, H - 200, 150, 150))
        pygame.draw.polygon(screen, (80, 50, 30), [(10, H - 200), (95, H - 280), (180, H - 200)])
        # Windows
        pygame.draw.rect(screen, (200, 180, 100), (50, H - 170, 30, 40))
        pygame.draw.rect(screen, (200, 180, 100), (110, H - 170, 30, 40))
    
    def draw_main_menu(self):
        self.draw_menu_background()
        
        # Title with shadow
        title = "CAT'S PVZ REPLANTED"
        subtitle = "Version 0.2"
        
        shadow = font_title.render(title, True, (30, 60, 0))
        screen.blit(shadow, (W//2 - shadow.get_width()//2 + 3, 63))
        title_surf = font_title.render(title, True, (100, 200, 50))
        screen.blit(title_surf, (W//2 - title_surf.get_width()//2, 60))
        
        sub_surf = font_large.render(subtitle, True, Colors.TEXT_YELLOW)
        screen.blit(sub_surf, (W//2 - sub_surf.get_width()//2, 120))
        
        # Draw buttons
        for btn in self.main_menu_buttons:
            btn.draw(screen)
        
        # Version
        ver = font_tiny.render("v1.0 — Team Flames / Samsoft", True, (200, 200, 200))
        screen.blit(ver, (10, H - 20))
    
    def draw_adventure_select(self):
        screen.fill((40, 80, 40))
        
        # Title
        title = font_large.render("Adventure Mode — Select Level", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        # World indicator
        worlds = ["Day", "Night", "Pool", "Fog", "Roof"]
        for i, world in enumerate(worlds):
            color = Colors.TEXT_YELLOW if i == 0 else (150, 150, 150)
            w_text = font_small.render(world, True, color)
            screen.blit(w_text, (100 + i * 130, 90))
        
        # Level grid
        for i, level in enumerate(ADVENTURE_LEVELS):
            x = 100 + (i % 5) * 130
            y = 150 + (i // 5) * 100 + self.scroll_offset
            
            unlocked = i < self.player_progress["adventure_level"]
            color = Colors.BUTTON_NORMAL if unlocked else Colors.BUTTON_DISABLED
            
            pygame.draw.rect(screen, color, (x, y, 120, 80), border_radius=8)
            pygame.draw.rect(screen, (0, 60, 0) if unlocked else (40, 40, 40), (x, y, 120, 80), 3, border_radius=8)
            
            # Level name
            name = font_small.render(level["name"], True, Colors.TEXT_WHITE if unlocked else (100, 100, 100))
            screen.blit(name, (x + 60 - name.get_width()//2, y + 30))
            
            if not unlocked:
                lock = font_medium.render("🔒", True, (150, 150, 150))
                screen.blit(lock, (x + 50, y + 50))
        
        self.back_button.draw(screen)
    
    def draw_minigames_menu(self):
        screen.fill((60, 40, 60))
        
        title = font_large.render("Mini-Games", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        for i, game in enumerate(MINIGAMES):
            x = 80 + (i % 4) * 170
            y = 100 + (i // 4) * 110 + self.scroll_offset
            
            color = Colors.BUTTON_NORMAL if game["unlocked"] else Colors.BUTTON_DISABLED
            pygame.draw.rect(screen, color, (x, y, 160, 90), border_radius=8)
            pygame.draw.rect(screen, (0, 60, 0) if game["unlocked"] else (40, 40, 40), (x, y, 160, 90), 3, border_radius=8)
            
            name = font_small.render(game["name"], True, Colors.TEXT_WHITE if game["unlocked"] else (100, 100, 100))
            screen.blit(name, (x + 80 - name.get_width()//2, y + 20))
            
            desc = font_tiny.render(game["desc"], True, (200, 200, 200) if game["unlocked"] else (80, 80, 80))
            screen.blit(desc, (x + 80 - desc.get_width()//2, y + 50))
            
            if not game["unlocked"]:
                lock = font_small.render("🔒", True, (150, 150, 150))
                screen.blit(lock, (x + 70, y + 65))
        
        self.back_button.draw(screen)
    
    def draw_survival_menu(self):
        screen.fill((40, 60, 40))
        
        title = font_large.render("Survival Mode", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        for i, mode in enumerate(SURVIVAL_MODES):
            x = 100 + (i % 3) * 200
            y = 100 + (i // 3) * 100 + self.scroll_offset
            
            color = Colors.BUTTON_NORMAL if mode["unlocked"] else Colors.BUTTON_DISABLED
            pygame.draw.rect(screen, color, (x, y, 180, 80), border_radius=8)
            
            name = font_small.render(mode["name"], True, Colors.TEXT_WHITE if mode["unlocked"] else (100, 100, 100))
            screen.blit(name, (x + 90 - name.get_width()//2, y + 20))
            
            desc = font_tiny.render(mode["desc"], True, (200, 200, 200) if mode["unlocked"] else (80, 80, 80))
            screen.blit(desc, (x + 90 - desc.get_width()//2, y + 50))
        
        self.back_button.draw(screen)
    
    def draw_puzzle_menu(self):
        screen.fill((50, 50, 70))
        
        title = font_large.render("Puzzle Mode", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        for i, mode in enumerate(PUZZLE_MODES):
            x = W//2 - 180 + (i % 2) * 200
            y = 150 + (i // 2) * 120
            
            color = Colors.BUTTON_NORMAL if mode["unlocked"] else Colors.BUTTON_DISABLED
            pygame.draw.rect(screen, color, (x, y, 180, 100), border_radius=8)
            
            name = font_medium.render(mode["name"], True, Colors.TEXT_WHITE if mode["unlocked"] else (100, 100, 100))
            screen.blit(name, (x + 90 - name.get_width()//2, y + 25))
            
            desc = font_small.render(mode["desc"], True, (200, 200, 200) if mode["unlocked"] else (80, 80, 80))
            screen.blit(desc, (x + 90 - desc.get_width()//2, y + 60))
        
        self.back_button.draw(screen)
    
    def draw_almanac(self):
        screen.fill((80, 60, 40))
        
        title = font_large.render("Suburban Almanac", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        subtitle = font_medium.render("Choose a section to browse", True, Colors.TEXT_YELLOW)
        screen.blit(subtitle, (W//2 - subtitle.get_width()//2, 100))
        
        # Plants section
        pygame.draw.rect(screen, Colors.GRASS_LIGHT, (W//2 - 200, 200, 180, 150), border_radius=12)
        pygame.draw.rect(screen, Colors.GRASS_DARK, (W//2 - 200, 200, 180, 150), 4, border_radius=12)
        plants_text = font_medium.render("Plants", True, Colors.TEXT_WHITE)
        screen.blit(plants_text, (W//2 - 200 + 90 - plants_text.get_width()//2, 260))
        
        # Zombies section
        pygame.draw.rect(screen, (100, 80, 60), (W//2 + 20, 200, 180, 150), border_radius=12)
        pygame.draw.rect(screen, (60, 40, 20), (W//2 + 20, 200, 180, 150), 4, border_radius=12)
        zombies_text = font_medium.render("Zombies", True, Colors.TEXT_WHITE)
        screen.blit(zombies_text, (W//2 + 20 + 90 - zombies_text.get_width()//2, 260))
        
        self.back_button.draw(screen)
    
    def draw_almanac_plants(self):
        screen.fill((60, 100, 40))
        
        title = font_large.render("Plant Almanac", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 20))
        
        for i, ptype in enumerate(PlantType):
            x = 50 + (i % 4) * 180
            y = 80 + (i // 4) * 130 + self.scroll_offset
            
            # Card
            pygame.draw.rect(screen, (80, 130, 60), (x, y, 170, 120), border_radius=8)
            pygame.draw.rect(screen, (40, 80, 30), (x, y, 170, 120), 3, border_radius=8)
            
            # Plant preview (colored box)
            pygame.draw.rect(screen, ptype.value["color"], (x + 10, y + 10, 50, 50))
            
            # Info
            name = font_small.render(ptype.value["name"], True, Colors.TEXT_WHITE)
            screen.blit(name, (x + 70, y + 15))
            
            cost = font_tiny.render(f"Cost: {ptype.value['cost']} sun", True, Colors.SUN_YELLOW)
            screen.blit(cost, (x + 70, y + 40))
            
            hp = font_tiny.render(f"HP: {ptype.value['hp']}", True, (200, 200, 200))
            screen.blit(hp, (x + 70, y + 60))
            
            if "damage" in ptype.value:
                dmg = font_tiny.render(f"Dmg: {ptype.value['damage']}", True, (255, 150, 150))
                screen.blit(dmg, (x + 70, y + 80))
        
        self.back_button.draw(screen)
    
    def draw_almanac_zombies(self):
        screen.fill((60, 50, 50))
        
        title = font_large.render("Zombie Almanac", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 20))
        
        for i, ztype in enumerate(ZombieType):
            x = 50 + (i % 3) * 240
            y = 80 + (i // 3) * 150 + self.scroll_offset
            
            # Card
            pygame.draw.rect(screen, (80, 70, 70), (x, y, 220, 130), border_radius=8)
            pygame.draw.rect(screen, (50, 40, 40), (x, y, 220, 130), 3, border_radius=8)
            
            # Zombie preview
            pygame.draw.rect(screen, ztype.value["color"], (x + 10, y + 15, 50, 70))
            pygame.draw.circle(screen, Colors.ZOMBIE_SKIN, (x + 35, y + 25), 20)
            
            # Info
            name = font_small.render(ztype.value["name"], True, Colors.TEXT_WHITE)
            screen.blit(name, (x + 70, y + 15))
            
            hp = font_tiny.render(f"HP: {ztype.value['hp']}", True, (255, 150, 150))
            screen.blit(hp, (x + 70, y + 45))
            
            speed = font_tiny.render(f"Speed: {ztype.value['speed']}", True, (200, 200, 200))
            screen.blit(speed, (x + 70, y + 65))
            
            dmg = font_tiny.render(f"Damage: {ztype.value['damage']}", True, (200, 150, 150))
            screen.blit(dmg, (x + 70, y + 85))
        
        self.back_button.draw(screen)
    
    def draw_options(self):
        screen.fill((50, 50, 60))
        
        title = font_large.render("Options", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        # Music volume
        music_label = font_medium.render("Music Volume:", True, Colors.TEXT_WHITE)
        screen.blit(music_label, (100, 150))
        pygame.draw.rect(screen, (80, 80, 80), (300, 150, 200, 20))
        pygame.draw.rect(screen, Colors.BUTTON_NORMAL, (300, 150, int(200 * self.options["music_volume"]), 20))
        pygame.draw.circle(screen, Colors.TEXT_WHITE, (300 + int(200 * self.options["music_volume"]), 160), 10)
        
        # SFX volume
        sfx_label = font_medium.render("SFX Volume:", True, Colors.TEXT_WHITE)
        screen.blit(sfx_label, (100, 220))
        pygame.draw.rect(screen, (80, 80, 80), (300, 220, 200, 20))
        pygame.draw.rect(screen, Colors.BUTTON_NORMAL, (300, 220, int(200 * self.options["sfx_volume"]), 20))
        pygame.draw.circle(screen, Colors.TEXT_WHITE, (300 + int(200 * self.options["sfx_volume"]), 230), 10)
        
        # Difficulty
        diff_label = font_medium.render("Difficulty:", True, Colors.TEXT_WHITE)
        screen.blit(diff_label, (100, 290))
        
        diff_colors = {"Easy": (100, 180, 100), "Normal": (180, 180, 100), "Hard": (180, 100, 100)}
        pygame.draw.rect(screen, diff_colors[self.options["difficulty"]], (300, 290, 200, 40), border_radius=8)
        diff_text = font_medium.render(self.options["difficulty"], True, Colors.TEXT_WHITE)
        screen.blit(diff_text, (400 - diff_text.get_width()//2, 297))
        
        click_hint = font_small.render("(Click to change)", True, (150, 150, 150))
        screen.blit(click_hint, (510, 297))
        
        self.back_button.draw(screen)
    
    def draw_credits(self):
        screen.fill((30, 30, 40))
        
        title = font_large.render("Credits", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        credits = [
            "PLANTS vs ZOMBIES — Replanted Engine",
            "",
            "Engine Development:",
            "Team Flames / Samsoft",
            "",
            "Original Game:",
            "PopCap Games",
            "",
            "Inspiration:",
            "PvZ Replanted Community",
            "",
            "Special Thanks:",
            "Pygame Community",
            "All PvZ Fans Worldwide",
            "",
            "Made with 💚 and Python",
        ]
        
        for i, line in enumerate(credits):
            color = Colors.TEXT_YELLOW if i == 0 else Colors.TEXT_WHITE if ":" in line else (180, 180, 180)
            text = font_medium.render(line, True, color) if i == 0 else font_small.render(line, True, color)
            screen.blit(text, (W//2 - text.get_width()//2, 100 + i * 28))
        
        self.back_button.draw(screen)
    
    def draw_help(self):
        screen.fill((40, 50, 40))
        
        title = font_large.render("How to Play", True, Colors.TEXT_WHITE)
        screen.blit(title, (W//2 - title.get_width()//2, 20))
        
        help_text = [
            "🌻 OBJECTIVE: Protect your house from zombies!",
            "",
            "🌱 PLANTING:",
            "   • Click seed packets to select plants",
            "   • Left-click on lawn to plant (costs sun)",
            "   • Right-click to remove plants",
            "",
            "☀️ SUN:",
            "   • Collect falling sun by clicking",
            "   • Sunflowers produce extra sun",
            "",
            "🧟 ZOMBIES:",
            "   • Different zombies have different abilities",
            "   • Don't let them reach your house!",
            "",
            "⌨️ CONTROLS:",
            "   • 1-8: Quick select plants",
            "   • ESC: Pause game",
        ]
        
        for i, line in enumerate(help_text):
            color = Colors.TEXT_YELLOW if line.startswith(("🌻", "🌱", "☀️", "🧟", "⌨️")) else Colors.TEXT_WHITE
            text = font_small.render(line, True, color)
            screen.blit(text, (80, 70 + i * 28))
        
        self.back_button.draw(screen)
    
    def draw_zen_garden(self):
        # Sky
        for y in range(H):
            ratio = y / H
            r = int(200 * (1 - ratio) + 100 * ratio)
            g = int(230 * (1 - ratio) + 180 * ratio)
            b = int(255 * (1 - ratio) + 200 * ratio)
            pygame.draw.line(screen, (r, g, b), (0, y), (W, y))
        
        # Grass
        pygame.draw.rect(screen, Colors.GRASS_LIGHT, (0, H - 150, W, 150))
        
        title = font_large.render("Zen Garden", True, (50, 100, 50))
        screen.blit(title, (W//2 - title.get_width()//2, 30))
        
        # Empty garden message
        msg = font_medium.render("Your garden is peaceful and empty...", True, (80, 120, 80))
        screen.blit(msg, (W//2 - msg.get_width()//2, H//2))
        
        hint = font_small.render("Complete Adventure levels to unlock plants!", True, (100, 140, 100))
        screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 40))
        
        self.back_button.draw(screen)
    
    def draw_gameplay(self):
        level = ADVENTURE_LEVELS[self.selected_level] if self.selected_level < len(ADVENTURE_LEVELS) else ADVENTURE_LEVELS[0]
        world = level.get("world", "day")
        
        # Sky
        if world == "night" or world == "fog":
            screen.fill(Colors.SKY_NIGHT)
        else:
            screen.fill(Colors.SKY_DAY)
        
        # UI Bar
        pygame.draw.rect(screen, (50, 35, 25), (0, 0, W, UI_HEIGHT))
        pygame.draw.rect(screen, (80, 55, 35), (0, UI_HEIGHT - 5, W, 5))
        
        # Sun counter
        pygame.draw.circle(screen, Colors.SUN_YELLOW, (35, 30), 20)
        sun_text = font_medium.render(str(self.sun), True, Colors.TEXT_WHITE)
        screen.blit(sun_text, (60, 18))
        
        # Seed tray
        for i, ptype in enumerate(PlantType):
            x = 120 + i * 70
            y = 5
            
            # Recharge overlay
            recharge_ratio = self.plant_recharges[ptype] / ptype.value["recharge"] if ptype.value["recharge"] > 0 else 0
            
            # Seed packet
            can_afford = self.sun >= ptype.value["cost"]
            is_ready = recharge_ratio <= 0
            
            if can_afford and is_ready:
                color = ptype.value["color"]
            else:
                color = tuple(max(0, c - 80) for c in ptype.value["color"])
            
            pygame.draw.rect(screen, color, (x, y, 60, 50), border_radius=5)
            pygame.draw.rect(screen, (0, 0, 0), (x, y, 60, 50), 2, border_radius=5)
            
            # Recharge bar
            if recharge_ratio > 0:
                pygame.draw.rect(screen, (0, 0, 0, 150), (x, y, 60, int(50 * recharge_ratio)))
            
            # Cost
            cost_text = font_tiny.render(str(ptype.value["cost"]), True, Colors.SUN_YELLOW)
            screen.blit(cost_text, (x + 30 - cost_text.get_width()//2, y + 35))
            
            # Selection indicator
            if self.selected_plant == ptype:
                pygame.draw.rect(screen, Colors.TEXT_YELLOW, (x - 2, y - 2, 64, 54), 3, border_radius=5)
        
        # Lawn
        for r in range(ROWS):
            for c in range(COLS):
                x = LAWN_OFFSET_X + c * CW
                y = LAWN_OFFSET_Y + r * CH
                
                # Checkerboard grass
                if (r + c) % 2 == 0:
                    color = Colors.GRASS_LIGHT
                else:
                    color = Colors.GRASS_DARK
                
                pygame.draw.rect(screen, color, (x, y, CW, CH))
                pygame.draw.rect(screen, (30, 80, 30), (x, y, CW, CH), 1)
        
        # Plants
        for (r, c), plant in self.plants.items():
            x, y = self.get_cell_center(r, c)
            ptype = plant["type"]
            
            # Draw plant based on type
            pygame.draw.rect(screen, ptype.value["color"], (x - 20, y - 25, 40, 50), border_radius=8)
            
            # Health bar
            hp_ratio = plant["hp"] / ptype.value["hp"]
            pygame.draw.rect(screen, (50, 50, 50), (x - 20, y + 30, 40, 5))
            pygame.draw.rect(screen, (50, 200, 50), (x - 20, y + 30, int(40 * hp_ratio), 5))
        
        # Peas
        for pea in self.peas:
            color = Colors.PEA if pea["type"] == "normal" else (150, 200, 255)
            pygame.draw.circle(screen, color, (int(pea["x"]), int(pea["y"])), 6)
        
        # Zombies
        for z in self.zombies:
            x = int(z["x"])
            y = LAWN_OFFSET_Y + z["r"] * CH + CH // 2
            
            ztype = z["type"]
            color = ztype.value["color"]
            
            # Body
            pygame.draw.rect(screen, Colors.ZOMBIE_CLOTHES, (x - 12, y - 5, 24, 40))
            # Head
            pygame.draw.circle(screen, color, (x, y - 15), 18)
            # Eyes
            pygame.draw.circle(screen, (255, 50, 50), (x - 6, y - 18), 4)
            pygame.draw.circle(screen, (255, 50, 50), (x + 6, y - 18), 4)
            
            # Health bar
            hp_ratio = z["hp"] / z["max_hp"]
            pygame.draw.rect(screen, (50, 50, 50), (x - 15, y - 40, 30, 4))
            pygame.draw.rect(screen, (200, 50, 50), (x - 15, y - 40, int(30 * hp_ratio), 4))
            
            # Slow indicator
            if z.get("slowed", 0) > 0:
                pygame.draw.circle(screen, (150, 200, 255), (x, y - 35), 5)
        
        # Falling suns
        for sun in self.falling_suns:
            pygame.draw.circle(screen, Colors.SUN_YELLOW, (int(sun["x"]), int(sun["y"])), 18)
            # Rays
            for i in range(6):
                angle = i * math.pi / 3
                dx = math.cos(angle) * 25
                dy = math.sin(angle) * 25
                pygame.draw.line(screen, Colors.SUN_YELLOW, 
                               (int(sun["x"]), int(sun["y"])),
                               (int(sun["x"] + dx), int(sun["y"] + dy)), 2)
        
        # Wave indicator
        wave_text = font_small.render(f"Wave: {self.wave_num}/{self.total_waves}", True, Colors.TEXT_WHITE)
        screen.blit(wave_text, (W - 120, 10))
        
        # Level name
        level_text = font_small.render(level["name"], True, Colors.TEXT_YELLOW)
        screen.blit(level_text, (W - 120, 35))
    
    def draw_pause_overlay(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = font_title.render("PAUSED", True, Colors.TEXT_WHITE)
        screen.blit(pause_text, (W//2 - pause_text.get_width()//2, 150))
        
        # Buttons
        pygame.draw.rect(screen, Colors.BUTTON_NORMAL, (W//2 - 100, 250, 200, 50), border_radius=10)
        resume = font_medium.render("Resume", True, Colors.TEXT_WHITE)
        screen.blit(resume, (W//2 - resume.get_width()//2, 262))
        
        pygame.draw.rect(screen, Colors.BUTTON_NORMAL, (W//2 - 100, 320, 200, 50), border_radius=10)
        menu = font_medium.render("Main Menu", True, Colors.TEXT_WHITE)
        screen.blit(menu, (W//2 - menu.get_width()//2, 332))
    
    def draw_game_over(self):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        go_text = font_title.render("GAME OVER", True, (255, 50, 50))
        screen.blit(go_text, (W//2 - go_text.get_width()//2, H//2 - 60))
        
        reason = font_medium.render(self.game_over_reason or "The zombies won!", True, Colors.TEXT_WHITE)
        screen.blit(reason, (W//2 - reason.get_width()//2, H//2 + 10))
        
        hint = font_small.render("Click or press any key to continue", True, (200, 200, 200))
        screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 60))
    
    def draw_level_complete(self):
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 100, 0, 180))
        screen.blit(overlay, (0, 0))
        
        win_text = font_title.render("LEVEL COMPLETE!", True, Colors.TEXT_YELLOW)
        screen.blit(win_text, (W//2 - win_text.get_width()//2, H//2 - 60))
        
        # Stars based on performance
        stars = "⭐⭐⭐"
        stars_text = font_large.render(stars, True, Colors.SUN_YELLOW)
        screen.blit(stars_text, (W//2 - stars_text.get_width()//2, H//2 + 10))
        
        hint = font_small.render("Click or press any key to continue", True, (200, 200, 200))
        screen.blit(hint, (W//2 - hint.get_width()//2, H//2 + 70))

# --- Main ---
def main():
    game = GameManager()
    
    while True:
        dt = clock.tick(60) / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        
        game.update(dt)
        game.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()
