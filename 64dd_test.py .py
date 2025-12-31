#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CAT'S ULTRA 64DD SOUND TEST                               ║
║              Dynamic Sound Engine with Synthesized Voice FX                  ║
║              100% Programmatic Audio - No External Files                     ║
║              (C) 2025 Samsoft / Flames Co.                                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk
import math
import struct
import wave
import tempfile
import os
import threading
import random
import time

# Cross-platform audio playback
try:
    import winsound
    AUDIO_BACKEND = 'winsound'
except ImportError:
    AUDIO_BACKEND = 'aplay'

class SoundEngine:
    """
    Cat's Ultra 64DD Sound Synthesizer
    Generates voice-like sounds programmatically using:
    - Formant synthesis for vowel sounds
    - Frequency modulation for expressiveness
    - Noise bursts for consonants
    - Pitch bending for natural feel
    """
    
    SAMPLE_RATE = 22050
    
    def __init__(self):
        self.temp_files = []
        
    def cleanup(self):
        """Remove temporary audio files"""
        for f in self.temp_files:
            try:
                os.remove(f)
            except:
                pass
    
    def _generate_formant(self, freq, formants, duration, amplitude=0.3):
        """Generate formant-based vowel sound"""
        samples = []
        n = int(self.SAMPLE_RATE * duration)
        
        for i in range(n):
            t = i / self.SAMPLE_RATE
            
            # Base frequency with slight vibrato
            vibrato = 1.0 + 0.02 * math.sin(2 * math.pi * 5 * t)
            base_freq = freq * vibrato
            
            # Generate formants (resonant frequencies for vowels)
            sample = 0
            for f_freq, f_amp in formants:
                # Each formant is a band-passed oscillator
                sample += f_amp * math.sin(2 * math.pi * f_freq * t)
            
            # Modulate with base pitch
            sample *= math.sin(2 * math.pi * base_freq * t)
            
            # Apply envelope
            attack = 0.05
            release = 0.1
            if t < attack:
                env = t / attack
            elif t > duration - release:
                env = (duration - t) / release
            else:
                env = 1.0
            
            sample *= env * amplitude
            samples.append(sample)
        
        return samples
    
    def _generate_noise_burst(self, duration, amplitude=0.2):
        """Generate noise burst for consonants like 'W', 'Y'"""
        samples = []
        n = int(self.SAMPLE_RATE * duration)
        
        for i in range(n):
            t = i / self.SAMPLE_RATE
            # Filtered noise
            noise = random.random() * 2 - 1
            # Quick decay
            env = max(0, 1.0 - t / duration * 2)
            samples.append(noise * env * amplitude)
        
        return samples
    
    def _pitch_bend(self, samples, start_mult, end_mult):
        """Apply pitch bend by resampling"""
        result = []
        n = len(samples)
        for i in range(n):
            progress = i / n
            mult = start_mult + (end_mult - start_mult) * progress
            src_idx = int(i * mult) % n
            result.append(samples[src_idx])
        return result
    
    def generate_wahoo(self):
        """Generate 'WAHOO!' sound"""
        samples = []
        
        # "W" - noise burst with rising formant
        w_noise = self._generate_noise_burst(0.08, 0.15)
        samples.extend(w_noise)
        
        # "AH" - open vowel, formants: F1=700, F2=1200
        ah_formants = [(700, 0.8), (1200, 0.5), (2500, 0.2)]
        ah = self._generate_formant(180, ah_formants, 0.15, 0.4)
        samples.extend(ah)
        
        # "HOO" - pitch rise, formants: F1=300, F2=800
        hoo_formants = [(300, 0.9), (800, 0.4), (2300, 0.15)]
        hoo = self._generate_formant(220, hoo_formants, 0.25, 0.5)
        # Add pitch rise
        hoo = self._pitch_bend(hoo, 0.8, 1.3)
        samples.extend(hoo)
        
        # "!" - sharp attack burst
        exclaim = self._generate_noise_burst(0.05, 0.3)
        samples.extend(exclaim)
        
        return self._normalize(samples)
    
    def generate_lets_a_go(self):
        """Generate 'LETS A GO!' sound"""
        samples = []
        
        # "L" - soft onset
        l_formants = [(350, 0.5), (1200, 0.3)]
        l_sound = self._generate_formant(150, l_formants, 0.08, 0.25)
        samples.extend(l_sound)
        
        # "EH" - front vowel
        eh_formants = [(530, 0.8), (1850, 0.5), (2500, 0.2)]
        eh = self._generate_formant(160, eh_formants, 0.1, 0.35)
        samples.extend(eh)
        
        # "TS" - noise
        ts = self._generate_noise_burst(0.06, 0.2)
        samples.extend(ts)
        
        # Short pause
        samples.extend([0] * int(self.SAMPLE_RATE * 0.05))
        
        # "A" - schwa
        a_formants = [(500, 0.7), (1500, 0.4)]
        a_sound = self._generate_formant(170, a_formants, 0.08, 0.3)
        samples.extend(a_sound)
        
        # Short pause
        samples.extend([0] * int(self.SAMPLE_RATE * 0.05))
        
        # "GO" - back vowel with pitch
        go_formants = [(400, 0.9), (900, 0.5), (2300, 0.15)]
        go = self._generate_formant(200, go_formants, 0.2, 0.45)
        go = self._pitch_bend(go, 1.0, 1.2)
        samples.extend(go)
        
        # "!" excitement burst
        exclaim = self._generate_noise_burst(0.04, 0.25)
        samples.extend(exclaim)
        
        return self._normalize(samples)
    
    def generate_yippee(self):
        """Generate 'YIPPEE!' sound - excited, high pitched"""
        samples = []
        
        # "Y" - glide onset
        y_formants = [(280, 0.6), (2300, 0.7), (3000, 0.3)]
        y_sound = self._generate_formant(250, y_formants, 0.06, 0.3)
        samples.extend(y_sound)
        
        # "I" - high front vowel
        i_formants = [(280, 0.8), (2250, 0.6), (2900, 0.3)]
        i_sound = self._generate_formant(280, i_formants, 0.1, 0.4)
        samples.extend(i_sound)
        
        # "PP" - stop burst
        pp = self._generate_noise_burst(0.04, 0.15)
        samples.extend(pp)
        
        # "EE" - high sustained, excited!
        ee_formants = [(270, 0.9), (2300, 0.7), (3000, 0.35)]
        ee = self._generate_formant(320, ee_formants, 0.25, 0.5)
        # Rising pitch for excitement
        ee = self._pitch_bend(ee, 0.9, 1.4)
        samples.extend(ee)
        
        # "!" - final burst
        exclaim = self._generate_noise_burst(0.03, 0.2)
        samples.extend(exclaim)
        
        return self._normalize(samples)
    
    def generate_meow(self):
        """Generate cat 'MEOW!' sound"""
        samples = []
        
        # "M" - nasal onset
        m_formants = [(250, 0.5), (1000, 0.2)]
        m_sound = self._generate_formant(200, m_formants, 0.1, 0.25)
        samples.extend(m_sound)
        
        # "E" transitioning to "OW"
        for i in range(10):
            progress = i / 10
            # Interpolate formants
            f1 = 500 + progress * (-200)  # 500 -> 300
            f2 = 1800 - progress * 1000    # 1800 -> 800
            formants = [(f1, 0.8), (f2, 0.5)]
            chunk = self._generate_formant(180 + progress * 40, formants, 0.03, 0.4)
            samples.extend(chunk)
        
        return self._normalize(samples)
    
    def generate_nya(self):
        """Generate cat 'NYA~!' sound"""
        samples = []
        
        # "N" - nasal
        n_formants = [(280, 0.4), (1500, 0.2)]
        n_sound = self._generate_formant(220, n_formants, 0.06, 0.25)
        samples.extend(n_sound)
        
        # "YA" - bright vowel
        ya_formants = [(750, 0.9), (1800, 0.6), (2800, 0.3)]
        ya = self._generate_formant(280, ya_formants, 0.2, 0.45)
        ya = self._pitch_bend(ya, 1.0, 1.15)
        samples.extend(ya)
        
        # Cute ending
        end_formants = [(300, 0.5), (1200, 0.3)]
        end = self._generate_formant(320, end_formants, 0.1, 0.25)
        samples.extend(end)
        
        return self._normalize(samples)
    
    def generate_coin(self):
        """Generate coin/bling sound"""
        samples = []
        n = int(self.SAMPLE_RATE * 0.2)
        
        freq1, freq2 = 988, 1319  # B5, E6
        
        for i in range(n):
            t = i / self.SAMPLE_RATE
            # Two-tone with decay
            wave1 = math.sin(2 * math.pi * freq1 * t)
            wave2 = math.sin(2 * math.pi * freq2 * t)
            env = max(0, 1.0 - t * 4)
            sample = (wave1 + wave2) * 0.5 * env * 0.4
            samples.append(sample)
        
        return self._normalize(samples)
    
    def generate_jump(self):
        """Generate jump sound with rising pitch"""
        samples = []
        n = int(self.SAMPLE_RATE * 0.15)
        
        for i in range(n):
            t = i / self.SAMPLE_RATE
            # Rising frequency
            freq = 200 + t * 600
            wave = 1.0 if (int(t * freq * 2) % 2 == 0) else -1.0
            env = max(0, 1.0 - t * 5)
            samples.append(wave * env * 0.35)
        
        return self._normalize(samples)
    
    def generate_powerup(self):
        """Generate power-up arpeggio"""
        samples = []
        notes = [262, 330, 392, 523, 659, 784]  # C major arpeggio
        
        for freq in notes:
            n = int(self.SAMPLE_RATE * 0.08)
            for i in range(n):
                t = i / self.SAMPLE_RATE
                wave = math.sin(2 * math.pi * freq * t)
                env = 1.0 - (i / n) * 0.3
                samples.append(wave * env * 0.3)
        
        return self._normalize(samples)
    
    def generate_1up(self):
        """Generate 1-UP sound"""
        samples = []
        notes = [330, 392, 523, 392, 523, 698]
        
        for freq in notes:
            n = int(self.SAMPLE_RATE * 0.1)
            for i in range(n):
                t = i / self.SAMPLE_RATE
                wave = 1.0 if (int(t * freq * 2) % 2 == 0) else -1.0
                env = 1.0 - (i / n) * 0.2
                samples.append(wave * env * 0.25)
        
        return self._normalize(samples)
    
    def _normalize(self, samples):
        """Normalize samples to prevent clipping"""
        if not samples:
            return samples
        max_val = max(abs(s) for s in samples)
        if max_val > 0:
            samples = [s / max_val * 0.9 for s in samples]
        return samples
    
    def samples_to_wav(self, samples):
        """Convert samples to WAV file and return path"""
        # Create temp file
        fd, path = tempfile.mkstemp(suffix='.wav')
        os.close(fd)
        self.temp_files.append(path)
        
        # Write WAV
        with wave.open(path, 'w') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.SAMPLE_RATE)
            
            # Convert to 16-bit PCM
            data = b''
            for s in samples:
                val = int(s * 32767)
                val = max(-32768, min(32767, val))
                data += struct.pack('<h', val)
            
            wav.writeframes(data)
        
        return path
    
    def play_samples(self, samples):
        """Play samples using available audio backend"""
        path = self.samples_to_wav(samples)
        
        def play_thread():
            try:
                if AUDIO_BACKEND == 'winsound':
                    winsound.PlaySound(path, winsound.SND_FILENAME)
                else:
                    os.system(f'aplay -q "{path}" 2>/dev/null || afplay "{path}" 2>/dev/null &')
            except Exception as e:
                print(f"Audio playback error: {e}")
        
        thread = threading.Thread(target=play_thread, daemon=True)
        thread.start()


