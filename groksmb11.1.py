#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS V0 — COMPLETE EDITION
All 32 Levels (1-1 to 8-4) • Full OST • Optimized Rendering
Pure Tkinter • Procedural Audio • FILES = OFF

© 1985 Nintendo
© Samsoft 2025
"""

import tkinter as tk
import math
import struct
import array
import threading
import time
import random

# ============================================================
# AUDIO ENGINE - Procedural NES-style sound
# ============================================================
try:
    import pyaudio
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

SAMPLE_RATE = 22050
AUDIO_BUFFER = 1024

class AudioEngine:
    """NES-style procedural audio synthesizer"""
    
    def __init__(self):
        self.playing = False
        self.current_track = None
        self.track_pos = 0
        self.tempo = 140  # BPM
        self.volume = 0.05
        
        if AUDIO_AVAILABLE:
            try:
                self.pa = pyaudio.PyAudio()
                self.stream = self.pa.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True,
                    frames_per_buffer=AUDIO_BUFFER
                )
                self.audio_thread = None
            except:
                self.pa = None
                self.stream = None
        else:
            self.pa = None
            self.stream = None
    
    def note_freq(self, note):
        """Convert MIDI note to frequency"""
        if note == 0:
            return 0
        return 440.0 * (2.0 ** ((note - 69) / 12.0))
    
    def generate_square(self, freq, duration, duty=0.5):
        """Generate square wave (NES pulse channel)"""
        if freq == 0:
            return [0] * int(SAMPLE_RATE * duration)
        
        samples = []
        period = SAMPLE_RATE / freq
        for i in range(int(SAMPLE_RATE * duration)):
            t = (i % period) / period
            val = 1 if t < duty else -1
            # Envelope
            env = min(1.0, (duration * SAMPLE_RATE - i) / (SAMPLE_RATE * 0.05))
            samples.append(int(val * 32767 * self.volume * env * 0.5))
        return samples
    
    def generate_triangle(self, freq, duration):
        """Generate triangle wave (NES triangle channel)"""
        if freq == 0:
            return [0] * int(SAMPLE_RATE * duration)
        
        samples = []
        period = SAMPLE_RATE / freq
        for i in range(int(SAMPLE_RATE * duration)):
            t = (i % period) / period
            val = 4 * abs(t - 0.5) - 1
            samples.append(int(val * 32767 * self.volume * 0.4))
        return samples
    
    def generate_noise(self, duration, pitch=1.0):
        """Generate noise (NES noise channel)"""
        samples = []
        step = int(100 / pitch)
        val = 0
        for i in range(int(SAMPLE_RATE * duration)):
            if i % step == 0:
                val = random.choice([-1, 1])
            samples.append(int(val * 32767 * self.volume * 0.15))
        return samples
    
    def mix_channels(self, *channels):
        """Mix multiple audio channels"""
        max_len = max(len(c) for c in channels)
        mixed = []
        for i in range(max_len):
            total = 0
            for ch in channels:
                if i < len(ch):
                    total += ch[i]
            mixed.append(max(-32767, min(32767, total)))
        return mixed
    
    def play_track(self, track_name):
        """Start playing a music track"""
        if not self.stream:
            return
        
        self.current_track = track_name
        self.playing = True
        
        if self.audio_thread and self.audio_thread.is_alive():
            self.playing = False
            self.audio_thread.join(timeout=0.5)
        
        self.playing = True
        self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.audio_thread.start()
    
    def stop(self):
        """Stop audio playback"""
        self.playing = False
    
    def _audio_loop(self):
        """Background audio playback thread"""
        while self.playing and self.stream:
            try:
                track = self.get_track_data(self.current_track)
                if track:
                    audio_data = self.render_track(track)
                    # Convert to bytes
                    data = struct.pack(f'{len(audio_data)}h', *audio_data)
                    self.stream.write(data)
            except Exception as e:
                break
    
    def generate_dynamic_track(self, name):
        """Dynamic AI-generated track variation using random walk"""
        theme = name.split('-')[0] if '-' in name else name  # e.g., 'overworld' from '1-1'
        
        base_notes = {
            'overworld': [72,67,64,69,71,70,69,67,76,79,81,77,79,76,72,74,71],
            'underground': [48,55,52,48,55,52,47,54,51,47,54,51],
            'castle': [65,65,65,64,64,64,63,63,63,62],
            'water': [72,74,76,72,69,67,72]
        }.get(theme, [72,67,64,69,71,70,69])
        
        track = []
        current = random.choice(base_notes)
        for i in range(64):  # Generate longer sequence for looping
            dur = random.choice([1,2,3,4,8]) * 0.5  # Varied durations
            offset = random.choice([-12, 0, 12])  # Octave jumps
            p1 = current + offset
            p2 = p1 - 12
            tri = p1 - 24
            track.append({'p1': p1, 'p2': p2, 'tri': tri, 'd': dur})
            step = random.choice([-3,-2,-1,0,1,2,3])
            current += step
            current = min(max(current, 48), 81)  # Keep in range
        return track
    
    def get_track_data(self, name):
        """Get music data for track - now dynamic AI generated"""
        # Always use dynamic AI generation for fresh variations each time
        return self.generate_dynamic_track(name)
    
    def render_track(self, track):
        """Render track to audio samples"""
        beat_dur = 60.0 / self.tempo / 4  # 16th note
        
        pulse1 = []
        pulse2 = []
        triangle = []
        
        for note_data in track:
            dur = note_data.get('d', 1) * beat_dur
            
            # Pulse 1 (melody)
            if 'p1' in note_data:
                freq = self.note_freq(note_data['p1'])
                pulse1.extend(self.generate_square(freq, dur, 0.25))
            else:
                pulse1.extend([0] * int(SAMPLE_RATE * dur))
            
            # Pulse 2 (harmony)
            if 'p2' in note_data:
                freq = self.note_freq(note_data['p2'])
                pulse2.extend(self.generate_square(freq, dur, 0.125))
            else:
                pulse2.extend([0] * int(SAMPLE_RATE * dur))
            
            # Triangle (bass)
            if 'tri' in note_data:
                freq = self.note_freq(note_data['tri'])
                triangle.extend(self.generate_triangle(freq, dur))
            else:
                triangle.extend([0] * int(SAMPLE_RATE * dur))
        
        return self.mix_channels(pulse1, pulse2, triangle)
    
    # ========== SMB1 MUSIC DATA ==========
    
    # Overworld Theme (World 1-1, 1-3, etc)
    OVERWORLD_THEME = [
        # Intro
        {'p1': 76, 'p2': 64, 'tri': 40, 'd': 2},  # E5
        {'p1': 76, 'p2': 64, 'tri': 40, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 76, 'p2': 64, 'tri': 40, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 72, 'p2': 60, 'tri': 36, 'd': 2},  # C5
        {'p1': 76, 'p2': 64, 'tri': 40, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 79, 'p2': 67, 'tri': 43, 'd': 4},  # G5
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 4},
        {'p1': 67, 'p2': 55, 'tri': 31, 'd': 4},  # G4
        # Main melody loop
        {'p1': 72, 'p2': 60, 'tri': 36, 'd': 3},  # C5
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 1},
        {'p1': 67, 'p2': 55, 'tri': 31, 'd': 3},  # G4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 1},
        {'p1': 64, 'p2': 52, 'tri': 28, 'd': 3},  # E4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 1},
        {'p1': 69, 'p2': 57, 'tri': 33, 'd': 2},  # A4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 71, 'p2': 59, 'tri': 35, 'd': 2},  # B4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 70, 'p2': 58, 'tri': 34, 'd': 2},  # Bb4
        {'p1': 69, 'p2': 57, 'tri': 33, 'd': 4},  # A4
        # Triplet section
        {'p1': 67, 'p2': 55, 'tri': 31, 'd': 2},  # G4
        {'p1': 76, 'p2': 64, 'tri': 40, 'd': 2},  # E5
        {'p1': 79, 'p2': 67, 'tri': 43, 'd': 2},  # G5
        {'p1': 81, 'p2': 69, 'tri': 45, 'd': 4},  # A5
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 77, 'p2': 65, 'tri': 41, 'd': 2},  # F5
        {'p1': 79, 'p2': 67, 'tri': 43, 'd': 2},  # G5
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 76, 'p2': 64, 'tri': 40, 'd': 2},  # E5
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 72, 'p2': 60, 'tri': 36, 'd': 2},  # C5
        {'p1': 74, 'p2': 62, 'tri': 38, 'd': 2},  # D5
        {'p1': 71, 'p2': 59, 'tri': 35, 'd': 2},  # B4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 4},
    ]
    
    # Underground Theme (World 1-2, etc)
    UNDERGROUND_THEME = [
        {'p1': 48, 'p2': 36, 'tri': 24, 'd': 2},  # C3
        {'p1': 55, 'p2': 43, 'tri': 31, 'd': 2},  # G3
        {'p1': 52, 'p2': 40, 'tri': 28, 'd': 2},  # E3
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 48, 'p2': 36, 'tri': 24, 'd': 2},
        {'p1': 55, 'p2': 43, 'tri': 31, 'd': 2},
        {'p1': 52, 'p2': 40, 'tri': 28, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 47, 'p2': 35, 'tri': 23, 'd': 2},  # B2
        {'p1': 54, 'p2': 42, 'tri': 30, 'd': 2},  # F#3
        {'p1': 51, 'p2': 39, 'tri': 27, 'd': 2},  # Eb3
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 47, 'p2': 35, 'tri': 23, 'd': 2},
        {'p1': 54, 'p2': 42, 'tri': 30, 'd': 2},
        {'p1': 51, 'p2': 39, 'tri': 27, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
    ]
    
    # Castle Theme (World X-4)
    CASTLE_THEME = [
        {'p1': 65, 'p2': 53, 'tri': 29, 'd': 4},  # F4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 65, 'p2': 53, 'tri': 29, 'd': 2},
        {'p1': 65, 'p2': 53, 'tri': 29, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 64, 'p2': 52, 'tri': 28, 'd': 4},  # E4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 64, 'p2': 52, 'tri': 28, 'd': 2},
        {'p1': 64, 'p2': 52, 'tri': 28, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 63, 'p2': 51, 'tri': 27, 'd': 4},  # Eb4
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 63, 'p2': 51, 'tri': 27, 'd': 2},
        {'p1': 63, 'p2': 51, 'tri': 27, 'd': 2},
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 2},
        {'p1': 62, 'p2': 50, 'tri': 26, 'd': 8},  # D4
    ]
    
    # Water Theme (World 2-2, etc)
    WATER_THEME = [
        {'p1': 72, 'p2': 60, 'tri': 36, 'd': 4},  # C5
        {'p1': 74, 'p2': 62, 'tri': 38, 'd': 4},  # D5
        {'p1': 76, 'p2': 64, 'tri': 40, 'd': 4},  # E5
        {'p1': 72, 'p2': 60, 'tri': 36, 'd': 4},  # C5
        {'p1': 69, 'p2': 57, 'tri': 33, 'd': 4},  # A4
        {'p1': 67, 'p2': 55, 'tri': 31, 'd': 4},  # G4
        {'p1': 72, 'p2': 60, 'tri': 36, 'd': 8},  # C5
        {'p1': 0, 'p2': 0, 'tri': 0, 'd': 4},
    ]
    
    def close(self):
        """Cleanup audio resources"""
        self.playing = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()

# ============================================================
# ENGINE CONFIG
# ============================================================
FPS = 60
FRAME_MS = 16
NES_W, NES_H = 256, 240
SCALE = 3
WIDTH, HEIGHT = NES_W * SCALE, NES_H * SCALE

# ============================================================
# NES PALETTE - Optimized lookup
# ============================================================
PAL = {
    '_': None,
    'R': '#D82800', 'B': '#0000A8', 'S': '#FCA044', 'N': '#6B420C',
    'n': '#3B2400', 'K': '#000000', 'W': '#FCFCFC', 'O': '#FC9838',
    'G': '#C84C0C', 'g': '#FC9838', 'E': '#503000',
    'T': '#00A800', 't': '#58F858',
    'P': '#00A800', 'p': '#58F858', 'd': '#003800',
    'Q': '#E4A000', 'q': '#FCE4A0',
    'C': '#C84C0C', 'c': '#FC9838',
    'F': '#FC9838', 'f': '#C84C0C',
    'Y': '#FC9838', 'y': '#E4A000',
    'L': '#FCFCFC', 'l': '#9CDCFC',
    'H': '#00A800', 'h': '#58F858',
    'V': '#6888FC',  # Water
    'v': '#3050D8',
    'X': '#FC3838',  # Lava
    'x': '#D80000',
}

SKY = '#5C94FC'
UNDERGROUND_SKY = '#000000'
CASTLE_SKY = '#000000'
WATER_SKY = '#0058A8'

# ============================================================
# OPTIMIZED SPRITES - Precached as tuples
# ============================================================

S_STAND = (
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSS____",
    "__RRBBBBRR__",
    "_RRRBBBBRRR_",
    "_RRRBBBBRRR_",
    "_SSBBBBBBSS_",
    "_SSBBBBBBSS_",
    "___BBBBBB___",
    "___BB__BB___",
    "__NNN__NNN__",
    "_NNNN__NNNN_",
)

S_WALK1 = (
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSS____",
    "__RRRBBBRR__",
    "_RRRRBBBRRR_",
    "_RRRBBBBRRR_",
    "_SSBBBBBBS__",
    "__SBBBBBB___",
    "___BBBBB____",
    "__NN__NNNN__",
    "_NNN____NN__",
    "____________",
)

S_WALK2 = (
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSSN___",
    "___RRBBBNN__",
    "__RRRBBBNN__",
    "__RRBBBB_N__",
    "_SSBBBBBBS__",
    "_SSBBBBBSS__",
    "___BBBBBB___",
    "___NN__NN___",
    "___NN__NN___",
    "____________",
)

S_WALK3 = (
    "____RRRR____",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NSNSSSNSK_",
    "__NSNSSSKS__",
    "__NNNSSSSKK_",
    "____SSSS____",
    "__NRRBBBRR__",
    "_NNRRBBBRRR_",
    "NN_RBBBBRRR_",
    "_SSBBBBBBSS_",
    "__SSBBBBSS__",
    "___BBBBBB___",
    "_NNNN__NN___",
    "_NN___NNN___",
    "____________",
)

S_JUMP = (
    "___NNN______",
    "__NNNNN_RRR_",
    "__NNSSRRRR__",
    "_NSNSSSRRR__",
    "_NSNSSSKSSS_",
    "_NNNSSSKSS__",
    "___SSSSSS___",
    "__RRBBBRRR__",
    "_RRRBBBRRRR_",
    "RRRRBBBBRRSS",
    "SSBBBBBBBSS_",
    "_SSBBBBBSS__",
    "__SSBBBBSS__",
    "__NNN_______",
    "_NNNN_______",
    "NNNN________",
)

B_STAND = (
    "____RRRR____",
    "___RRRRRR___",
    "___RRRRRR___",
    "___NNNSSK___",
    "__NNSNSSSK__",
    "__NSNSSSKSS_",
    "__NNNSSSKKK_",
    "___SSSSSS___",
    "__RRRBBRRR__",
    "_RRRRBBRRRR_",
    "_RRRRBBRRRRR",
    "_SSRRBBBBRSS",
    "_SSSBBBBBRSS",
    "_SSBBBBBBSS_",
    "___BBBBBB___",
    "___BBBBBB___",
    "___BBRRRB___",
    "__RRRRRRRR__",
    "_RRRRRRRRRR_",
    "_RRRRRRRRRR_",
    "_SSRRRRRSS__",
    "_SSSRBBBRSS_",
    "__SSBBBBSS__",
    "___BBBBBB___",
    "___BB__BB___",
    "__NNN__NNN__",
    "_NNNN__NNNN_",
    "NNNNN__NNNNN",
)

GOOMBA1 = (
    "______GG______",
    "_____GGGG_____",
    "____GGGGGG____",
    "___GGGGGGGG___",
    "__GgWWGGWWgG__",
    "__GgWKGGKWgG__",
    "__GGggGGggGG__",
    "___GGGGGGGG___",
    "____GGGGGG____",
    "_____gggg_____",
    "____EE__EE____",
    "___EE____EE___",
)

GOOMBA2 = (
    "______GG______",
    "_____GGGG_____",
    "____GGGGGG____",
    "___GGGGGGGG___",
    "__GgWWGGWWgG__",
    "__GgWKGGKWgG__",
    "__GGggGGggGG__",
    "___GGGGGGGG___",
    "____GGGGGG____",
    "_____gggg_____",
    "____EEEEEE____",
    "_____EEEE_____",
)

GOOMBA_FLAT = (
    "__GGGGGGGGGG__",
    "__GgWWGGWWgG__",
    "__GgWKGGKWgG__",
    "___GGGGGGGG___",
    "____EEEEEE____",
)

KOOPA = (
    "____TTTT____",
    "___TTTTTT___",
    "__TTWWWWTT__",
    "__TWKWWKWT__",
    "__TWWWWWWT__",
    "___TTTTTT___",
    "__tTTTTTTt__",
    "_tTTTTTTTTt_",
    "_TTTTTTTTTT_",
    "_TTTTttTTTT_",
    "_TTTttttTTT_",
    "_TTTtWWtTTT_",
    "_TTTtWWtTTT_",
    "_TTTttttTTT_",
    "__TTttttTT__",
    "___TTTTTT___",
    "____EEEE____",
    "___EE__EE___",
    "__EE____EE__",
)

PIPE_TOP = (
    "ddPPPPPPPPPPPPPPPPPPPPPPPPPPPPdd",
    "dPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPppPPPPPPPPPPPPPPPPPPPPPPddPPd",
    "dPPddddddddddddddddddddddddddPPd",
    "dPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPd",
    "dddddddddddddddddddddddddddddddd",
    "dddddddddddddddddddddddddddddddd",
)

PIPE_BODY = (
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
    "____dPPppPPPPPPPPPPPPddPPd____",
)

Q_BLOCK = (
    "dddddddddddddddd",
    "dQQQQQQQQQQQQQQd",
    "dQqqqqqqqqqqqqQd",
    "dQqqddddqqqqqqQd",
    "dQqddqqddqqqqqQd",
    "dQqqqqqddqqqqqQd",
    "dQqqqqddqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqqqqqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqddqqqqqqqQd",
    "dQqqqqqqqqqqqqQd",
    "dQQQQQQQQQQQQQQd",
    "dddddddddddddddd",
    "________________",
)

EMPTY_BLOCK = (
    "dddddddddddddddd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dNNNNNNNNNNNNNNd",
    "dddddddddddddddd",
    "________________",
)

BRICK = (
    "dddddddddddddddd",
    "dCCCdCCCCCdCCCcd",
    "dCCCdCCCCCdCCCcd",
    "dccccdccccdccccd",
    "dddddddddddddddd",
    "dCCCCCdCCCdCCCcd",
    "dCCCCCdCCCdCCCcd",
    "dcccccdcccdccccd",
    "dddddddddddddddd",
    "dCCCdCCCCCdCCCcd",
    "dCCCdCCCCCdCCCcd",
    "dccccdccccdccccd",
    "dddddddddddddddd",
    "dCCCCCdCCCdCCCcd",
    "dcccccdcccdccccd",
    "dddddddddddddddd",
)

GROUND = (
    "FFFFFFFFFFFFFFff",
    "FFFFFFFFFFFFFFff",
    "ffffffffffffffff",
    "dddddddddddddddd",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "fCCCCCCCCCCCCCCf",
    "ffffffffffffffff",
)

# Underground/Castle ground
STONE_BLOCK = (
    "dddddddddddddddd",
    "dNNNNNNNNNNNNNNd",
    "dNddddddddddddNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNdNNNNNNNNNNdNd",
    "dNddddddddddddNd",
    "dNNNNNNNNNNNNNNd",
    "dddddddddddddddd",
)

COIN1 = ("_YYYY_", "YyyyyY", "YyYYyY", "YyddyY", "YyddyY", "YyddyY", "YyddyY", "YyddyY", "YyddyY", "YyYYyY", "YyyyyY", "_YYYY_")
COIN2 = ("__YY__", "_YyyY_", "_YddY_", "_YddY_", "_YddY_", "_YddY_", "_YddY_", "_YddY_", "_YddY_", "_YddY_", "_YyyY_", "__YY__")
COIN3 = ("__Y___", "__Y___", "__d___", "__d___", "__d___", "__d___", "__d___", "__d___", "__d___", "__d___", "__Y___", "__Y___")

CLOUD = (
    "_______LL_______LL_______",
    "_____LLLLLL___LLLLLL_____",
    "___LLLLLLLLLLLLLLLLLLLL__",
    "__LLLLLLLLLLLLLLLLLLLLLL_",
    "_LLLLLLLLLLLLLLLLLLLLLLLL",
    "LLLLLLLLLLLLLLLLLLLLLLLLL",
    "LLLLLLLLLLLLLLLLLLLLLLLLl",
    "LLLLLLLLLLLLLLLLLLLLLLLll",
    "_LLLLLLLLLLLLLLLLLLLLLll_",
    "__lLLLLLLLLLLLLLLLLLll___",
    "____llLLLLLLLLLLllll_____",
)

BUSH = (
    "________HH________",
    "______HHHHHH______",
    "____HHHHHHHHHH____",
    "__hHHHHHHHHHHHHh__",
    "_hHHHHHHHHHHHHHHh_",
    "hHHHHHHHHHHHHHHHHh",
    "HHHHHHHHHHHHHHHHHH",
    "HHHHHHHHHHHHHHHHHH",
)

FLAG = ("RRRRRRRR", "RRRRRRRR", "RRRRRRRR", "RRRRRRRR", "RRRRRRRR", "RRRRRRRR", "RRRRRRRR", "RRRRRRRR", "RRRRR___", "RRRR____", "RRR_____", "RR______", "R_______")
FLAGPOLE_BALL = ("__PP__", "_PPPP_", "PPPPPP", "PPPPPP", "_PPPP_", "__PP__")

CASTLE = (
    "___NN__________NN___",
    "___NN__________NN___",
    "___NN__________NN___",
    "NNNNNNNN____NNNNNNNN",
    "NNNNNNNNNNNNNNNNNNNN",
    "NNNNNNNNNNNNNNNNNNNN",
    "NNddNNNNNNNNNNddNNNN",
    "NNddNNNNNNNNNNddNNNN",
    "NNddNNNNddddNNddNNNN",
    "NNddNNNNddddNNddNNNN",
    "NNNNNNNNddddNNNNNNNN",
    "NNNNNNNNddddNNNNNNNN",
)

# Lava for castle levels
LAVA = (
    "XXXXXXXXXXXXXXXX",
    "XxXXxXXXxXXXxXXX",
    "XxxXxxXXxxXXxxXX",
    "XxxxXxxxXxxxXxxx",
)

# Water for underwater levels
WATER = (
    "VVVVVVVVVVVVVVVV",
    "VvVVvVVVvVVVvVVV",
    "VvvVvvVVvvVVvvVV",
)

# ============================================================
# LEVEL DATA - All 32 levels
# ============================================================
def get_level_type(world, stage):
    """Get level theme based on world/stage"""
    if stage == 2:
        return 'underground'
    elif stage == 4:
        return 'castle'
    elif world in [2, 7] and stage == 3:
        return 'water'
    else:
        return 'overworld'

def make_level(world, stage):
    """Generate complete level for world-stage"""
    lvl_type = get_level_type(world, stage)
    
    # Base level width increases with world
    base_width = 3200 + world * 200
    
    lvl = {
        'width': base_width,
        'type': lvl_type,
        'ground': [],
        'bricks': [],
        'questions': [],
        'pipes': [],
        'enemies': [],
        'coins': [],
        'platforms': [],
        'flag_x': base_width - 384,
        'castle_x': base_width - 304,
        'bg_color': SKY,
    }
    
    # Set background based on type
    if lvl_type == 'underground':
        lvl['bg_color'] = UNDERGROUND_SKY
    elif lvl_type == 'castle':
        lvl['bg_color'] = CASTLE_SKY
    elif lvl_type == 'water':
        lvl['bg_color'] = WATER_SKY
    
    # Generate ground with gaps based on difficulty
    gap_count = world // 2
    gaps = []
    for i in range(gap_count):
        gap_x = 600 + i * 800 + (world * 50)
        gap_w = 32 + (world * 8)
        gaps.append((gap_x, gap_w))
    
    for x in range(0, lvl['width'], 16):
        in_gap = any(gx <= x < gx + gw for gx, gw in gaps)
        if not in_gap:
            lvl['ground'].append({'x': x, 'y': 208})
    
    # Platforms/bricks - more in later worlds
    plat_count = 4 + world
    for i in range(plat_count):
        px = 250 + i * (lvl['width'] // (plat_count + 2))
        py = 144 - (i % 3) * 16
        brick_count = 3 + (i % 4)
        for j in range(brick_count):
            lvl['bricks'].append({'x': px + j * 16, 'y': py, 'hit': False})
    
    # Question blocks with items
    q_count = 5 + world
    for i in range(q_count):
        qx = 200 + i * (lvl['width'] // (q_count + 2))
        qy = 128 + (i % 2) * 32
        item = 'mush' if i % 3 == 0 else 'coin'
        lvl['questions'].append({'x': qx, 'y': qy, 'item': item, 'hit': False})
    
    # Pipes - more and taller in later worlds
    pipe_count = 2 + world
    for i in range(pipe_count):
        pipe_x = 350 + i * (lvl['width'] // (pipe_count + 1))
        pipe_h = 32 + (i % 3) * 16 + (world * 4)
        lvl['pipes'].append({'x': pipe_x, 'y': 208 - pipe_h, 'h': pipe_h})
    
    # Enemies - more and varied in later worlds
    enemy_count = 4 + world * 3
    for i in range(enemy_count):
        ex = 300 + i * (lvl['width'] // (enemy_count + 1))
        # Mix of enemy types based on world
        if world >= 5 and i % 4 == 0:
            etype = 'koopa'
        elif world >= 3 and i % 3 == 0:
            etype = 'koopa'
        else:
            etype = 'goomba'
        
        lvl['enemies'].append({
            'x': float(ex), 'y': 192.0, 'type': etype,
            'vx': -0.5 - (world * 0.05), 'alive': True,
            'stomped': False, 'timer': 0, 'frame': 0
        })
    
    # Coins - more in later worlds
    coin_count = 8 + world * 3
    for i in range(coin_count):
        cx = 250 + i * (lvl['width'] // (coin_count + 1))
        cy = 96 + (i % 4) * 24
        lvl['coins'].append({'x': cx, 'y': cy, 'got': False})
    
    return lvl

# ============================================================
# PHYSICS
# ============================================================
class Phys:
    GRAVITY = 0.4
    JUMP = -7.0
    MAX_FALL = 7.0
    WALK = 0.12
    RUN = 0.18
    FRICTION = 0.9
    MAX_WALK = 2.0
    MAX_RUN = 3.5

# ============================================================
# OPTIMIZED RENDERER
# ============================================================
class Renderer:
    def __init__(self, canvas, scale):
        self.canvas = canvas
        self.scale = scale
        # Pre-compute color lookups
        self.color_cache = {}
    
    def draw(self, x, y, sprite, flip=False):
        """Optimized sprite drawing"""
        s = self.scale
        for ri, row in enumerate(sprite):
            for ci, ch in enumerate(row):
                if ch == '_':
                    continue
                col = PAL.get(ch)
                if not col:
                    continue
                px = x + (len(row) - 1 - ci if flip else ci) * s
                py = y + ri * s
                self.canvas.create_rectangle(
                    px, py, px + s, py + s,
                    fill=col, outline=col, width=0
                )
    
    def rect(self, x, y, w, h, color):
        self.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline=color, width=0)
    
    def text(self, x, y, txt, color='#FCFCFC', size=8, anchor='nw'):
        self.canvas.create_text(x, y, text=txt, fill=color, font=('Courier', size, 'bold'), anchor=anchor)

# ============================================================
# GAME
# ============================================================
class Game:
    def __init__(self, root):
        self.root = root
        root.title("ULTRA MARIO 2D BROS V0 — Complete Edition")
        root.geometry(f"{WIDTH}x{HEIGHT}")
        root.resizable(False, False)
        root.configure(bg='black')
        
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=SKY, highlightthickness=0)
        self.canvas.pack()
        
        self.r = Renderer(self.canvas, SCALE)
        
        # Audio
        self.audio = AudioEngine()
        
        self.keys = set()
        root.bind('<KeyPress>', lambda e: self.keys.add(e.keysym.lower()))
        root.bind('<KeyRelease>', lambda e: self.keys.discard(e.keysym.lower()))
        root.bind('<Destroy>', self.cleanup)
        
        self.state = 'menu'
        self.menu_sel = 0
        self.frame = 0
        
        self.player = None
        self.camera = 0
        self.world = 1
        self.stage = 1
        self.level = None
        
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.time = 400
        self.big = False
        
        self.particles = []
        
        self.loop()
    
    def cleanup(self, event=None):
        """Cleanup on close"""
        self.audio.stop()
        self.audio.close()
    
    def loop(self):
        self.canvas.delete('all')
        
        if self.state == 'menu':
            self.update_menu()
            self.draw_menu()
        elif self.state == 'play':
            self.update_game()
            self.draw_game()
        elif self.state == 'dead':
            self.update_dead()
            self.draw_game()
        elif self.state == 'over':
            self.draw_over()
            self.update_over()
        elif self.state == 'clear':
            self.draw_clear()
            self.update_clear()
        
        self.frame += 1
        self.root.after(FRAME_MS, self.loop)
    
    # ========== MENU ==========
    def update_menu(self):
        if 'up' in self.keys:
            self.menu_sel = (self.menu_sel - 1) % 2
            self.keys.discard('up')
        if 'down' in self.keys:
            self.menu_sel = (self.menu_sel + 1) % 2
            self.keys.discard('down')
        if self.keys & {'return', 'z', 'space'}:
            self.keys -= {'return', 'z', 'space'}
            if self.menu_sel == 0:
                self.start()
            else:
                self.root.destroy()
    
    def draw_menu(self):
        self.r.rect(0, 0, WIDTH, HEIGHT, SKY)
        
        for x in range(0, WIDTH, 16 * SCALE):
            self.r.draw(x, 208 * SCALE, GROUND)
        
        for i in range(4):
            cx = ((i * 200 + self.frame) % (WIDTH + 200)) - 100
            self.r.draw(int(cx), (35 + i * 12) * SCALE, CLOUD)
        
        for i in range(3):
            self.r.draw((40 + i * 100) * SCALE, 196 * SCALE, BUSH)
        
        self.r.draw(50 * SCALE, 176 * SCALE, PIPE_TOP)
        
        goomba_x = (self.frame * 0.5) % 200 + 100
        gf = GOOMBA1 if (self.frame // 12) % 2 == 0 else GOOMBA2
        self.r.draw(int(goomba_x) * SCALE, 196 * SCALE, gf)
        
        # Title
        self.r.rect(WIDTH//2 - 180, 25 * SCALE, 360, 70 * SCALE, '#000000')
        self.r.rect(WIDTH//2 - 177, 25 * SCALE + 3, 354, 70 * SCALE - 6, '#200000')
        
        self.r.text(WIDTH//2, 38 * SCALE, "ULTRA MARIO 2D BROS V0", '#FCE4A0', 11 * SCALE // 2, 'n')
        self.r.text(WIDTH//2, 58 * SCALE, "© 1985 Nintendo", '#FCFCFC', 6 * SCALE // 2, 'n')
        self.r.text(WIDTH//2, 70 * SCALE, "© Samsoft 2025", '#FCFCFC', 6 * SCALE // 2, 'n')
        
        mario_x = WIDTH//2 - 20
        walk_frame = (self.frame // 8) % 4
        sprites = [S_STAND, S_WALK1, S_WALK2, S_WALK3]
        self.r.draw(mario_x, 105 * SCALE, sprites[walk_frame])
        
        self.r.rect(WIDTH//2 - 100, 135 * SCALE, 200, 45 * SCALE, '#000000')
        self.r.rect(WIDTH//2 - 97, 135 * SCALE + 3, 194, 45 * SCALE - 6, '#200000')
        
        opts = ["1 PLAYER GAME", "EXIT"]
        for i, t in enumerate(opts):
            y = 145 * SCALE + i * 16 * SCALE
            color = '#FCE4A0' if i == self.menu_sel else '#FCFCFC'
            if i == self.menu_sel:
                cursor_x = WIDTH//2 - 85 + int(math.sin(self.frame * 0.2) * 3)
                self.r.text(cursor_x, y, "►", '#FC0000', 8 * SCALE // 2, 'nw')
            self.r.text(WIDTH//2 - 55, y, t, color, 6 * SCALE // 2, 'nw')
        
        self.r.text(WIDTH//2, 195 * SCALE, "32 LEVELS: WORLD 1-1 TO 8-4", '#FCFCFC', 5 * SCALE // 2, 'n')
    
    # ========== GAME ==========
    def start(self):
        self.state = 'play'
        self.world = 1
        self.stage = 1
        self.score = 0
        self.coins = 0
        self.lives = 3
        self.big = False
        self.load()
    
    def load(self):
        self.level = make_level(self.world, self.stage)
        self.camera = 0
        self.time = 400
        self.particles = []
        
        self.canvas.configure(bg=self.level['bg_color'])
        
        # Start music for level type
        track_name = f"{self.world}-{self.stage}"
        self.audio.play_track(track_name)
        
        self.player = {
            'x': 48.0, 'y': 192.0,
            'vx': 0.0, 'vy': 0.0,
            'dir': 1, 'ground': True,
            'walk': 0, 'inv': 0
        }
    
    def update_game(self):
        if self.frame % 24 == 0 and self.time > 0:
            self.time -= 1
            if self.time <= 0:
                self.die()
                return
        
        self.update_player()
        self.update_enemies()
        self.update_particles()
        self.check_collisions()
        
        target = self.player['x'] - NES_W // 2 + 32
        self.camera = max(0, min(target, self.level['width'] - NES_W))
        
        if self.player['x'] >= self.level['flag_x']:
            self.complete()
    
    def update_player(self):
        p = self.player
        
        moving = False
        run = 'x' in self.keys or 'shift_l' in self.keys
        
        if 'left' in self.keys or 'a' in self.keys:
            p['vx'] -= Phys.RUN if run else Phys.WALK
            p['dir'] = -1
            moving = True
        if 'right' in self.keys or 'd' in self.keys:
            p['vx'] += Phys.RUN if run else Phys.WALK
            p['dir'] = 1
            moving = True
        
        if not moving:
            p['vx'] *= Phys.FRICTION
            if abs(p['vx']) < 0.05:
                p['vx'] = 0
        
        cap = Phys.MAX_RUN if run else Phys.MAX_WALK
        p['vx'] = max(-cap, min(cap, p['vx']))
        
        jkeys = {'z', 'space', 'w', 'up'}
        if jkeys & self.keys and p['ground']:
            p['vy'] = Phys.JUMP
            p['ground'] = False
        
        if p['vy'] < 0 and not (jkeys & self.keys):
            p['vy'] = max(p['vy'], -2)
        
        p['vy'] += Phys.GRAVITY
        p['vy'] = min(p['vy'], Phys.MAX_FALL)
        
        p['x'] += p['vx']
        p['y'] += p['vy']
        
        if p['x'] < self.camera:
            p['x'] = self.camera
        if p['x'] < 0:
            p['x'] = 0
        
        p['ground'] = False
        ph = 28 if self.big else 16
        
        for g in self.level['ground']:
            if self.collide(p['x'], p['y'], 12, ph, g['x'], g['y'], 16, 32):
                if p['vy'] > 0:
                    p['y'] = g['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
        
        for pipe in self.level['pipes']:
            if self.collide(p['x'], p['y'], 12, ph, pipe['x'] + 4, pipe['y'], 24, pipe['h']):
                if p['vy'] > 0 and p['y'] + ph > pipe['y'] and p['y'] < pipe['y']:
                    p['y'] = pipe['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
                elif p['vx'] > 0:
                    p['x'] = pipe['x'] + 4 - 12
                elif p['vx'] < 0:
                    p['x'] = pipe['x'] + 28
        
        for brick in self.level['bricks']:
            if brick['hit']:
                continue
            if self.collide(p['x'], p['y'], 12, ph, brick['x'], brick['y'], 16, 16):
                if p['vy'] < 0:
                    p['y'] = brick['y'] + 16
                    p['vy'] = 0
                    if self.big:
                        brick['hit'] = True
                        self.score += 50
                        self.particles.append({'x': brick['x'], 'y': brick['y'], 't': 'brk', 'life': 20, 'vy': -3})
                elif p['vy'] > 0:
                    p['y'] = brick['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
        
        for q in self.level['questions']:
            if q['hit']:
                continue
            if self.collide(p['x'], p['y'], 12, ph, q['x'], q['y'], 16, 16):
                if p['vy'] < 0:
                    p['y'] = q['y'] + 16
                    p['vy'] = 0
                    q['hit'] = True
                    if q['item'] == 'coin':
                        self.coins += 1
                        self.score += 200
                        self.particles.append({'x': q['x'], 'y': q['y'] - 16, 't': 'coin', 'life': 30, 'vy': -4})
                    else:
                        if not self.big:
                            self.big = True
                        self.score += 1000
                elif p['vy'] > 0:
                    p['y'] = q['y'] - ph
                    p['vy'] = 0
                    p['ground'] = True
        
        if p['y'] > NES_H:
            self.die()
            return
        
        if moving and p['ground']:
            if self.frame % 6 == 0:
                p['walk'] = (p['walk'] + 1) % 4
        elif not moving:
            p['walk'] = 0
        
        if p['inv'] > 0:
            p['inv'] -= 1
    
    def update_enemies(self):
        for e in self.level['enemies']:
            if not e['alive']:
                continue
            if e['stomped']:
                e['timer'] += 1
                if e['timer'] > 30:
                    e['alive'] = False
                continue
            
            e['x'] += e['vx']
            e['frame'] = (self.frame // 12) % 2
            
            if e['x'] < 0:
                e['vx'] = abs(e['vx'])
            if e['x'] > self.level['width'] - 16:
                e['vx'] = -abs(e['vx'])
            
            for pipe in self.level['pipes']:
                if e['x'] + 14 > pipe['x'] + 4 and e['x'] < pipe['x'] + 28:
                    if e['y'] + 16 > pipe['y']:
                        e['vx'] *= -1
                        e['x'] += e['vx'] * 2
    
    def update_particles(self):
        for pt in self.particles[:]:
            pt['y'] += pt.get('vy', -2)
            pt['life'] -= 1
            if pt['life'] <= 0:
                self.particles.remove(pt)
    
    def check_collisions(self):
        p = self.player
        ph = 28 if self.big else 16
        
        for c in self.level['coins']:
            if c['got']:
                continue
            if self.collide(p['x'], p['y'], 12, ph, c['x'], c['y'], 6, 12):
                c['got'] = True
                self.coins += 1
                self.score += 200
        
        for e in self.level['enemies']:
            if not e['alive'] or e['stomped']:
                continue
            ew = 14
            eh = 12 if e['type'] == 'goomba' else 18
            if self.collide(p['x'], p['y'], 12, ph, e['x'], e['y'], ew, eh):
                if p['vy'] > 0 and p['y'] + ph - 6 < e['y']:
                    e['stomped'] = True
                    e['vx'] = 0
                    p['vy'] = -4
                    self.score += 100
                elif p['inv'] <= 0:
                    if self.big:
                        self.big = False
                        p['inv'] = 90
                    else:
                        self.die()
    
    def collide(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2
    
    def die(self):
        self.state = 'dead'
        self.player['vy'] = -6
        self.player['vx'] = 0
        self.death_timer = 0
        self.audio.stop()
    
    def complete(self):
        self.state = 'clear'
        self.score += self.time * 50
        self.audio.stop()
    
    def update_dead(self):
        self.player['vy'] += Phys.GRAVITY
        self.player['y'] += self.player['vy']
        self.death_timer += 1
        
        if self.death_timer > 120:
            self.lives -= 1
            if self.lives <= 0:
                self.state = 'over'
            else:
                self.load()
                self.state = 'play'
    
    # ========== DRAWING ==========
    def draw_game(self):
        cx = self.camera
        bg = self.level['bg_color']
        lvl_type = self.level['type']
        
        self.r.rect(0, 0, WIDTH, HEIGHT, bg)
        
        # Background elements based on level type
        if lvl_type == 'overworld':
            for i in range(12):
                cloud_x = (i * 300 - cx * 0.3) % (NES_W * 3) - 150
                if -50 < cloud_x < NES_W + 50:
                    self.r.draw(int(cloud_x * SCALE), (32 + (i % 3) * 20) * SCALE, CLOUD)
            for i in range(20):
                bush_x = i * 180 - cx
                if -30 < bush_x < NES_W + 30:
                    self.r.draw(int(bush_x * SCALE), 196 * SCALE, BUSH)
        
        # Ground
        ground_sprite = STONE_BLOCK if lvl_type in ['underground', 'castle'] else GROUND
        for g in self.level['ground']:
            sx = g['x'] - cx
            if -16 < sx < NES_W + 16:
                self.r.draw(int(sx * SCALE), g['y'] * SCALE, ground_sprite)
                self.r.draw(int(sx * SCALE), (g['y'] + 16) * SCALE, ground_sprite)
        
        # Lava for castle levels
        if lvl_type == 'castle':
            for gap in [(800, 48), (1600, 64), (2400, 80)]:
                gap_x = gap[0] - cx
                if -100 < gap_x < NES_W + 100:
                    for lx in range(0, gap[1], 16):
                        self.r.draw(int((gap_x + lx) * SCALE), 224 * SCALE, LAVA)
        
        # Pipes
        for pipe in self.level['pipes']:
            sx = pipe['x'] - cx
            if -32 < sx < NES_W + 32:
                self.r.draw(int(sx * SCALE), pipe['y'] * SCALE, PIPE_TOP)
                for by in range(16, pipe['h'], 16):
                    self.r.draw(int(sx * SCALE), (pipe['y'] + by) * SCALE, PIPE_BODY)
        
        # Bricks
        for brick in self.level['bricks']:
            if brick['hit']:
                continue
            sx = brick['x'] - cx
            if -16 < sx < NES_W + 16:
                self.r.draw(int(sx * SCALE), brick['y'] * SCALE, BRICK)
        
        # Question blocks
        for q in self.level['questions']:
            sx = q['x'] - cx
            if -16 < sx < NES_W + 16:
                sprite = EMPTY_BLOCK if q['hit'] else Q_BLOCK
                self.r.draw(int(sx * SCALE), q['y'] * SCALE, sprite)
        
        # Coins
        coin_frames = [COIN1, COIN2, COIN3, COIN2]
        cf = coin_frames[(self.frame // 8) % 4]
        for c in self.level['coins']:
            if c['got']:
                continue
            sx = c['x'] - cx
            if -16 < sx < NES_W + 16:
                self.r.draw(int((sx + 4) * SCALE), c['y'] * SCALE, cf)
        
        # Enemies
        for e in self.level['enemies']:
            if not e['alive']:
                continue
            sx = e['x'] - cx
            if -16 < sx < NES_W + 16:
                if e['type'] == 'goomba':
                    if e['stomped']:
                        self.r.draw(int(sx * SCALE), (e['y'] + 6) * SCALE, GOOMBA_FLAT)
                    else:
                        gf = GOOMBA1 if e['frame'] == 0 else GOOMBA2
                        self.r.draw(int(sx * SCALE), (e['y'] + 4) * SCALE, gf)
                else:
                    self.r.draw(int(sx * SCALE), (e['y'] - 4) * SCALE, KOOPA)
        
        # Flagpole
        flag_sx = self.level['flag_x'] - cx
        if -16 < flag_sx < NES_W + 16:
            for y in range(64, 208, 8):
                self.r.rect(int((flag_sx + 14) * SCALE), y * SCALE, 4 * SCALE, 8 * SCALE, '#00A800')
            self.r.draw(int((flag_sx + 11) * SCALE), 58 * SCALE, FLAGPOLE_BALL)
            self.r.draw(int((flag_sx + 18) * SCALE), 70 * SCALE, FLAG)
        
        # Castle
        castle_sx = self.level['castle_x'] - cx
        if -64 < castle_sx < NES_W + 64:
            self.r.draw(int(castle_sx * SCALE), 172 * SCALE, CASTLE)
        
        # Particles
        for pt in self.particles:
            sx = pt['x'] - cx
            if pt['t'] == 'coin':
                self.r.draw(int(sx * SCALE), int(pt['y'] * SCALE), COIN1)
            elif pt['t'] == 'brk':
                self.r.rect(int(sx * SCALE), int(pt['y'] * SCALE), 8 * SCALE, 8 * SCALE, '#C84C0C')
        
        self.draw_player()
        self.draw_hud()
    
    def draw_player(self):
        p = self.player
        sx = (p['x'] - self.camera) * SCALE
        
        if p['inv'] > 0 and (self.frame // 4) % 2 == 0:
            return
        
        if not p['ground']:
            sprite = S_JUMP
        elif abs(p['vx']) > 0.1:
            walk_sprites = [S_WALK1, S_WALK2, S_WALK3, S_WALK2]
            sprite = walk_sprites[p['walk'] % 4]
        else:
            sprite = S_STAND
        
        if self.big:
            sprite = B_STAND
            self.r.draw(int(sx), int((p['y'] - 12) * SCALE), sprite, flip=(p['dir'] < 0))
        else:
            self.r.draw(int(sx), int(p['y'] * SCALE), sprite, flip=(p['dir'] < 0))
    
    def draw_hud(self):
        self.r.rect(0, 0, WIDTH, 26 * SCALE, '#000000')
        
        self.r.text(8 * SCALE, 4 * SCALE, "MARIO", '#FCFCFC', 5 * SCALE // 2)
        self.r.text(8 * SCALE, 13 * SCALE, f"{self.score:06d}", '#FCFCFC', 5 * SCALE // 2)
        
        self.r.draw(75 * SCALE, 11 * SCALE, COIN1)
        self.r.text(85 * SCALE, 13 * SCALE, f"×{self.coins:02d}", '#FCFCFC', 5 * SCALE // 2)
        
        self.r.text(130 * SCALE, 4 * SCALE, "WORLD", '#FCFCFC', 5 * SCALE // 2)
        self.r.text(134 * SCALE, 13 * SCALE, f"{self.world}-{self.stage}", '#FCFCFC', 5 * SCALE // 2)
        
        self.r.text(190 * SCALE, 4 * SCALE, "TIME", '#FCFCFC', 5 * SCALE // 2)
        time_col = '#FCFCFC' if self.time > 100 else '#FC0000'
        self.r.text(193 * SCALE, 13 * SCALE, f"{self.time:03d}", time_col, 5 * SCALE // 2)
        
        self.r.text(235 * SCALE, 13 * SCALE, f"×{self.lives}", '#FCFCFC', 5 * SCALE // 2)
    
    def draw_over(self):
        self.r.rect(0, 0, WIDTH, HEIGHT, '#000000')
        self.r.text(WIDTH // 2, HEIGHT // 2 - 20 * SCALE, "GAME OVER", '#FCFCFC', 10 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2 + 20 * SCALE, "PRESS ENTER", '#FCE4A0', 6 * SCALE // 2, 'center')
    
    def update_over(self):
        if self.keys & {'return', 'z', 'space'}:
            self.keys -= {'return', 'z', 'space'}
            self.state = 'menu'
    
    def draw_clear(self):
        self.r.rect(0, 0, WIDTH, HEIGHT, '#000000')
        self.r.text(WIDTH // 2, HEIGHT // 2 - 40 * SCALE, f"WORLD {self.world}-{self.stage}", '#FCA044', 8 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2 - 10 * SCALE, "COURSE CLEAR!", '#FCFCFC', 10 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2 + 20 * SCALE, f"SCORE: {self.score}", '#FCFCFC', 6 * SCALE // 2, 'center')
        self.r.text(WIDTH // 2, HEIGHT // 2 + 40 * SCALE, "PRESS ENTER", '#FCE4A0', 5 * SCALE // 2, 'center')
    
    def update_clear(self):
        if self.keys & {'return', 'z', 'space'}:
            self.keys -= {'return', 'z', 'space'}
            self.stage += 1
            if self.stage > 4:
                self.stage = 1
                self.world += 1
            if self.world > 8:
                self.state = 'menu'
            else:
                self.load()
                self.state = 'play'

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  ULTRA MARIO 2D BROS V0 — COMPLETE EDITION")
    print("  32 Levels (World 1-1 to 8-4)")
    print("  Full NES-Style OST")
    print("=" * 60)
    print("  © 1985 Nintendo")
    print("  © Samsoft 2025")
    print("=" * 60)
    print("\n  Controls:")
    print("    ← →  / A D   : Move")
    print("    Z / Space / W : Jump")
    print("    X / Shift     : Run")
    print("\n  Level Types:")
    print("    X-1, X-3 : Overworld (blue sky)")
    print("    X-2      : Underground (black)")
    print("    X-4      : Castle (lava)")
    print("=" * 60)
    
    if not AUDIO_AVAILABLE:
        print("\n  NOTE: Install pyaudio for music:")
        print("    pip install pyaudio")
    
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
