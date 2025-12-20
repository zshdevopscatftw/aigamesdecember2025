import pygame
import math

# Initialize Pygame
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("B3313 Pygame Tech Demo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# 3D Object class
class Object3D:
    def __init__(self, vertices, edges):
        self.vertices = vertices  # list of [x, y, z]
        self.edges = edges  # list of [index1, index2]
        self.rotation = [0, 0, 0]  # x, y, z rotation angles
        self.position = [0, 0, 200]  # x, y, z position

    def rotate(self, axis, angle):
        self.rotation[axis] += angle

    def get_projected(self):
        projected = []
        for v in self.vertices:
            # Rotate around x, y, z
            rx = self.rotate_x(v, self.rotation[0])
            rxy = self.rotate_y(rx, self.rotation[1])
            rxyz = self.rotate_z(rxy, self.rotation[2])
            # Translate
            tx, ty, tz = rxyz[0] + self.position[0], rxyz[1] + self.position[1], rxyz[2] + self.position[2]
            # Perspective projection (simple)
            if tz > 0:
                f = 200 / tz  # Focal length
                px = tx * f + width / 2
                py = ty * f + height / 2
                projected.append([px, py])
            else:
                projected.append(None)  # Behind camera
        return projected

    def draw(self, surface, color=white):
        projected = self.get_projected()
        for edge in self.edges:
            p1 = projected[edge[0]]
            p2 = projected[edge[1]]
            if p1 and p2:
                pygame.draw.line(surface, color, p1, p2, 2)

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

# Simple Peach's Castle model (wireframe, manual vertices for main building and towers)
castle_vertices = [
    # Main building base
    [-100, -50, -100], [100, -50, -100], [100, -50, 100], [-100, -50, 100],
    [-100, 50, -100], [100, 50, -100], [100, 50, 100], [-100, 50, 100],
    # Roof pyramid (simplified)
    [-80, 70, -80], [80, 70, -80], [80, 70, 80], [-80, 70, 80], [0, 100, 0],
    # Tower 1 (front left)
    [-120, -50, -120], [-80, -50, -120], [-80, -50, -80], [-120, -50, -80],
    [-120, 0, -120], [-80, 0, -120], [-80, 0, -80], [-120, 0, -80],
    # Tower 2 (front right), simplified similarly
    [80, -50, -120], [120, -50, -120], [120, -50, -80], [80, -50, -80],
    [80, 0, -120], [120, 0, -120], [120, 0, -80], [80, 0, -80],
    # Add more towers if needed...
]

castle_edges = [
    # Main building
    [0,1], [1,2], [2,3], [3,0], [4,5], [5,6], [6,7], [7,4],
    [0,4], [1,5], [2,6], [3,7],
    # Roof
    [4,8], [5,9], [6,10], [7,11], [8,9], [9,10], [10,11], [11,8],
    [8,12], [9,12], [10,12], [11,12],
    # Tower 1
    [13,14], [14,15], [15,16], [16,13], [17,18], [18,19], [19,20], [20,17],
    [13,17], [14,18], [15,19], [16,20],
    # Connect tower to main
    [13,0], [16,3], [14,1], # Approximate
    # Tower 2 similarly...
    [21,22], [22,23], [23,24], [24,21], [25,26], [26,27], [27,28], [28,25],
    [21,25], [22,26], [23,27], [24,28],
]

castle = Object3D(castle_vertices, castle_edges)

# Game states
STATE_MENU = 0
STATE_OVERWORLD = 1
STATE_TECHDEMO = 2
state = STATE_MENU

# Main loop
running = True
while running:
    screen.fill(black)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and state == STATE_MENU:
            mx, my = pygame.mouse.get_pos()
            if 200 < mx < 600 and 200 < my < 250:
                state = STATE_OVERWORLD
            if 200 < mx < 600 and 300 < my < 350:
                state = STATE_TECHDEMO

    if state == STATE_MENU:
        title = font.render("B3313 Pygame Edition", True, red)
        screen.blit(title, (150, 100))
        pygame.draw.rect(screen, white, (200, 200, 400, 50), 2)
        play_text = font.render("Play (Overworld)", True, white)
        screen.blit(play_text, (250, 210))
        pygame.draw.rect(screen, white, (200, 300, 400, 50), 2)
        demo_text = font.render("Tech Demo", True, white)
        screen.blit(demo_text, (300, 310))

    elif state == STATE_OVERWORLD:
        # Static overworld view of castle
        castle.draw(screen)
        overworld_text = font.render("Peach's Castle Overworld", True, white)
        screen.blit(overworld_text, (200, 50))

    elif state == STATE_TECHDEMO:
        # Rotating tech demo
        castle.rotate(1, 0.02)  # Rotate around y-axis
        castle.draw(screen, red)  # Creepy red for B3313 vibe
        demo_text = font.render("B3313 Tech Demo", True, red)
        screen.blit(demo_text, (250, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
