#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                            ULTRA! TETRIS                                       ║
║                     Classic Russian Style Edition                              ║
║                                                                                ║
║  Featuring the legendary Korobeiniki theme music!                              ║
║  Python 3.13/3.14 + tkinter only - No external dependencies                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Controls:
  Left/Right - Move piece
  Down - Soft drop
  Up - Rotate clockwise
  Space - Hard drop
  C - Hold piece
  P - Pause
  R - Restart (when game over)
  M - Toggle Music
  ESC - Return to Menu
"""

import tkinter as tk
import math
import random
import struct
import wave
import io
import threading
import tempfile
import os
import sys
import subprocess

# =============================================================================
# GAME CONSTANTS
# =============================================================================

CELL_SIZE = 22
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
PREVIEW_SIZE = 4

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 520

BOARD_X = 30
BOARD_Y = 30

# Colors - Enhanced Tetris palette
COLORS = {
    'I': '#00FFFF',
    'O': '#FFFF00',
    'T': '#AA00FF',
    'S': '#00FF00',
    'Z': '#FF0000',
    'J': '#0000FF',
    'L': '#FF8800',
    'ghost': '#333333',
    'bg': '#000000',
    'grid': '#1a1a2e',
    'border': '#444444'
}

# Tetromino shapes
TETROMINOES = {
    'I': [
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 1), (1, 1), (2, 1), (3, 1)]
    ],
    'O': [
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)],
        [(0, 0), (0, 1), (1, 0), (1, 1)]
    ],
    'T': [
        [(0, 1), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 0), (1, 1), (2, 1)]
    ],
    'S': [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 1), (1, 2), (2, 0), (2, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)]
    ],
    'Z': [
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 2), (1, 1), (1, 2), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)]
    ],
    'J': [
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (0, 2), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 0), (2, 1)]
    ],
    'L': [
        [(0, 2), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (1, 2), (2, 0)],
        [(0, 0), (0, 1), (1, 1), (2, 1)]
    ]
}

LEVEL_SPEEDS = [800, 720, 630, 550, 470, 380, 300, 220, 130, 100]
SCORE_TABLE = {1: 100, 2: 300, 3: 500, 4: 800}


# =============================================================================
# KOROBEINIKI MUSIC SYNTHESIZER (Russian Tetris Theme)
# =============================================================================

class TetrisMusicSynthesizer:
    """Pure Python synthesizer for the Korobeiniki (Tetris theme) melody."""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.playing = False
        self.audio_thread = None
        self.temp_file = None
        
    def note_to_freq(self, note):
        """Convert note name to frequency."""
        notes = {
            'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61,
            'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
            'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
            'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
            'C5': 523.25, 'D5': 587.33, 'E5': 659.26, 'F5': 698.46,
            'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
            'R': 0  # Rest
        }
        return notes.get(note, 0)
    
    def generate_tone(self, freq, duration, volume=0.3):
        """Generate a square wave tone with envelope."""
        samples = int(self.sample_rate * duration)
        data = []
        
        # Attack/decay envelope
        attack = int(samples * 0.05)
        decay = int(samples * 0.1)
        
        for i in range(samples):
            # Envelope
            if i < attack:
                env = i / attack
            elif i > samples - decay:
                env = (samples - i) / decay
            else:
                env = 1.0
            
            if freq > 0:
                # Square wave with some harmonics for richer sound
                t = i / self.sample_rate
                val = 0
                # Fundamental + harmonics
                for h in range(1, 6, 2):  # Odd harmonics
                    val += math.sin(2 * math.pi * freq * h * t) / h
                val = max(-1, min(1, val * 0.5))  # Normalize
                sample = int(val * 32767 * volume * env)
            else:
                sample = 0
            
            data.append(struct.pack('<h', max(-32768, min(32767, sample))))
        
        return b''.join(data)
    
    def generate_korobeiniki(self):
        """Generate the complete Korobeiniki melody (Tetris Theme A)."""
        # Korobeiniki melody - the legendary Russian folk song
        # Format: (note, duration in beats)
        # BPM ~= 140, so quarter note = ~0.43s
        beat = 0.18  # Speed up for game feel
        
        melody = [
            # First phrase - "DUH DUH DUH"
            ('E5', 1), ('B4', 0.5), ('C5', 0.5), ('D5', 1), ('C5', 0.5), ('B4', 0.5),
            ('A4', 1), ('A4', 0.5), ('C5', 0.5), ('E5', 1), ('D5', 0.5), ('C5', 0.5),
            ('B4', 1.5), ('C5', 0.5), ('D5', 1), ('E5', 1),
            ('C5', 1), ('A4', 1), ('A4', 2),
            
            # Second phrase
            ('R', 0.5), ('D5', 1), ('F5', 0.5), ('A5', 1), ('G5', 0.5), ('F5', 0.5),
            ('E5', 1.5), ('C5', 0.5), ('E5', 1), ('D5', 0.5), ('C5', 0.5),
            ('B4', 1), ('B4', 0.5), ('C5', 0.5), ('D5', 1), ('E5', 1),
            ('C5', 1), ('A4', 1), ('A4', 2),
            
            # Repeat with variation
            ('E5', 1), ('B4', 0.5), ('C5', 0.5), ('D5', 1), ('C5', 0.5), ('B4', 0.5),
            ('A4', 1), ('A4', 0.5), ('C5', 0.5), ('E5', 1), ('D5', 0.5), ('C5', 0.5),
            ('B4', 1.5), ('C5', 0.5), ('D5', 1), ('E5', 1),
            ('C5', 1), ('A4', 1), ('A4', 2),
            
            # Bridge section
            ('E4', 2), ('C4', 2), ('D4', 2), ('B3', 2),
            ('C4', 2), ('A3', 2), ('G3', 2), ('B3', 2),
            ('E4', 2), ('C4', 2), ('D4', 2), ('B3', 2),
            ('C4', 1), ('E4', 1), ('A4', 2), ('A4', 2),
        ]
        
        audio_data = b''
        for note, beats in melody:
            freq = self.note_to_freq(note)
            duration = beat * beats
            audio_data += self.generate_tone(freq, duration)
        
        return audio_data
    
    def create_wav(self, audio_data):
        """Create a WAV file in memory."""
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_data)
        wav_buffer.seek(0)
        return wav_buffer
    
    def play_loop(self):
        """Play music in a loop (platform-dependent)."""
        audio_data = self.generate_korobeiniki()
        
        # Create temp file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        wav_data = self.create_wav(audio_data)
        self.temp_file.write(wav_data.read())
        self.temp_file.close()
        
        while self.playing:
            try:
                if sys.platform == 'darwin':  # macOS
                    self.process = subprocess.Popen(['afplay', self.temp_file.name], 
                                                     stdout=subprocess.DEVNULL, 
                                                     stderr=subprocess.DEVNULL)
                elif sys.platform == 'win32':  # Windows
                    import winsound
                    winsound.PlaySound(self.temp_file.name, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:  # Linux
                    self.process = subprocess.Popen(['aplay', self.temp_file.name], 
                                                     stdout=subprocess.DEVNULL, 
                                                     stderr=subprocess.DEVNULL)
                
                # Wait for process to finish (or be killed)
                if hasattr(self, 'process') and self.process:
                    self.process.wait()
            except:
                pass
            
            if not self.playing:
                break
    
    def start(self):
        """Start playing music."""
        if not self.playing:
            self.playing = True
            self.process = None
            self.audio_thread = threading.Thread(target=self.play_loop, daemon=True)
            self.audio_thread.start()
    
    def stop(self):
        """Stop playing music."""
        self.playing = False
        # Kill the audio process
        if hasattr(self, 'process') and self.process:
            try:
                self.process.terminate()
                self.process.kill()
            except:
                pass
            self.process = None
        # Also try to kill any afplay/aplay processes (backup)
        if sys.platform == 'darwin':
            os.system('killall afplay 2>/dev/null')
        elif sys.platform != 'win32':
            os.system('killall aplay 2>/dev/null')
        # Clean up temp file
        if self.temp_file and os.path.exists(self.temp_file.name):
            try:
                os.unlink(self.temp_file.name)
            except:
                pass


# =============================================================================
# MAIN MENU SYSTEM
# =============================================================================

class MenuSystem:
    """Handles main menu, how to play, and credits screens."""
    
    def __init__(self, canvas, on_start_game):
        self.canvas = canvas
        self.on_start_game = on_start_game
        self.current_screen = 'menu'  # menu, howto, credits
        self.animation_frame = 0
        self.title_colors = ['#FF0000', '#FF8800', '#FFFF00', '#00FF00', '#00FFFF', '#0088FF', '#AA00FF']
        
    def render(self):
        """Render current menu screen."""
        self.canvas.delete('all')
        
        # Background with gradient effect
        for i in range(WINDOW_HEIGHT // 10):
            shade = max(0, int(20 - i * 0.3))
            blue_shade = min(255, max(0, shade + 10))
            color = f'#{shade:02x}{shade:02x}{blue_shade:02x}'
            self.canvas.create_rectangle(0, i*10, WINDOW_WIDTH, (i+1)*10, fill=color, outline='')
        
        # Falling tetromino decoration
        self.draw_falling_pieces()
        
        if self.current_screen == 'menu':
            self.draw_main_menu()
        elif self.current_screen == 'howto':
            self.draw_howto()
        elif self.current_screen == 'credits':
            self.draw_credits()
    
    def draw_falling_pieces(self):
        """Draw decorative falling tetrominoes."""
        random.seed(42)  # Consistent pattern
        pieces = list(TETROMINOES.keys())
        
        for i in range(8):
            piece = pieces[i % len(pieces)]
            x = 50 + i * 85
            y = (self.animation_frame * 2 + i * 70) % (WINDOW_HEIGHT + 100) - 50
            
            color = COLORS[piece]
            # Draw faded version
            for row, col in TETROMINOES[piece][0]:
                px = x + col * 15
                py = y + row * 15
                self.canvas.create_rectangle(
                    px, py, px + 14, py + 14,
                    fill=self.fade_color(color, 0.7), outline=''
                )
    
    def fade_color(self, hex_color, factor):
        """Fade a color towards black."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def draw_main_menu(self):
        """Draw the main menu."""
        cx = WINDOW_WIDTH // 2
        
        # Animated "ULTRA!" title with rainbow effect
        ultra_text = "ULTRA!"
        for i, char in enumerate(ultra_text):
            color_idx = (i + self.animation_frame // 3) % len(self.title_colors)
            x = cx - 100 + i * 35
            y = 80 + math.sin((self.animation_frame + i * 10) / 10) * 5
            
            # Shadow
            self.canvas.create_text(x + 3, y + 3, text=char, fill='#000000',
                                   font=('Impact', 48, 'bold'))
            # Main text
            self.canvas.create_text(x, y, text=char, fill=self.title_colors[color_idx],
                                   font=('Impact', 48, 'bold'))
        
        # "TETRIS" subtitle
        self.canvas.create_text(cx + 3, 153, text="T E T R I S", fill='#000000',
                               font=('Courier', 36, 'bold'))
        self.canvas.create_text(cx, 150, text="T E T R I S", fill='#00FFFF',
                               font=('Courier', 36, 'bold'))
        
        # Russian subtitle
        self.canvas.create_text(cx, 190, text="« Классическая Русская Игра »",
                               fill='#888888', font=('Arial', 12, 'italic'))
        
        # Menu options
        menu_y = 270
        pulse = abs(math.sin(self.animation_frame / 15)) * 0.3 + 0.7
        
        # Press SPACE to Start (pulsing)
        self.canvas.create_rectangle(cx - 150, menu_y - 5, cx + 150, menu_y + 35,
                                    fill='#222244', outline='#4444AA', width=2)
        start_color = f'#{int(255*pulse):02x}{int(255*pulse):02x}{int(50):02x}'
        self.canvas.create_text(cx, menu_y + 15, text="► PRESS SPACE TO START ◄",
                               fill=start_color, font=('Courier', 16, 'bold'))
        
        # Other menu options
        options = [
            ("[ H ] HOW TO PLAY", menu_y + 80),
            ("[ C ] CREDITS", menu_y + 120),
            ("[ Q ] QUIT", menu_y + 160)
        ]
        
        for text, y in options:
            self.canvas.create_text(cx, y, text=text, fill='#AAAAAA',
                                   font=('Courier', 14))
        
        # Version info
        self.canvas.create_text(WINDOW_WIDTH - 10, WINDOW_HEIGHT - 10,
                               text="v1.0 ULTRA", fill='#444444',
                               font=('Courier', 10), anchor='se')
        
        # Music note indicator
        self.canvas.create_text(10, WINDOW_HEIGHT - 10,
                               text="♪ Music: Korobeiniki", fill='#666666',
                               font=('Courier', 10), anchor='sw')
    
    def draw_howto(self):
        """Draw How to Play screen."""
        cx = WINDOW_WIDTH // 2
        
        # Title
        self.canvas.create_text(cx, 50, text="HOW TO PLAY",
                               fill='#00FFFF', font=('Impact', 36, 'bold'))
        
        # Controls box
        controls = [
            ("←  →", "Move piece left/right"),
            ("↓", "Soft drop (faster fall)"),
            ("↑", "Rotate clockwise"),
            ("SPACE", "Hard drop (instant)"),
            ("C", "Hold piece"),
            ("P", "Pause game"),
            ("M", "Toggle music"),
            ("R", "Restart (game over)"),
            ("ESC", "Return to menu")
        ]
        
        y = 110
        self.canvas.create_rectangle(cx - 250, y - 10, cx + 250, y + len(controls) * 35 + 10,
                                    fill='#111122', outline='#333366', width=2)
        
        for key, desc in controls:
            self.canvas.create_text(cx - 200, y + 10, text=key, fill='#FFFF00',
                                   font=('Courier', 14, 'bold'), anchor='w')
            self.canvas.create_text(cx - 60, y + 10, text=desc, fill='#FFFFFF',
                                   font=('Courier', 12), anchor='w')
            y += 35
        
        # Scoring info
        y += 30
        self.canvas.create_text(cx, y, text="SCORING", fill='#FF8800',
                               font=('Courier', 18, 'bold'))
        
        score_info = [
            "1 Line  = 100 pts    │    3 Lines = 500 pts",
            "2 Lines = 300 pts    │    4 Lines = 800 pts (TETRIS!)",
            "Points multiply by (Level + 1)"
        ]
        
        for i, line in enumerate(score_info):
            self.canvas.create_text(cx, y + 30 + i * 25, text=line,
                                   fill='#AAAAAA', font=('Courier', 11))
        
        # Back instruction
        self.canvas.create_text(cx, WINDOW_HEIGHT - 40,
                               text="Press SPACE or ESC to return",
                               fill='#666666', font=('Courier', 12))
    
    def draw_credits(self):
        """Draw Credits screen."""
        cx = WINDOW_WIDTH // 2
        
        # Title
        self.canvas.create_text(cx, 50, text="CREDITS",
                               fill='#AA00FF', font=('Impact', 36, 'bold'))
        
        credits_info = [
            ("ULTRA! TETRIS", "#00FFFF", 18),
            ("", "", 10),
            ("Original Tetris © 1984", "#888888", 12),
            ("Alexey Pajitnov", "#FFFFFF", 14),
            ("", "", 10),
            ("Music: Korobeiniki", "#888888", 12),
            ("Traditional Russian Folk Song", "#FFFFFF", 14),
            ("", "", 10),
            ("This Recreation:", "#888888", 12),
            ("Pure Python Implementation", "#FFFFFF", 14),
            ("tkinter Graphics", "#FFFFFF", 14),
            ("Synthesized Audio", "#FFFFFF", 14),
            ("", "", 10),
            ("Made for:", "#888888", 12),
            ("Team Flames / Samsoft", "#FFFF00", 14),
            ("Flames Co.", "#FFFF00", 14),
            ("", "", 10),
            ("« Спасибо за игру! »", "#FF8800", 14),
            ("(Thank you for playing!)", "#666666", 10),
        ]
        
        y = 100
        for text, color, size in credits_info:
            if text:
                self.canvas.create_text(cx, y, text=text, fill=color,
                                       font=('Courier', size, 'bold' if size > 12 else ''))
            y += size + 8
        
        # Back instruction
        self.canvas.create_text(cx, WINDOW_HEIGHT - 40,
                               text="Press SPACE or ESC to return",
                               fill='#666666', font=('Courier', 12))
    
    def handle_key(self, event):
        """Handle key press in menu."""
        key = event.keysym
        
        if self.current_screen == 'menu':
            if key == 'space':
                self.on_start_game()
            elif key.lower() == 'h':
                self.current_screen = 'howto'
            elif key.lower() == 'c':
                self.current_screen = 'credits'
            elif key.lower() == 'q':
                self.canvas.master.quit()
        else:
            if key in ('space', 'Escape'):
                self.current_screen = 'menu'
        
        self.render()
    
    def animate(self):
        """Update animation frame."""
        self.animation_frame += 1
        self.render()


# =============================================================================
# TETRIS GAME CLASS
# =============================================================================

class TetrisGame:
    """Main Tetris game class."""

    def __init__(self, root):
        self.root = root
        self.root.title("ULTRA! TETRIS - Classic Russian Style")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg='#000000')

        self.canvas = tk.Canvas(
            root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT,
            bg=COLORS['bg'], highlightthickness=0
        )
        self.canvas.pack()

        # Music system
        self.music = TetrisMusicSynthesizer()
        self.music_enabled = True
        
        # Menu system
        self.menu = MenuSystem(self.canvas, self.start_game)
        self.in_menu = True
        
        # Bind keys
        self.root.bind('<KeyPress>', self.handle_key)
        
        # Start in menu
        self.menu_animation_loop()

    def menu_animation_loop(self):
        """Animate menu."""
        if self.in_menu:
            self.menu.animate()
            self.root.after(50, self.menu_animation_loop)

    def start_game(self):
        """Start the actual game."""
        self.in_menu = False
        self.init_game()
        
        # Start music
        if self.music_enabled:
            self.music.start()
        
        self.game_loop()

    def return_to_menu(self):
        """Return to main menu."""
        self.music.stop()
        self.in_menu = True
        self.menu.current_screen = 'menu'
        self.menu_animation_loop()

    def init_game(self):
        """Initialize game state."""
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.level = 0
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.piece_bag = []
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        self.next_piece = self.get_next_piece()
        self.hold_piece_type = None
        self.can_hold = True
        self.spawn_piece()

    def get_next_piece(self):
        """7-bag randomizer."""
        if not self.piece_bag:
            self.piece_bag = list(TETROMINOES.keys())
            random.shuffle(self.piece_bag)
        return self.piece_bag.pop()

    def spawn_piece(self):
        """Spawn new piece."""
        self.current_piece = self.next_piece
        self.next_piece = self.get_next_piece()
        self.current_rotation = 0
        self.current_x = BOARD_WIDTH // 2 - 2
        self.current_y = 0
        self.can_hold = True

        if not self.is_valid_position(self.current_x, self.current_y, self.current_rotation):
            self.game_over = True

    def is_valid_position(self, x, y, rotation):
        """Check if position is valid."""
        for row, col in TETROMINOES[self.current_piece][rotation]:
            new_x = x + col
            new_y = y + row
            if new_x < 0 or new_x >= BOARD_WIDTH:
                return False
            if new_y >= BOARD_HEIGHT:
                return False
            if new_y >= 0 and self.board[new_y][new_x] is not None:
                return False
        return True

    def move(self, dx, dy):
        """Move piece."""
        if self.game_over or self.paused or self.current_piece is None:
            return False
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        if self.is_valid_position(new_x, new_y, self.current_rotation):
            self.current_x = new_x
            self.current_y = new_y
            self.render()
            return True
        return False

    def rotate(self):
        """Rotate piece with wall kicks."""
        if self.game_over or self.paused or self.current_piece is None:
            return
        new_rotation = (self.current_rotation + 1) % 4

        if self.is_valid_position(self.current_x, self.current_y, new_rotation):
            self.current_rotation = new_rotation
            self.render()
            return

        kicks = [(-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1), (-2, 0), (2, 0)]
        for dx, dy in kicks:
            if self.is_valid_position(self.current_x + dx, self.current_y + dy, new_rotation):
                self.current_x += dx
                self.current_y += dy
                self.current_rotation = new_rotation
                self.render()
                return

    def soft_drop(self):
        """Soft drop."""
        if self.move(0, 1):
            self.score += 1

    def hard_drop(self):
        """Hard drop."""
        if self.game_over or self.paused or self.current_piece is None:
            return
        drop_distance = 0
        while self.is_valid_position(self.current_x, self.current_y + 1, self.current_rotation):
            self.current_y += 1
            drop_distance += 1
        self.score += drop_distance * 2
        self.lock_piece()

    def get_ghost_y(self):
        """Get ghost piece Y position."""
        ghost_y = self.current_y
        while self.is_valid_position(self.current_x, ghost_y + 1, self.current_rotation):
            ghost_y += 1
        return ghost_y

    def lock_piece(self):
        """Lock piece to board."""
        if self.current_piece is None:
            return

        for row, col in TETROMINOES[self.current_piece][self.current_rotation]:
            board_y = self.current_y + row
            board_x = self.current_x + col
            if 0 <= board_y < BOARD_HEIGHT and 0 <= board_x < BOARD_WIDTH:
                self.board[board_y][board_x] = self.current_piece

        lines_to_clear = []
        for y in range(BOARD_HEIGHT):
            if all(self.board[y][x] is not None for x in range(BOARD_WIDTH)):
                lines_to_clear.append(y)

        if lines_to_clear:
            for y in lines_to_clear:
                del self.board[y]
                self.board.insert(0, [None for _ in range(BOARD_WIDTH)])

            num_lines = len(lines_to_clear)
            self.lines_cleared += num_lines
            self.score += SCORE_TABLE.get(num_lines, 0) * (self.level + 1)

            new_level = min(self.lines_cleared // 10, 9)
            if new_level > self.level:
                self.level = new_level

        self.spawn_piece()
        self.render()

    def hold_piece(self):
        """Hold current piece."""
        if self.game_over or self.paused or not self.can_hold:
            return

        self.can_hold = False

        if self.hold_piece_type is None:
            self.hold_piece_type = self.current_piece
            self.spawn_piece()
        else:
            self.current_piece, self.hold_piece_type = self.hold_piece_type, self.current_piece
            self.current_rotation = 0
            self.current_x = BOARD_WIDTH // 2 - 2
            self.current_y = 0

        self.render()

    def toggle_pause(self):
        """Toggle pause."""
        if not self.game_over:
            self.paused = not self.paused
            self.render()

    def toggle_music(self):
        """Toggle music (only during gameplay)."""
        if self.in_menu:
            return
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.music.start()
        else:
            self.music.stop()
        self.render()

    def restart(self):
        """Restart game."""
        self.init_game()
        self.render()

    def get_drop_speed(self):
        """Get drop speed."""
        return LEVEL_SPEEDS[min(self.level, len(LEVEL_SPEEDS) - 1)]

    def handle_key(self, event):
        """Handle key press."""
        if self.in_menu:
            self.menu.handle_key(event)
            return
        
        key = event.keysym
        
        if key == 'Left':
            self.move(-1, 0)
        elif key == 'Right':
            self.move(1, 0)
        elif key == 'Down':
            self.soft_drop()
        elif key == 'Up':
            self.rotate()
        elif key == 'space':
            self.hard_drop()
        elif key.lower() == 'c':
            self.hold_piece()
        elif key.lower() == 'p':
            self.toggle_pause()
        elif key.lower() == 'm':
            self.toggle_music()
        elif key.lower() == 'r':
            if self.game_over:
                self.restart()
        elif key == 'Escape':
            self.return_to_menu()

    def game_loop(self):
        """Main game loop."""
        if self.in_menu:
            return
            
        if not self.game_over and not self.paused:
            if not self.move(0, 1):
                self.lock_piece()

        self.render()

        speed = self.get_drop_speed() if not self.paused else 100
        self.root.after(speed, self.game_loop)

    # =========================================================================
    # RENDERING
    # =========================================================================

    def render(self):
        """Render game."""
        self.canvas.delete('all')
        
        # Background gradient
        for i in range(WINDOW_HEIGHT // 20):
            shade = min(255, max(0, int(10 + i * 0.5)))
            blue_shade = min(255, max(0, shade + 5))
            color = f'#{shade:02x}{shade:02x}{blue_shade:02x}'
            self.canvas.create_rectangle(0, i*20, WINDOW_WIDTH, (i+1)*20, fill=color, outline='')
        
        self.draw_board()
        self.draw_ghost()
        self.draw_current_piece()
        self.draw_next_preview()
        self.draw_hold_preview()
        self.draw_stats()

        if self.paused:
            self.draw_pause_overlay()
        if self.game_over:
            self.draw_game_over_overlay()

    def draw_block(self, x, y, color, size=CELL_SIZE, border=True):
        """Draw a block with 3D effect."""
        self.canvas.create_rectangle(
            x, y, x + size, y + size,
            fill=color, outline='#000000', width=1
        )

        if border and color != COLORS['ghost']:
            highlight = self.lighten_color(color, 0.4)
            self.canvas.create_line(x+1, y+1, x+size-1, y+1, fill=highlight, width=2)
            self.canvas.create_line(x+1, y+1, x+1, y+size-1, fill=highlight, width=2)

            shadow = self.darken_color(color, 0.4)
            self.canvas.create_line(x+size-1, y+2, x+size-1, y+size-1, fill=shadow, width=2)
            self.canvas.create_line(x+2, y+size-1, x+size-1, y+size-1, fill=shadow, width=2)

    def lighten_color(self, hex_color, factor):
        """Lighten color."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f'#{r:02x}{g:02x}{b:02x}'

    def darken_color(self, hex_color, factor):
        """Darken color."""
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f'#{r:02x}{g:02x}{b:02x}'

    def draw_board(self):
        """Draw game board."""
        # Border glow effect
        for i in range(3):
            offset = i * 2
            alpha = 0.3 - i * 0.1
            glow_color = f'#{int(0x44*alpha):02x}{int(0x44*alpha):02x}{int(0xAA*alpha):02x}'
            self.canvas.create_rectangle(
                BOARD_X - 4 - offset, BOARD_Y - 4 - offset,
                BOARD_X + BOARD_WIDTH * CELL_SIZE + 4 + offset,
                BOARD_Y + BOARD_HEIGHT * CELL_SIZE + 4 + offset,
                outline=glow_color, width=2
            )
        
        self.canvas.create_rectangle(
            BOARD_X - 2, BOARD_Y - 2,
            BOARD_X + BOARD_WIDTH * CELL_SIZE + 2,
            BOARD_Y + BOARD_HEIGHT * CELL_SIZE + 2,
            outline=COLORS['border'], width=2
        )

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                px = BOARD_X + x * CELL_SIZE
                py = BOARD_Y + y * CELL_SIZE

                if self.board[y][x] is not None:
                    self.draw_block(px, py, COLORS[self.board[y][x]])
                else:
                    self.canvas.create_rectangle(
                        px, py, px + CELL_SIZE, py + CELL_SIZE,
                        fill=COLORS['bg'], outline=COLORS['grid'], width=1
                    )

    def draw_ghost(self):
        """Draw ghost piece."""
        if self.current_piece is None or self.game_over:
            return

        ghost_y = self.get_ghost_y()
        if ghost_y == self.current_y:
            return

        for row, col in TETROMINOES[self.current_piece][self.current_rotation]:
            board_y = ghost_y + row
            board_x = self.current_x + col
            if 0 <= board_y < BOARD_HEIGHT and 0 <= board_x < BOARD_WIDTH:
                px = BOARD_X + board_x * CELL_SIZE
                py = BOARD_Y + board_y * CELL_SIZE
                self.draw_block(px, py, COLORS['ghost'], border=False)

    def draw_current_piece(self):
        """Draw current piece."""
        if self.current_piece is None:
            return

        for row, col in TETROMINOES[self.current_piece][self.current_rotation]:
            board_y = self.current_y + row
            board_x = self.current_x + col
            if board_y >= 0 and 0 <= board_x < BOARD_WIDTH:
                px = BOARD_X + board_x * CELL_SIZE
                py = BOARD_Y + board_y * CELL_SIZE
                self.draw_block(px, py, COLORS[self.current_piece])

    def draw_preview_piece(self, piece_type, start_x, start_y, cell_size=18):
        """Draw preview piece."""
        if piece_type is None:
            return

        cells = TETROMINOES[piece_type][0]
        min_col = min(c for _, c in cells)
        max_col = max(c for _, c in cells)
        min_row = min(r for r, _ in cells)
        max_row = max(r for r, _ in cells)

        width = max_col - min_col + 1
        height = max_row - min_row + 1

        offset_x = (4 - width) / 2 - min_col
        offset_y = (4 - height) / 2 - min_row

        for row, col in cells:
            px = start_x + (col + offset_x) * cell_size
            py = start_y + (row + offset_y) * cell_size
            self.draw_block(px, py, COLORS[piece_type], size=cell_size)

    def draw_next_preview(self):
        """Draw next piece preview."""
        panel_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 30
        panel_y = BOARD_Y

        self.canvas.create_text(
            panel_x + 40, panel_y,
            text="NEXT", fill='#00FFFF', font=('Courier', 14, 'bold'),
            anchor='n'
        )

        box_y = panel_y + 25
        self.canvas.create_rectangle(
            panel_x, box_y, panel_x + 80, box_y + 80,
            outline='#4444AA', fill='#0a0a1a', width=2
        )

        self.draw_preview_piece(self.next_piece, panel_x + 4, box_y + 4)

    def draw_hold_preview(self):
        """Draw hold piece preview."""
        panel_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 30
        panel_y = BOARD_Y + 120

        self.canvas.create_text(
            panel_x + 40, panel_y,
            text="HOLD", fill='#FF8800', font=('Courier', 14, 'bold'),
            anchor='n'
        )

        box_y = panel_y + 25
        self.canvas.create_rectangle(
            panel_x, box_y, panel_x + 80, box_y + 80,
            outline='#4444AA', fill='#0a0a1a', width=2
        )

        if self.hold_piece_type:
            self.draw_preview_piece(self.hold_piece_type, panel_x + 4, box_y + 4)

    def draw_stats(self):
        """Draw stats panel."""
        panel_x = BOARD_X + BOARD_WIDTH * CELL_SIZE + 30
        panel_y = BOARD_Y + 240

        stats = [
            ("SCORE", str(self.score), '#FFFF00'),
            ("LEVEL", str(self.level), '#00FF00'),
            ("LINES", str(self.lines_cleared), '#00FFFF')
        ]

        for i, (label, value, color) in enumerate(stats):
            y = panel_y + i * 55

            self.canvas.create_text(
                panel_x, y, text=label, fill='#888888',
                font=('Courier', 11, 'bold'), anchor='nw'
            )
            self.canvas.create_text(
                panel_x, y + 18, text=value, fill=color,
                font=('Courier', 18, 'bold'), anchor='nw'
            )

        # Music indicator
        music_text = "♪ ON" if self.music_enabled else "♪ OFF"
        music_color = '#00FF00' if self.music_enabled else '#666666'
        self.canvas.create_text(
            panel_x, WINDOW_HEIGHT - 80, text=f"MUSIC: {music_text}",
            fill=music_color, font=('Courier', 10), anchor='nw'
        )

        # Controls hint
        controls = ["↑↓←→ Move", "SPACE Drop", "C Hold", "P Pause", "M Music", "ESC Menu"]
        for i, text in enumerate(controls):
            self.canvas.create_text(
                panel_x, WINDOW_HEIGHT - 60 + i * 12,
                text=text, fill='#444444', font=('Courier', 8), anchor='nw'
            )

    def draw_pause_overlay(self):
        """Draw pause overlay."""
        self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill='#000000', stipple='gray50'
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20,
            text="▌▌ PAUSED", fill='#FFFF00', font=('Impact', 32, 'bold')
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30,
            text="Press P to continue", fill='#FFFFFF', font=('Courier', 14)
        )

    def draw_game_over_overlay(self):
        """Draw game over overlay."""
        self.canvas.create_rectangle(
            0, 0, WINDOW_WIDTH, WINDOW_HEIGHT,
            fill='#000000', stipple='gray50'
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60,
            text="GAME OVER", fill='#FF0000', font=('Impact', 40, 'bold')
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2,
            text=f"Final Score: {self.score}", fill='#FFFF00', font=('Courier', 20, 'bold')
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 35,
            text=f"Level: {self.level}  |  Lines: {self.lines_cleared}",
            fill='#AAAAAA', font=('Courier', 14)
        )
        self.canvas.create_text(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80,
            text="Press R to restart  |  ESC for menu",
            fill='#00FFFF', font=('Courier', 14)
        )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point."""
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - WINDOW_WIDTH) // 2
    y = (screen_height - WINDOW_HEIGHT) // 2
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    game = TetrisGame(root)
    
    def on_closing():
        game.music.stop()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == '__main__':
    main()
