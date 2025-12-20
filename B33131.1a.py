import pygame
import math

# Initialize Pygame
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("SAMSOFT ! B3313 ! 1.0 - Pygame Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 24)

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
pink = (255, 105, 180)  # Melee wireframe color
yellow = (255, 255, 0)
blue = (0, 0, 255)

# 3D Object class
class Object3D:
    def __init__(self, vertices, edges, color=white):
        self.vertices = vertices
        self.edges = edges
        self.color = color
        self.rotation = [0, 0, 0]
        self.position = [0, 0, 200]

    def rotate(self, axis, angle):
        self.rotation[axis] += angle

    def get_projected(self):
        projected = []
        for v in self.vertices:
            rx = self.rotate_x(v, self.rotation[0])
            rxy = self.rotate_y(rx, self.rotation[1])
            rxyz = self.rotate_z(rxy, self.rotation[2])
            tx, ty, tz = rxyz[0] + self.position[0], rxyz[1] + self.position[1], rxyz[2] + self.position[2]
            if tz > 0:
                f = 200 / tz
                px = tx * f + width / 2
                py = ty * f + height / 2
                projected.append([px, py])
            else:
                projected.append(None)
        return projected

    def draw(self, surface):
        projected = self.get_projected()
        for edge in self.edges:
            p1 = projected[edge[0]]
            p2 = projected[edge[1]]
            if p1 and p2:
                pygame.draw.line(surface, self.color, p1, p2, 2)

    @staticmethod
    def rotate_x(v, angle):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return [v[0], v[1] * cos_a - v[2] * sin_a, v[1] * sin_a + v[2] * cos_a]

    @staticmethod
    def rotate_y(v, angle):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return [v[0] * cos_a + v[2] * sin_a, v[1], -v[0] * sin_a + v[2] * cos_a]

    @staticmethod
    def rotate_z(v, angle):
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return [v[0] * cos_a - v[1] * sin_a, v[0] * sin_a + v[1] * cos_a, v[2]]

# Simple Peach's Castle model
castle_vertices = [
    # Base
    [-100, -50, -100], [100, -50, -100], [100, -50, 100], [-100, -50, 100],
    [-100, 50, -100], [100, 50, -100], [100, 50, 100], [-100, 50, 100],
    # Tower
    [0, 50, 0], [0, 100, 0], [-20, 50, -20], [20, 50, -20], [20, 50, 20], [-20, 50, 20],
    [-20, 100, -20], [20, 100, -20], [20, 100, 20], [-20, 100, 20],
    # Roof pyramid
    [0, 150, 0]
]
castle_edges = [
    # Base
    [0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4],
    [0,4], [1,5], [2,6], [3,7],
    # Tower
    [10,11], [11,12], [12,13], [13,10],
    [14,15], [15,16], [16,17], [17,14],
    [10,14], [11,15], [12,16], [13,17],
    # Connect to base (approximate)
    [8,4], [8,5], [8,6], [8,7],
    # Roof
    [14,18], [15,18], [16,18], [17,18]
]
castle = Object3D(castle_vertices, castle_edges)

# Space World debug level (simple beta-inspired: ground plane + low-poly hills)
spaceworld_vertices = [
    # Ground plane
    [-200, -50, -200], [200, -50, -200], [200, -50, 200], [-200, -50, 200],
    # Hill 1 (pyramid)
    [-100, -50, -100], [-50, -50, -100], [-50, -50, -50], [-100, -50, -50],
    [-75, 20, -75],
    # Hill 2
    [50, -50, 50], [100, -50, 50], [100, -50, 100], [50, -50, 100],
    [75, 30, 75]
]
spaceworld_edges = [
    # Ground
    [0,1], [1,2], [2,3], [3,0],
    # Hill 1
    [4,5], [5,6], [6,7], [7,4], [4,8], [5,8], [6,8], [7,8],
    # Hill 2
    [9,10], [10,11], [11,12], [12,9], [9,13], [10,13], [11,13], [12,13]
]
spaceworld = Object3D(spaceworld_vertices, spaceworld_edges, white)

# Smash Melee wireframe fighter (simple humanoid)
wireframe_vertices = [
    # Head
    [0, 40, 0], [10, 50, 0], [-10, 50, 0], [0, 60, 0],
    # Torso
    [0, 20, 0], [15, 20, 0], [-15, 20, 0], [0, 0, 0],
    # Arms
    [15, 20, 0], [30, 10, 0], [-15, 20, 0], [-30, 10, 0],
    # Legs
    [10, 0, 0], [10, -30, 0], [-10, 0, 0], [-10, -30, 0]
]
wireframe_edges = [
    # Head
    [0,1], [1,3], [3,2], [2,0],
    # Torso
    [4,5], [5,7], [7,6], [6,4],
    # Connect head to torso
    [0,4],
    # Arms
    [5,9], [6,11],
    # Legs
    [7,13], [7,15]
]
wireframe_fighter = Object3D(wireframe_vertices, wireframe_edges, pink)
wireframe_fighter.position = [50, 0, 250]  # Place in scene

# B3313 Peach's Castle Courtyard (simple model: ground, walls, fountain, hedges)
courtyard_vertices = [
    # Ground plane
    [-200, -50, -200], [200, -50, -200], [200, -50, 200], [-200, -50, 200],
    # Walls (back courtyard walls)
    [-200, -50, -200], [-200, 20, -200], [200, 20, -200], [200, -50, -200],
    [-200, -50, 200], [-200, 20, 200], [200, 20, 200], [200, -50, 200],
    [-200, -50, -200], [-200, 20, -200], [-200, 20, 200], [-200, -50, 200],
    [200, -50, -200], [200, 20, -200], [200, 20, 200], [200, -50, 200],
    # Fountain (simple octagon base and top)
    [0, -50, 0], [20, -50, 0], [14, -50, 14], [0, -50, 20], [-14, -50, 14], [-20, -50, 0], [-14, -50, -14], [0, -50, -20], [14, -50, -14],
    [0, -30, 0], [15, -30, 0], [10, -30, 10], [0, -30, 15], [-10, -30, 10], [-15, -30, 0], [-10, -30, -10], [0, -30, -15], [10, -30, -10],
    # Hedges (simple boxes for maze)
    [-100, -50, -100], [-50, -50, -100], [-50, 0, -100], [-100, 0, -100],
    [-100, -50, -50], [-50, -50, -50], [-50, 0, -50], [-100, 0, -50],
    [50, -50, 50], [100, -50, 50], [100, 0, 50], [50, 0, 50],
    [50, -50, 100], [100, -50, 100], [100, 0, 100], [50, 0, 100]
]
courtyard_edges = [
    # Ground
    [0,1], [1,2], [2,3], [3,0],
    # Walls
    [4,5], [5,6], [6,7], [7,4],
    [8,9], [9,10], [10,11], [11,8],
    [12,13], [13,14], [14,15], [15,12],
    [16,17], [17,18], [18,19], [19,16],
    # Fountain base
    [20,21], [21,22], [22,23], [23,24], [24,25], [25,26], [26,27], [27,28], [28,20],
    # Fountain top
    [29,30], [30,31], [31,32], [32,33], [33,34], [34,35], [35,36], [36,37], [37,29],
    # Connect base to top
    [20,29], [21,30], [22,31], [23,32], [24,33], [25,34], [26,35], [27,36], [28,37],
    # Hedges
    [38,39], [39,40], [40,41], [41,38], [38,42], [39,43], [40,44], [41,45], [42,43], [43,44], [44,45], [45,42],
    [46,47], [47,48], [48,49], [49,46], [46,50], [47,51], [48,52], [49,53], [50,51], [51,52], [52,53], [53,50]
]
courtyard = Object3D(courtyard_vertices, courtyard_edges, white)

# Player physics (N64 emulation approx: gravity -0.2/frame, jump 5)
player_pos = [0, 0, 0]
player_vel = [0, 0, 0]
gravity = 0.2
jump_vel = 5
ground_y = -50

# Game states
STATE_INTRO = -1
STATE_MENU = 0
STATE_OVERWORLD = 1
STATE_TECHDEMO = 2
STATE_SPACEWORLD = 3
STATE_COURTYARD = 4
state = STATE_INTRO
start_time = pygame.time.get_ticks()

# HUD variables (demo values)
lives = 3
coins = 0
stars = 0
health = 8  # Out of 8

def draw_beta_hud(screen, font, small_font):
    # Simple beta-inspired HUD without images
    # Lives (Mario head icon approximated with text)
    pygame.draw.circle(screen, red, (40, 40), 20, 2)  # Simple head
    lives_text = small_font.render(f"x {lives}", True, white)
    screen.blit(lives_text, (70, 30))

    # Coins
    pygame.draw.circle(screen, yellow, (40, 80), 10, 2)  # Coin icon
    coins_text = small_font.render(f"x {coins}", True, white)
    screen.blit(coins_text, (70, 70))

    # Stars
    # Simple star shape
    star_points = [(40, 120), (50, 100), (60, 120), (50, 140)]
    pygame.draw.lines(screen, yellow, True, star_points, 2)
    stars_text = small_font.render(f"x {stars}", True, white)
    screen.blit(stars_text, (70, 110))

    # Health (circle meter like some betas)
    pygame.draw.circle(screen, blue, (width - 50, 50), 30, 0)  # Full circle
    # Empty part
    angle = (8 - health) / 8 * 360
    pygame.draw.arc(screen, black, (width - 80, 20, 60, 60), 0, math.radians(angle), 30)
    health_text = small_font.render("POWER", True, white)
    screen.blit(health_text, (width - 80, 80))

# Main loop
running = True
while running:
    screen.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and state not in [STATE_INTRO, STATE_MENU]:
                state = STATE_MENU
        if event.type == pygame.MOUSEBUTTONDOWN and state == STATE_MENU:
            mx, my = pygame.mouse.get_pos()
            if 200 < mx < 600 and 150 < my < 200:
                state = STATE_OVERWORLD
            if 200 < mx < 600 and 250 < my < 300:
                state = STATE_TECHDEMO
            if 200 < mx < 600 and 350 < my < 400:
                state = STATE_SPACEWORLD
            if 200 < mx < 600 and 450 < my < 500:
                state = STATE_COURTYARD

    if state == STATE_INTRO:
        text = font.render("SAMSOFT ! B3313 ! 1.0", True, red)
        screen.blit(text, (150, 250))
        if pygame.time.get_ticks() - start_time > 3000:
            state = STATE_MENU

    elif state == STATE_MENU:
        title = font.render("B3313 Pygame Edition", True, red)
        screen.blit(title, (150, 50))
        pygame.draw.rect(screen, white, (200, 150, 400, 50), 2)
        overworld_text = font.render("Overworld", True, white)
        screen.blit(overworld_text, (300, 160))
        pygame.draw.rect(screen, white, (200, 250, 400, 50), 2)
        demo_text = font.render("Tech Demo", True, white)
        screen.blit(demo_text, (300, 260))
        pygame.draw.rect(screen, white, (200, 350, 400, 50), 2)
        space_text = font.render("Debug Space World", True, white)
        screen.blit(space_text, (250, 360))
        pygame.draw.rect(screen, white, (200, 450, 400, 50), 2)
        courtyard_text = font.render("Peach's Courtyard", True, white)
        screen.blit(courtyard_text, (250, 460))

    else:
        # Physics update for player
        player_vel[1] -= gravity
        player_pos[0] += player_vel[0]
        player_pos[1] += player_vel[1]
        player_pos[2] += player_vel[2]
        if player_pos[1] <= ground_y:
            player_pos[1] = ground_y
            player_vel[1] = 0

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and player_pos[1] == ground_y:
            player_vel[1] = jump_vel
        if keys[pygame.K_w]:
            player_pos[2] -= 2  # Forward in z negative? Wait, code has + for w, but position z increases away
        if keys[pygame.K_s]:
            player_pos[2] += 2
        if keys[pygame.K_a]:
            player_pos[0] -= 2
        if keys[pygame.K_d]:
            player_pos[0] += 2

        # Apply player position to objects (simulate camera movement)
        if state == STATE_OVERWORLD:
            castle.position = [-player_pos[0], -player_pos[1] + 50, 200 - player_pos[2]]  # Offset y for ground
            castle.draw(screen)
            text = font.render("Peach's Castle Overworld", True, white)
            screen.blit(text, (200, 50))
        elif state == STATE_TECHDEMO:
            castle.rotate(1, 0.02)
            castle.position = [-player_pos[0], -player_pos[1] + 50, 200 - player_pos[2]]
            castle.draw(screen)
            wireframe_fighter.position = [50 - player_pos[0], -player_pos[1] + 50, 250 - player_pos[2]]
            wireframe_fighter.draw(screen)  # Add Melee wireframe
            text = font.render("B3313 Tech Demo with Melee Wireframe", True, red)
            screen.blit(text, (150, 50))
        elif state == STATE_SPACEWORLD:
            spaceworld.position = [-player_pos[0], -player_pos[1] + 50, 200 - player_pos[2]]
            spaceworld.draw(screen)
            text = font.render("Debug Space World Beta", True, white)
            screen.blit(text, (200, 50))
            # Placeholder minimap (beta feature)
            pygame.draw.rect(screen, white, (width - 100, 0, 100, 100), 1)
            minimap_text = font.render("Minimap", True, white, black)
            screen.blit(minimap_text, (width - 90, 40))
        elif state == STATE_COURTYARD:
            courtyard.position = [-player_pos[0], -player_pos[1] + 50, 200 - player_pos[2]]
            courtyard.draw(screen)
            text = font.render("B3313 Peach's Castle Courtyard", True, white)
            screen.blit(text, (150, 50))

        # Draw beta HUD in game states
        draw_beta_hud(screen, font, small_font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
