#!/usr/bin/env python3
"""
FNF: Mario Forever - 3 Weeks of Corruption
A Friday Night Funkin' inspired rhythm game featuring corrupted Mario
Built with Pygame - Complete single-file implementation

By Team Flames / Samsoft
"""

import pygame
import random
import math
import time
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 100, 150)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Mario Colors
MARIO_RED = (228, 52, 52)
MARIO_BLUE = (52, 100, 228)
MARIO_SKIN = (255, 200, 150)
MARIO_BROWN = (139, 90, 43)

# Arrow colors
ARROW_COLORS = {
    'left': PURPLE,
    'down': CYAN,
    'up': GREEN,
    'right': RED
}

# Note timing windows (in milliseconds)
TIMING_SICK = 45
TIMING_GOOD = 90
TIMING_BAD = 135
TIMING_MISS = 180

class GameState(Enum):
    MENU = 0
    WEEK_SELECT = 1
    SONG_INTRO = 2
    PLAYING = 3
    PAUSED = 4
    GAME_OVER = 5
    WEEK_COMPLETE = 6
    CREDITS = 7

class Rating(Enum):
    SICK = "SICK!!"
    GOOD = "Good!"
    BAD = "Bad"
    MISS = "Miss"

@dataclass
class Note:
    time: float  # Time in ms when note should be hit
    direction: str  # 'left', 'down', 'up', 'right'
    is_opponent: bool  # True for opponent notes
    duration: float = 0  # For hold notes
    hit: bool = False
    missed: bool = False
    hold_progress: float = 0

@dataclass
class Song:
    name: str
    bpm: float
    notes: List[Note]
    scroll_speed: float = 1.0
    
