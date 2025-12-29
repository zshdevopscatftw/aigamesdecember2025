#!/usr/bin/env python3
"""
MEGA CAT 2 — AUTHENTIC MM2 RECREATION
=====================================
Featuring SAMSOFT SOUND MEDIA ENGINE v2.0
All music synthesized in real-time - no external files needed!

Controls:
  Arrow Keys  - Move
  Space       - Jump  
  X           - Shoot
  C           - Cycle Weapons
  Enter       - Select/Confirm
  Esc         - Pause
  M           - Toggle Music

nya~ Team Flames x Samsoft 2025
"""

import pygame
import sys
import random
import math
import array
import threading
import time

# =============================================================================
# CONFIGURATION
# =============================================================================
SCREEN_W, SCREEN_H = 256, 240
SCALE = 3
FPS = 60
TILE = 16

# Physics
GRAVITY = 0.25
TERMINAL_VEL = 5.0
PLAYER_SPEED = 1.5
JUMP_VELOCITY = -4.8
PLAYER_ACCEL = 0.5

# =============================================================================
# NES COLOR PALETTE
# =============================================================================
BLACK = (0, 0, 0)
WHITE = (252, 252, 252)
GRAY1 = (188, 188, 188)
GRAY2 = (124, 124, 124)
GRAY3 = (80, 80, 80)
DKGRAY = (44, 44, 44)

BLUE1 = (0, 120, 248)
BLUE2 = (0, 88, 248)
BLUE3 = (0, 64, 184)
LTBLUE = (60, 188, 252)
CYAN = (0, 232, 216)
DKCYAN = (0, 168, 168)

RED = (248, 56, 0)
DKRED = (168, 16, 0)
PINK = (248, 120, 188)
LTPINK = (252, 160, 200)

GREEN = (0, 168, 0)
LTGREEN = (88, 216, 84)
DKGREEN = (0, 120, 0)

YELLOW = (248, 216, 0)
ORANGE = (248, 120, 88)
DKORANGE = (228, 92, 16)
BROWN = (172, 124, 0)

PURPLE = (152, 78, 200)
DKPURPLE = (104, 68, 152)

SKIN = (252, 188, 148)

# =============================================================================
# GAME STATES
# =============================================================================
STATE_TITLE_INTRO = 0
STATE_TITLE_MENU = 1
STATE_STAGE_SELECT = 2
STATE_READY = 3
STATE_PLAYING = 4
STATE_BOSS_INTRO = 5
STATE_BOSS_FIGHT = 6
STATE_WEAPON_GET = 7
STATE_PAUSE = 8
STATE_GAME_OVER = 9

# =============================================================================
# ROBOT MASTER DATA
# =============================================================================
ROBOT_MASTERS = [
    {"name": "BUBBLE MAN", "color1": LTGREEN, "color2": DKGREEN, 
     "weapon": "BUBBLE LEAD", "weapon_short": "B", "weakness": 5,
     "stage_bg": BLUE3, "stage_fg": DKCYAN},
    {"name": "AIR MAN", "color1": LTBLUE, "color2": BLUE2,
     "weapon": "AIR SHOOTER", "weapon_short": "A", "weakness": 4,
     "stage_bg": (40, 60, 100), "stage_fg": GRAY1},
    {"name": "QUICK MAN", "color1": RED, "color2": DKRED,
     "weapon": "QUICK BOOMERANG", "weapon_short": "Q", "weakness": 6,
     "stage_bg": DKRED, "stage_fg": ORANGE},
    {"name": "HEAT MAN", "color1": ORANGE, "color2": DKORANGE,
     "weapon": "ATOMIC FIRE", "weapon_short": "H", "weakness": 0,
     "stage_bg": (80, 32, 0), "stage_fg": ORANGE},
    {"name": "WOOD MAN", "color1": DKGREEN, "color2": BROWN,
     "weapon": "LEAF SHIELD", "weapon_short": "W", "weakness": 3,
     "stage_bg": DKGREEN, "stage_fg": BROWN},
    {"name": "METAL MAN", "color1": DKORANGE, "color2": GRAY2,
     "weapon": "METAL BLADE", "weapon_short": "M", "weakness": 5,
     "stage_bg": DKGRAY, "stage_fg": ORANGE},
    {"name": "FLASH MAN", "color1": LTBLUE, "color2": PURPLE,
     "weapon": "TIME STOPPER", "weapon_short": "F", "weakness": 5,
     "stage_bg": DKPURPLE, "stage_fg": PINK},
    {"name": "CRASH MAN", "color1": DKORANGE, "color2": GRAY3,
     "weapon": "CRASH BOMBER", "weapon_short": "C", "weakness": 1,
     "stage_bg": GRAY3, "stage_fg": DKORANGE},
]

WEAPON_DMG = [
    [1,1,1,1,1,1,1,1], [0,1,2,4,1,1,2,1], [2,1,0,1,4,1,0,4],
    [1,1,1,2,1,1,1,1], [1,2,1,0,1,1,2,1], [4,0,1,1,0,1,1,1],
    [2,2,4,2,4,14,4,2], [0,0,0,0,0,0,0,0], [1,1,1,1,1,1,2,0],
]

# =============================================================================
# PYGAME INIT
# =============================================================================
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=8, buffer=512)
screen = pygame.display.set_mode((SCREEN_W * SCALE, SCREEN_H * SCALE))
pygame.display.set_caption("Mega Cat 2 - Samsoft Sound Engine")
clock = pygame.time.Clock()
canvas = pygame.Surface((SCREEN_W, SCREEN_H))