class Cat64DDSoundTest:
    """
    Cat's Ultra 64DD Sound Test GUI
    Tkinter-based interface with 60fps update loop
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Cat's Ultra 64DD Sound Test")
        self.root.geometry("700x550")
        self.root.configure(bg='#0a0a1a')
        self.root.resizable(False, False)
        
        self.sound_engine = SoundEngine()
        self.frame_count = 0
        self.fps = 60
        self.frame_time = 1000 // self.fps
        
        # Animation states
        self.visualizer_data = [0] * 32
        self.last_sound = ""
        self.flash_timer = 0
        self.cat_frame = 0
        
        self._create_ui()
        self._start_loop()
    
    def _create_ui(self):
        """Create the GUI"""
        # Header with cat ASCII
        header_frame = tk.Frame(self.root, bg='#0a0a1a')
        header_frame.pack(pady=10)
        
        cat_art = """
   /\\_/\\  
  ( o.o ) 
   > ^ <
        """
        cat_label = tk.Label(
            header_frame,
            text=cat_art,
            font=('Courier', 12),
            fg='#ff69b4',
            bg='#0a0a1a'
        )
        cat_label.pack()
        
        # Title
        title = tk.Label(
            header_frame,
            text="🎮 CAT'S ULTRA 64DD 🎮",
            font=('Courier', 28, 'bold'),
            fg='#ff6b6b',
            bg='#0a0a1a'
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text="✨ DYNAMIC SOUND TEST ENGINE ✨",
            font=('Courier', 14, 'bold'),
            fg='#4ecdc4',
            bg='#0a0a1a'
        )
        subtitle.pack()
        
        # Visualizer canvas
        self.canvas = tk.Canvas(
            self.root,
            width=650,
            height=80,
            bg='#16213e',
            highlightthickness=3,
            highlightbackground='#ff6b6b'
        )
        self.canvas.pack(pady=10)
        
        # Sound display
        self.sound_label = tk.Label(
            self.root,
            text="🔊 Press a button! 🔊",
            font=('Courier', 22, 'bold'),
            fg='#ffffff',
            bg='#0a0a1a'
        )
        self.sound_label.pack(pady=5)
        
        # Voice buttons frame
        voice_frame = tk.Frame(self.root, bg='#0a0a1a')
        voice_frame.pack(pady=10)
        
        voice_label = tk.Label(
            voice_frame,
            text="━━━━━ VOICE FX ━━━━━",
            font=('Courier', 12, 'bold'),
            fg='#ff6b6b',
            bg='#0a0a1a'
        )
        voice_label.pack(pady=5)
        
        btn_frame1 = tk.Frame(voice_frame, bg='#0a0a1a')
        btn_frame1.pack()
        
        self._create_button(btn_frame1, "WAHOO!", self._play_wahoo, '#ff6b6b')
        self._create_button(btn_frame1, "LETS A GO!", self._play_lets_a_go, '#4ecdc4')
        self._create_button(btn_frame1, "YIPPEE!", self._play_yippee, '#ffe66d')
        
        btn_frame2 = tk.Frame(voice_frame, bg='#0a0a1a')
        btn_frame2.pack(pady=5)
        
        self._create_button(btn_frame2, "MEOW!", self._play_meow, '#ff69b4')
        self._create_button(btn_frame2, "NYA~!", self._play_nya, '#da70d6')
        
        # SFX buttons frame
        sfx_frame = tk.Frame(self.root, bg='#0a0a1a')
        sfx_frame.pack(pady=10)
        
        sfx_label = tk.Label(
            sfx_frame,
            text="━━━━━ SOUND FX ━━━━━",
            font=('Courier', 12, 'bold'),
            fg='#4ecdc4',
            bg='#0a0a1a'
        )
        sfx_label.pack(pady=5)
        
        btn_frame3 = tk.Frame(sfx_frame, bg='#0a0a1a')
        btn_frame3.pack()
        
        self._create_button(btn_frame3, "💰 COIN", self._play_coin, '#ffd700')
        self._create_button(btn_frame3, "⬆ JUMP", self._play_jump, '#32cd32')
        self._create_button(btn_frame3, "⭐ POWER-UP", self._play_powerup, '#9370db')
        self._create_button(btn_frame3, "❤ 1-UP", self._play_1up, '#ff4500')
        
        # Info footer
        footer_frame = tk.Frame(self.root, bg='#0a0a1a')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # FPS counter
        self.fps_label = tk.Label(
            footer_frame,
            text="⚡ 60 FPS ⚡",
            font=('Courier', 11, 'bold'),
            fg='#32cd32',
            bg='#0a0a1a'
        )
        self.fps_label.pack()
        
        footer = tk.Label(
            footer_frame,
            text="(C) 2025 Samsoft / Flames Co. - All sounds synthesized programmatically - No external files!",
            font=('Courier', 9),
            fg='#555555',
            bg='#0a0a1a'
        )
        footer.pack()
    
    def _create_button(self, parent, text, command, color):
        """Create a styled button"""
        btn = tk.Button(
            parent,
            text=text,
            font=('Courier', 11, 'bold'),
            fg='#0a0a1a',
            bg=color,
            activebackground='#ffffff',
            activeforeground='#0a0a1a',
            width=12,
            height=2,
            relief=tk.RAISED,
            bd=4,
            cursor='hand2',
            command=command
        )
        btn.pack(side=tk.LEFT, padx=4, pady=4)
        
        # Hover effects
        def on_enter(e):
            btn.configure(bg='#ffffff', fg=color)
        def on_leave(e):
            btn.configure(bg=color, fg='#0a0a1a')
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
    
    def _play_wahoo(self):
        self.last_sound = "🎉 WAHOO! 🎉"
        self.flash_timer = 30
        self._trigger_visualizer()
        samples = self.sound_engine.generate_wahoo()
        self.sound_engine.play_samples(samples)
    
    def _play_lets_a_go(self):
        self.last_sound = "🏃 LETS A GO! 🏃"
        self.flash_timer = 30
        self._trigger_visualizer()
        samples = self.sound_engine.generate_lets_a_go()
        self.sound_engine.play_samples(samples)
    
    def _play_yippee(self):
        self.last_sound = "🌟 YIPPEE! 🌟"
        self.flash_timer = 30
        self._trigger_visualizer()
        samples = self.sound_engine.generate_yippee()
        self.sound_engine.play_samples(samples)
    
    def _play_meow(self):
        self.last_sound = "🐱 MEOW! 🐱"
        self.flash_timer = 30
        self._trigger_visualizer()
        samples = self.sound_engine.generate_meow()
        self.sound_engine.play_samples(samples)
    
    def _play_nya(self):
        self.last_sound = "😺 NYA~! 😺"
        self.flash_timer = 30
        self._trigger_visualizer()
        samples = self.sound_engine.generate_nya()
        self.sound_engine.play_samples(samples)
    
    def _play_coin(self):
        self.last_sound = "💰 COIN! 💰"
        self.flash_timer = 20
        self._trigger_visualizer()
        samples = self.sound_engine.generate_coin()
        self.sound_engine.play_samples(samples)
    
    def _play_jump(self):
        self.last_sound = "⬆ JUMP! ⬆"
        self.flash_timer = 15
        self._trigger_visualizer()
        samples = self.sound_engine.generate_jump()
        self.sound_engine.play_samples(samples)
    
    def _play_powerup(self):
        self.last_sound = "⭐ POWER-UP! ⭐"
        self.flash_timer = 40
        self._trigger_visualizer()
        samples = self.sound_engine.generate_powerup()
        self.sound_engine.play_samples(samples)
    
    def _play_1up(self):
        self.last_sound = "❤ 1-UP! ❤"
        self.flash_timer = 45
        self._trigger_visualizer()
        samples = self.sound_engine.generate_1up()
        self.sound_engine.play_samples(samples)
    
    def _trigger_visualizer(self):
        """Trigger visualizer animation"""
        for i in range(len(self.visualizer_data)):
            self.visualizer_data[i] = random.randint(40, 75)
    
    def _update_visualizer(self):
        """Update visualizer bars"""
        self.canvas.delete('all')
        
        bar_width = 650 // len(self.visualizer_data)
        colors = ['#ff6b6b', '#ff8e72', '#4ecdc4', '#45b7aa', '#ffe66d', '#ffd93d', 
                  '#9370db', '#8a60d6', '#ff69b4', '#ff85c0', '#32cd32', '#5fd35f']
        
        for i, height in enumerate(self.visualizer_data):
            x = i * bar_width
            color = colors[i % len(colors)]
            
            # Draw bar with gradient effect
            self.canvas.create_rectangle(
                x + 2, 80 - height,
                x + bar_width - 2, 80,
                fill=color,
                outline='#ffffff',
                width=1
            )
            
            # Add glow at top
            if height > 20:
                self.canvas.create_rectangle(
                    x + 4, 80 - height,
                    x + bar_width - 4, 80 - height + 4,
                    fill='#ffffff',
                    outline=''
                )
            
            # Decay with slight randomness
            decay = random.randint(1, 3)
            self.visualizer_data[i] = max(5, height - decay)
    
    def _update(self):
        """Main update loop - 60fps"""
        self.frame_count += 1
        
        # Update visualizer
        self._update_visualizer()
        
        # Update sound display
        if self.flash_timer > 0:
            self.flash_timer -= 1
            # Flash effect with colors
            colors = ['#ff6b6b', '#4ecdc4', '#ffe66d', '#ff69b4', '#9370db']
            color = colors[(self.flash_timer // 3) % len(colors)]
            self.sound_label.configure(fg=color, text=self.last_sound)
        else:
            self.sound_label.configure(fg='#555555', text='🔊 Press a button! 🔊')
        
        # Update FPS display with color pulse
        if self.frame_count % 30 == 0:
            fps_colors = ['#32cd32', '#4ecdc4', '#32cd32']
            self.fps_label.configure(
                fg=fps_colors[(self.frame_count // 30) % len(fps_colors)]
            )
        
        # Schedule next frame
        self.root.after(self.frame_time, self._update)
    
    def _start_loop(self):
        """Start the 60fps update loop"""
        self._update()
    
    def run(self):
        """Run the application"""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║         CAT'S ULTRA 64DD SOUND TEST ENGINE                   ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║  VOICE FX:                                                   ║")
        print("║    • WAHOO!     - Excited jump exclamation                   ║")
        print("║    • LETS A GO! - Ready to go phrase                         ║")
        print("║    • YIPPEE!    - Happy celebration                          ║")
        print("║    • MEOW!      - Cat meow                                   ║")
        print("║    • NYA~!      - Cute cat sound                             ║")
        print("║                                                              ║")
        print("║  SOUND FX:                                                   ║")
        print("║    • COIN       - Collection bling                           ║")
        print("║    • JUMP       - Rising pitch jump                          ║")
        print("║    • POWER-UP   - Arpeggio fanfare                           ║")
        print("║    • 1-UP       - Extra life jingle                          ║")
        print("║                                                              ║")
        print("║  ✨ All sounds synthesized programmatically! ✨              ║")
        print("║  🎮 Running at 60 FPS with Tkinter GUI                       ║")
        print("║  📁 No external files required!                              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()
        
        try:
            self.root.mainloop()
        finally:
            self.sound_engine.cleanup()


if __name__ == "__main__":
    app = Cat64DDSoundTest()
    app.run()