class PixelSprite:
    """Generates pixel art sprites programmatically"""
    
    @staticmethod
    def draw_mario_classic(surface, x, y, scale=4, frame=0):
        """Draw classic NES-style Mario"""
        # Mario sprite data (simplified pixel art)
        mario_pixels = [
            "   RRRRR   ",
            "  RRRRRRRRR",
            "  BBBSSBS  ",
            " BSBSSSBS B",
            " BSBBBSSSBB",
            " BBSSSSSBBB",
            "   SSSSSS  ",
            "  BBRBBB   ",
            " BBBRBBBBB ",
            "BBBBRBBBBB ",
            "SSBRYYRBSS ",
            "SSSYYYYSSS ",
            "SSYYYYYSS  ",
            "  YYY YYY  ",
            " BBB   BBB ",
            "BBBB   BBBB",
        ]
        
        color_map = {
            'R': MARIO_RED,
            'B': MARIO_BLUE,
            'S': MARIO_SKIN,
            'Y': MARIO_BROWN,
            ' ': None
        }
        
        # Animation bounce
        bounce = int(math.sin(frame * 0.2) * 2)
        
        for row_idx, row in enumerate(mario_pixels):
            for col_idx, pixel in enumerate(row):
                if pixel in color_map and color_map[pixel]:
                    color = color_map[pixel]
                    px = x + col_idx * scale
                    py = y + row_idx * scale + bounce
                    pygame.draw.rect(surface, color, (px, py, scale, scale))
    
    @staticmethod
    def draw_mario_forever(surface, x, y, scale=4, frame=0, corruption=0.0):
        """Draw Mario Forever style - taller, slightly off"""
        # Taller sprite with odd proportions
        mario_pixels = [
            "   RRRRR   ",
            "  RRRRRRRRR",
            "  RRRRRRRRR",
            "  BBBSSBS  ",
            " BSBSSSBS B",
            " BSBSSSBS B",
            " BSBBBSSSBB",
            " BBSSSSSBBB",
            "   SSSSSS  ",
            "   SSSSSS  ",
            "  BBRBBB   ",
            " BBBRBBBBB ",
            " BBBRBBBBB ",
            "BBBBRBBBBB ",
            "SSBRYYRBSS ",
            "SSSYYYYSSS ",
            "SSSYYYYSSS ",
            "SSYYYYYSS  ",
            "  YYY YYY  ",
            "  YYY YYY  ",
            " BBB   BBB ",
            "BBBB   BBBB",
        ]
        
        color_map = {
            'R': MARIO_RED,
            'B': MARIO_BLUE,
            'S': MARIO_SKIN,
            'Y': MARIO_BROWN,
            ' ': None
        }
        
        # Uncanny animation - slightly too fast
        bounce = int(math.sin(frame * 0.35) * 3)
        sway = int(math.sin(frame * 0.15) * 2)
        
        for row_idx, row in enumerate(mario_pixels):
            for col_idx, pixel in enumerate(row):
                if pixel in color_map and color_map[pixel]:
                    color = list(color_map[pixel])
                    # Add slight color corruption
                    if random.random() < corruption * 0.1:
                        color[0] = min(255, color[0] + random.randint(-30, 30))
                        color[1] = min(255, color[1] + random.randint(-30, 30))
                    px = x + col_idx * scale + sway
                    py = y + row_idx * scale + bounce
                    # Occasional pixel displacement
                    if random.random() < corruption * 0.05:
                        px += random.randint(-scale, scale)
                    pygame.draw.rect(surface, tuple(color), (px, py, scale, scale))
    
    @staticmethod
    def draw_mario_corrupted(surface, x, y, scale=4, frame=0, corruption=1.0):
        """Draw fully corrupted Mario - horror version"""
        mario_pixels = [
            "   DDDDD   ",
            "  DDDDDDDDD",
            "  DDDDDDDDD",
            "  XXXSSXS  ",
            " XSXSSSXS X",
            " XSXSSSXS X",
            " XSXXXSSSXX",
            " XXSSSSSSXX",
            "   SSSSSS  ",
            "   SSSSSS  ",
            "  XXRXXX   ",
            " XXXRXXXXX ",
            " XXXRXXXXX ",
            "XXXXRXXXXX ",
            "SSXRYYRYSS ",
            "SSSYYYYSSS ",
            "SSSYYYYSSS ",
            "SSYYYYYSS  ",
            "  YYY YYY  ",
            "  YYY YYY  ",
            " XXX   XXX ",
            "XXXX   XXXX",
        ]
        
        dark_red = (100, 0, 0)
        void_black = (10, 10, 10)
        
        color_map = {
            'D': dark_red,
            'X': void_black,
            'S': (200, 150, 100),  # Pale skin
            'Y': (80, 50, 20),
            'R': (60, 0, 0),
            ' ': None
        }
        
        # Erratic, glitchy animation
        glitch_offset_x = random.randint(-5, 5) if random.random() < 0.3 else 0
        glitch_offset_y = random.randint(-3, 3) if random.random() < 0.2 else 0
        
        for row_idx, row in enumerate(mario_pixels):
            for col_idx, pixel in enumerate(row):
                if pixel in color_map and color_map[pixel]:
                    color = list(color_map[pixel])
                    
                    # Heavy corruption effects
                    if random.random() < 0.15:
                        color = [random.randint(0, 50), 0, 0]
                    
                    px = x + col_idx * scale + glitch_offset_x
                    py = y + row_idx * scale + glitch_offset_y
                    
                    # Pixel tearing
                    if random.random() < 0.1:
                        px += random.randint(-scale*2, scale*2)
                    
                    # Draw with occasional scanline effect
                    if row_idx % 2 == 0 or random.random() > 0.1:
                        pygame.draw.rect(surface, tuple(color), (px, py, scale, scale))
        
        # Draw creepy eyes (black voids with red dots)
        eye_y = y + 4 * scale + glitch_offset_y
        left_eye_x = x + 3 * scale + glitch_offset_x
        right_eye_x = x + 7 * scale + glitch_offset_x
        
        # Black eye sockets
        pygame.draw.circle(surface, BLACK, (left_eye_x, eye_y), scale * 2)
        pygame.draw.circle(surface, BLACK, (right_eye_x, eye_y), scale * 2)
        
        # Red pupils that track randomly
        pupil_offset = (random.randint(-2, 2), random.randint(-2, 2))
        pygame.draw.circle(surface, RED, (left_eye_x + pupil_offset[0], eye_y + pupil_offset[1]), scale // 2)
        pygame.draw.circle(surface, RED, (right_eye_x + pupil_offset[0], eye_y + pupil_offset[1]), scale // 2)
    
    @staticmethod
    def draw_boyfriend(surface, x, y, scale=3, frame=0):
        """Draw FNF Boyfriend"""
        bf_pixels = [
            "  CCCCC  ",
            " CCCCCCC ",
            " CCCCCCC ",
            "SSWSSWSS ",
            "SSSSSSSS ",
            " SSMSSS  ",
            "  BBBB   ",
            " BBBBBB  ",
            " BWBBWB  ",
            " BBBBBB  ",
            "  SSSS   ",
            " SS  SS  ",
            " WW  WW  ",
        ]
        
        color_map = {
            'C': CYAN,
            'S': MARIO_SKIN,
            'W': WHITE,
            'B': BLUE,
            'M': (200, 100, 100),
            ' ': None
        }
        
        bounce = int(math.sin(frame * 0.3) * 2)
        
        for row_idx, row in enumerate(bf_pixels):
            for col_idx, pixel in enumerate(row):
                if pixel in color_map and color_map[pixel]:
                    px = x + col_idx * scale
                    py = y + row_idx * scale + bounce
                    pygame.draw.rect(surface, color_map[pixel], (px, py, scale, scale))

class SoundGenerator:
    """Generates game sounds programmatically"""
    
    @staticmethod
    def generate_tone(frequency, duration, volume=0.3, wave_type='square'):
        """Generate a tone as a pygame Sound object"""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        # Generate waveform
        samples = []
        for i in range(n_samples):
            t = i / sample_rate
            if wave_type == 'square':
                value = 1 if math.sin(2 * math.pi * frequency * t) > 0 else -1
            elif wave_type == 'sine':
                value = math.sin(2 * math.pi * frequency * t)
            elif wave_type == 'triangle':
                value = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1
            elif wave_type == 'noise':
                value = random.uniform(-1, 1)
            else:
                value = math.sin(2 * math.pi * frequency * t)
            
            # Apply envelope
            envelope = 1.0
            attack = 0.01
            release = 0.1
            if t < attack:
                envelope = t / attack
            elif t > duration - release:
                envelope = (duration - t) / release
            
            value *= envelope * volume
            
            # Convert to 16-bit integer
            sample = int(value * 32767)
            samples.append(sample)
        
        # Create stereo buffer
        import array
        buf = array.array('h', [0] * (n_samples * 2))
        for i, s in enumerate(samples):
            buf[i * 2] = s  # Left
            buf[i * 2 + 1] = s  # Right
        
        sound = pygame.mixer.Sound(buffer=buf)
        return sound
    
    @staticmethod
    def generate_hit_sound():
        """Generate note hit sound"""
        return SoundGenerator.generate_tone(880, 0.05, 0.2, 'square')
    
    @staticmethod
    def generate_miss_sound():
        """Generate miss sound"""
        return SoundGenerator.generate_tone(150, 0.15, 0.3, 'noise')
    
    @staticmethod
    def generate_menu_select():
        """Generate menu select sound"""
        return SoundGenerator.generate_tone(660, 0.1, 0.2, 'square')

class ChartGenerator:
    """Generates song charts procedurally"""
    
    @staticmethod
    def generate_week1_song(song_idx: int) -> Song:
        """Generate cheerful, bouncy Week 1 songs"""
        bpms = [120, 130, 140]
        names = ["Mushroom-Kingdom", "Pipe-Dreams", "Castle-Hop"]
        
        bpm = bpms[song_idx]
        beat_duration = 60000 / bpm  # ms per beat
        
        notes = []
        song_length = 60000  # 60 seconds
        
        # Generate opponent notes (Mario)
        directions = ['left', 'down', 'up', 'right']
        current_time = 2000  # Start after 2 seconds
        
        while current_time < song_length:
            # Simple patterns for Week 1
            pattern_type = random.choice(['single', 'double', 'stair'])
            
            if pattern_type == 'single':
                notes.append(Note(
                    time=current_time,
                    direction=random.choice(directions),
                    is_opponent=True
                ))
                current_time += beat_duration
                
            elif pattern_type == 'double':
                d1, d2 = random.sample(directions, 2)
                notes.append(Note(time=current_time, direction=d1, is_opponent=True))
                notes.append(Note(time=current_time, direction=d2, is_opponent=True))
                current_time += beat_duration
                
            elif pattern_type == 'stair':
                for i, d in enumerate(directions):
                    notes.append(Note(
                        time=current_time + i * (beat_duration / 4),
                        direction=d,
                        is_opponent=True
                    ))
                current_time += beat_duration * 2
            
            # Add some rest
            if random.random() < 0.3:
                current_time += beat_duration
        
        # Generate player notes (mirror opponent with slight delay)
        player_notes = []
        for note in notes:
            player_notes.append(Note(
                time=note.time + beat_duration * 2,
                direction=note.direction,
                is_opponent=False
            ))
        
        notes.extend(player_notes)
        notes.sort(key=lambda n: n.time)
        
        return Song(name=names[song_idx], bpm=bpm, notes=notes, scroll_speed=1.0)
    
    @staticmethod
    def generate_week2_song(song_idx: int) -> Song:
        """Generate uncanny Week 2 songs with BPM shifts"""
        base_bpms = [145, 155, 165]
        names = ["Forever-Loop", "Uncanny-Valley", "XP-Error"]
        
        bpm = base_bpms[song_idx]
        beat_duration = 60000 / bpm
        
        notes = []
        song_length = 70000
        
        directions = ['left', 'down', 'up', 'right']
        current_time = 1500
        
        while current_time < song_length:
            # More complex patterns
            pattern = random.choice(['jack', 'stream', 'jumps', 'chaos'])
            
            # Occasional BPM shift simulation
            if random.random() < 0.1:
                beat_duration *= random.choice([0.8, 1.2])
            
            if pattern == 'jack':
                # Same direction repeated
                d = random.choice(directions)
                for i in range(4):
                    notes.append(Note(
                        time=current_time + i * (beat_duration / 2),
                        direction=d,
                        is_opponent=True
                    ))
                current_time += beat_duration * 2
                
            elif pattern == 'stream':
                # Fast alternating notes
                for i in range(8):
                    notes.append(Note(
                        time=current_time + i * (beat_duration / 4),
                        direction=directions[i % 4],
                        is_opponent=True
                    ))
                current_time += beat_duration * 2
                
            elif pattern == 'jumps':
                # Double notes
                for i in range(3):
                    d1, d2 = random.sample(directions, 2)
                    t = current_time + i * beat_duration
                    notes.append(Note(time=t, direction=d1, is_opponent=True))
                    notes.append(Note(time=t, direction=d2, is_opponent=True))
                current_time += beat_duration * 3
                
            elif pattern == 'chaos':
                # Random fast notes
                for i in range(6):
                    notes.append(Note(
                        time=current_time + i * (beat_duration / 3),
                        direction=random.choice(directions),
                        is_opponent=True
                    ))
                current_time += beat_duration * 2
            
            current_time += beat_duration / 2
        
        # Player notes
        player_notes = []
        for note in notes:
            player_notes.append(Note(
                time=note.time + beat_duration * 1.5,
                direction=note.direction,
                is_opponent=False
            ))
        
        notes.extend(player_notes)
        notes.sort(key=lambda n: n.time)
        
        return Song(name=names[song_idx], bpm=bpm, notes=notes, scroll_speed=1.3)
    
    @staticmethod
    def generate_week3_song(song_idx: int) -> Song:
        """Generate aggressive Week 3 songs with fake-outs"""
        base_bpms = [170, 185, 200]
        names = ["Corruption", "V̷O̷I̷D̷", "F̸I̸N̸A̸L̸E̸"]
        
        bpm = base_bpms[song_idx]
        beat_duration = 60000 / bpm
        
        notes = []
        song_length = 80000
        
        directions = ['left', 'down', 'up', 'right']
        current_time = 1000
        
        while current_time < song_length:
            pattern = random.choice(['death_stream', 'quad', 'minijack', 'burst', 'fakeout'])
            
            if pattern == 'death_stream':
                # Long stream of notes
                for i in range(16):
                    notes.append(Note(
                        time=current_time + i * (beat_duration / 4),
                        direction=directions[i % 4],
                        is_opponent=True
                    ))
                current_time += beat_duration * 4
                
            elif pattern == 'quad':
                # All 4 directions at once
                for d in directions:
                    notes.append(Note(time=current_time, direction=d, is_opponent=True))
                current_time += beat_duration
                
            elif pattern == 'minijack':
                # Triple jacks
                d = random.choice(directions)
                for i in range(3):
                    notes.append(Note(
                        time=current_time + i * (beat_duration / 4),
                        direction=d,
                        is_opponent=True
                    ))
                current_time += beat_duration
                
            elif pattern == 'burst':
                # Quick burst of notes
                for i in range(4):
                    notes.append(Note(
                        time=current_time + i * (beat_duration / 8),
                        direction=random.choice(directions),
                        is_opponent=True
                    ))
                current_time += beat_duration
                
            elif pattern == 'fakeout':
                # Notes that appear then disappear (handled in rendering)
                notes.append(Note(
                    time=current_time,
                    direction=random.choice(directions),
                    is_opponent=True
                ))
                current_time += beat_duration / 2
            
            current_time += beat_duration / 4
        
        # Player notes with tighter timing
        player_notes = []
        for note in notes:
            player_notes.append(Note(
                time=note.time + beat_duration,
                direction=note.direction,
                is_opponent=False
            ))
        
        notes.extend(player_notes)
        notes.sort(key=lambda n: n.time)
        
        return Song(name=names[song_idx], bpm=bpm, notes=notes, scroll_speed=1.8)

class BackgroundRenderer:
    """Renders week-specific backgrounds"""
    
    @staticmethod
    def render_week1(surface, frame):
        """Bright, cheerful Mario background"""
        # Sky gradient
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(135 + ratio * 50)
            g = int(206 + ratio * 30)
            b = int(235 - ratio * 50)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Hills
        for i in range(3):
            hill_x = (i * 500 - frame * 0.5) % (SCREEN_WIDTH + 300) - 150
            hill_y = SCREEN_HEIGHT - 150 + i * 30
            pygame.draw.ellipse(surface, (100, 200, 100), 
                              (hill_x, hill_y, 400, 200))
        
        # Floating blocks
        for i in range(5):
            block_x = (i * 250 + frame * 0.3) % SCREEN_WIDTH
            block_y = 150 + math.sin(frame * 0.05 + i) * 20
            pygame.draw.rect(surface, (200, 150, 50), 
                           (block_x, block_y, 40, 40))
            pygame.draw.rect(surface, (255, 200, 100), 
                           (block_x + 5, block_y + 5, 30, 30))
            # Question mark
            font = pygame.font.Font(None, 30)
            text = font.render("?", True, (150, 100, 0))
            surface.blit(text, (block_x + 13, block_y + 8))
        
        # Pipes
        for i in range(3):
            pipe_x = 200 + i * 400
            pipe_height = 100 + i * 20
            # Pipe body
            pygame.draw.rect(surface, (0, 180, 0), 
                           (pipe_x, SCREEN_HEIGHT - pipe_height, 60, pipe_height))
            # Pipe top
            pygame.draw.rect(surface, (0, 200, 0), 
                           (pipe_x - 5, SCREEN_HEIGHT - pipe_height, 70, 20))
        
        # Ground
        pygame.draw.rect(surface, (139, 90, 43), 
                        (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        # Ground pattern
        for i in range(SCREEN_WIDTH // 50):
            pygame.draw.rect(surface, (100, 60, 30), 
                           (i * 50, SCREEN_HEIGHT - 50, 25, 25))
            pygame.draw.rect(surface, (100, 60, 30), 
                           (i * 50 + 25, SCREEN_HEIGHT - 25, 25, 25))
    
    @staticmethod
    def render_week2(surface, frame):
        """Uncanny Windows XP era aesthetic"""
        # Dull sky with wrong colors
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(150 - ratio * 30)
            g = int(150 - ratio * 20)
            b = int(180 - ratio * 40)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Looping background elements (unsettling repeat)
        loop_offset = frame % 200
        
        # Broken castle in background
        castle_x = SCREEN_WIDTH // 2 - 150
        # Castle body
        pygame.draw.rect(surface, (80, 80, 90), 
                        (castle_x, 200, 300, 300))
        # Towers
        pygame.draw.rect(surface, (70, 70, 80), 
                        (castle_x - 30, 150, 60, 350))
        pygame.draw.rect(surface, (70, 70, 80), 
                        (castle_x + 270, 150, 60, 350))
        # Windows (some glitched)
        for i in range(3):
            for j in range(2):
                wx = castle_x + 50 + i * 80
                wy = 250 + j * 100
                if random.random() < 0.1:  # Glitch effect
                    pygame.draw.rect(surface, (255, 0, 0), (wx, wy, 40, 50))
                else:
                    pygame.draw.rect(surface, (30, 30, 40), (wx, wy, 40, 50))
        
        # Floating error messages
        if frame % 120 < 60:
            font = pygame.font.Font(None, 24)
            errors = ["ERROR", "404", "NULL", "???"]
            for i, err in enumerate(errors):
                err_x = (i * 300 + frame) % SCREEN_WIDTH
                err_y = 100 + math.sin(frame * 0.1 + i) * 30
                text = font.render(err, True, (200, 50, 50))
                surface.blit(text, (err_x, err_y))
        
        # Glitchy ground
        pygame.draw.rect(surface, (60, 60, 70), 
                        (0, SCREEN_HEIGHT - 80, SCREEN_WIDTH, 80))
        # Scanlines
        for y in range(SCREEN_HEIGHT - 80, SCREEN_HEIGHT, 4):
            if random.random() < 0.1:
                pygame.draw.line(surface, (100, 100, 110), 
                               (0, y), (SCREEN_WIDTH, y))
        
        # Occasional screen tear
        if random.random() < 0.05:
            tear_y = random.randint(0, SCREEN_HEIGHT)
            tear_height = random.randint(5, 20)
            tear_offset = random.randint(-30, 30)
            # Capture and offset a slice
            pygame.draw.rect(surface, (0, 0, 0), 
                           (tear_offset, tear_y, SCREEN_WIDTH, tear_height))
    
    @staticmethod
    def render_week3(surface, frame, corruption_level=1.0):
        """Full horror corruption"""
        # Void background
        surface.fill((5, 0, 0))
        
        # Pulsing darkness
        pulse = abs(math.sin(frame * 0.05)) * 0.5 + 0.5
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((int(20 * pulse), 0, 0))
        overlay.set_alpha(100)
        surface.blit(overlay, (0, 0))
        
        # Corrupted Mario assets floating in void
        for i in range(10):
            x = (i * 150 + frame * (0.5 + i * 0.1)) % (SCREEN_WIDTH + 100) - 50
            y = 100 + math.sin(frame * 0.03 + i) * 200
            size = 20 + i * 5
            
            # Glitched sprites
            if random.random() < 0.3:
                color = (random.randint(50, 150), 0, 0)
            else:
                color = (50, 50, 60)
            
            pygame.draw.rect(surface, color, (x, y, size, size))
            
            # Trailing effect
            for t in range(3):
                trail_alpha = 100 - t * 30
                trail_x = x - t * 10
                trail_surf = pygame.Surface((size, size))
                trail_surf.fill(color)
                trail_surf.set_alpha(trail_alpha)
                surface.blit(trail_surf, (trail_x, y))
        
        # Static noise overlay
        noise_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for _ in range(500):
            nx = random.randint(0, SCREEN_WIDTH)
            ny = random.randint(0, SCREEN_HEIGHT)
            nc = random.randint(0, 30)
            pygame.draw.rect(noise_surface, (nc, nc, nc), (nx, ny, 2, 2))
        noise_surface.set_alpha(50)
        surface.blit(noise_surface, (0, 0))
        
        # VHS tracking lines
        for i in range(3):
            line_y = (frame * 2 + i * 200) % SCREEN_HEIGHT
            pygame.draw.line(surface, (40, 0, 0), 
                           (0, line_y), (SCREEN_WIDTH, line_y), 3)
        
        # Glitch blocks
        if random.random() < 0.15:
            for _ in range(5):
                gx = random.randint(0, SCREEN_WIDTH)
                gy = random.randint(0, SCREEN_HEIGHT)
                gw = random.randint(20, 100)
                gh = random.randint(5, 30)
                gc = (random.randint(100, 255), 0, 0)
                pygame.draw.rect(surface, gc, (gx, gy, gw, gh))
        
        # Creepy text flashes
        if frame % 180 < 30:
            font = pygame.font.Font(None, 72)
            scary_texts = ["RUN", "HELP", "ERROR", "IT HURTS", "FOREVER"]
            text = font.render(random.choice(scary_texts), True, (150, 0, 0))
            text_x = SCREEN_WIDTH // 2 - text.get_width() // 2 + random.randint(-10, 10)
            text_y = SCREEN_HEIGHT // 2 + random.randint(-20, 20)
            surface.blit(text, (text_x, text_y))

class StrumLine:
    """Renders the strum line and arrows"""
    
    def __init__(self, x_offset, is_opponent=False):
        self.x_offset = x_offset
        self.is_opponent = is_opponent
        self.arrow_spacing = 100
        self.arrow_y = 100
        self.press_states = {'left': False, 'down': False, 'up': False, 'right': False}
        self.glow_timers = {'left': 0, 'down': 0, 'up': 0, 'right': 0}
    
    def get_arrow_x(self, direction):
        positions = {'left': 0, 'down': 1, 'up': 2, 'right': 3}
        return self.x_offset + positions[direction] * self.arrow_spacing
    
    def draw_arrow(self, surface, direction, x, y, pressed=False, size=60, corruption=0):
        """Draw an arrow receptor or note"""
        color = ARROW_COLORS[direction]
        
        if pressed:
            # Brighter when pressed
            color = tuple(min(255, c + 80) for c in color)
        
        # Corruption effect
        if corruption > 0 and random.random() < corruption * 0.2:
            color = (random.randint(100, 255), random.randint(0, 50), random.randint(0, 50))
        
        # Arrow shape based on direction
        center_x = x + size // 2
        center_y = y + size // 2
        
        if direction == 'left':
            points = [
                (x + 10, center_y),
                (x + size - 10, y + 10),
                (x + size - 10, y + size - 10)
            ]
        elif direction == 'right':
            points = [
                (x + size - 10, center_y),
                (x + 10, y + 10),
                (x + 10, y + size - 10)
            ]
        elif direction == 'up':
            points = [
                (center_x, y + 10),
                (x + 10, y + size - 10),
                (x + size - 10, y + size - 10)
            ]
        else:  # down
            points = [
                (center_x, y + size - 10),
                (x + 10, y + 10),
                (x + size - 10, y + 10)
            ]
        
        # Glow effect
        if self.glow_timers[direction] > 0:
            glow_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
            glow_color = (*color, min(255, self.glow_timers[direction] * 10))
            pygame.draw.polygon(glow_surf, glow_color, 
                              [(p[0] - x + 10, p[1] - y + 10) for p in points])
            surface.blit(glow_surf, (x - 10, y - 10))
        
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, WHITE, points, 2)
    
    def render(self, surface, corruption=0):
        """Render the strum line receptors"""
        for direction in ['left', 'down', 'up', 'right']:
            x = self.get_arrow_x(direction)
            self.draw_arrow(surface, direction, x, self.arrow_y, 
                          self.press_states[direction], corruption=corruption)
            
            # Update glow
            if self.glow_timers[direction] > 0:
                self.glow_timers[direction] -= 1
    
    def trigger_glow(self, direction):
        self.glow_timers[direction] = 15

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("FNF: Mario Forever - 3 Weeks of Corruption")
        self.clock = pygame.time.Clock()
        
        self.state = GameState.MENU
        self.current_week = 0
        self.current_song_idx = 0
        self.current_song: Optional[Song] = None
        
        # UI elements
        self.player_strum = StrumLine(SCREEN_WIDTH - 480)
        self.opponent_strum = StrumLine(80, is_opponent=True)
        
        # Game state
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 50  # 0-100
        self.misses = 0
        self.hits = {'sick': 0, 'good': 0, 'bad': 0}
        
        # Timing
        self.song_start_time = 0
        self.song_position = 0
        
        # Visual effects
        self.frame_count = 0
        self.rating_display = None
        self.rating_timer = 0
        self.combo_display = None
        
        # Corruption effects
        self.corruption_level = 0
        self.screen_shake = 0
        self.glitch_active = False
        
        # Sounds
        self.hit_sound = SoundGenerator.generate_hit_sound()
        self.miss_sound = SoundGenerator.generate_miss_sound()
        self.menu_sound = SoundGenerator.generate_menu_select()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.ui_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Menu
        self.menu_selection = 0
        self.menu_items = ["Play", "Week Select", "Credits", "Exit"]
        self.week_names = ["Week 1: Classic Mario", "Week 2: Mario Forever", "Week 3: Corrupted"]
        
        # Key bindings
        self.key_bindings = {
            pygame.K_LEFT: 'left',
            pygame.K_DOWN: 'down',
            pygame.K_UP: 'up',
            pygame.K_RIGHT: 'right',
            pygame.K_a: 'left',
            pygame.K_s: 'down',
            pygame.K_w: 'up',
            pygame.K_d: 'right'
        }
        
        # Dialogue system
        self.dialogue_active = False
        self.dialogue_text = ""
        self.dialogue_timer = 0
        self.dialogue_corruption = 0
    
    def start_song(self, week: int, song_idx: int):
        """Start a song"""
        self.current_week = week
        self.current_song_idx = song_idx
        
        # Generate chart based on week
        if week == 0:
            self.current_song = ChartGenerator.generate_week1_song(song_idx)
            self.corruption_level = 0
        elif week == 1:
            self.current_song = ChartGenerator.generate_week2_song(song_idx)
            self.corruption_level = 0.3 + song_idx * 0.1
        else:
            self.current_song = ChartGenerator.generate_week3_song(song_idx)
            self.corruption_level = 0.6 + song_idx * 0.15
        
        # Reset game state
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.health = 50
        self.misses = 0
        self.hits = {'sick': 0, 'good': 0, 'bad': 0}
        
        self.song_start_time = pygame.time.get_ticks()
        self.state = GameState.PLAYING
    
    def get_song_position(self):
        """Get current position in song (ms)"""
        return pygame.time.get_ticks() - self.song_start_time
    
    def check_note_hit(self, direction: str) -> Optional[Tuple[Note, Rating]]:
        """Check if a note was hit and return rating"""
        if not self.current_song:
            return None
        
        current_time = self.get_song_position()
        
        for note in self.current_song.notes:
            if note.is_opponent or note.hit or note.missed:
                continue
            
            if note.direction != direction:
                continue
            
            time_diff = abs(current_time - note.time)
            
            if time_diff <= TIMING_SICK:
                return (note, Rating.SICK)
            elif time_diff <= TIMING_GOOD:
                return (note, Rating.GOOD)
            elif time_diff <= TIMING_BAD:
                return (note, Rating.BAD)
            elif time_diff <= TIMING_MISS:
                return (note, Rating.MISS)
        
        return None
    
    def process_hit(self, note: Note, rating: Rating):
        """Process a successful hit"""
        note.hit = True
        self.player_strum.trigger_glow(note.direction)
        
        if rating == Rating.SICK:
            self.score += 350
            self.combo += 1
            self.hits['sick'] += 1
            self.health = min(100, self.health + 2)
            self.hit_sound.play()
        elif rating == Rating.GOOD:
            self.score += 200
            self.combo += 1
            self.hits['good'] += 1
            self.health = min(100, self.health + 1)
            self.hit_sound.play()
        elif rating == Rating.BAD:
            self.score += 50
            self.hits['bad'] += 1
            # No health change
        else:  # MISS rating from timing
            self.process_miss()
            return
        
        self.max_combo = max(self.max_combo, self.combo)
        self.rating_display = rating
        self.rating_timer = 30
        self.combo_display = self.combo
    
    def process_miss(self):
        """Process a miss"""
        self.combo = 0
        self.misses += 1
        self.health = max(0, self.health - 5)
        self.miss_sound.play()
        
        self.rating_display = Rating.MISS
        self.rating_timer = 30
        
        # Screen shake on miss
        self.screen_shake = 10
        
        if self.health <= 0:
            self.state = GameState.GAME_OVER
    
    def update_notes(self):
        """Update note positions and check for misses"""
        if not self.current_song:
            return
        
        current_time = self.get_song_position()
        
        for note in self.current_song.notes:
            if note.hit or note.missed:
                continue
            
            # Check for missed notes (past the hit window)
            if not note.is_opponent and current_time - note.time > TIMING_MISS:
                note.missed = True
                self.process_miss()
            
            # Auto-hit opponent notes
            if note.is_opponent and current_time >= note.time:
                note.hit = True
                self.opponent_strum.trigger_glow(note.direction)
        
        # Check if song is complete
        all_done = all(n.hit or n.missed or n.is_opponent for n in self.current_song.notes 
                      if not n.is_opponent)
        
        if all_done or current_time > max(n.time for n in self.current_song.notes) + 2000:
            self.song_complete()
    
    def song_complete(self):
        """Handle song completion"""
        if self.current_song_idx < 2:
            # Next song in week
            self.current_song_idx += 1
            self.show_song_intro()
        else:
            # Week complete
            self.state = GameState.WEEK_COMPLETE
    
    def show_song_intro(self):
        """Show intro before song"""
        self.state = GameState.SONG_INTRO
        self.dialogue_timer = 180  # 3 seconds
        
        # Set dialogue based on week
        intros = {
            (0, 0): "Let's-a go! Time for a funky battle!",
            (0, 1): "Mama mia! You're good, but can you handle this?",
            (0, 2): "It's-a me! Let's finish this!",
            (1, 0): "Something feels... wrong...",
            (1, 1): "Why does everything keep... looping?",
            (1, 2): "Can you hear it? The errors?",
            (2, 0): "Y̷o̷u̷ ̷s̷h̷o̷u̷l̷d̷n̷'̷t̷ ̷h̷a̷v̷e̷ ̷c̷o̷m̷e̷ ̷h̷e̷r̷e̷",
            (2, 1): "T̸H̸E̸R̸E̸ ̸I̸S̸ ̸N̸O̸ ̸E̸S̸C̸A̸P̸E̸",
            (2, 2): "F̷̢O̵R̵͘E̴V̶̧E̴R̵.̷.̵.̴ ̴F̴O̶R̵E̸V̵E̷R̶.̴.̴.̵ ̴F̴O̶R̵E̵V̵E̸R̴.̵.̸.̴"
        }
        
        self.dialogue_text = intros.get((self.current_week, self.current_song_idx), "...")
        self.dialogue_corruption = self.current_week * 0.3
    
    def render_notes(self, surface):
        """Render all notes"""
        if not self.current_song:
            return
        
        current_time = self.get_song_position()
        scroll_speed = self.current_song.scroll_speed
        
        for note in self.current_song.notes:
            if note.hit or note.missed:
                continue
            
            # Calculate Y position
            time_until = note.time - current_time
            y_offset = time_until * scroll_speed * 0.5
            y = self.player_strum.arrow_y + y_offset
            
            # Only render visible notes
            if y < -100 or y > SCREEN_HEIGHT + 100:
                continue
            
            # Get X position
            if note.is_opponent:
                x = self.opponent_strum.get_arrow_x(note.direction)
            else:
                x = self.player_strum.get_arrow_x(note.direction)
            
            # Note appearance corruption in later weeks
            note_corruption = self.corruption_level if not note.is_opponent else 0
            
            # Draw note
            self.player_strum.draw_arrow(surface, note.direction, x, y, 
                                        corruption=note_corruption)
    
    def render_ui(self, surface):
        """Render UI elements"""
        # Health bar
        bar_width = 400
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT - 40
        
        # Background
        pygame.draw.rect(surface, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill (gradient from red to green)
        health_width = int(bar_width * self.health / 100)
        health_color = (
            int(255 * (1 - self.health / 100)),
            int(255 * self.health / 100),
            0
        )
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Score
        score_text = self.ui_font.render(f"Score: {self.score}", True, WHITE)
        surface.blit(score_text, (10, 10))
        
        # Misses
        miss_text = self.ui_font.render(f"Misses: {self.misses}", True, RED)
        surface.blit(miss_text, (10, 50))
        
        # Combo
        if self.combo > 0:
            combo_text = self.ui_font.render(f"Combo: {self.combo}", True, YELLOW)
            surface.blit(combo_text, (SCREEN_WIDTH - 150, 10))
        
        # Rating display
        if self.rating_timer > 0:
            rating_colors = {
                Rating.SICK: CYAN,
                Rating.GOOD: GREEN,
                Rating.BAD: YELLOW,
                Rating.MISS: RED
            }
            
            alpha = min(255, self.rating_timer * 8)
            rating_text = self.menu_font.render(self.rating_display.value, True, 
                                               rating_colors[self.rating_display])
            
            # Center of screen with combo
            text_x = SCREEN_WIDTH // 2 - rating_text.get_width() // 2
            text_y = SCREEN_HEIGHT // 2 - 50
            
            surface.blit(rating_text, (text_x, text_y))
            
            if self.combo_display and self.combo_display > 1:
                combo_text = self.ui_font.render(f"{self.combo_display}x", True, WHITE)
                surface.blit(combo_text, (text_x + rating_text.get_width() // 2 - 20, text_y + 50))
            
            self.rating_timer -= 1
        
        # Song name
        if self.current_song:
            song_text = self.small_font.render(self.current_song.name, True, WHITE)
            surface.blit(song_text, (SCREEN_WIDTH // 2 - song_text.get_width() // 2, 10))
    
    def render_characters(self, surface):
        """Render BF and opponent"""
        # Opponent (Mario variants)
        opponent_x = 200
        opponent_y = 300
        
        if self.current_week == 0:
            PixelSprite.draw_mario_classic(surface, opponent_x, opponent_y, 
                                          scale=5, frame=self.frame_count)
        elif self.current_week == 1:
            PixelSprite.draw_mario_forever(surface, opponent_x, opponent_y, 
                                          scale=5, frame=self.frame_count,
                                          corruption=self.corruption_level)
        else:
            PixelSprite.draw_mario_corrupted(surface, opponent_x, opponent_y, 
                                            scale=5, frame=self.frame_count,
                                            corruption=self.corruption_level)
        
        # Boyfriend
        bf_x = SCREEN_WIDTH - 300
        bf_y = 350
        PixelSprite.draw_boyfriend(surface, bf_x, bf_y, scale=5, frame=self.frame_count)
    
    def render_menu(self, surface):
        """Render main menu"""
        # Background with Mario theme
        BackgroundRenderer.render_week1(surface, self.frame_count)
        
        # Darken
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        surface.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("FNF: Mario Forever", True, WHITE)
        subtitle = self.menu_font.render("3 Weeks of Corruption", True, RED)
        
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        surface.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 180))
        
        # Menu items
        for i, item in enumerate(self.menu_items):
            color = YELLOW if i == self.menu_selection else WHITE
            text = self.menu_font.render(item, True, color)
            y = 300 + i * 60
            
            if i == self.menu_selection:
                # Selection indicator
                indicator = self.menu_font.render(">", True, YELLOW)
                surface.blit(indicator, (SCREEN_WIDTH // 2 - 150, y))
            
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        
        # Controls hint
        hint = self.small_font.render("Arrow Keys / WASD to Play | Enter to Select", True, GRAY)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))
        
        # Credits
        credits = self.small_font.render("Team Flames / Samsoft", True, GRAY)
        surface.blit(credits, (SCREEN_WIDTH // 2 - credits.get_width() // 2, SCREEN_HEIGHT - 25))
    
    def render_week_select(self, surface):
        """Render week selection"""
        surface.fill((30, 30, 50))
        
        title = self.title_font.render("Select Week", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        for i, week in enumerate(self.week_names):
            color = YELLOW if i == self.menu_selection else WHITE
            
            # Week preview box
            box_x = SCREEN_WIDTH // 2 - 200
            box_y = 150 + i * 150
            box_width = 400
            box_height = 120
            
            if i == self.menu_selection:
                pygame.draw.rect(surface, YELLOW, (box_x - 5, box_y - 5, 
                                                   box_width + 10, box_height + 10), 3)
            
            pygame.draw.rect(surface, DARK_GRAY, (box_x, box_y, box_width, box_height))
            
            # Week name
            text = self.menu_font.render(week, True, color)
            surface.blit(text, (box_x + 20, box_y + 20))
            
            # Song previews
            if i == 0:
                songs = ["Mushroom-Kingdom", "Pipe-Dreams", "Castle-Hop"]
            elif i == 1:
                songs = ["Forever-Loop", "Uncanny-Valley", "XP-Error"]
            else:
                songs = ["Corruption", "V̷O̷I̷D̷", "F̸I̸N̸A̸L̸E̸"]
            
            song_text = self.small_font.render(" | ".join(songs), True, GRAY)
            surface.blit(song_text, (box_x + 20, box_y + 70))
        
        # Back hint
        hint = self.small_font.render("ESC to go back", True, GRAY)
        surface.blit(hint, (20, SCREEN_HEIGHT - 30))
    
    def render_song_intro(self, surface):
        """Render song intro dialogue"""
        # Render background based on week
        if self.current_week == 0:
            BackgroundRenderer.render_week1(surface, self.frame_count)
        elif self.current_week == 1:
            BackgroundRenderer.render_week2(surface, self.frame_count)
        else:
            BackgroundRenderer.render_week3(surface, self.frame_count)
        
        # Darken
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(150)
        surface.blit(overlay, (0, 0))
        
        # Dialogue box
        box_width = 800
        box_height = 150
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = SCREEN_HEIGHT - 200
        
        # Box corruption effect
        if self.dialogue_corruption > 0:
            box_x += random.randint(-3, 3)
            box_y += random.randint(-2, 2)
        
        pygame.draw.rect(surface, (20, 20, 30), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surface, WHITE, (box_x, box_y, box_width, box_height), 3)
        
        # Character name
        name = "Mario" if self.current_week < 2 else "???"
        name_text = self.ui_font.render(name, True, MARIO_RED if self.current_week < 2 else RED)
        surface.blit(name_text, (box_x + 20, box_y + 15))
        
        # Dialogue text (typewriter effect)
        chars_to_show = min(len(self.dialogue_text), 
                           (180 - self.dialogue_timer) // 2)
        display_text = self.dialogue_text[:chars_to_show]
        
        # Corruption on text
        if self.dialogue_corruption > 0.5:
            display_text = ''.join(
                c if random.random() > 0.1 else random.choice(['█', '▓', '░', c.upper()])
                for c in display_text
            )
        
        text = self.menu_font.render(display_text, True, WHITE)
        surface.blit(text, (box_x + 20, box_y + 60))
        
        # Song name
        if self.current_song:
            song_name = self.title_font.render(self.current_song.name, True, WHITE)
            surface.blit(song_name, (SCREEN_WIDTH // 2 - song_name.get_width() // 2, 200))
        
        # Countdown
        if self.dialogue_timer < 60:
            countdown = 3 - (60 - self.dialogue_timer) // 20
            if countdown > 0:
                count_text = self.title_font.render(str(countdown), True, YELLOW)
                surface.blit(count_text, (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2))
        
        self.dialogue_timer -= 1
        if self.dialogue_timer <= 0:
            self.start_song(self.current_week, self.current_song_idx)
    
    def render_game_over(self, surface):
        """Render game over screen"""
        surface.fill((30, 0, 0))
        
        # Glitch effect
        if random.random() < 0.2:
            for _ in range(10):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                w = random.randint(50, 200)
                h = random.randint(5, 20)
                pygame.draw.rect(surface, (random.randint(50, 100), 0, 0), (x, y, w, h))
        
        # Game over text
        go_text = self.title_font.render("GAME OVER", True, RED)
        surface.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 200))
        
        # Stats
        stats = [
            f"Score: {self.score}",
            f"Max Combo: {self.max_combo}",
            f"Misses: {self.misses}",
            f"Accuracy: {self.calculate_accuracy():.1f}%"
        ]
        
        for i, stat in enumerate(stats):
            text = self.menu_font.render(stat, True, WHITE)
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 320 + i * 50))
        
        # Retry prompt
        hint = self.ui_font.render("Press ENTER to retry | ESC for menu", True, GRAY)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100))
    
    def render_week_complete(self, surface):
        """Render week complete screen"""
        # Background based on week
        if self.current_week == 0:
            surface.fill((100, 200, 100))
        elif self.current_week == 1:
            surface.fill((100, 100, 150))
        else:
            surface.fill((50, 0, 50))
        
        # Victory text
        if self.current_week < 2:
            title = "WEEK COMPLETE!"
            color = GREEN
        else:
            title = "Y̸O̷U̴ ̵S̷U̶R̵V̶I̷V̶E̷D̷.̵.̸.̵"
            color = RED
        
        title_text = self.title_font.render(title, True, color)
        surface.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 150))
        
        # Stats
        stats = [
            f"Final Score: {self.score}",
            f"Max Combo: {self.max_combo}",
            f"Total Misses: {self.misses}",
            f"Accuracy: {self.calculate_accuracy():.1f}%"
        ]
        
        for i, stat in enumerate(stats):
            text = self.menu_font.render(stat, True, WHITE)
            surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 280 + i * 50))
        
        # Special message for Week 3
        if self.current_week == 2:
            secret = self.small_font.render("Secret: Try the EX songs... if you dare", True, (150, 0, 0))
            surface.blit(secret, (SCREEN_WIDTH // 2 - secret.get_width() // 2, 550))
        
        # Continue prompt
        hint = self.ui_font.render("Press ENTER to continue", True, WHITE)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))
    
    def render_credits(self, surface):
        """Render credits screen"""
        surface.fill((20, 20, 40))
        
        title = self.title_font.render("CREDITS", True, WHITE)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        credits_list = [
            "FNF: Mario Forever - 3 Weeks of Corruption",
            "",
            "Created by Team Flames / Samsoft",
            "",
            "Inspired by:",
            "Friday Night Funkin' - Ninjamuffin99, Phantom Arcade,",
            "  evilsk8r, Kawai Sprite",
            "Mario Forever - Softendo",
            "Super Mario Bros - Nintendo",
            "",
            "Engine: Pygame",
            "",
            "This is a fan game made for fun!",
            "All characters belong to their respective owners.",
            "",
            "Thanks for playing!"
        ]
        
        for i, line in enumerate(credits_list):
            text = self.ui_font.render(line, True, WHITE if line else GRAY)
            surface.blit(text, (100, 130 + i * 35))
        
        hint = self.small_font.render("Press ESC to return", True, GRAY)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))
    
    def calculate_accuracy(self):
        """Calculate hit accuracy"""
        total = self.hits['sick'] + self.hits['good'] + self.hits['bad'] + self.misses
        if total == 0:
            return 100.0
        
        weighted = (self.hits['sick'] * 100 + self.hits['good'] * 75 + 
                   self.hits['bad'] * 25 + self.misses * 0)
        return weighted / total
    
    def apply_screen_effects(self, surface):
        """Apply post-processing effects"""
        # Screen shake
        if self.screen_shake > 0:
            offset_x = random.randint(-self.screen_shake, self.screen_shake)
            offset_y = random.randint(-self.screen_shake, self.screen_shake)
            self.screen_shake -= 1
            
            temp = surface.copy()
            surface.fill((0, 0, 0))
            surface.blit(temp, (offset_x, offset_y))
        
        # Corruption glitch effects (Week 2+)
        if self.corruption_level > 0 and self.state == GameState.PLAYING:
            if random.random() < self.corruption_level * 0.1:
                # Color channel shift
                offset = random.randint(2, 8)
                temp = surface.copy()
                surface.blit(temp, (offset, 0), special_flags=pygame.BLEND_RGB_ADD)
            
            if random.random() < self.corruption_level * 0.05:
                # Random pixel blocks
                for _ in range(int(self.corruption_level * 10)):
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.randint(0, SCREEN_HEIGHT)
                    w = random.randint(10, 50)
                    h = random.randint(5, 20)
                    color = (random.randint(0, 255), 0, 0)
                    pygame.draw.rect(surface, color, (x, y, w, h))
    
    def handle_input(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                if event.key == pygame.K_UP:
                    self.menu_selection = (self.menu_selection - 1) % len(self.menu_items)
                    self.menu_sound.play()
                elif event.key == pygame.K_DOWN:
                    self.menu_selection = (self.menu_selection + 1) % len(self.menu_items)
                    self.menu_sound.play()
                elif event.key == pygame.K_RETURN:
                    self.menu_sound.play()
                    if self.menu_selection == 0:  # Play
                        self.current_week = 0
                        self.current_song_idx = 0
                        self.current_song = ChartGenerator.generate_week1_song(0)
                        self.show_song_intro()
                    elif self.menu_selection == 1:  # Week Select
                        self.state = GameState.WEEK_SELECT
                        self.menu_selection = 0
                    elif self.menu_selection == 2:  # Credits
                        self.state = GameState.CREDITS
                    elif self.menu_selection == 3:  # Exit
                        pygame.quit()
                        exit()
            
            elif self.state == GameState.WEEK_SELECT:
                if event.key == pygame.K_UP:
                    self.menu_selection = (self.menu_selection - 1) % len(self.week_names)
                    self.menu_sound.play()
                elif event.key == pygame.K_DOWN:
                    self.menu_selection = (self.menu_selection + 1) % len(self.week_names)
                    self.menu_sound.play()
                elif event.key == pygame.K_RETURN:
                    self.menu_sound.play()
                    self.current_week = self.menu_selection
                    self.current_song_idx = 0
                    if self.current_week == 0:
                        self.current_song = ChartGenerator.generate_week1_song(0)
                    elif self.current_week == 1:
                        self.current_song = ChartGenerator.generate_week2_song(0)
                    else:
                        self.current_song = ChartGenerator.generate_week3_song(0)
                    self.show_song_intro()
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                    self.menu_selection = 0
            
            elif self.state == GameState.PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED
                elif event.key in self.key_bindings:
                    direction = self.key_bindings[event.key]
                    self.player_strum.press_states[direction] = True
                    
                    # Check for hit
                    result = self.check_note_hit(direction)
                    if result:
                        note, rating = result
                        self.process_hit(note, rating)
            
            elif self.state == GameState.PAUSED:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.PLAYING
                elif event.key == pygame.K_RETURN:
                    self.state = GameState.MENU
                    self.menu_selection = 0
            
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_RETURN:
                    # Retry
                    self.start_song(self.current_week, self.current_song_idx)
                elif event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                    self.menu_selection = 0
            
            elif self.state == GameState.WEEK_COMPLETE:
                if event.key == pygame.K_RETURN:
                    if self.current_week < 2:
                        # Next week
                        self.current_week += 1
                        self.current_song_idx = 0
                        if self.current_week == 1:
                            self.current_song = ChartGenerator.generate_week2_song(0)
                        else:
                            self.current_song = ChartGenerator.generate_week3_song(0)
                        self.show_song_intro()
                    else:
                        # Game complete, return to menu
                        self.state = GameState.MENU
                        self.menu_selection = 0
            
            elif self.state == GameState.CREDITS:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                    self.menu_selection = 0
        
        elif event.type == pygame.KEYUP:
            if event.key in self.key_bindings:
                direction = self.key_bindings[event.key]
                self.player_strum.press_states[direction] = False
    
    def update(self):
        """Update game state"""
        self.frame_count += 1
        
        if self.state == GameState.PLAYING:
            self.update_notes()
    
    def render(self):
        """Render current frame"""
        surface = self.screen
        
        if self.state == GameState.MENU:
            self.render_menu(surface)
        
        elif self.state == GameState.WEEK_SELECT:
            self.render_week_select(surface)
        
        elif self.state == GameState.SONG_INTRO:
            self.render_song_intro(surface)
        
        elif self.state == GameState.PLAYING:
            # Background
            if self.current_week == 0:
                BackgroundRenderer.render_week1(surface, self.frame_count)
            elif self.current_week == 1:
                BackgroundRenderer.render_week2(surface, self.frame_count)
            else:
                BackgroundRenderer.render_week3(surface, self.frame_count, self.corruption_level)
            
            # Characters
            self.render_characters(surface)
            
            # Strum lines
            self.opponent_strum.render(surface)
            self.player_strum.render(surface, self.corruption_level)
            
            # Notes
            self.render_notes(surface)
            
            # UI
            self.render_ui(surface)
            
            # Apply effects
            self.apply_screen_effects(surface)
        
        elif self.state == GameState.PAUSED:
            # Render game state behind pause
            if self.current_week == 0:
                BackgroundRenderer.render_week1(surface, self.frame_count)
            elif self.current_week == 1:
                BackgroundRenderer.render_week2(surface, self.frame_count)
            else:
                BackgroundRenderer.render_week3(surface, self.frame_count)
            
            # Darken
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            surface.blit(overlay, (0, 0))
            
            # Pause text
            pause_text = self.title_font.render("PAUSED", True, WHITE)
            surface.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 
                                     SCREEN_HEIGHT // 2 - 50))
            
            hint = self.ui_font.render("ESC to resume | ENTER for menu", True, GRAY)
            surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 
                               SCREEN_HEIGHT // 2 + 50))
        
        elif self.state == GameState.GAME_OVER:
            self.render_game_over(surface)
        
        elif self.state == GameState.WEEK_COMPLETE:
            self.render_week_complete(surface)
        
        elif self.state == GameState.CREDITS:
            self.render_credits(surface)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.handle_input(event)
            
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    """Entry point"""
    print("=" * 50)
    print("FNF: Mario Forever - 3 Weeks of Corruption")
    print("Team Flames / Samsoft")
    print("=" * 50)
    print()
    print("Controls:")
    print("  Arrow Keys or WASD - Hit notes")
    print("  Enter - Select/Confirm")
    print("  ESC - Pause/Back")
    print()
    print("Starting game...")
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