# =============================================================================
# SAMSOFT SOUND MEDIA ENGINE v2.0
# =============================================================================
class SamsoftSoundEngine:
    """
    SAMSOFT SOUND MEDIA ENGINE v2.0
    ===============================
    Real-time chiptune synthesis engine
    Supports: Square, Triangle, Noise, Pulse waves
    3-channel playback with bass + melody + harmony
    """
    
    # Note frequencies (A4 = 440Hz standard)
    NOTE_FREQ = {}
    
    def __init__(self):
        self.sample_rate = 22050
        self.enabled = True
        self.playing = False
        self.current_track = None
        self.position = 0
        self.tick = 0
        self.tempo = 150
        
        # Sound channels
        self.channels = [
            pygame.mixer.Channel(0),  # Melody (Square)
            pygame.mixer.Channel(1),  # Harmony (Square)
            pygame.mixer.Channel(2),  # Bass (Triangle)
        ]
        
        # Pre-generate note table
        self._build_note_table()
        
        # Pre-generate all note sounds
        self.sounds = {}
        self._generate_sounds()
        
        # Track data
        self.tracks = self._define_tracks()
        
        # Playback thread
        self.thread = None
        self.stop_flag = False
    
    def _build_note_table(self):
        """Build frequency table for all notes"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        a4_freq = 440.0
        
        for octave in range(1, 8):
            for i, note in enumerate(notes):
                # Calculate semitones from A4
                semitones = (octave - 4) * 12 + (i - 9)
                freq = a4_freq * (2 ** (semitones / 12))
                self.NOTE_FREQ[f"{note}{octave}"] = freq
        
        # Add flat note aliases
        flats = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
        for octave in range(1, 8):
            for flat, sharp in flats.items():
                self.NOTE_FREQ[f"{flat}{octave}"] = self.NOTE_FREQ[f"{sharp}{octave}"]
    
    def _generate_wave(self, freq, duration, wave_type='square', volume=0.3):
        """Generate a waveform"""
        n_samples = int(self.sample_rate * duration)
        buf = array.array('h', [0] * (n_samples * 2))
        
        for i in range(n_samples):
            t = i / self.sample_rate
            
            if wave_type == 'square':
                # 50% duty cycle square wave
                val = volume if (int(t * freq * 2) % 2) else -volume
            elif wave_type == 'square25':
                # 25% duty cycle (pulse)
                val = volume if ((t * freq) % 1.0) < 0.25 else -volume
            elif wave_type == 'triangle':
                # Triangle wave
                phase = (t * freq) % 1.0
                val = volume * (4 * abs(phase - 0.5) - 1)
            elif wave_type == 'noise':
                # Noise
                val = volume * random.uniform(-1, 1)
            else:
                val = 0
            
            # Envelope - quick attack, sustain, release at end
            env = 1.0
            attack = int(n_samples * 0.02)
            release = int(n_samples * 0.1)
            if i < attack:
                env = i / attack
            elif i > n_samples - release:
                env = (n_samples - i) / release
            
            sample = int(val * env * 32767)
            sample = max(-32767, min(32767, sample))
            buf[i * 2] = sample
            buf[i * 2 + 1] = sample
        
        return pygame.mixer.Sound(buffer=buf.tobytes())
    
    def _generate_sounds(self):
        """Pre-generate all note sounds"""
        durations = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
        
        for note, freq in self.NOTE_FREQ.items():
            for dur in durations:
                # Melody (square)
                key = f"{note}_{dur}_sq"
                try:
                    self.sounds[key] = self._generate_wave(freq, dur, 'square', 0.2)
                except:
                    pass
                
                # Bass (triangle) - only for low notes
                if any(c.isdigit() and int(c) <= 3 for c in note):
                    key = f"{note}_{dur}_tri"
                    try:
                        self.sounds[key] = self._generate_wave(freq, dur, 'triangle', 0.25)
                    except:
                        pass
        
        # Rest sound (silence)
        self.sounds['rest'] = self._generate_wave(1, 0.1, 'square', 0)
    
    def _define_tracks(self):
        """Define all music tracks with authentic MM2-style melodies"""
        
        # Note duration constants (in beats)
        W = 4    # Whole
        H = 2    # Half
        Q = 1    # Quarter
        E = 0.5  # Eighth
        S = 0.25 # Sixteenth
        
        tracks = {
            # =========================================================
            # TITLE THEME - Iconic MM2 opening
            # =========================================================
            'title': {
                'tempo': 140,
                'melody': [
                    # Main riff
                    ('E5', E), ('E5', E), ('E5', E), ('R', E),
                    ('E5', E), ('E5', E), ('E5', E), ('R', E),
                    ('E5', E), ('G5', E), ('C5', E), ('D5', E),
                    ('E5', H),
                    ('D5', E), ('D5', E), ('D5', E), ('R', E),
                    ('D5', E), ('D5', E), ('D5', E), ('R', E),
                    ('D5', E), ('F5', E), ('B4', E), ('C5', E),
                    ('D5', H),
                    # Repeat with variation
                    ('C5', E), ('E5', E), ('G5', E), ('C6', E),
                    ('B5', E), ('G5', E), ('E5', E), ('G5', E),
                    ('A5', Q), ('G5', Q), ('E5', Q), ('C5', Q),
                    ('D5', H), ('R', H),
                ],
                'bass': [
                    ('C2', Q), ('C3', Q), ('C2', Q), ('C3', Q),
                    ('C2', Q), ('C3', Q), ('G2', Q), ('G3', Q),
                    ('G2', Q), ('G3', Q), ('G2', Q), ('G3', Q),
                    ('G2', Q), ('G3', Q), ('C2', Q), ('C3', Q),
                    ('A2', Q), ('A3', Q), ('A2', Q), ('A3', Q),
                    ('F2', Q), ('F3', Q), ('G2', Q), ('G3', Q),
                ],
            },
            
            # =========================================================
            # STAGE SELECT
            # =========================================================
            'stage_select': {
                'tempo': 130,
                'melody': [
                    ('A4', E), ('C5', E), ('E5', E), ('A5', E),
                    ('G5', E), ('E5', E), ('C5', E), ('E5', E),
                    ('F5', E), ('A5', E), ('C6', E), ('A5', E),
                    ('G5', E), ('E5', E), ('D5', E), ('E5', E),
                    ('A4', E), ('C5', E), ('E5', E), ('A5', E),
                    ('B5', E), ('A5', E), ('G5', E), ('E5', E),
                    ('F5', Q), ('E5', Q), ('D5', Q), ('C5', Q),
                    ('A4', H), ('R', H),
                ],
                'bass': [
                    ('A2', Q), ('A2', Q), ('E2', Q), ('E2', Q),
                    ('F2', Q), ('F2', Q), ('C2', Q), ('C2', Q),
                    ('A2', Q), ('A2', Q), ('E2', Q), ('E2', Q),
                    ('F2', Q), ('G2', Q), ('A2', H),
                ],
            },
            
            # =========================================================
            # BUBBLE MAN STAGE
            # =========================================================
            'bubble': {
                'tempo': 115,
                'melody': [
                    ('E4', E), ('G4', E), ('B4', E), ('E5', E),
                    ('D5', E), ('B4', E), ('G4', E), ('B4', E),
                    ('C5', E), ('E5', E), ('G5', E), ('E5', E),
                    ('D5', E), ('B4', E), ('A4', E), ('B4', E),
                    ('E4', E), ('G4', E), ('B4', E), ('E5', E),
                    ('F#5', E), ('E5', E), ('D5', E), ('B4', E),
                    ('C5', Q), ('B4', Q), ('A4', Q), ('G4', Q),
                    ('E4', H), ('R', H),
                ],
                'bass': [
                    ('E2', Q), ('E2', Q), ('B2', Q), ('B2', Q),
                    ('C2', Q), ('C2', Q), ('G2', Q), ('G2', Q),
                    ('E2', Q), ('E2', Q), ('D2', Q), ('D2', Q),
                    ('C2', Q), ('B2', Q), ('E2', H),
                ],
            },
            
            # =========================================================
            # AIR MAN STAGE - Famous "I can't defeat Air Man"
            # =========================================================
            'air': {
                'tempo': 155,
                'melody': [
                    # Main theme
                    ('A5', E), ('A5', E), ('G5', E), ('A5', E),
                    ('E5', Q), ('R', E), ('E5', E),
                    ('F5', E), ('F5', E), ('E5', E), ('F5', E),
                    ('D5', Q), ('R', E), ('D5', E),
                    ('E5', E), ('E5', E), ('D5', E), ('E5', E),
                    ('C5', E), ('D5', E), ('E5', E), ('F5', E),
                    ('G5', Q), ('F5', Q), ('E5', Q), ('D5', Q),
                    # Second part
                    ('C5', E), ('E5', E), ('G5', E), ('C6', E),
                    ('B5', E), ('G5', E), ('E5', E), ('G5', E),
                    ('A5', E), ('G5', E), ('F5', E), ('E5', E),
                    ('D5', Q), ('C5', Q), ('D5', H),
                ],
                'bass': [
                    ('A2', Q), ('E3', Q), ('A2', Q), ('E3', Q),
                    ('D2', Q), ('A2', Q), ('D2', Q), ('A2', Q),
                    ('C2', Q), ('G2', Q), ('C2', Q), ('G2', Q),
                    ('G2', Q), ('D2', Q), ('G2', H),
                    ('C2', Q), ('G2', Q), ('C2', Q), ('G2', Q),
                    ('F2', Q), ('C2', Q), ('G2', H),
                ],
            },
            
            # =========================================================
            # QUICK MAN STAGE - Fast and intense
            # =========================================================
            'quick': {
                'tempo': 180,
                'melody': [
                    ('A5', S), ('A5', S), ('G5', S), ('A5', S),
                    ('B5', S), ('A5', S), ('G5', S), ('E5', E),
                    ('F5', S), ('F5', S), ('E5', S), ('F5', S),
                    ('G5', S), ('F5', S), ('E5', S), ('D5', E),
                    ('E5', S), ('E5', S), ('D5', S), ('E5', S),
                    ('F5', S), ('E5', S), ('D5', S), ('C5', E),
                    ('D5', E), ('E5', E), ('F5', E), ('G5', E),
                    ('A5', Q), ('R', Q),
                    # Repeat variation
                    ('A5', E), ('C6', E), ('A5', E), ('G5', E),
                    ('F5', E), ('G5', E), ('A5', E), ('G5', E),
                    ('F5', E), ('E5', E), ('D5', E), ('E5', E),
                    ('A4', H), ('R', H),
                ],
                'bass': [
                    ('A2', E), ('A2', E), ('E2', E), ('E2', E),
                    ('D2', E), ('D2', E), ('A2', E), ('A2', E),
                    ('C2', E), ('C2', E), ('G2', E), ('G2', E),
                    ('F2', E), ('G2', E), ('A2', Q),
                    ('A2', E), ('E2', E), ('A2', E), ('E2', E),
                    ('D2', E), ('A2', E), ('A2', Q),
                ],
            },
            
            # =========================================================
            # HEAT MAN STAGE
            # =========================================================
            'heat': {
                'tempo': 125,
                'melody': [
                    ('D5', E), ('F5', E), ('A5', E), ('D6', E),
                    ('C6', E), ('A5', E), ('F5', E), ('A5', E),
                    ('Bb5', E), ('D6', E), ('F6', E), ('D6', E),
                    ('C6', E), ('A5', E), ('G5', E), ('A5', E),
                    ('D5', E), ('F5', E), ('A5', E), ('D6', E),
                    ('E6', E), ('D6', E), ('C6', E), ('A5', E),
                    ('Bb5', Q), ('A5', Q), ('G5', Q), ('F5', Q),
                    ('D5', H), ('R', H),
                ],
                'bass': [
                    ('D2', Q), ('D2', Q), ('A2', Q), ('A2', Q),
                    ('Bb2', Q), ('Bb2', Q), ('F2', Q), ('F2', Q),
                    ('D2', Q), ('D2', Q), ('C2', Q), ('C2', Q),
                    ('Bb2', Q), ('A2', Q), ('D2', H),
                ],
            },
            
            # =========================================================
            # WOOD MAN STAGE
            # =========================================================
            'wood': {
                'tempo': 120,
                'melody': [
                    ('G4', E), ('B4', E), ('D5', E), ('G5', E),
                    ('F#5', E), ('D5', E), ('B4', E), ('D5', E),
                    ('E5', E), ('G5', E), ('B5', E), ('G5', E),
                    ('F#5', E), ('D5', E), ('C5', E), ('D5', E),
                    ('G4', E), ('B4', E), ('D5', E), ('G5', E),
                    ('A5', E), ('G5', E), ('F#5', E), ('D5', E),
                    ('E5', Q), ('D5', Q), ('C5', Q), ('B4', Q),
                    ('G4', H), ('R', H),
                ],
                'bass': [
                    ('G2', Q), ('G2', Q), ('D2', Q), ('D2', Q),
                    ('E2', Q), ('E2', Q), ('B2', Q), ('B2', Q),
                    ('G2', Q), ('G2', Q), ('F#2', Q), ('F#2', Q),
                    ('E2', Q), ('D2', Q), ('G2', H),
                ],
            },
            
            # =========================================================
            # METAL MAN STAGE - Driving beat
            # =========================================================
            'metal': {
                'tempo': 160,
                'melody': [
                    ('E5', E), ('E5', S), ('E5', S), ('D5', E), ('E5', E),
                    ('G5', E), ('G5', S), ('G5', S), ('F5', E), ('E5', E),
                    ('D5', E), ('D5', S), ('D5', S), ('C5', E), ('D5', E),
                    ('E5', E), ('D5', E), ('C5', E), ('B4', E),
                    ('E5', E), ('E5', S), ('E5', S), ('D5', E), ('E5', E),
                    ('A5', E), ('G5', E), ('E5', E), ('G5', E),
                    ('F5', Q), ('E5', Q), ('D5', Q), ('C5', Q),
                    ('E5', H), ('R', H),
                ],
                'bass': [
                    ('E2', E), ('E2', E), ('E2', E), ('E2', E),
                    ('G2', E), ('G2', E), ('G2', E), ('G2', E),
                    ('D2', E), ('D2', E), ('D2', E), ('D2', E),
                    ('E2', E), ('D2', E), ('C2', E), ('B1', E),
                    ('E2', E), ('E2', E), ('A2', E), ('A2', E),
                    ('F2', E), ('E2', E), ('D2', E), ('C2', E),
                    ('E2', H), ('R', H),
                ],
            },
            
            # =========================================================
            # FLASH MAN STAGE
            # =========================================================
            'flash': {
                'tempo': 135,
                'melody': [
                    ('B4', E), ('D5', E), ('F#5', E), ('B5', E),
                    ('A5', E), ('F#5', E), ('D5', E), ('F#5', E),
                    ('G5', E), ('B5', E), ('D6', E), ('B5', E),
                    ('A5', E), ('F#5', E), ('E5', E), ('F#5', E),
                    ('B4', E), ('D5', E), ('F#5', E), ('B5', E),
                    ('C6', E), ('B5', E), ('A5', E), ('F#5', E),
                    ('G5', Q), ('F#5', Q), ('E5', Q), ('D5', Q),
                    ('B4', H), ('R', H),
                ],
                'bass': [
                    ('B2', Q), ('B2', Q), ('F#2', Q), ('F#2', Q),
                    ('G2', Q), ('G2', Q), ('D2', Q), ('D2', Q),
                    ('B2', Q), ('B2', Q), ('A2', Q), ('A2', Q),
                    ('G2', Q), ('F#2', Q), ('B2', H),
                ],
            },
            
            # =========================================================
            # CRASH MAN STAGE
            # =========================================================
            'crash': {
                'tempo': 145,
                'melody': [
                    ('A4', E), ('C5', E), ('E5', E), ('A5', E),
                    ('G5', E), ('E5', E), ('C5', E), ('E5', E),
                    ('F5', E), ('A5', E), ('C6', E), ('A5', E),
                    ('G5', E), ('E5', E), ('D5', E), ('E5', E),
                    ('A4', E), ('C5', E), ('E5', E), ('A5', E),
                    ('B5', E), ('A5', E), ('G5', E), ('E5', E),
                    ('F5', Q), ('E5', Q), ('D5', Q), ('C5', Q),
                    ('A4', H), ('R', H),
                ],
                'bass': [
                    ('A2', Q), ('A2', Q), ('E2', Q), ('E2', Q),
                    ('F2', Q), ('F2', Q), ('C2', Q), ('C2', Q),
                    ('A2', Q), ('A2', Q), ('G2', Q), ('G2', Q),
                    ('F2', Q), ('E2', Q), ('A2', H),
                ],
            },
            
            # =========================================================
            # BOSS BATTLE - Intense!
            # =========================================================
            'boss': {
                'tempo': 175,
                'melody': [
                    ('E5', S), ('E5', S), ('E5', S), ('E5', S),
                    ('E5', S), ('D5', S), ('E5', E),
                    ('E5', S), ('E5', S), ('E5', S), ('E5', S),
                    ('E5', S), ('F5', S), ('E5', E),
                    ('E5', S), ('E5', S), ('E5', S), ('G5', S),
                    ('F5', S), ('E5', S), ('D5', E),
                    ('D5', S), ('D5', S), ('D5', S), ('D5', S),
                    ('D5', S), ('E5', S), ('D5', E),
                    # Part 2
                    ('C5', E), ('E5', E), ('G5', E), ('C6', E),
                    ('B5', E), ('A5', E), ('G5', E), ('E5', E),
                    ('F5', E), ('A5', E), ('C6', E), ('A5', E),
                    ('G5', Q), ('E5', Q),
                ],
                'bass': [
                    ('E2', E), ('E2', E), ('E2', E), ('E2', E),
                    ('D2', E), ('D2', E), ('D2', E), ('D2', E),
                    ('C2', E), ('C2', E), ('C2', E), ('C2', E),
                    ('B1', E), ('B1', E), ('C2', E), ('D2', E),
                    ('E2', E), ('E2', E), ('E2', E), ('E2', E),
                    ('F2', E), ('F2', E), ('G2', E), ('E2', E),
                ],
            },
            
            # =========================================================
            # VICTORY / WEAPON GET
            # =========================================================
            'victory': {
                'tempo': 130,
                'melody': [
                    ('C5', E), ('E5', E), ('G5', E), ('C6', Q),
                    ('R', E), ('B5', E), ('C6', E),
                    ('G5', E), ('C6', E), ('E6', E), ('G6', Q),
                    ('R', E), ('E6', E), ('G6', E),
                    ('C6', Q), ('G5', Q), ('E5', Q), ('C5', Q),
                    ('D5', E), ('E5', E), ('F5', E), ('G5', E),
                    ('C6', H), ('R', H),
                ],
                'bass': [
                    ('C3', Q), ('G3', Q), ('C3', Q), ('G3', Q),
                    ('C3', Q), ('G3', Q), ('C3', Q), ('G3', Q),
                    ('F3', Q), ('C3', Q), ('G3', Q), ('C3', Q),
                    ('C3', H), ('R', H),
                ],
            },
            
            # =========================================================
            # GAME OVER
            # =========================================================
            'gameover': {
                'tempo': 75,
                'melody': [
                    ('E4', Q), ('D4', Q), ('C4', Q), ('B3', H),
                    ('R', Q), ('A3', Q), ('G3', H), ('R', H),
                ],
                'bass': [
                    ('E2', Q), ('D2', Q), ('C2', Q), ('B1', H),
                    ('R', Q), ('A1', Q), ('G1', H), ('R', H),
                ],
            },
        }
        
        return tracks
    
    def _get_sound(self, note, duration, wave='sq'):
        """Get pre-generated sound for a note"""
        if note == 'R' or note == 'rest':
            return None
        
        # Find closest pre-generated duration
        dur_secs = duration * 60 / self.tempo
        available = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
        closest = min(available, key=lambda x: abs(x - dur_secs))
        
        key = f"{note}_{closest}_{wave}"
        return self.sounds.get(key)
    
    def _playback_loop(self):
        """Main playback loop (runs in thread)"""
        while not self.stop_flag and self.playing:
            if not self.current_track or self.current_track not in self.tracks:
                time.sleep(0.1)
                continue
            
            track = self.tracks[self.current_track]
            self.tempo = track['tempo']
            melody = track['melody']
            bass = track['bass']
            
            beat_duration = 60.0 / self.tempo
            
            melody_pos = 0
            bass_pos = 0
            melody_time = 0
            bass_time = 0
            
            while not self.stop_flag and self.playing and self.current_track:
                current_time = time.time()
                
                # Play melody
                if melody_pos < len(melody):
                    note, dur = melody[melody_pos]
                    if time.time() >= melody_time:
                        sound = self._get_sound(note, dur, 'sq')
                        if sound and self.enabled:
                            try:
                                self.channels[0].play(sound)
                            except:
                                pass
                        melody_time = time.time() + dur * beat_duration
                        melody_pos += 1
                else:
                    melody_pos = 0
                    melody_time = time.time()
                
                # Play bass
                if bass_pos < len(bass):
                    note, dur = bass[bass_pos]
                    if time.time() >= bass_time:
                        sound = self._get_sound(note, dur, 'tri')
                        if sound and self.enabled:
                            try:
                                self.channels[2].play(sound)
                            except:
                                pass
                        bass_time = time.time() + dur * beat_duration
                        bass_pos += 1
                else:
                    bass_pos = 0
                    bass_time = time.time()
                
                time.sleep(0.01)
    
    def play(self, track_name):
        """Start playing a track"""
        if track_name == self.current_track and self.playing:
            return
        
        self.stop()
        
        if track_name not in self.tracks:
            return
        
        self.current_track = track_name
        self.playing = True
        self.stop_flag = False
        
        self.thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop playback"""
        self.stop_flag = True
        self.playing = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        
        for ch in self.channels:
            try:
                ch.stop()
            except:
                pass
        
        self.current_track = None
    
    def toggle(self):
        """Toggle music on/off"""
        self.enabled = not self.enabled
        if not self.enabled:
            for ch in self.channels:
                try:
                    ch.stop()
                except:
                    pass

