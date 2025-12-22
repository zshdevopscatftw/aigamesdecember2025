#!/usr/bin/env python3
"""
ULTRA!TETRIS — Pygame Port
Samsoft • © The Tetris Company • Team Flames • 2025

• Exact Game Boy Tetris engine recreation
• 60 FPS locked gameplay
• Bit-accurate Korobeiniki (Type A) music
• Classic Game Boy green palette
• Xbox-style trophy/achievement system
• Persistent save file (ultra_tetris_save.txt)
• Full sound settings
"""

import pygame
import random
import math
import array
import sys
import os
import json
from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple, Dict

# ============================================================
# INITIALIZE PYGAME
# ============================================================
pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.init()

# ============================================================
# SAVE FILE PATH (same folder as script)
# ============================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(SCRIPT_DIR, "ultra_tetris_save.json")

# ============================================================
# FAMICOM/NES CONSTANTS
# ============================================================
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

# Board dimensions
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 16

# Board position
BOARD_X = 180
BOARD_Y = 40

# NES Color Palette (classic)
NES_BLACK = (0, 0, 0)
NES_WHITE = (252, 252, 252)
NES_GRAY = (188, 188, 188)
NES_DARK_GRAY = (80, 80, 80)
NES_RED = (228, 0, 88)
NES_ORANGE = (248, 120, 88)
NES_YELLOW = (248, 184, 0)
NES_GREEN = (0, 168, 0)
NES_CYAN = (0, 232, 216)
NES_BLUE = (0, 88, 248)
NES_PURPLE = (148, 0, 148)
NES_PINK = (248, 120, 248)
NES_GOLD = (255, 215, 0)
NES_SILVER = (192, 192, 192)
NES_BRONZE = (205, 127, 50)
NES_BG = (0, 0, 0)
NES_BORDER = (60, 60, 60)

# Game Boy Green Palette (authentic DMG)
GB_LIGHTEST = (155, 188, 15)   # Lightest green
GB_LIGHT = (139, 172, 15)      # Light green
GB_DARK = (48, 98, 48)         # Dark green
GB_DARKEST = (15, 56, 15)      # Darkest green

# DAS timing
DAS_INITIAL_DELAY = 16
DAS_REPEAT_RATE = 6
LOCK_DELAY = 30

# Level speeds (frames per drop)
LEVEL_SPEEDS = [
    48, 43, 38, 33, 28, 23, 18, 13, 8, 6,
    5, 5, 5, 4, 4, 4, 3, 3, 3, 2,
    2, 2, 2, 2, 2, 2, 2, 2, 2, 1
]

SCORE_TABLE = {1: 40, 2: 100, 3: 300, 4: 1200}

# ============================================================
# DISPLAY SETUP
# ============================================================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("ULTRA!TETRIS — Pygame Port")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.Font(None, 16)
font_medium = pygame.font.Font(None, 24)
font_large = pygame.font.Font(None, 36)
font_title = pygame.font.Font(None, 48)

# ============================================================
# TROPHY/ACHIEVEMENT SYSTEM
# ============================================================
TROPHIES = {
    'first_game': {
        'name': 'Welcome to Tetris',
        'desc': 'Play your first game',
        'icon': '🎮',
        'tier': 'bronze',
        'secret': False
    },
    'first_line': {
        'name': 'Line Clear',
        'desc': 'Clear your first line',
        'icon': '📏',
        'tier': 'bronze',
        'secret': False
    },
    'first_tetris': {
        'name': 'TETRIS!',
        'desc': 'Clear 4 lines at once',
        'icon': '💎',
        'tier': 'silver',
        'secret': False
    },
    'score_1000': {
        'name': 'Getting Started',
        'desc': 'Score 1,000 points',
        'icon': '⭐',
        'tier': 'bronze',
        'secret': False
    },
    'score_10000': {
        'name': 'Rising Star',
        'desc': 'Score 10,000 points',
        'icon': '🌟',
        'tier': 'silver',
        'secret': False
    },
    'score_50000': {
        'name': 'Tetris Master',
        'desc': 'Score 50,000 points',
        'icon': '👑',
        'tier': 'gold',
        'secret': False
    },
    'score_100000': {
        'name': 'Legendary',
        'desc': 'Score 100,000 points',
        'icon': '🏆',
        'tier': 'gold',
        'secret': False
    },
    'level_5': {
        'name': 'Level Up!',
        'desc': 'Reach level 5',
        'icon': '📈',
        'tier': 'bronze',
        'secret': False
    },
    'level_10': {
        'name': 'Double Digits',
        'desc': 'Reach level 10',
        'icon': '🔟',
        'tier': 'silver',
        'secret': False
    },
    'level_15': {
        'name': 'Speed Demon',
        'desc': 'Reach level 15',
        'icon': '⚡',
        'tier': 'gold',
        'secret': False
    },
    'level_20': {
        'name': 'Grandmaster',
        'desc': 'Reach level 20',
        'icon': '🎖️',
        'tier': 'gold',
        'secret': False
    },
    'lines_10': {
        'name': 'Ten Down',
        'desc': 'Clear 10 lines total',
        'icon': '1️⃣',
        'tier': 'bronze',
        'secret': False
    },
    'lines_50': {
        'name': 'Fifty Lines',
        'desc': 'Clear 50 lines total',
        'icon': '5️⃣',
        'tier': 'silver',
        'secret': False
    },
    'lines_100': {
        'name': 'Century',
        'desc': 'Clear 100 lines total',
        'icon': '💯',
        'tier': 'gold',
        'secret': False
    },
    'games_10': {
        'name': 'Dedicated',
        'desc': 'Play 10 games',
        'icon': '🎯',
        'tier': 'bronze',
        'secret': False
    },
    'games_50': {
        'name': 'Addicted',
        'desc': 'Play 50 games',
        'icon': '🔥',
        'tier': 'silver',
        'secret': False
    },
    'games_100': {
        'name': 'Obsessed',
        'desc': 'Play 100 games',
        'icon': '💀',
        'tier': 'gold',
        'secret': False
    },
    'hold_master': {
        'name': 'Hold Master',
        'desc': 'Use hold 50 times',
        'icon': '🤲',
        'tier': 'bronze',
        'secret': False
    },
    'hard_dropper': {
        'name': 'Hard Dropper',
        'desc': 'Hard drop 100 times',
        'icon': '⬇️',
        'tier': 'bronze',
        'secret': False
    },
    'back_to_back': {
        'name': 'Back to Back',
        'desc': 'Get 2 Tetrises in a row',
        'icon': '🔄',
        'tier': 'silver',
        'secret': False
    },
    'triple_tetris': {
        'name': 'Triple Threat',
        'desc': 'Get 3 Tetrises in one game',
        'icon': '3️⃣',
        'tier': 'gold',
        'secret': False
    },
    'no_hold': {
        'name': 'Purist',
        'desc': 'Score 10,000 without using hold',
        'icon': '🧘',
        'tier': 'gold',
        'secret': True
    },
    'speed_start': {
        'name': 'Fast Starter',
        'desc': 'Clear 4 lines in first 30 seconds',
        'icon': '🚀',
        'tier': 'silver',
        'secret': True
    }
}

