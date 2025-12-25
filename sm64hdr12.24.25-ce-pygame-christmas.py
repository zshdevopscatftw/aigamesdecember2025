"""
Super Mario 64 3D Clone - College English Version
A 3D platformer using pygame-ce with OpenGL rendering
"""

import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
from collections import defaultdict

class Vector3:
    """3D vector class for position and movement"""
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length > 0:
            return Vector3(self.x/length, self.y/length, self.z/length)
        return Vector3(0, 0, 0)

class Mario64Game:
    def __init__(self):
        pygame.init()
        self.display_size = (1280, 720)
        pygame.display.set_mode(self.display_size, DOUBLEBUF|OPENGL)
        pygame.display.set_caption("Super Mario 64 Pygame-CE Clone")
        
        # Initialize OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        
        # Camera setup
        self.camera_distance = 10
        self.camera_angle_x = 45
        self.camera_angle_y = -30
        
        # Player properties
        self.player_pos = Vector3(0, 5, 0)
        self.player_velocity = Vector3(0, 0, 0)
        self.player_rotation = 0
        self.grounded = False
        self.jump_power = 15
        self.gravity = 0.8
        
        # Game state
        self.stars_collected = 0
        self.current_level = "Bob-omb Battlefield"
        self.in_castle = True
        self.levels_unlocked = 1
        
        # Controls
        self.keys = defaultdict(bool)
        
        # Level data structures
        self.platforms = []
        self.coins = []
        self.enemies = []
        self.stars = []
        
        # Initialize test level
        self.load_test_level()
    
    def load_test_level(self):
        """Load a simple test level with platforms and collectibles"""
        # Ground platform
        self.platforms.append({
            'pos': Vector3(0, 0, 0),
            'size': Vector3(20, 1, 20),
            'color': (0.2, 0.6, 0.2, 1)  # Green
        })
        
        # Raised platform
        self.platforms.append({
            'pos': Vector3(5, 3, 5),
            'size': Vector3(4, 1, 4),
            'color': (0.8, 0.3, 0.1, 1)  # Brown
        })
        
        # Coins
        for i in range(5):
            angle = (i / 5) * 2 * math.pi
            self.coins.append({
                'pos': Vector3(math.cos(angle) * 8, 2, math.sin(angle) * 8),
                'collected': False
            })
        
        # Stars
        self.stars.append({
            'pos': Vector3(5, 5, 5),
            'collected': False,
            'rotation': 0
        })
    
    def draw_cube(self, pos, size, color):
        """Draw a colored cube at position"""
        glPushMatrix()
        glTranslatef(pos.x, pos.y, pos.z)
        glColor4f(*color)
        
        s = size
        vertices = [
            [s.x/2, s.y/2, -s.z/2], [-s.x/2, s.y/2, -s.z/2], [-s.x/2, -s.y/2, -s.z/2], [s.x/2, -s.y/2, -s.z/2],
            [s.x/2, s.y/2, s.z/2], [-s.x/2, s.y/2, s.z/2], [-s.x/2, -s.y/2, s.z/2], [s.x/2, -s.y/2, s.z/2]
        ]
        
        edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]
        
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()
        
        glPopMatrix()
    
    def draw_sphere(self, pos, radius, color):
        """Draw a sphere for coins and stars"""
        glPushMatrix()
        glTranslatef(pos.x, pos.y, pos.z)
        glColor4f(*color)
        
        # Simple sphere approximation
        slices = 10
        stacks = 10
        
        for i in range(stacks):
            lat0 = math.pi * (-0.5 + float(i) / stacks)
            z0 = radius * math.sin(lat0)
            zr0 = radius * math.cos(lat0)
            
            lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
            z1 = radius * math.sin(lat1)
            zr1 = radius * math.cos(lat1)
            
            glBegin(GL_QUAD_STRIP)
            for j in range(slices + 1):
                lng = 2 * math.pi * float(j) / slices
                x = math.cos(lng)
                y = math.sin(lng)
                
                glVertex3f(x * zr0, y * zr0, z0)
                glVertex3f(x * zr1, y * zr1, z1)
            glEnd()
        
        glPopMatrix()
    
    def draw_player(self):
        """Draw Mario character"""
        glPushMatrix()
        glTranslatef(self.player_pos.x, self.player_pos.y, self.player_pos.z)
        glRotatef(self.player_rotation, 0, 1, 0)
        
        # Body (red)
        glColor4f(1, 0, 0, 1)
        glPushMatrix()
        glScalef(1, 1.5, 1)
        glutSolidCube(1)
        glPopMatrix()
        
        # Head (skin tone)
        glColor4f(1, 0.8, 0.6, 1)
        glPushMatrix()
        glTranslatef(0, 1.2, 0)
        glutSolidSphere(0.5, 10, 10)
        glPopMatrix()
        
        # Hat (red with M)
        glColor4f(1, 0, 0, 1)
        glPushMatrix()
        glTranslatef(0, 1.7, 0)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(0.6, 0.4, 10, 2)
        glPopMatrix()
        
        glPopMatrix()
    
    def update_camera(self):
        """Update camera position based on player"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.display_size[0]/self.display_size[1]), 0.1, 1000.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Third-person camera
        cam_x = self.player_pos.x - self.camera_distance * math.sin(math.radians(self.camera_angle_y))
        cam_y = self.player_pos.y + self.camera_distance * math.sin(math.radians(self.camera_angle_x))
        cam_z = self.player_pos.z - self.camera_distance * math.cos(math.radians(self.camera_angle_y))
        
        gluLookAt(
            cam_x, cam_y, cam_z,  # Camera position
            self.player_pos.x, self.player_pos.y, self.player_pos.z,  # Look at point
            0, 1, 0  # Up vector
        )
    
    def handle_input(self):
        """Process keyboard input for movement"""
        speed = 0.3
        rotation_speed = 3
        
        # Camera rotation
        if self.keys[K_LEFT]:
            self.camera_angle_y -= rotation_speed
        if self.keys[K_RIGHT]:
            self.camera_angle_y += rotation_speed
        if self.keys[K_UP]:
            self.camera_angle_x = min(80, self.camera_angle_x + rotation_speed)
        if self.keys[K_DOWN]:
            self.camera_angle_x = max(10, self.camera_angle_x - rotation_speed)
        
        # Player movement (relative to camera)
        move_x = 0
        move_z = 0
        
        if self.keys[K_w]:  # Forward
            move_z -= speed
        if self.keys[K_s]:  # Backward
            move_z += speed
        if self.keys[K_a]:  # Strafe left
            move_x -= speed
        if self.keys[K_d]:  # Strafe right
            move_x += speed
        
        # Rotate movement based on camera
        rad_angle = math.radians(self.camera_angle_y)
        rotated_x = move_x * math.cos(rad_angle) - move_z * math.sin(rad_angle)
        rotated_z = move_x * math.sin(rad_angle) + move_z * math.cos(rad_angle)
        
        self.player_velocity.x = rotated_x
        self.player_velocity.z = rotated_z
        
        # Jump
        if self.keys[K_SPACE] and self.grounded:
            self.player_velocity.y = self.jump_power
            self.grounded = False
    
    def update_physics(self):
        """Update player position and physics"""
        # Apply gravity
        self.player_velocity.y -= self.gravity
        
        # Update position
        self.player_pos.x += self.player_velocity.x
        self.player_pos.z += self.player_velocity.z
        
        # Simple collision with ground
        if self.player_pos.y > 0:
            self.player_pos.y += self.player_velocity.y
        else:
            self.player_pos.y = 0
            self.player_velocity.y = 0
            self.grounded = True
        
        # Platform collision
        for platform in self.platforms:
            plat = platform['pos']
            size = platform['size']
            
            if (plat.x - size.x/2 < self.player_pos.x < plat.x + size.x/2 and
                plat.z - size.z/2 < self.player_pos.z < plat.z + size.z/2 and
                self.player_pos.y <= plat.y + size.y/2 and
                self.player_pos.y + self.player_velocity.y >= plat.y - size.y/2):
                
                self.player_pos.y = plat.y + size.y/2
                self.player_velocity.y = 0
                self.grounded = True
        
        # Collect coins
        for coin in self.coins[:]:
            if not coin['collected']:
                dist = math.sqrt(
                    (self.player_pos.x - coin['pos'].x)**2 +
                    (self.player_pos.y - coin['pos'].y)**2 +
                    (self.player_pos.z - coin['pos'].z)**2
                )
                if dist < 1.5:
                    coin['collected'] = True
        
        # Collect stars
        for star in self.stars[:]:
            if not star['collected']:
                dist = math.sqrt(
                    (self.player_pos.x - star['pos'].x)**2 +
                    (self.player_pos.y - star['pos'].y)**2 +
                    (self.player_pos.z - star['pos'].z)**2
                )
                if dist < 2:
                    star['collected'] = True
                    self.stars_collected += 1
                    print(f"Star collected! Total: {self.stars_collected}")
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Switch to 2D orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.display_size[0], self.display_size[1], 0)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        
        # Draw star counter
        font = pygame.font.Font(None, 36)
        text = font.render(f"Stars: {self.stars_collected}", True, (255, 255, 255))
        text_surface = pygame.image.fromstring(text.tobytes(), text.get_size(), "RGBA")
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text.get_width(), text.get_height(), 
                    0, GL_RGBA, GL_UNSIGNED_BYTE, text_surface.get_buffer())
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(20, 20)
        glTexCoord2f(1, 0); glVertex2f(20 + text.get_width(), 20)
        glTexCoord2f(1, 1); glVertex2f(20 + text.get_width(), 20 + text.get_height())
        glTexCoord2f(0, 1); glVertex2f(20, 20 + text.get_height())
        glEnd()
        
        glDeleteTextures([texture])
        
        # Restore 3D settings
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
    
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        running = True
        
        # Import GLUT for shapes (requires pygame to be initialized first)
        global glutSolidCube, glutSolidSphere, glutSolidCone
        from OpenGL.GLUT import glutSolidCube, glutSolidSphere, glutSolidCone
        
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    self.keys[event.key] = True
                    if event.key == K_ESCAPE:
                        running = False
                elif event.type == KEYUP:
                    self.keys[event.key] = False
            
            # Update
            self.handle_input()
            self.update_physics()
            
            # Render
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(0.53, 0.81, 0.98, 1)  # Sky blue
            
            self.update_camera()
            
            # Draw platforms
            for platform in self.platforms:
                self.draw_cube(platform['pos'], platform['size'], platform['color'])
            
            # Draw coins
            for coin in self.coins:
                if not coin['collected']:
                    self.draw_sphere(coin['pos'], 0.3, (1, 0.84, 0, 1))  # Gold
            
            # Draw stars
            for star in self.stars:
                if not star['collected']:
                    star['rotation'] += 2
                    glPushMatrix()
                    glTranslatef(star['pos'].x, star['pos'].y, star['pos'].z)
                    glRotatef(star['rotation'], 0, 1, 0)
                    self.draw_sphere(Vector3(0, 0, 0), 0.5, (1, 1, 0.3, 1))
                    glPopMatrix()
            
            # Draw player
            self.draw_player()
            
            # Draw HUD
            self.draw_hud()
            
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

class CastleArea:
    """Represents the castle hub world"""
    def __init__(self):
        self.rooms = {
            "Main Hall": {
                "doors": ["Bob-omb Battlefield", "Whomp's Fortress", "Jolly Roger Bay"],
                "position": Vector3(0, 0, 0),
                "size": Vector3(30, 15, 30)
            },
            "Basement": {
                "doors": ["Cool Cool Mountain", "Big Boo's Haunt"],
                "position": Vector3(0, -10, 0),
                "size": Vector3(25, 10, 25)
            },
            "Upper Floor": {
                "doors": ["Hazy Maze Cave", "Lethal Lava Land", "Shifting Sand Land"],
                "position": Vector3(0, 10, 0),
                "size": Vector3(20, 10, 20)
            }
        }
        
        self.paintings = []  # Portal to levels
        self.secret_stars = 0
    
    def draw_castle(self):
        """Render the castle environment"""
        # This would be expanded with actual castle geometry
        pass

class LevelManager:
    """Manages loading and switching between levels"""
    def __init__(self):
        self.levels = {
            1: {
                "name": "Bob-omb Battlefield",
                "stars_required": 0,
                "enemies": ["Bob-omb", "Chain Chomp"],
                "terrain": "grassy hills",
                "boss": "Big Bob-omb"
            },
            2: {
                "name": "Whomp's Fortress",
                "stars_required": 1,
                "enemies": ["Whomp", "Bully"],
                "terrain": "floating fortress",
                "boss": "King Whomp"
            },
            3: {
                "name": "Jolly Roger Bay",
                "stars_required": 3,
                "enemies": ["Cheep Cheep", "Unagi"],
                "terrain": "sunken ship ocean",
                "boss": "Eel"
            }
        }
        
        self.current_level_id = 1
    
    def load_level(self, level_id):
        """Load level data and geometry"""
        level = self.levels.get(level_id)
        if level:
            print(f"Loading level: {level['name']}")
            return level
        return None

def main():
    """Entry point for the game"""
    print("Super Mario 64 Pygame-CE Clone")
    print("Controls:")
    print("WASD - Move")
    print("Space - Jump")
    print("Arrow Keys - Rotate Camera")
    print("ESC - Exit")
    
    game = Mario64Game()
    game.run()

if __name__ == "__main__":
    main()