# Global sound engine
music = SamsoftSoundEngine()

# Stage track mapping
STAGE_TRACKS = ['bubble', 'air', 'quick', 'heat', 'wood', 'metal', 'flash', 'crash']

# =============================================================================
# SOUND EFFECTS
# =============================================================================
def synth_sfx(freq, dur, wave="square", vol=0.2, decay=0.7):
    sr = 22050
    n = int(sr * dur)
    if n < 1:
        return None
    buf = array.array('h', [0] * n * 2)
    
    for i in range(n):
        t = i / sr
        if wave == "square":
            v = vol if (int(t * freq * 2) % 2) else -vol
        elif wave == "triangle":
            p = (t * freq) % 1.0
            v = vol * (4.0 * abs(p - 0.5) - 1.0)
        elif wave == "noise":
            v = vol * random.uniform(-1, 1)
        else:
            v = vol * math.sin(2 * math.pi * freq * t)
        
        env = max(0, 1.0 - (i / n) * decay)
        sample = int(v * env * 32767)
        buf[i*2] = max(-32767, min(32767, sample))
        buf[i*2+1] = buf[i*2]
    
    try:
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except:
        return None

SFX = {}
def init_sfx():
    global SFX
    SFX = {
        "shoot": synth_sfx(880, 0.05, "square", 0.15),
        "hit": synth_sfx(180, 0.08, "square", 0.2),
        "enemy_hit": synth_sfx(300, 0.06, "noise", 0.15),
        "boss_hit": synth_sfx(120, 0.12, "square", 0.25),
        "jump": synth_sfx(500, 0.03, "triangle", 0.12),
        "death": synth_sfx(200, 0.5, "square", 0.25),
        "menu_move": synth_sfx(440, 0.03, "square", 0.1),
        "menu_select": synth_sfx(660, 0.08, "square", 0.15),
        "pause": synth_sfx(220, 0.1, "square", 0.15),
        "ready": synth_sfx(330, 0.3, "triangle", 0.15),
        "boss_door": synth_sfx(100, 0.3, "square", 0.2),
    }