# ============================================================
# SAVE DATA CLASS
# ============================================================
@dataclass
class SaveData:
    # Settings
    music_volume: float = 0.3
    sfx_volume: float = 0.5
    music_enabled: bool = True
    sfx_enabled: bool = True
    
    # Statistics
    total_games: int = 0
    total_lines: int = 0
    total_tetrises: int = 0
    total_score: int = 0
    high_score: int = 0
    max_level: int = 1
    total_holds: int = 0
    total_hard_drops: int = 0
    play_time_seconds: int = 0
    
    # Trophies (list of unlocked trophy IDs)
    unlocked_trophies: List[str] = field(default_factory=list)
    trophy_timestamps: Dict[str, str] = field(default_factory=dict)
    
    # Last played
    last_played: str = ""
    
    def to_dict(self) -> dict:
        return {
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'music_enabled': self.music_enabled,
            'sfx_enabled': self.sfx_enabled,
            'total_games': self.total_games,
            'total_lines': self.total_lines,
            'total_tetrises': self.total_tetrises,
            'total_score': self.total_score,
            'high_score': self.high_score,
            'max_level': self.max_level,
            'total_holds': self.total_holds,
            'total_hard_drops': self.total_hard_drops,
            'play_time_seconds': self.play_time_seconds,
            'unlocked_trophies': self.unlocked_trophies,
            'trophy_timestamps': self.trophy_timestamps,
            'last_played': self.last_played
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SaveData':
        return cls(
            music_volume=data.get('music_volume', 0.3),
            sfx_volume=data.get('sfx_volume', 0.5),
            music_enabled=data.get('music_enabled', True),
            sfx_enabled=data.get('sfx_enabled', True),
            total_games=data.get('total_games', 0),
            total_lines=data.get('total_lines', 0),
            total_tetrises=data.get('total_tetrises', 0),
            total_score=data.get('total_score', 0),
            high_score=data.get('high_score', 0),
            max_level=data.get('max_level', 1),
            total_holds=data.get('total_holds', 0),
            total_hard_drops=data.get('total_hard_drops', 0),
            play_time_seconds=data.get('play_time_seconds', 0),
            unlocked_trophies=data.get('unlocked_trophies', []),
            trophy_timestamps=data.get('trophy_timestamps', {}),
            last_played=data.get('last_played', '')
        )

def load_save() -> SaveData:
    """Load save data from JSON file"""
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                return SaveData.from_dict(data)
    except Exception as e:
        print(f"Could not load save file: {e}")
    
    return SaveData()

def save_game(save_data: SaveData):
    """Save data to JSON file"""
    try:
        save_data.last_played = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(SAVE_FILE, 'w') as f:
            json.dump(save_data.to_dict(), f, indent=2)
        
        print(f"Game saved to: {SAVE_FILE}")
    except Exception as e:
        print(f"Could not save game: {e}")

# ============================================================
# TETROMINO DEFINITIONS
# ============================================================
SHAPES = {
    'I': {
        'color': NES_CYAN,
        'rotations': [
            [(0,1), (1,1), (2,1), (3,1)],
            [(2,0), (2,1), (2,2), (2,3)],
            [(0,2), (1,2), (2,2), (3,2)],
            [(1,0), (1,1), (1,2), (1,3)]
        ]
    },
    'O': {
        'color': NES_YELLOW,
        'rotations': [[(1,0), (2,0), (1,1), (2,1)]]
    },
    'T': {
        'color': NES_PURPLE,
        'rotations': [
            [(1,0), (0,1), (1,1), (2,1)],
            [(1,0), (1,1), (2,1), (1,2)],
            [(0,1), (1,1), (2,1), (1,2)],
            [(1,0), (0,1), (1,1), (1,2)]
        ]
    },
    'S': {
        'color': NES_GREEN,
        'rotations': [
            [(1,0), (2,0), (0,1), (1,1)],
            [(1,0), (1,1), (2,1), (2,2)],
            [(1,1), (2,1), (0,2), (1,2)],
            [(0,0), (0,1), (1,1), (1,2)]
        ]
    },
    'Z': {
        'color': NES_RED,
        'rotations': [
            [(0,0), (1,0), (1,1), (2,1)],
            [(2,0), (1,1), (2,1), (1,2)],
            [(0,1), (1,1), (1,2), (2,2)],
            [(1,0), (0,1), (1,1), (0,2)]
        ]
    },
    'J': {
        'color': NES_BLUE,
        'rotations': [
            [(0,0), (0,1), (1,1), (2,1)],
            [(1,0), (2,0), (1,1), (1,2)],
            [(0,1), (1,1), (2,1), (2,2)],
            [(1,0), (1,1), (0,2), (1,2)]
        ]
    },
    'L': {
        'color': NES_ORANGE,
        'rotations': [
            [(2,0), (0,1), (1,1), (2,1)],
            [(1,0), (1,1), (1,2), (2,2)],
            [(0,1), (1,1), (2,1), (0,2)],
            [(0,0), (1,0), (1,1), (1,2)]
        ]
    }
}

# ============================================================
# SOUND ENGINE
# ============================================================
class FamicomSoundEngine:
    def __init__(self, save_data: SaveData):
        self.sample_rate = 44100
        self.save_data = save_data
        
        self.music_channel = pygame.mixer.Channel(0)
        self.sfx_channel = pygame.mixer.Channel(1)
        
        self.sounds = {}
        self._generate_sfx()
        self.korobeiniki = self._generate_korobeiniki()
        self.gameover_music = self._generate_gameover()
        self.trophy_sound = self._generate_trophy_sound()
        
        self.music_playing = False
        self._apply_volumes()
    
    def _apply_volumes(self):
        self.music_channel.set_volume(self.save_data.music_volume if self.save_data.music_enabled else 0)
        self.sfx_channel.set_volume(self.save_data.sfx_volume if self.save_data.sfx_enabled else 0)
    
    def set_music_volume(self, vol: float):
        self.save_data.music_volume = max(0.0, min(1.0, vol))
        self._apply_volumes()
    
    def set_sfx_volume(self, vol: float):
        self.save_data.sfx_volume = max(0.0, min(1.0, vol))
        self._apply_volumes()
    
    def toggle_music(self):
        self.save_data.music_enabled = not self.save_data.music_enabled
        self._apply_volumes()
        if not self.save_data.music_enabled:
            self.music_channel.stop()
    
    def toggle_sfx(self):
        self.save_data.sfx_enabled = not self.save_data.sfx_enabled
        self._apply_volumes()
    
    def _square_wave(self, frequency: float, duration: float, duty: float = 0.5, volume: float = 0.15) -> array.array:
        n_samples = int(self.sample_rate * duration)
        samples = array.array('h')
        
        for i in range(n_samples):
            t = i / self.sample_rate
            phase = (t * frequency) % 1.0
            wave = 1.0 if phase < duty else -1.0
            progress = i / n_samples
            env = max(0, 1.0 - progress * 0.3)
            sample = int(wave * env * volume * 32767)
            samples.append(max(-32767, min(32767, sample)))
        
        return samples
    
    def _generate_sfx(self):
        self.sounds['move'] = pygame.mixer.Sound(buffer=self._square_wave(800, 0.03, 0.25).tobytes())
        self.sounds['rotate'] = pygame.mixer.Sound(buffer=self._square_wave(1000, 0.04, 0.25).tobytes())
        self.sounds['land'] = pygame.mixer.Sound(buffer=self._square_wave(200, 0.08, 0.5).tobytes())
        self.sounds['clear'] = pygame.mixer.Sound(buffer=self._square_wave(600, 0.1, 0.5).tobytes())
        
        tetris_data = array.array('h')
        for freq in [523, 659, 784, 1047]:
            tetris_data.extend(self._square_wave(freq, 0.1, 0.5))
        self.sounds['tetris'] = pygame.mixer.Sound(buffer=tetris_data.tobytes())
        
        levelup_data = array.array('h')
        for freq in [440, 554, 659, 880]:
            levelup_data.extend(self._square_wave(freq, 0.08, 0.25))
        self.sounds['levelup'] = pygame.mixer.Sound(buffer=levelup_data.tobytes())
        
        self.sounds['drop'] = pygame.mixer.Sound(buffer=self._square_wave(150, 0.05, 0.5).tobytes())
        self.sounds['hold'] = pygame.mixer.Sound(buffer=self._square_wave(660, 0.06, 0.25).tobytes())
        self.sounds['select'] = pygame.mixer.Sound(buffer=self._square_wave(880, 0.08, 0.25).tobytes())
        self.sounds['menu_move'] = pygame.mixer.Sound(buffer=self._square_wave(440, 0.04, 0.25).tobytes())
    
    def _generate_trophy_sound(self) -> pygame.mixer.Sound:
        """Xbox achievement-style sound"""
        data = array.array('h')
        # Ascending arpeggio
        for freq in [523, 659, 784, 1047, 1319]:
            data.extend(self._square_wave(freq, 0.12, 0.5, 0.2))
        return pygame.mixer.Sound(buffer=data.tobytes())
    
    def _generate_korobeiniki(self) -> pygame.mixer.Sound:
        tempo = 140
        beat = 60.0 / tempo
        
        # Full Korobeiniki - doubled for seamless looping
        melody_single = [
            ('E5', beat), ('B4', beat/2), ('C5', beat/2), ('D5', beat), ('C5', beat/2), ('B4', beat/2),
            ('A4', beat), ('A4', beat/2), ('C5', beat/2), ('E5', beat), ('D5', beat/2), ('C5', beat/2),
            ('B4', beat*1.5), ('C5', beat/2), ('D5', beat), ('E5', beat),
            ('C5', beat), ('A4', beat), ('A4', beat*2),
            ('R', beat/2), ('D5', beat), ('F5', beat/2), ('A5', beat), ('G5', beat/2), ('F5', beat/2),
            ('E5', beat*1.5), ('C5', beat/2), ('E5', beat), ('D5', beat/2), ('C5', beat/2),
            ('B4', beat), ('B4', beat/2), ('C5', beat/2), ('D5', beat), ('E5', beat),
            ('C5', beat), ('A4', beat), ('A4', beat*2),
        ]
        melody = melody_single * 2  # Double for longer seamless loop
        
        samples = array.array('h')
        for note, duration in melody:
            freq = self._note_to_freq(note)
            if freq > 0:
                samples.extend(self._square_wave(freq, duration * 0.9, 0.5))
                silence = array.array('h', [0] * int(self.sample_rate * duration * 0.1))
                samples.extend(silence)
            else:
                silence = array.array('h', [0] * int(self.sample_rate * duration))
                samples.extend(silence)
        
        return pygame.mixer.Sound(buffer=samples.tobytes())
    
    def _generate_gameover(self) -> pygame.mixer.Sound:
        beat = 0.4
        notes = [('C5', beat), ('B4', beat), ('A4', beat), ('G4', beat), ('F4', beat), ('E4', beat*2)]
        samples = array.array('h')
        for note, duration in notes:
            samples.extend(self._square_wave(self._note_to_freq(note), duration, 0.5))
        return pygame.mixer.Sound(buffer=samples.tobytes())
    
    def _note_to_freq(self, note: str) -> float:
        notes = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
        if note == 'R':
            return 0
        name = note[:-1]
        octave = int(note[-1])
        semitone = notes.get(name, 0)
        return 440.0 * (2.0 ** ((semitone - 9 + (octave - 4) * 12) / 12.0))
    
    def play_sfx(self, name: str):
        if self.save_data.sfx_enabled and name in self.sounds:
            self.sfx_channel.play(self.sounds[name])
    
    def play_trophy(self):
        if self.save_data.sfx_enabled:
            self.sfx_channel.play(self.trophy_sound)
    
    def start_music(self):
        if self.save_data.music_enabled:
            self.music_channel.play(self.korobeiniki, loops=-1)
            self.music_playing = True
    
    def stop_music(self):
        self.music_channel.stop()
        self.music_playing = False
    
    def play_gameover(self):
        self.stop_music()
        if self.save_data.sfx_enabled:
            self.sfx_channel.play(self.gameover_music)

# ============================================================
# GAME STATES
# ============================================================
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    OPTIONS = auto()
    TROPHIES = auto()
    CREDITS = auto()

class MenuOption(Enum):
    START = 0
    OPTIONS = 1
    TROPHIES = 2
    CREDITS = 3
    QUIT = 4

# ============================================================
# TROPHY MANAGER
# ============================================================
class TrophyManager:
    def __init__(self, save_data: SaveData, sound_engine):
        self.save_data = save_data
        self.sound = sound_engine
        self.pending_trophies = []  # Queue of trophies to show
        self.display_timer = 0
        self.current_display = None
    
    def check_and_unlock(self, trophy_id: str) -> bool:
        """Check if trophy should be unlocked"""
        if trophy_id not in self.save_data.unlocked_trophies and trophy_id in TROPHIES:
            self.save_data.unlocked_trophies.append(trophy_id)
            self.save_data.trophy_timestamps[trophy_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.pending_trophies.append(trophy_id)
            self.sound.play_trophy()
            return True
        return False
    
    def check_all(self, engine, session_stats: dict):
        """Check all trophy conditions"""
        sd = self.save_data
        
        # First game
        if sd.total_games >= 1:
            self.check_and_unlock('first_game')
        
        # Lines
        if sd.total_lines >= 1:
            self.check_and_unlock('first_line')
        if sd.total_lines >= 10:
            self.check_and_unlock('lines_10')
        if sd.total_lines >= 50:
            self.check_and_unlock('lines_50')
        if sd.total_lines >= 100:
            self.check_and_unlock('lines_100')
        
        # Tetrises
        if sd.total_tetrises >= 1:
            self.check_and_unlock('first_tetris')
        
        # Score
        if sd.high_score >= 1000:
            self.check_and_unlock('score_1000')
        if sd.high_score >= 10000:
            self.check_and_unlock('score_10000')
        if sd.high_score >= 50000:
            self.check_and_unlock('score_50000')
        if sd.high_score >= 100000:
            self.check_and_unlock('score_100000')
        
        # Levels
        if sd.max_level >= 5:
            self.check_and_unlock('level_5')
        if sd.max_level >= 10:
            self.check_and_unlock('level_10')
        if sd.max_level >= 15:
            self.check_and_unlock('level_15')
        if sd.max_level >= 20:
            self.check_and_unlock('level_20')
        
        # Games played
        if sd.total_games >= 10:
            self.check_and_unlock('games_10')
        if sd.total_games >= 50:
            self.check_and_unlock('games_50')
        if sd.total_games >= 100:
            self.check_and_unlock('games_100')
        
        # Holds
        if sd.total_holds >= 50:
            self.check_and_unlock('hold_master')
        
        # Hard drops
        if sd.total_hard_drops >= 100:
            self.check_and_unlock('hard_dropper')
        
        # Session-specific
        if session_stats.get('tetrises_in_game', 0) >= 3:
            self.check_and_unlock('triple_tetris')
        
        if session_stats.get('back_to_back_tetris', False):
            self.check_and_unlock('back_to_back')
        
        if session_stats.get('no_hold_10k', False):
            self.check_and_unlock('no_hold')
    
    def update(self):
        """Update trophy display"""
        if self.current_display:
            self.display_timer -= 1
            if self.display_timer <= 0:
                self.current_display = None
        
        if not self.current_display and self.pending_trophies:
            self.current_display = self.pending_trophies.pop(0)
            self.display_timer = 180  # 3 seconds at 60fps
    
    def draw_notification(self, surface):
        """Draw trophy unlock notification"""
        if self.current_display and self.current_display in TROPHIES:
            trophy = TROPHIES[self.current_display]
            
            # Slide in animation
            progress = min(1.0, (180 - self.display_timer) / 20)
            slide_y = int(-60 + progress * 60)
            
            if self.display_timer < 30:
                slide_y = int((30 - self.display_timer) / 30 * -60)
            
            # Background box
            box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, slide_y, 300, 50)
            pygame.draw.rect(surface, NES_DARK_GRAY, box_rect)
            pygame.draw.rect(surface, self._tier_color(trophy['tier']), box_rect, 3)
            
            # Trophy icon and text
            icon_text = font_large.render(trophy['icon'], True, NES_WHITE)
            surface.blit(icon_text, (box_rect.x + 10, box_rect.y + 8))
            
            title_text = font_medium.render("TROPHY UNLOCKED!", True, self._tier_color(trophy['tier']))
            surface.blit(title_text, (box_rect.x + 50, box_rect.y + 5))
            
            name_text = font_small.render(trophy['name'], True, NES_WHITE)
            surface.blit(name_text, (box_rect.x + 50, box_rect.y + 28))
    
    def _tier_color(self, tier: str) -> Tuple[int, int, int]:
        return {'bronze': NES_BRONZE, 'silver': NES_SILVER, 'gold': NES_GOLD}.get(tier, NES_WHITE)

# ============================================================
# TETRIS ENGINE
# ============================================================
class TetrisEngine:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = None
        self.current_shape = None
        self.current_x = 0
        self.current_y = 0
        self.rotation = 0
        self.bag = []
        self.next_piece = None
        self.hold_piece = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines = 0
        self.drop_timer = 0
        self.lock_timer = 0
        self.lock_active = False
        self.clearing_lines = []
        self.clear_timer = 0
        self.pending_clear_sound = 0  # For immediate sound sync
        
        # Session stats
        self.tetrises_in_game = 0
        self.last_clear_was_tetris = False
        self.back_to_back_tetris = False
        self.holds_used = 0
        self.hard_drops_used = 0
        self.game_time = 0
        
        self._fill_bag()
        self.next_piece = self._get_from_bag()
        self._spawn_piece()
    
    def _fill_bag(self):
        self.bag = list(SHAPES.keys())
        random.shuffle(self.bag)
    
    def _get_from_bag(self) -> str:
        if not self.bag:
            self._fill_bag()
        return self.bag.pop()
    
    def _spawn_piece(self):
        self.current_shape = self.next_piece
        self.next_piece = self._get_from_bag()
        self.current_piece = SHAPES[self.current_shape]
        self.rotation = 0
        self.current_x = 3
        self.current_y = 0
        self.lock_active = False
        self.lock_timer = 0
        self.can_hold = True
        
        if self._check_collision(self.current_x, self.current_y, self.rotation):
            return False
        return True
    
    def _get_cells(self, x: int, y: int, rotation: int) -> List[Tuple[int, int]]:
        rotations = self.current_piece['rotations']
        rot = rotation % len(rotations)
        return [(x + cx, y + cy) for cx, cy in rotations[rot]]
    
    def _check_collision(self, x: int, y: int, rotation: int) -> bool:
        cells = self._get_cells(x, y, rotation)
        for cx, cy in cells:
            if cx < 0 or cx >= BOARD_WIDTH or cy >= BOARD_HEIGHT:
                return True
            if cy >= 0 and self.board[cy][cx] is not None:
                return True
        return False
    
    def _lock_piece(self):
        cells = self._get_cells(self.current_x, self.current_y, self.rotation)
        color = self.current_piece['color']
        
        for cx, cy in cells:
            if 0 <= cy < BOARD_HEIGHT and 0 <= cx < BOARD_WIDTH:
                self.board[cy][cx] = color
        
        self._check_lines()
        
        if not self._spawn_piece():
            return False
        return True
    
    def _check_lines(self):
        lines_to_clear = []
        for y in range(BOARD_HEIGHT):
            if all(cell is not None for cell in self.board[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            self.clearing_lines = lines_to_clear
            self.clear_timer = 20
            # Flag for immediate sound playback (fixes sound/animation sync)
            self.pending_clear_sound = len(lines_to_clear)
            
            num = len(lines_to_clear)
            if num == 4:
                self.tetrises_in_game += 1
                if self.last_clear_was_tetris:
                    self.back_to_back_tetris = True
                self.last_clear_was_tetris = True
            else:
                self.last_clear_was_tetris = False
    
    def _clear_lines(self):
        num_lines = len(self.clearing_lines)
        
        for y in sorted(self.clearing_lines, reverse=True):
            del self.board[y]
            self.board.insert(0, [None for _ in range(BOARD_WIDTH)])
        
        self.score += SCORE_TABLE.get(num_lines, 0) * self.level
        self.lines += num_lines
        
        new_level = (self.lines // 10) + 1
        if new_level > self.level:
            self.level = new_level
        
        self.clearing_lines = []
        return num_lines
    
    def move(self, dx: int, dy: int) -> bool:
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        if not self._check_collision(new_x, new_y, self.rotation):
            self.current_x = new_x
            self.current_y = new_y
            if self.lock_active and dy == 0:
                self.lock_timer = 0
            return True
        return False
    
    def rotate(self, direction: int = 1) -> bool:
        new_rotation = (self.rotation + direction) % len(self.current_piece['rotations'])
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)]
        
        for kick_x, kick_y in kicks:
            if not self._check_collision(self.current_x + kick_x, self.current_y + kick_y, new_rotation):
                self.current_x += kick_x
                self.current_y += kick_y
                self.rotation = new_rotation
                if self.lock_active:
                    self.lock_timer = 0
                return True
        return False
    
    def hard_drop(self) -> int:
        drop_distance = 0
        while self.move(0, 1):
            drop_distance += 1
        self.score += drop_distance * 2
        self.hard_drops_used += 1
        return drop_distance
    
    def soft_drop(self) -> bool:
        if self.move(0, 1):
            self.score += 1
            return True
        return False
    
    def hold(self) -> bool:
        if not self.can_hold:
            return False
        self.can_hold = False
        # Only count successful holds for trophy tracking
        self.holds_used += 1
        
        if self.hold_piece is None:
            self.hold_piece = self.current_shape
            self._spawn_piece()
        else:
            self.hold_piece, self.current_shape = self.current_shape, self.hold_piece
            self.current_piece = SHAPES[self.current_shape]
            self.rotation = 0
            self.current_x = 3
            self.current_y = 0
        return True
    
    def get_ghost_y(self) -> int:
        ghost_y = self.current_y
        while not self._check_collision(self.current_x, ghost_y + 1, self.rotation):
            ghost_y += 1
        return ghost_y
    
    def update(self) -> Tuple[bool, int]:
        """Returns (game_continues, lines_cleared_this_frame)"""
        self.game_time += 1
        lines_cleared = 0
        
        if self.clearing_lines:
            self.clear_timer -= 1
            if self.clear_timer <= 0:
                lines_cleared = self._clear_lines()
            return True, lines_cleared
        
        self.drop_timer += 1
        drop_speed = LEVEL_SPEEDS[min(self.level - 1, len(LEVEL_SPEEDS) - 1)]
        
        if self.drop_timer >= drop_speed:
            self.drop_timer = 0
            if not self.move(0, 1):
                if not self.lock_active:
                    self.lock_active = True
                    self.lock_timer = 0
        
        if self.lock_active:
            self.lock_timer += 1
            if self.lock_timer >= LOCK_DELAY:
                if not self._lock_piece():
                    return False, 0
        
        return True, lines_cleared

# ============================================================
# DRAWING FUNCTIONS
# ============================================================
def draw_cell(surface, x: int, y: int, color: Tuple[int, int, int], ghost: bool = False):
    rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
    if ghost:
        pygame.draw.rect(surface, color, rect, 1)
    else:
        pygame.draw.rect(surface, color, rect)
        highlight = tuple(min(255, c + 60) for c in color)
        shadow = tuple(max(0, c - 60) for c in color)
        pygame.draw.line(surface, highlight, (x, y), (x + CELL_SIZE - 1, y))
        pygame.draw.line(surface, highlight, (x, y), (x, y + CELL_SIZE - 1))
        pygame.draw.line(surface, shadow, (x + CELL_SIZE - 1, y), (x + CELL_SIZE - 1, y + CELL_SIZE - 1))
        pygame.draw.line(surface, shadow, (x, y + CELL_SIZE - 1), (x + CELL_SIZE - 1, y + CELL_SIZE - 1))

def draw_board(surface, engine: TetrisEngine):
    board_rect = pygame.Rect(BOARD_X - 2, BOARD_Y - 2, BOARD_WIDTH * CELL_SIZE + 4, BOARD_HEIGHT * CELL_SIZE + 4)
    pygame.draw.rect(surface, NES_BORDER, board_rect, 2)
    
    for x in range(BOARD_WIDTH + 1):
        px = BOARD_X + x * CELL_SIZE
        pygame.draw.line(surface, NES_DARK_GRAY, (px, BOARD_Y), (px, BOARD_Y + BOARD_HEIGHT * CELL_SIZE))
    for y in range(BOARD_HEIGHT + 1):
        py = BOARD_Y + y * CELL_SIZE
        pygame.draw.line(surface, NES_DARK_GRAY, (BOARD_X, py), (BOARD_X + BOARD_WIDTH * CELL_SIZE, py))
    
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if engine.board[y][x] is not None:
                if engine.clearing_lines and y in engine.clearing_lines:
                    if (engine.clear_timer // 4) % 2 == 0:
                        draw_cell(surface, BOARD_X + x * CELL_SIZE, BOARD_Y + y * CELL_SIZE, NES_WHITE)
                else:
                    draw_cell(surface, BOARD_X + x * CELL_SIZE, BOARD_Y + y * CELL_SIZE, engine.board[y][x])
    
    if engine.current_piece and not engine.clearing_lines:
        ghost_y = engine.get_ghost_y()
        cells = engine._get_cells(engine.current_x, ghost_y, engine.rotation)
        for cx, cy in cells:
            if 0 <= cy < BOARD_HEIGHT:
                draw_cell(surface, BOARD_X + cx * CELL_SIZE, BOARD_Y + cy * CELL_SIZE, engine.current_piece['color'], ghost=True)
        
        cells = engine._get_cells(engine.current_x, engine.current_y, engine.rotation)
        for cx, cy in cells:
            if 0 <= cy < BOARD_HEIGHT:
                draw_cell(surface, BOARD_X + cx * CELL_SIZE, BOARD_Y + cy * CELL_SIZE, engine.current_piece['color'])

def draw_piece_preview(surface, shape: str, x: int, y: int, size: int = CELL_SIZE):
    if shape is None:
        return
    piece = SHAPES[shape]
    rotations = piece['rotations'][0]
    color = piece['color']
    
    # Scale up small pieces (O is 2x2, others vary)
    # Use larger cells for O-piece to make it more visible
    actual_size = size
    if shape == 'O':
        actual_size = int(size * 1.3)  # Scale up O-piece
    elif shape == 'I':
        actual_size = int(size * 0.9)  # Slightly smaller for I to fit
    
    min_x = min(cx for cx, cy in rotations)
    max_x = max(cx for cx, cy in rotations)
    min_y = min(cy for cx, cy in rotations)
    max_y = max(cy for cx, cy in rotations)
    
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    
    # Center in preview box
    total_width = width * actual_size
    total_height = height * actual_size
    offset_x = x + (4 * size - total_width) // 2
    offset_y = y + (4 * size - total_height) // 2
    
    for cx, cy in rotations:
        px = offset_x + (cx - min_x) * actual_size
        py = offset_y + (cy - min_y) * actual_size
        rect = pygame.Rect(px, py, actual_size - 1, actual_size - 1)
        pygame.draw.rect(surface, color, rect)
        # Add highlight for 3D effect
        pygame.draw.line(surface, tuple(min(255, c + 50) for c in color), 
                        (px, py), (px + actual_size - 2, py))
        pygame.draw.line(surface, tuple(min(255, c + 50) for c in color), 
                        (px, py), (px, py + actual_size - 2))

def draw_sidebar(surface, engine: TetrisEngine, save_data: SaveData):
    # Score
    score_text = font_medium.render("SCORE", True, NES_WHITE)
    surface.blit(score_text, (20, 40))
    score_val = font_large.render(f"{engine.score:06d}", True, NES_WHITE)
    surface.blit(score_val, (20, 60))
    
    # High score
    hi_text = font_small.render(f"HI: {save_data.high_score:06d}", True, NES_GRAY)
    surface.blit(hi_text, (20, 95))
    
    # Level
    level_text = font_medium.render("LEVEL", True, NES_WHITE)
    surface.blit(level_text, (20, 120))
    level_val = font_large.render(f"{engine.level:02d}", True, NES_WHITE)
    surface.blit(level_val, (20, 140))
    
    # Lines
    lines_text = font_medium.render("LINES", True, NES_WHITE)
    surface.blit(lines_text, (20, 180))
    lines_val = font_large.render(f"{engine.lines:03d}", True, NES_WHITE)
    surface.blit(lines_val, (20, 200))
    
    # Hold box
    hold_x, hold_y = 20, 250
    pygame.draw.rect(surface, NES_BORDER, (hold_x - 5, hold_y - 20, 80, 80), 2)
    hold_label = font_small.render("HOLD", True, NES_WHITE)
    surface.blit(hold_label, (hold_x + 18, hold_y - 18))
    if engine.hold_piece:
        draw_piece_preview(surface, engine.hold_piece, hold_x, hold_y, CELL_SIZE - 4)
    
    # Next box
    next_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 30
    next_y = 60
    pygame.draw.rect(surface, NES_BORDER, (next_x - 5, next_y - 20, 90, 90), 2)
    next_label = font_small.render("NEXT", True, NES_WHITE)
    surface.blit(next_label, (next_x + 25, next_y - 18))
    draw_piece_preview(surface, engine.next_piece, next_x + 5, next_y + 5, CELL_SIZE - 2)
    
    # Controls hint
    controls_y = 170
    controls = ["← → Move", "↓ Drop", "↑/X Rotate", "SPACE Hard", "C Hold", "P Pause"]
    for i, line in enumerate(controls):
        text = font_small.render(line, True, NES_DARK_GRAY)
        surface.blit(text, (next_x - 5, controls_y + i * 14))

def draw_menu(surface, selected: int, save_data: SaveData):
    surface.fill(NES_BG)
    
    # Title
    title1 = font_title.render("ULTRA!", True, NES_CYAN)
    title2 = font_title.render("TETRIS", True, NES_RED)
    surface.blit(title1, (SCREEN_WIDTH // 2 - title1.get_width() // 2, 40))
    surface.blit(title2, (SCREEN_WIDTH // 2 - title2.get_width() // 2, 85))
    
    version = font_small.render("PYGAME PORT v1.0", True, NES_GRAY)
    surface.blit(version, (SCREEN_WIDTH // 2 - version.get_width() // 2, 130))
    
    # Menu options
    options = ["START GAME", "OPTIONS", "TROPHIES", "CREDITS", "QUIT"]
    for i, opt in enumerate(options):
        color = NES_YELLOW if i == selected else NES_WHITE
        text = font_medium.render(opt, True, color)
        y = 170 + i * 35
        surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        if i == selected:
            pygame.draw.rect(surface, color, (SCREEN_WIDTH // 2 - text.get_width() // 2 - 20, y + 5, 10, 10))
    
    # Stats preview
    stats_y = 350
    hi_text = font_small.render(f"HIGH SCORE: {save_data.high_score:,}", True, NES_GRAY)
    surface.blit(hi_text, (SCREEN_WIDTH // 2 - hi_text.get_width() // 2, stats_y))
    
    trophies_unlocked = len(save_data.unlocked_trophies)
    trophies_total = len(TROPHIES)
    trophy_text = font_small.render(f"TROPHIES: {trophies_unlocked}/{trophies_total}", True, NES_GOLD)
    surface.blit(trophy_text, (SCREEN_WIDTH // 2 - trophy_text.get_width() // 2, stats_y + 18))

def draw_options(surface, selected: int, save_data: SaveData, sound: FamicomSoundEngine):
    surface.fill(NES_BG)
    
    title = font_large.render("OPTIONS", True, NES_WHITE)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
    
    options = [
        f"MUSIC VOLUME: {int(save_data.music_volume * 100)}%",
        f"SFX VOLUME: {int(save_data.sfx_volume * 100)}%",
        f"MUSIC: {'ON' if save_data.music_enabled else 'OFF'}",
        f"SFX: {'ON' if save_data.sfx_enabled else 'OFF'}",
        "BACK"
    ]
    
    for i, opt in enumerate(options):
        color = NES_YELLOW if i == selected else NES_WHITE
        text = font_medium.render(opt, True, color)
        y = 100 + i * 40
        surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
        if i == selected:
            pygame.draw.rect(surface, color, (SCREEN_WIDTH // 2 - 150, y + 5, 10, 10))
            if i < 2:
                # Volume bar
                bar_x = SCREEN_WIDTH // 2 + 80
                bar_width = 100
                vol = save_data.music_volume if i == 0 else save_data.sfx_volume
                pygame.draw.rect(surface, NES_DARK_GRAY, (bar_x, y + 3, bar_width, 14))
                pygame.draw.rect(surface, NES_GREEN, (bar_x, y + 3, int(bar_width * vol), 14))
    
    hint = font_small.render("← → to adjust, ENTER to toggle/select", True, NES_GRAY)
    surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 350))

def draw_trophies(surface, save_data: SaveData, scroll: int):
    surface.fill(NES_BG)
    
    title = font_large.render("TROPHIES", True, NES_GOLD)
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
    
    unlocked = len(save_data.unlocked_trophies)
    total = len(TROPHIES)
    count_text = font_medium.render(f"{unlocked}/{total} Unlocked", True, NES_WHITE)
    surface.blit(count_text, (SCREEN_WIDTH // 2 - count_text.get_width() // 2, 55))
    
    # Trophy list
    y = 90
    trophy_list = list(TROPHIES.items())
    visible_start = scroll
    visible_end = min(scroll + 8, len(trophy_list))
    
    for i in range(visible_start, visible_end):
        trophy_id, trophy = trophy_list[i]
        is_unlocked = trophy_id in save_data.unlocked_trophies
        
        # Background box
        box_y = y + (i - scroll) * 36
        tier_color = {'bronze': NES_BRONZE, 'silver': NES_SILVER, 'gold': NES_GOLD}.get(trophy['tier'], NES_WHITE)
        
        if is_unlocked:
            pygame.draw.rect(surface, NES_DARK_GRAY, (50, box_y, SCREEN_WIDTH - 100, 32))
            pygame.draw.rect(surface, tier_color, (50, box_y, SCREEN_WIDTH - 100, 32), 2)
            
            icon = font_medium.render(trophy['icon'], True, NES_WHITE)
            surface.blit(icon, (60, box_y + 4))
            
            name = font_medium.render(trophy['name'], True, tier_color)
            surface.blit(name, (95, box_y + 2))
            
            desc = font_small.render(trophy['desc'], True, NES_GRAY)
            surface.blit(desc, (95, box_y + 18))
        else:
            pygame.draw.rect(surface, (30, 30, 30), (50, box_y, SCREEN_WIDTH - 100, 32))
            pygame.draw.rect(surface, NES_DARK_GRAY, (50, box_y, SCREEN_WIDTH - 100, 32), 1)
            
            if trophy.get('secret', False):
                text = font_medium.render("??? SECRET ???", True, NES_DARK_GRAY)
            else:
                text = font_medium.render(f"🔒 {trophy['name']}", True, NES_DARK_GRAY)
            surface.blit(text, (60, box_y + 8))
    
    # Scroll hint
    if len(trophy_list) > 8:
        hint = font_small.render("↑↓ to scroll, ESC to return", True, NES_GRAY)
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 380))

def draw_credits(surface):
    surface.fill(NES_BG)
    
    # Centered copyright notices
    line1 = font_medium.render("© Samsoft 1999-2025", True, NES_WHITE)
    line2 = font_medium.render("© Tetris Company", True, NES_WHITE)
    
    # Center vertically and horizontally
    total_height = line1.get_height() + 20 + line2.get_height()
    start_y = (SCREEN_HEIGHT - total_height) // 2
    
    surface.blit(line1, (SCREEN_WIDTH // 2 - line1.get_width() // 2, start_y))
    surface.blit(line2, (SCREEN_WIDTH // 2 - line2.get_width() // 2, start_y + line1.get_height() + 20))
    
    # ESC hint at bottom
    hint = font_small.render("PRESS ESC TO RETURN", True, NES_GRAY)
    surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))

def draw_game_over(surface, engine: TetrisEngine, save_data: SaveData):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(NES_BG)
    overlay.set_alpha(180)
    surface.blit(overlay, (0, 0))
    
    go_text = font_title.render("GAME OVER", True, NES_RED)
    surface.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 100))
    
    score_text = font_large.render(f"SCORE: {engine.score:,}", True, NES_WHITE)
    surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 170))
    
    if engine.score >= save_data.high_score:
        new_hi = font_medium.render("NEW HIGH SCORE!", True, NES_GOLD)
        surface.blit(new_hi, (SCREEN_WIDTH // 2 - new_hi.get_width() // 2, 210))
    
    stats = [
        f"LEVEL: {engine.level}",
        f"LINES: {engine.lines}",
        f"TETRISES: {engine.tetrises_in_game}"
    ]
    for i, stat in enumerate(stats):
        text = font_medium.render(stat, True, NES_GRAY)
        surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 25))
    
    restart = font_medium.render("ENTER: Restart  ESC: Menu", True, NES_WHITE)
    surface.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 350))

def draw_pause(surface):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(NES_BG)
    overlay.set_alpha(180)
    surface.blit(overlay, (0, 0))
    
    pause_text = font_title.render("PAUSED", True, NES_WHITE)
    surface.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 180))
    
    resume = font_medium.render("PRESS P TO RESUME", True, NES_GRAY)
    surface.blit(resume, (SCREEN_WIDTH // 2 - resume.get_width() // 2, 250))

# ============================================================
# MAIN GAME
# ============================================================
def main():
    # Load save data
    save_data = load_save()
    
    # Create sound engine
    sound = FamicomSoundEngine(save_data)
    
    # Create trophy manager
    trophy_mgr = TrophyManager(save_data, sound)
    
    # Game engine
    engine = TetrisEngine()
    
    # State
    state = GameState.MENU
    menu_selection = 0
    options_selection = 0
    trophy_scroll = 0
    
    # DAS
    das_left = 0
    das_right = 0
    das_down = 0
    
    # Key cooldown
    key_cooldown = 0
    
    # Session stats
    session_start_time = 0
    
    running = True
    while running:
        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if state == GameState.MENU:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        menu_selection = (menu_selection - 1) % 5
                        sound.play_sfx('menu_move')
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        menu_selection = (menu_selection + 1) % 5
                        sound.play_sfx('menu_move')
                    elif event.key == pygame.K_RETURN:
                        sound.play_sfx('select')
                        if menu_selection == 0:  # Start
                            engine.reset()
                            save_data.total_games += 1
                            session_start_time = pygame.time.get_ticks()
                            state = GameState.PLAYING
                            sound.start_music()
                        elif menu_selection == 1:  # Options
                            state = GameState.OPTIONS
                            options_selection = 0
                        elif menu_selection == 2:  # Trophies
                            state = GameState.TROPHIES
                            trophy_scroll = 0
                        elif menu_selection == 3:  # Credits
                            state = GameState.CREDITS
                        elif menu_selection == 4:  # Quit
                            running = False
                
                elif state == GameState.OPTIONS:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        options_selection = (options_selection - 1) % 5
                        sound.play_sfx('menu_move')
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        options_selection = (options_selection + 1) % 5
                        sound.play_sfx('menu_move')
                    elif event.key == pygame.K_LEFT:
                        if options_selection == 0:
                            sound.set_music_volume(save_data.music_volume - 0.1)
                        elif options_selection == 1:
                            sound.set_sfx_volume(save_data.sfx_volume - 0.1)
                        sound.play_sfx('menu_move')
                    elif event.key == pygame.K_RIGHT:
                        if options_selection == 0:
                            sound.set_music_volume(save_data.music_volume + 0.1)
                        elif options_selection == 1:
                            sound.set_sfx_volume(save_data.sfx_volume + 0.1)
                        sound.play_sfx('menu_move')
                    elif event.key == pygame.K_RETURN:
                        sound.play_sfx('select')
                        if options_selection == 2:
                            sound.toggle_music()
                        elif options_selection == 3:
                            sound.toggle_sfx()
                        elif options_selection == 4:
                            state = GameState.MENU
                            save_game(save_data)
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU
                        save_game(save_data)
                
                elif state == GameState.TROPHIES:
                    if event.key == pygame.K_UP:
                        trophy_scroll = max(0, trophy_scroll - 1)
                    elif event.key == pygame.K_DOWN:
                        trophy_scroll = min(len(TROPHIES) - 8, trophy_scroll + 1)
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU
                
                elif state == GameState.CREDITS:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.MENU
                
                elif state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        state = GameState.MENU
                        sound.stop_music()
                        save_game(save_data)
                    elif event.key == pygame.K_p:
                        state = GameState.PAUSED
                        sound.stop_music()
                    elif event.key in (pygame.K_UP, pygame.K_x):
                        if engine.rotate(1):
                            sound.play_sfx('rotate')
                    elif event.key == pygame.K_z:
                        if engine.rotate(-1):
                            sound.play_sfx('rotate')
                    elif event.key == pygame.K_SPACE:
                        engine.hard_drop()
                        sound.play_sfx('drop')
                        save_data.total_hard_drops += 1
                        if not engine._lock_piece():
                            # Game over
                            session_time = (pygame.time.get_ticks() - session_start_time) // 1000
                            save_data.play_time_seconds += session_time
                            save_data.total_score += engine.score
                            save_data.total_lines += engine.lines
                            save_data.total_tetrises += engine.tetrises_in_game
                            if engine.score > save_data.high_score:
                                save_data.high_score = engine.score
                            if engine.level > save_data.max_level:
                                save_data.max_level = engine.level
                            
                            # Check trophies
                            session_stats = {
                                'tetrises_in_game': engine.tetrises_in_game,
                                'back_to_back_tetris': engine.back_to_back_tetris,
                                'no_hold_10k': engine.score >= 10000 and engine.holds_used == 0
                            }
                            trophy_mgr.check_all(engine, session_stats)
                            
                            save_game(save_data)
                            sound.play_gameover()
                            state = GameState.GAME_OVER
                    elif event.key == pygame.K_c:
                        if engine.hold():
                            sound.play_sfx('hold')
                            save_data.total_holds += 1
                
                elif state == GameState.PAUSED:
                    if event.key == pygame.K_p:
                        state = GameState.PLAYING
                        sound.start_music()
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU
                
                elif state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        engine.reset()
                        save_data.total_games += 1
                        session_start_time = pygame.time.get_ticks()
                        state = GameState.PLAYING
                        sound.start_music()
                    elif event.key == pygame.K_ESCAPE:
                        state = GameState.MENU
        
        # Continuous input (DAS)
        if state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_LEFT]:
                das_left += 1
                if das_left == 1 or (das_left > DAS_INITIAL_DELAY and das_left % DAS_REPEAT_RATE == 0):
                    if engine.move(-1, 0):
                        sound.play_sfx('move')
            else:
                das_left = 0
            
            if keys[pygame.K_RIGHT]:
                das_right += 1
                if das_right == 1 or (das_right > DAS_INITIAL_DELAY and das_right % DAS_REPEAT_RATE == 0):
                    if engine.move(1, 0):
                        sound.play_sfx('move')
            else:
                das_right = 0
            
            if keys[pygame.K_DOWN]:
                # 1G soft drop - 1 cell per frame when held (authentic Tetris)
                engine.soft_drop()
            else:
                das_down = 0
        
        # Update
        if state == GameState.PLAYING:
            game_ok, lines_cleared = engine.update()
            
            # Play sound IMMEDIATELY when lines detected (sync with animation start)
            if engine.pending_clear_sound > 0:
                if engine.pending_clear_sound == 4:
                    sound.play_sfx('tetris')
                else:
                    sound.play_sfx('clear')
                engine.pending_clear_sound = 0  # Reset flag
            
            # Update stats when lines actually cleared (after animation)
            if lines_cleared > 0:
                save_data.total_lines += lines_cleared
                if lines_cleared == 4:
                    save_data.total_tetrises += 1
                
                # Check level up
                old_level = (engine.lines - lines_cleared) // 10 + 1
                if engine.level > old_level:
                    sound.play_sfx('levelup')
            
            if not game_ok:
                # Game over
                session_time = (pygame.time.get_ticks() - session_start_time) // 1000
                save_data.play_time_seconds += session_time
                save_data.total_score += engine.score
                if engine.score > save_data.high_score:
                    save_data.high_score = engine.score
                if engine.level > save_data.max_level:
                    save_data.max_level = engine.level
                
                session_stats = {
                    'tetrises_in_game': engine.tetrises_in_game,
                    'back_to_back_tetris': engine.back_to_back_tetris,
                    'no_hold_10k': engine.score >= 10000 and engine.holds_used == 0
                }
                trophy_mgr.check_all(engine, session_stats)
                
                save_game(save_data)
                sound.play_gameover()
                state = GameState.GAME_OVER
        
        # Update trophy notifications
        trophy_mgr.update()
        
        # Draw
        screen.fill(NES_BG)
        
        if state == GameState.MENU:
            draw_menu(screen, menu_selection, save_data)
        
        elif state == GameState.OPTIONS:
            draw_options(screen, options_selection, save_data, sound)
        
        elif state == GameState.TROPHIES:
            draw_trophies(screen, save_data, trophy_scroll)
        
        elif state == GameState.CREDITS:
            draw_credits(screen)
        
        elif state in (GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER):
            draw_board(screen, engine)
            draw_sidebar(screen, engine, save_data)
            
            if state == GameState.PAUSED:
                draw_pause(screen)
            elif state == GameState.GAME_OVER:
                draw_game_over(screen, engine, save_data)
        
        # Trophy notification overlay
        trophy_mgr.draw_notification(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Final save
    save_game(save_data)
    pygame.quit()
    sys.exit()

# ============================================================
# ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  ULTRA!TETRIS — Pygame Port")
    print("  Samsoft • © The Tetris Company • Team Flames")
    print("=" * 50)
    print(f"  Save file: {SAVE_FILE}")
    print("=" * 50)
    main()