init_sfx()

def play_sfx(name):
    if name in SFX and SFX[name]:
        try:
            SFX[name].play()
        except:
            pass

# =============================================================================
# BITMAP FONT
# =============================================================================
FONT = {}
def init_font():
    glyphs = {
        'A': [0x18,0x3C,0x66,0x66,0x7E,0x66,0x66,0x00],
        'B': [0x7C,0x66,0x66,0x7C,0x66,0x66,0x7C,0x00],
        'C': [0x3C,0x66,0x60,0x60,0x60,0x66,0x3C,0x00],
        'D': [0x7C,0x66,0x66,0x66,0x66,0x66,0x7C,0x00],
        'E': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x7E,0x00],
        'F': [0x7E,0x60,0x60,0x7C,0x60,0x60,0x60,0x00],
        'G': [0x3C,0x66,0x60,0x6E,0x66,0x66,0x3E,0x00],
        'H': [0x66,0x66,0x66,0x7E,0x66,0x66,0x66,0x00],
        'I': [0x3C,0x18,0x18,0x18,0x18,0x18,0x3C,0x00],
        'J': [0x1E,0x0C,0x0C,0x0C,0x0C,0x6C,0x38,0x00],
        'K': [0x66,0x6C,0x78,0x70,0x78,0x6C,0x66,0x00],
        'L': [0x60,0x60,0x60,0x60,0x60,0x60,0x7E,0x00],
        'M': [0x63,0x77,0x7F,0x6B,0x63,0x63,0x63,0x00],
        'N': [0x66,0x76,0x7E,0x7E,0x6E,0x66,0x66,0x00],
        'O': [0x3C,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
        'P': [0x7C,0x66,0x66,0x7C,0x60,0x60,0x60,0x00],
        'Q': [0x3C,0x66,0x66,0x66,0x6A,0x6C,0x36,0x00],
        'R': [0x7C,0x66,0x66,0x7C,0x6C,0x66,0x66,0x00],
        'S': [0x3C,0x66,0x60,0x3C,0x06,0x66,0x3C,0x00],
        'T': [0x7E,0x18,0x18,0x18,0x18,0x18,0x18,0x00],
        'U': [0x66,0x66,0x66,0x66,0x66,0x66,0x3C,0x00],
        'V': [0x66,0x66,0x66,0x66,0x66,0x3C,0x18,0x00],
        'W': [0x63,0x63,0x63,0x6B,0x7F,0x77,0x63,0x00],
        'X': [0x66,0x66,0x3C,0x18,0x3C,0x66,0x66,0x00],
        'Y': [0x66,0x66,0x66,0x3C,0x18,0x18,0x18,0x00],
        'Z': [0x7E,0x06,0x0C,0x18,0x30,0x60,0x7E,0x00],
        '0': [0x3C,0x66,0x6E,0x7E,0x76,0x66,0x3C,0x00],
        '1': [0x18,0x38,0x18,0x18,0x18,0x18,0x7E,0x00],
        '2': [0x3C,0x66,0x06,0x0C,0x18,0x30,0x7E,0x00],
        '3': [0x3C,0x66,0x06,0x1C,0x06,0x66,0x3C,0x00],
        '4': [0x0C,0x1C,0x3C,0x6C,0x7E,0x0C,0x0C,0x00],
        '5': [0x7E,0x60,0x7C,0x06,0x06,0x66,0x3C,0x00],
        '6': [0x1C,0x30,0x60,0x7C,0x66,0x66,0x3C,0x00],
        '7': [0x7E,0x06,0x0C,0x18,0x30,0x30,0x30,0x00],
        '8': [0x3C,0x66,0x66,0x3C,0x66,0x66,0x3C,0x00],
        '9': [0x3C,0x66,0x66,0x3E,0x06,0x0C,0x38,0x00],
        ' ': [0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
        '-': [0x00,0x00,0x00,0x7E,0x00,0x00,0x00,0x00],
        '.': [0x00,0x00,0x00,0x00,0x00,0x18,0x18,0x00],
        '!': [0x18,0x18,0x18,0x18,0x18,0x00,0x18,0x00],
        '>': [0x60,0x30,0x18,0x0C,0x18,0x30,0x60,0x00],
    }
    for c, data in glyphs.items():
        FONT[c] = data
init_font()

def draw_char(surf, ch, x, y, color):
    ch = ch.upper()
    if ch not in FONT:
        return
    for row, bits in enumerate(FONT[ch]):
        for col in range(8):
            if bits & (0x80 >> col):
                px, py = int(x + col), int(y + row)
                if 0 <= px < SCREEN_W and 0 <= py < SCREEN_H:
                    surf.set_at((px, py), color)

def draw_text(surf, text, x, y, color=WHITE, center=False):
    if center:
        x = (SCREEN_W - len(text) * 8) // 2
    for i, ch in enumerate(text):
        draw_char(surf, ch, x + i * 8, y, color)

# =============================================================================
# SPRITE DRAWING
# =============================================================================
def draw_mega_cat(surf, x, y, facing=1, frame=0, shooting=False, 
                  color1=CYAN, color2=LTBLUE, jumping=False):
    x, y = int(x), int(y)
    
    pygame.draw.rect(surf, color1, (x+3, y+8, 10, 8))
    pygame.draw.rect(surf, color1, (x+2, y+0, 12, 10))
    pygame.draw.rect(surf, color2, (x+3, y+1, 10, 3))
    pygame.draw.rect(surf, SKIN, (x+4, y+4, 8, 5))
    
    ex1, ex2 = (x+6, x+10) if facing > 0 else (x+4, x+8)
    pygame.draw.rect(surf, BLACK, (ex1, y+5, 2, 2))
    pygame.draw.rect(surf, BLACK, (ex2, y+5, 2, 2))
    surf.set_at((ex1, y+5), WHITE)
    surf.set_at((ex2, y+5), WHITE)
    
    pygame.draw.polygon(surf, color1, [(x+1, y+3), (x+3, y-3), (x+6, y+3)])
    pygame.draw.polygon(surf, color1, [(x+10, y+3), (x+13, y-3), (x+15, y+3)])
    pygame.draw.polygon(surf, PINK, [(x+2, y+2), (x+3, y-1), (x+5, y+2)])
    pygame.draw.polygon(surf, PINK, [(x+11, y+2), (x+13, y-1), (x+14, y+2)])
    
    surf.set_at((x+3, y+7), GRAY2)
    surf.set_at((x+12, y+7), GRAY2)
    
    if jumping:
        pygame.draw.rect(surf, color1, (x+3, y+16, 5, 5))
        pygame.draw.rect(surf, color1, (x+8, y+16, 5, 5))
    else:
        walk = (frame // 6) % 4
        off = [0, 1, 0, -1][walk]
        pygame.draw.rect(surf, color1, (x+3+off, y+16, 4, 8))
        pygame.draw.rect(surf, color1, (x+9-off, y+16, 4, 8))
        pygame.draw.rect(surf, color2, (x+2+off, y+22, 5, 2))
        pygame.draw.rect(surf, color2, (x+9-off, y+22, 5, 2))
    
    if shooting:
        if facing > 0:
            pygame.draw.rect(surf, color1, (x+12, y+9, 7, 5))
            pygame.draw.rect(surf, GRAY2, (x+17, y+10, 4, 3))
        else:
            pygame.draw.rect(surf, color1, (x-3, y+9, 7, 5))
            pygame.draw.rect(surf, GRAY2, (x-5, y+10, 4, 3))
    else:
        ax = x+11 if facing > 0 else x+1
        pygame.draw.rect(surf, color1, (ax, y+10, 4, 5))
    
    tw = math.sin(frame * 0.15) * 3
    tx = x+2 if facing > 0 else x+14
    pygame.draw.line(surf, color1, (tx, y+14), (tx + (-4 if facing > 0 else 4) + int(tw), y+10), 2)

def draw_robot_master(surf, x, y, idx, frame=0, hurt=False):
    x, y = int(x), int(y)
    rm = ROBOT_MASTERS[idx]
    c1 = WHITE if hurt and frame % 4 < 2 else rm["color1"]
    c2 = rm["color2"]
    
    pygame.draw.rect(surf, c1, (x+4, y+0, 16, 12))
    pygame.draw.rect(surf, SKIN, (x+6, y+4, 12, 6))
    pygame.draw.rect(surf, BLACK, (x+7, y+5, 3, 3))
    pygame.draw.rect(surf, BLACK, (x+14, y+5, 3, 3))
    pygame.draw.rect(surf, c1, (x+3, y+12, 18, 12))
    
    lf = (frame // 10) % 2
    pygame.draw.rect(surf, c1, (x+4+lf*2, y+24, 6, 8))
    pygame.draw.rect(surf, c1, (x+14-lf*2, y+24, 6, 8))
    
    if idx == 0:
        pygame.draw.polygon(surf, c2, [(x+1, y+4), (x+4, y+2), (x+4, y+10)])
        pygame.draw.polygon(surf, c2, [(x+20, y+2), (x+23, y+4), (x+20, y+10)])
        pygame.draw.ellipse(surf, LTBLUE, (x+6, y-4, 12, 6))
    elif idx == 1:
        pygame.draw.circle(surf, GRAY2, (x+12, y+17), 6)
        for i in range(3):
            a = frame * 0.2 + i * 2.1
            pygame.draw.line(surf, GRAY1, (x+12, y+17), 
                           (int(x+12+math.cos(a)*5), int(y+17+math.sin(a)*5)), 2)
    elif idx == 2:
        pygame.draw.polygon(surf, YELLOW, [(x+12, y-3), (x+6, y+3), (x+18, y+3)])
    elif idx == 3:
        pygame.draw.rect(surf, c1, (x+2, y+8, 20, 18))
        pygame.draw.rect(surf, YELLOW, (x+8, y+2, 8, 6))
        if frame % 10 < 5:
            pygame.draw.rect(surf, RED, (x+10, y-2, 4, 5))
    elif idx == 4:
        pygame.draw.rect(surf, c2, (x+2, y+12, 20, 14))
        for i in range(5):
            pygame.draw.polygon(surf, LTGREEN, [(x+2+i*4, y+2), (x+4+i*4, y-4), (x+6+i*4, y+2)])
    elif idx == 5:
        pygame.draw.circle(surf, GRAY1, (x+12, y+4), 5, 1)
        pygame.draw.circle(surf, YELLOW, (x+12, y+4), 2)
    elif idx == 6:
        pygame.draw.ellipse(surf, c1, (x+3, y-6, 18, 10))
        pygame.draw.rect(surf, LTBLUE, (x+8, y+2, 8, 3))
    elif idx == 7:
        pygame.draw.polygon(surf, GRAY2, [(x-4, y+14), (x+3, y+16), (x+3, y+20)])
        pygame.draw.polygon(surf, GRAY2, [(x+28, y+14), (x+21, y+16), (x+21, y+20)])

# =============================================================================
# PLAYER CLASS
# =============================================================================
class Player:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x, self.y = 16.0, 176.0
        self.vx, self.vy = 0.0, 0.0
        self.facing = 1
        self.grounded = False
        self.hp, self.max_hp = 28, 28
        self.lives = 3
        self.weapon = 0
        self.weapon_energy = [28] * 9
        self.weapons_unlocked = [True] + [False] * 8
        self.shooting = False
        self.shoot_timer = 0
        self.invincible = 0
        self.alive = True
        self.frame = 0
        self.width, self.height = 16, 24
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, keys, level):
        if not self.alive:
            return
        self.frame += 1
        
        if keys[pygame.K_LEFT]:
            self.vx = max(self.vx - PLAYER_ACCEL, -PLAYER_SPEED)
            self.facing = -1
        elif keys[pygame.K_RIGHT]:
            self.vx = min(self.vx + PLAYER_ACCEL, PLAYER_SPEED)
            self.facing = 1
        else:
            self.vx = self.vx * 0.8 if abs(self.vx) > 0.1 else 0
        
        self.vy = min(self.vy + GRAVITY, TERMINAL_VEL)
        self.x += self.vx
        self.y += self.vy
        
        self.grounded = False
        rect = self.get_rect()
        for plat in level.platforms:
            if rect.colliderect(plat):
                dx = (rect.centerx - plat.centerx) / max(1, plat.width/2)
                dy = (rect.centery - plat.centery) / max(1, plat.height/2)
                if abs(dx) > abs(dy):
                    self.x = plat.right if dx > 0 else plat.left - self.width
                    self.vx = 0
                else:
                    if dy > 0:
                        self.y = plat.bottom
                    else:
                        self.y = plat.top - self.height
                        self.grounded = True
                    self.vy = 0
                rect = self.get_rect()
        
        self.x = max(0, min(SCREEN_W - self.width, self.x))
        if self.y > SCREEN_H + 32:
            self.die()
        
        if self.shoot_timer > 0:
            self.shoot_timer -= 1
            if self.shoot_timer == 0:
                self.shooting = False
        if self.invincible > 0:
            self.invincible -= 1
    
    def jump(self):
        if self.grounded and self.alive:
            self.vy = JUMP_VELOCITY
            self.grounded = False
            play_sfx("jump")
    
    def shoot(self):
        if not self.alive:
            return None
        if self.weapon > 0 and self.weapon_energy[self.weapon] <= 0:
            return None
        if self.weapon > 0:
            self.weapon_energy[self.weapon] -= 1
        self.shooting = True
        self.shoot_timer = 12
        play_sfx("shoot")
        return Bullet(self.x + (self.width if self.facing > 0 else -8), self.y + 10, self.facing, self.weapon)
    
    def take_damage(self, amount):
        if self.invincible > 0 or not self.alive:
            return
        self.hp -= amount
        self.invincible = 90
        play_sfx("hit")
        if self.hp <= 0:
            self.die()
    
    def die(self):
        self.alive = False
        self.hp = 0
        play_sfx("death")
    
    def draw(self, surf):
        if not self.alive or (self.invincible > 0 and (self.invincible // 3) % 2):
            return
        colors = [(CYAN, LTBLUE), (LTGREEN, DKGREEN), (LTBLUE, BLUE2), (RED, DKRED),
                  (ORANGE, DKORANGE), (DKGREEN, BROWN), (DKORANGE, GRAY2), (LTBLUE, PURPLE), (DKORANGE, GRAY3)]
        c1, c2 = colors[min(self.weapon, len(colors)-1)]
        draw_mega_cat(surf, self.x, self.y, self.facing, self.frame, self.shooting, c1, c2, not self.grounded)

# =============================================================================
# BULLET, ENEMY, BOSS, LEVEL CLASSES
# =============================================================================
class Bullet:
    def __init__(self, x, y, direction, weapon=0):
        self.x, self.y = x, y
        self.vx, self.vy = direction * 5, 0
        self.weapon = weapon
        self.alive = True
        self.damage = 2 if weapon == 6 else 1
        if weapon == 1: self.vy, self.vx = 1, direction * 2
        elif weapon == 2: self.vy = -0.5
        elif weapon == 3: self.vx = direction * 6
        elif weapon == 6: self.vx = direction * 4
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.weapon == 1 and self.y > SCREEN_H - 20:
            self.y, self.vy = SCREEN_H - 20, -abs(self.vy) * 0.8
        if self.x < -8 or self.x > SCREEN_W + 8 or self.y < -8 or self.y > SCREEN_H + 8:
            self.alive = False
    
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        if self.weapon == 0:
            pygame.draw.circle(surf, YELLOW, (x, y), 3)
        elif self.weapon == 1:
            pygame.draw.circle(surf, LTGREEN, (x, y), 4, 1)
        elif self.weapon == 2:
            pygame.draw.ellipse(surf, LTBLUE, (x-4, y-6, 8, 12))
        elif self.weapon == 6:
            pygame.draw.circle(surf, GRAY1, (x, y), 5, 1)
        else:
            pygame.draw.circle(surf, YELLOW, (x, y), 3)

class Enemy:
    def __init__(self, x, y, etype="met"):
        self.x, self.y = x, y
        self.etype = etype
        self.hp = 1
        self.frame = 0
        self.alive = True
        self.hiding = True
        self.timer = random.randint(30, 90)
        self.vx = -1 if etype == "telly" else 0
    
    def update(self, px, py):
        self.frame += 1
        self.timer -= 1
        if self.etype == "met" and self.timer <= 0:
            self.hiding = not self.hiding
            self.timer = 30 if not self.hiding else random.randint(40, 100)
        elif self.etype == "telly":
            self.x += self.vx
            self.y += math.sin(self.frame * 0.1) * 0.5
            if self.x < -20: self.x = SCREEN_W + 20
    
    def take_damage(self, dmg):
        if self.etype == "met" and self.hiding:
            return False
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False
        return True
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, 16, 16)
    
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        if self.etype == "met":
            if self.hiding:
                pygame.draw.ellipse(surf, YELLOW, (x, y+6, 16, 10))
            else:
                pygame.draw.ellipse(surf, YELLOW, (x, y, 16, 10))
                pygame.draw.rect(surf, BLACK, (x+4, y+10, 8, 6))
        elif self.etype == "telly":
            pygame.draw.circle(surf, RED, (x+8, y+8), 8)
            pygame.draw.circle(surf, GRAY2, (x+8, y+8), 5)

class Boss:
    def __init__(self, idx):
        self.idx = idx
        self.x, self.y = 200.0, 176.0
        self.vx, self.vy = 0.0, 0.0
        self.hp, self.max_hp = 28, 28
        self.facing, self.frame = -1, 0
        self.alive = True
        self.hurt_timer = 0
        self.attack_timer = 60
        self.projectiles = []
        self.grounded = False
        self.width, self.height = 24, 32
    
    def update(self, player, platforms):
        if not self.alive:
            return
        self.frame += 1
        self.facing = -1 if player.x < self.x else 1
        self.vy = min(self.vy + GRAVITY, TERMINAL_VEL)
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        
        self.grounded = False
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for plat in platforms:
            if rect.colliderect(plat) and self.vy > 0:
                self.y, self.vy, self.grounded = plat.top - self.height, 0, True
        self.x = max(0, min(SCREEN_W - self.width, self.x))
        
        self.attack_timer -= 1
        if self.attack_timer <= 0:
            self.do_attack(player)
            self.attack_timer = random.randint(40, 80)
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        
        for p in self.projectiles[:]:
            p[0] += p[2]
            p[1] += p[3]
            if p[0] < -16 or p[0] > SCREEN_W+16 or p[1] < -16 or p[1] > SCREEN_H+16:
                self.projectiles.remove(p)
    
    def do_attack(self, player):
        idx = self.idx
        if idx == 0:
            self.projectiles.append([self.x+12, self.y+16, self.facing*2, 1, "bubble"])
            if self.grounded and random.random() < 0.3: self.vy = -6
        elif idx == 1:
            for i in range(5):
                self.projectiles.append([self.x+12, self.y+16, self.facing*3, -0.5+i*0.25, "tornado"])
        elif idx == 2:
            if random.random() < 0.5:
                self.vx = self.facing * 4
                if self.grounded: self.vy = -4
            else:
                self.projectiles.append([self.x+12, self.y+10, self.facing*5, 0, "boomerang"])
        elif idx == 3:
            if random.random() < 0.4: self.vx = self.facing * 5
            self.projectiles.append([self.x+12, self.y+10, self.facing*3, 0, "fire"])
        elif idx == 4:
            for a in range(0, 360, 45):
                r = math.radians(a)
                self.projectiles.append([self.x+12, self.y+12, math.cos(r)*2, math.sin(r)*2, "leaf"])
        elif idx == 5:
            for dy in [-1, 0, 1]:
                self.projectiles.append([self.x+12, self.y+12, self.facing*4, dy*0.5, "blade"])
        elif idx == 6:
            self.projectiles.append([self.x+12, self.y+10, self.facing*3, 0, "flash"])
            self.vx = self.facing * 2
        elif idx == 7:
            if self.grounded: self.vy = -5
            self.projectiles.append([self.x+12, self.y+8, self.facing*2, -2, "bomb"])
    
    def take_damage(self, amount, weapon_idx):
        if self.hurt_timer > 0: return
        dmg = WEAPON_DMG[weapon_idx][self.idx] if weapon_idx < len(WEAPON_DMG) else amount
        self.hp -= max(1, dmg)
        self.hurt_timer = 30
        play_sfx("boss_hit")
        if self.hp <= 0: self.alive = False
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, surf):
        if not self.alive: return
        draw_robot_master(surf, self.x, self.y, self.idx, self.frame, self.hurt_timer > 0)
        for p in self.projectiles:
            px, py, ptype = int(p[0]), int(p[1]), p[4]
            colors = {"bubble": LTGREEN, "tornado": LTBLUE, "boomerang": RED, "fire": ORANGE, 
                     "leaf": LTGREEN, "blade": GRAY1, "flash": WHITE, "bomb": DKORANGE}
            pygame.draw.circle(surf, colors.get(ptype, WHITE), (px, py), 5)

class Level:
    def __init__(self, idx):
        self.idx = idx
        self.rm = ROBOT_MASTERS[idx]
        self.platforms = []
        self.enemies = []
        self.build()
    
    def build(self):
        self.platforms = [pygame.Rect(0, 208, SCREEN_W, 32)]
        self.enemies = []
        layouts = [
            [(40,176,48,16), (120,144,48,16), (56,112,64,16), (168,128,48,16)],
            [(32,168,40,16), (96,136,40,16), (160,104,40,16), (64,80,56,16)],
            [(40,176,32,16), (88,160,32,16), (136,144,32,16), (184,128,48,16)],
            [(48,168,48,16), (128,152,48,16), (80,120,64,16), (176,136,48,16)],
            [(32,176,56,16), (112,160,56,16), (64,128,72,16), (168,144,56,16)],
            [(40,176,48,16), (112,160,56,16), (56,128,64,16), (152,144,48,16)],
            [(48,168,40,16), (112,144,48,16), (176,120,48,16), (72,96,56,16)],
            [(40,176,48,16), (104,152,48,16), (168,128,48,16), (64,104,56,16)],
        ]
        for p in layouts[self.idx]:
            self.platforms.append(pygame.Rect(*p))
        enemy_configs = [
            [("met", 80, 160), ("telly", 150, 128)],
            [("telly", 60, 152), ("telly", 130, 120)],
            [("met", 70, 160), ("met", 160, 128)],
            [("met", 100, 104), ("met", 180, 120)],
            [("met", 60, 160), ("telly", 90, 112)],
            [("met", 70, 160), ("met", 130, 144)],
            [("met", 80, 152), ("telly", 150, 128)],
            [("met", 70, 160), ("met", 200, 112)],
        ]
        for e in enemy_configs[self.idx]:
            self.enemies.append(Enemy(e[1], e[2], e[0]))
    
    def update(self, px):
        for e in self.enemies:
            e.update(px, 0)
    
    def draw(self, surf):
        surf.fill(self.rm["stage_bg"])
        for plat in self.platforms:
            pygame.draw.rect(surf, self.rm["stage_fg"], plat)
            pygame.draw.line(surf, WHITE, (plat.x, plat.y), (plat.x + plat.width, plat.y))
        for e in self.enemies:
            if e.alive: e.draw(surf)
        pygame.draw.rect(surf, GRAY2, (SCREEN_W - 24, 160, 24, 48))

# =============================================================================
# STAGE SELECT & TITLE
# =============================================================================
class StageSelect:
    def __init__(self):
        self.cursor, self.frame = 0, 0
        self.grid = [[0, 1, 2], [3, -1, 4], [5, 6, 7]]
        self.cx, self.cy = 0, 0
    
    def move(self, dx, dy):
        for _ in range(4):
            nx, ny = (self.cx + dx) % 3, (self.cy + dy) % 3
            if self.grid[ny][nx] >= 0:
                self.cx, self.cy = nx, ny
                self.cursor = self.grid[ny][nx]
                play_sfx("menu_move")
                return
            self.cx, self.cy = nx, ny
    
    def draw(self, surf, defeated):
        self.frame += 1
        surf.fill(BLACK)
        for i in range(20):
            sx, sy = (i * 37 + self.frame) % SCREEN_W, (i * 23) % 160
            if (self.frame + i * 7) % 30 < 15:
                surf.set_at((sx, sy + 40), WHITE)
        draw_text(surf, "STAGE SELECT", 0, 12, WHITE, True)
        box, gap = 48, 8
        sx = (SCREEN_W - (box * 3 + gap * 2)) // 2
        for gy in range(3):
            for gx in range(3):
                boss_idx = self.grid[gy][gx]
                x, y = sx + gx * (box + gap), 44 + gy * (box + gap)
                if boss_idx < 0:
                    pygame.draw.rect(surf, GRAY3, (x, y, box, box))
                    continue
                rm = ROBOT_MASTERS[boss_idx]
                sel = (gx == self.cx and gy == self.cy)
                pygame.draw.rect(surf, YELLOW if sel and self.frame % 16 < 8 else GRAY2, (x, y, box, box), 2)
                if defeated[boss_idx]:
                    pygame.draw.line(surf, RED, (x+4, y+4), (x+box-4, y+box-4), 3)
                    pygame.draw.line(surf, RED, (x+box-4, y+4), (x+4, y+box-4), 3)
                else:
                    cx_p, cy_p = x + box//2, y + box//2 - 4
                    pygame.draw.rect(surf, rm["color1"], (cx_p-14, cy_p-10, 28, 24))
                    pygame.draw.rect(surf, SKIN, (cx_p-10, cy_p-2, 20, 12))
                    pygame.draw.rect(surf, BLACK, (cx_p-7, cy_p+1, 4, 4))
                    pygame.draw.rect(surf, BLACK, (cx_p+3, cy_p+1, 4, 4))
                if sel:
                    pygame.draw.rect(surf, WHITE, (x-2, y-2, box+4, box+4), 2)
        if self.grid[self.cy][self.cx] >= 0:
            draw_text(surf, ROBOT_MASTERS[self.cursor]["name"], 0, 210, ROBOT_MASTERS[self.cursor]["color1"], True)
        draw_text(surf, "PRESS ENTER", 0, 226, GRAY1, True)

class TitleScreen:
    def __init__(self):
        self.frame, self.phase, self.scroll_y, self.option = 0, 0, 0, 0
        self.stars = [(random.randint(0, SCREEN_W), random.randint(0, 100)) for _ in range(30)]
        self.buildings = []
        x = 0
        while x < SCREEN_W + 32:
            w, h = random.randint(16, 40), random.randint(40, 100)
            self.buildings.append((x, h, w))
            x += w + random.randint(0, 8)
    
    def update(self):
        self.frame += 1
        if self.phase == 0:
            self.scroll_y += 1
            if self.scroll_y > 120: self.phase = 1
        elif self.phase == 1 and self.frame > 180:
            self.phase = 2
    
    def draw(self, surf):
        surf.fill(BLACK)
        for i, (sx, sy) in enumerate(self.stars):
            if (self.frame + i * 5) % 40 < 30:
                surf.set_at((sx, sy), WHITE if (self.frame + i * 3) % 20 < 10 else GRAY1)
        base_y = SCREEN_H - 60 + min(self.scroll_y, 60)
        for bx, bh, bw in self.buildings:
            pygame.draw.rect(surf, (20, 20, 40), (bx, base_y, bw, bh))
        if self.phase >= 1:
            ty = 50 if self.phase == 2 else 50 + max(0, 100 - (self.frame - 120))
            draw_text(surf, "MEGA", 0, ty, CYAN, True)
            draw_text(surf, "CAT", 0, ty + 20, CYAN, True)
            draw_text(surf, "2", 0, ty + 40, LTBLUE, True)
            if self.phase == 2:
                cx, cy = SCREEN_W // 2, 125
                pygame.draw.circle(surf, CYAN, (cx, cy), 20)
                pygame.draw.polygon(surf, CYAN, [(cx-18, cy-8), (cx-12, cy-26), (cx-6, cy-8)])
                pygame.draw.polygon(surf, CYAN, [(cx+18, cy-8), (cx+12, cy-26), (cx+6, cy-8)])
                pygame.draw.polygon(surf, PINK, [(cx-14, cy-10), (cx-12, cy-20), (cx-10, cy-10)])
                pygame.draw.polygon(surf, PINK, [(cx+14, cy-10), (cx+12, cy-20), (cx+10, cy-10)])
        if self.phase == 2:
            for i, opt in enumerate(["GAME START", "QUIT"]):
                col = YELLOW if i == self.option else WHITE
                draw_text(surf, opt, 0, 165 + i * 16, col, True)
                if i == self.option:
                    draw_text(surf, ">", SCREEN_W//2 - len(opt)*4 - 12, 165 + i * 16, YELLOW)
            draw_text(surf, "SAMSOFT SOUND ENGINE", 0, 205, GRAY2, True)
            draw_text(surf, "NYA! TEAM FLAMES 2025", 0, 220, GRAY2, True)
    
    def handle_key(self, key):
        if self.phase < 2:
            self.phase, self.frame = 2, 200
            return None
        if key in (pygame.K_UP, pygame.K_DOWN):
            self.option = 1 - self.option
            play_sfx("menu_move")
        elif key == pygame.K_RETURN:
            play_sfx("menu_select")
            return "start" if self.option == 0 else "quit"
        return None

# =============================================================================
# GAME CLASS
# =============================================================================
class Game:
    def __init__(self):
        self.state = STATE_TITLE_INTRO
        self.title = TitleScreen()
        self.player = Player()
        self.boss = None
        self.level = None
        self.stage_select = StageSelect()
        self.bullets = []
        self.defeated = [False] * 8
        self.frame, self.timer, self.pause_option = 0, 0, 0
        self.jump_held = False
    
    def start_stage(self, idx):
        self.level = Level(idx)
        self.player.reset()
        self.player.x, self.player.y = 24, 176
        self.boss, self.bullets = None, []
        self.timer, self.state = 90, STATE_READY
        play_sfx("ready")
        music.play(STAGE_TRACKS[idx])
    
    def start_boss(self):
        self.boss = Boss(self.level.idx)
        self.timer, self.state = 60, STATE_BOSS_INTRO
        play_sfx("boss_door")
        music.play("boss")
    
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            music.stop()
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                music.toggle()
                return
            
            if self.state in (STATE_TITLE_INTRO, STATE_TITLE_MENU):
                result = self.title.handle_key(event.key)
                if result == "start":
                    self.state = STATE_STAGE_SELECT
                    music.play("stage_select")
                elif result == "quit":
                    music.stop()
                    pygame.quit()
                    sys.exit()
                elif self.title.phase == 2 and self.state == STATE_TITLE_INTRO:
                    self.state = STATE_TITLE_MENU
                    music.play("title")
            
            elif self.state == STATE_STAGE_SELECT:
                if event.key == pygame.K_LEFT: self.stage_select.move(-1, 0)
                elif event.key == pygame.K_RIGHT: self.stage_select.move(1, 0)
                elif event.key == pygame.K_UP: self.stage_select.move(0, -1)
                elif event.key == pygame.K_DOWN: self.stage_select.move(0, 1)
                elif event.key == pygame.K_RETURN and not self.defeated[self.stage_select.cursor]:
                    play_sfx("menu_select")
                    self.start_stage(self.stage_select.cursor)
            
            elif self.state in (STATE_PLAYING, STATE_BOSS_FIGHT):
                if event.key == pygame.K_SPACE and not self.jump_held:
                    self.player.jump()
                    self.jump_held = True
                elif event.key == pygame.K_x:
                    bullet = self.player.shoot()
                    if bullet: self.bullets.append(bullet)
                elif event.key == pygame.K_c:
                    for i in range(1, 9):
                        nw = (self.player.weapon + i) % 9
                        if self.player.weapons_unlocked[nw]:
                            self.player.weapon = nw
                            play_sfx("menu_move")
                            break
                elif event.key == pygame.K_ESCAPE:
                    play_sfx("pause")
                    self.state = STATE_PAUSE
            
            elif self.state == STATE_PAUSE:
                if event.key == pygame.K_ESCAPE:
                    self.state = STATE_BOSS_FIGHT if self.boss else STATE_PLAYING
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.pause_option = (self.pause_option + 1) % 2
                    play_sfx("menu_move")
                elif event.key == pygame.K_RETURN:
                    if self.pause_option == 0:
                        self.state = STATE_BOSS_FIGHT if self.boss else STATE_PLAYING
                    else:
                        self.state = STATE_STAGE_SELECT
                        music.play("stage_select")
            
            elif self.state == STATE_GAME_OVER and event.key == pygame.K_RETURN:
                self.player.lives = 3
                self.state = STATE_STAGE_SELECT
                music.play("stage_select")
            
            elif self.state == STATE_WEAPON_GET and event.key == pygame.K_RETURN:
                self.state = STATE_STAGE_SELECT
                music.play("stage_select")
        
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            self.jump_held = False
    
    def update(self, keys):
        self.frame += 1
        
        if self.state in (STATE_TITLE_INTRO, STATE_TITLE_MENU):
            self.title.update()
            if self.title.phase == 2 and self.state == STATE_TITLE_INTRO:
                self.state = STATE_TITLE_MENU
                music.play("title")
        
        elif self.state == STATE_READY:
            self.timer -= 1
            if self.timer <= 0: self.state = STATE_PLAYING
        
        elif self.state == STATE_PLAYING:
            self.player.update(keys, self.level)
            self.level.update(self.player.x)
            for b in self.bullets[:]:
                b.update()
                if not b.alive: self.bullets.remove(b)
            for b in self.bullets[:]:
                if not b.alive: continue
                brect = pygame.Rect(b.x-4, b.y-4, 8, 8)
                for e in self.level.enemies:
                    if e.alive and brect.colliderect(e.get_rect()):
                        if e.take_damage(b.damage): play_sfx("enemy_hit")
                        b.alive = False
                        break
            prect = self.player.get_rect()
            for e in self.level.enemies:
                if e.alive and prect.colliderect(e.get_rect()):
                    self.player.take_damage(2)
            if self.player.x > SCREEN_W - 40: self.start_boss()
            if not self.player.alive: self.handle_death()
        
        elif self.state == STATE_BOSS_INTRO:
            self.timer -= 1
            if self.timer <= 0: self.state = STATE_BOSS_FIGHT
        
        elif self.state == STATE_BOSS_FIGHT:
            self.player.update(keys, self.level)
            if self.boss:
                self.boss.update(self.player, self.level.platforms)
                prect = self.player.get_rect()
                for p in self.boss.projectiles[:]:
                    if pygame.Rect(p[0]-4, p[1]-4, 8, 8).colliderect(prect):
                        self.player.take_damage(3)
                        self.boss.projectiles.remove(p)
                for b in self.bullets[:]:
                    b.update()
                    if not b.alive:
                        self.bullets.remove(b)
                        continue
                    if pygame.Rect(b.x-4, b.y-4, 8, 8).colliderect(self.boss.get_rect()):
                        self.boss.take_damage(b.damage, b.weapon)
                        b.alive = False
                if prect.colliderect(self.boss.get_rect()):
                    self.player.take_damage(4)
                if not self.boss.alive:
                    self.defeated[self.level.idx] = True
                    self.player.weapons_unlocked[self.level.idx + 1] = True
                    self.state = STATE_WEAPON_GET
                    music.play("victory")
            if not self.player.alive: self.handle_death()
    
    def handle_death(self):
        self.player.lives -= 1
        music.stop()
        if self.player.lives <= 0:
            self.state = STATE_GAME_OVER
            music.play("gameover")
        else:
            self.player.reset()
            if self.boss:
                self.boss = Boss(self.level.idx)
                self.bullets = []
                music.play("boss")
            else:
                self.level.build()
                self.bullets = []
                music.play(STAGE_TRACKS[self.level.idx])
    
    def draw(self, surf):
        if self.state in (STATE_TITLE_INTRO, STATE_TITLE_MENU):
            self.title.draw(surf)
        elif self.state == STATE_STAGE_SELECT:
            self.stage_select.draw(surf, self.defeated)
        elif self.state == STATE_READY:
            rm = ROBOT_MASTERS[self.level.idx]
            surf.fill(BLACK)
            draw_text(surf, rm["name"], 0, 100, rm["color1"], True)
            draw_text(surf, "READY", 0, 120, WHITE, True)
        elif self.state in (STATE_PLAYING, STATE_BOSS_FIGHT, STATE_BOSS_INTRO):
            self.level.draw(surf)
            for b in self.bullets: b.draw(surf)
            if self.boss: self.boss.draw(surf)
            self.player.draw(surf)
            pygame.draw.rect(surf, BLACK, (8, 16, 8, 58))
            pygame.draw.rect(surf, YELLOW, (9, 17 + int((1 - self.player.hp/28)*56), 6, int(self.player.hp/28*56)))
            if self.boss and self.state == STATE_BOSS_FIGHT:
                pygame.draw.rect(surf, BLACK, (SCREEN_W-16, 16, 8, 58))
                pygame.draw.rect(surf, RED, (SCREEN_W-15, 17 + int((1-self.boss.hp/28)*56), 6, int(self.boss.hp/28*56)))
            draw_text(surf, f"x{self.player.lives}", SCREEN_W - 32, 8, WHITE)
            if self.state == STATE_BOSS_INTRO and (self.frame // 8) % 2:
                draw_text(surf, "WARNING", 0, 80, RED, True)
                draw_text(surf, ROBOT_MASTERS[self.level.idx]["name"], 0, 100, ROBOT_MASTERS[self.level.idx]["color1"], True)
        elif self.state == STATE_PAUSE:
            self.level.draw(surf)
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surf.blit(overlay, (0, 0))
            draw_text(surf, "PAUSE", 0, 100, WHITE, True)
            for i, opt in enumerate(["CONTINUE", "STAGE SELECT"]):
                draw_text(surf, opt, 0, 130 + i * 16, YELLOW if i == self.pause_option else WHITE, True)
        elif self.state == STATE_GAME_OVER:
            surf.fill(BLACK)
            draw_text(surf, "GAME OVER", 0, 100, RED, True)
            draw_text(surf, "NYA...", 0, 120, GRAY1, True)
        elif self.state == STATE_WEAPON_GET:
            surf.fill(BLACK)
            rm = ROBOT_MASTERS[self.level.idx]
            draw_text(surf, "YOU GOT", 0, 56, WHITE, True)
            draw_text(surf, rm["weapon"], 0, 72, rm["color1"], True)
            draw_mega_cat(surf, SCREEN_W//2 - 8, 100, 1, self.frame, False, CYAN, LTBLUE, False)

# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 50)
    print("MEGA CAT 2 - SAMSOFT SOUND MEDIA ENGINE v2.0")
    print("=" * 50)
    print("All music synthesized in real-time!")
    print("Press M to toggle music on/off")
    print("=" * 50)
    
    game = Game()
    
    try:
        while True:
            for event in pygame.event.get():
                game.handle_event(event)
            
            keys = pygame.key.get_pressed()
            game.update(keys)
            game.draw(canvas)
            
            scaled = pygame.transform.scale(canvas, (SCREEN_W * SCALE, SCREEN_H * SCALE))
            screen.blit(scaled, (0, 0))
            pygame.display.flip()
            clock.tick(FPS)
    except KeyboardInterrupt:
        pass
    finally:
        music.stop()
        pygame.quit()

if __name__ == "__main__":
    main()
