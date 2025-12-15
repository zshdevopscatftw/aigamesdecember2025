#!/usr/bin/env python3
"""
Cat's CHIP-8 ROM v1.0 - SAMSOFT RTX ! ON 1999-2025
Project64-Style GUI | Functional Menus | Multiple ROMs
Universal Controller Support (Atari 2600 to PS5)
"""

import pygame
import sys
import random

# ═══════════════════════════════════════════════════════════════════════════════
# EMBEDDED ROMS
# ═══════════════════════════════════════════════════════════════════════════════

ROMS = {
    "pong.chip8": {
        "name": "Pong",
        "author": "David Winter",
        "desc": "Classic 2-player Pong. P1: 1/Q, P2: 4/R",
        "data": bytes([
            0x6A, 0x02, 0x6B, 0x0C, 0x6C, 0x3F, 0x6D, 0x0C, 0xA2, 0xEA, 0xDA, 0xB6,
            0xDC, 0xD6, 0x6E, 0x00, 0x22, 0xD4, 0x66, 0x03, 0x68, 0x02, 0x60, 0x60,
            0xF0, 0x15, 0xF0, 0x07, 0x30, 0x00, 0x12, 0x1A, 0xC7, 0x17, 0x77, 0x08,
            0x69, 0xFF, 0xA2, 0xF0, 0xD6, 0x71, 0xA2, 0xEA, 0xDA, 0xB6, 0x86, 0x48,
            0x87, 0x58, 0x60, 0x04, 0x61, 0x01, 0x87, 0x84, 0x87, 0x94, 0x47, 0x1F,
            0x69, 0xFF, 0x47, 0x00, 0x69, 0x01, 0xD6, 0x71, 0x12, 0x2A, 0x68, 0x02,
            0x63, 0x01, 0x80, 0x70, 0x80, 0xB5, 0x12, 0x8A, 0x68, 0xFE, 0x63, 0x0A,
            0x80, 0x70, 0x80, 0xD5, 0x3F, 0x01, 0x12, 0xA2, 0x61, 0x02, 0x80, 0x15,
            0x3F, 0x01, 0x12, 0xBA, 0x80, 0x15, 0x3F, 0x01, 0x12, 0xC8, 0x80, 0x15,
            0x3F, 0x01, 0x12, 0xC2, 0x60, 0x20, 0xF0, 0x18, 0x22, 0xD4, 0x8E, 0x34,
            0x22, 0xD4, 0x66, 0x3E, 0x33, 0x01, 0x66, 0x03, 0x68, 0xFE, 0x33, 0x01,
            0x68, 0x02, 0x12, 0x16, 0x79, 0xFF, 0x49, 0xFE, 0x69, 0xFF, 0x12, 0xC8,
            0x79, 0x01, 0x49, 0x02, 0x69, 0x01, 0x60, 0x04, 0xF0, 0x18, 0x76, 0x01,
            0x46, 0x40, 0x76, 0xFE, 0x12, 0x6C, 0xA2, 0xF2, 0xFE, 0x33, 0xF2, 0x65,
            0xF1, 0x29, 0x64, 0x14, 0x65, 0x00, 0xD4, 0x55, 0x74, 0x15, 0xF2, 0x29,
            0xD4, 0x55, 0x00, 0xEE, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x00,
            0x00, 0x00, 0x00, 0x00
        ])
    },
    "calc.chip8": {
        "name": "Calculator",
        "author": "Samsoft",
        "desc": "Keypad demo - press keys to display digits. F=Clear",
        "data": bytes([
            0x00, 0xE0, 0x6A, 0x00, 0x6B, 0x00, 0x6C, 0x08, 0x6D, 0x08,
            0x6E, 0x00, 0xFE, 0x0A, 0x3E, 0x0F, 0x12, 0x18, 0x00, 0xE0,
            0x6C, 0x08, 0x6D, 0x08, 0x12, 0x06, 0xFE, 0x29, 0xDC, 0xD5,
            0x7C, 0x06, 0x3C, 0x38, 0x12, 0x06, 0x6C, 0x08, 0x7D, 0x07,
            0x3D, 0x1D, 0x12, 0x06, 0x6D, 0x08, 0x12, 0x06,
        ])
    },
    "maze.chip8": {
        "name": "Maze",
        "author": "David Winter",
        "desc": "Random maze generator demo - watch it draw!",
        "data": bytes([
            0x60, 0x00, 0x61, 0x00, 0xA2, 0x22, 0xC2, 0x01, 0x32, 0x01,
            0xA2, 0x1E, 0xD0, 0x14, 0x70, 0x04, 0x30, 0x40, 0x12, 0x04,
            0x60, 0x00, 0x71, 0x04, 0x31, 0x20, 0x12, 0x04, 0x12, 0x1C,
            0x10, 0x20, 0x40, 0x80, 0x80, 0x40, 0x20, 0x10,
        ])
    },
    "snake.chip8": {
        "name": "Snake Demo",
        "author": "Samsoft",
        "desc": "Simple snake game. WASD to move",
        "data": bytes([
            0x00, 0xE0, 0x6A, 0x20, 0x6B, 0x10, 0x6C, 0x02, 0x6D, 0x00,
            0xA2, 0x50, 0xDA, 0xB2, 0x60, 0x03, 0xF0, 0x15, 0xF0, 0x07,
            0x30, 0x00, 0x12, 0x10, 0x60, 0x05, 0xE0, 0x9E, 0x12, 0x20,
            0x6C, 0x00, 0x6D, 0xFE, 0x60, 0x08, 0xE0, 0x9E, 0x12, 0x2A,
            0x6C, 0x00, 0x6D, 0x02, 0x60, 0x07, 0xE0, 0x9E, 0x12, 0x34,
            0x6C, 0xFE, 0x6D, 0x00, 0x60, 0x09, 0xE0, 0x9E, 0x12, 0x3E,
            0x6C, 0x02, 0x6D, 0x00, 0xDA, 0xB2, 0x8A, 0xC0, 0x8B, 0xD0,
            0x6E, 0x3F, 0x8A, 0xE2, 0x6E, 0x1F, 0x8B, 0xE2, 0xDA, 0xB2,
            0x12, 0x0A, 0xC0, 0xC0,
        ])
    },
    "particle.chip8": {
        "name": "Particles",
        "author": "Samsoft",
        "desc": "Random particle explosion demo",
        "data": bytes([
            0x00, 0xE0, 0x60, 0x20, 0x61, 0x10, 0x62, 0x20, 0x63, 0x10,
            0x64, 0x20, 0x65, 0x10, 0x66, 0x20, 0x67, 0x10, 0xA2, 0x50,
            0xC8, 0x03, 0xC9, 0x03, 0x78, 0xFE, 0x79, 0xFE, 0xD0, 0x11,
            0x80, 0x80, 0x81, 0x90, 0x6E, 0x3F, 0x80, 0xE2, 0x6E, 0x1F,
            0x81, 0xE2, 0xD0, 0x11, 0xC8, 0x07, 0xC9, 0x07, 0x78, 0xFC,
            0x79, 0xFC, 0xD2, 0x31, 0x82, 0x80, 0x83, 0x90, 0x6E, 0x3F,
            0x82, 0xE2, 0x6E, 0x1F, 0x83, 0xE2, 0xD2, 0x31, 0x6A, 0x01,
            0xFA, 0x15, 0xFA, 0x07, 0x3A, 0x00, 0x12, 0x40, 0x12, 0x14,
            0x80,
        ])
    },
    "ibm.chip8": {
        "name": "IBM Logo",
        "author": "Unknown",
        "desc": "Classic IBM Logo test ROM",
        "data": bytes([
            0x00, 0xE0, 0xA2, 0x2A, 0x60, 0x0C, 0x61, 0x08, 0xD0, 0x1F,
            0x70, 0x09, 0xA2, 0x39, 0xD0, 0x1F, 0xA2, 0x48, 0x70, 0x08,
            0xD0, 0x1F, 0x70, 0x04, 0xA2, 0x57, 0xD0, 0x1F, 0x70, 0x08,
            0xA2, 0x66, 0xD0, 0x1F, 0x70, 0x08, 0xA2, 0x75, 0xD0, 0x1F,
            0x12, 0x28,
            0xFF, 0x00, 0xFF, 0x00, 0x3C, 0x00, 0x3C, 0x00, 0x3C, 0x00,
            0x3C, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00, 0xFF, 0x00,
            0x38, 0x00, 0x3F, 0x00, 0x3F, 0x00, 0x38, 0x00, 0xFF, 0x00,
            0xFF, 0x00, 0xFF, 0x00, 0x80, 0x00, 0xE0, 0x00, 0xE0, 0x00,
            0x80, 0x00, 0x80, 0x00, 0xE0, 0x00, 0xE0, 0x00, 0x80, 0x00,
            0xF8, 0x00, 0xFC, 0x00, 0x3E, 0x00, 0x3F, 0x00, 0x3B, 0x00,
            0x39, 0x00, 0xF8, 0x00, 0xF8, 0x00, 0x03, 0x00, 0x07, 0x00,
            0x0F, 0x00, 0xBF, 0x00, 0xFB, 0x00, 0xF3, 0x00, 0xE3, 0x00,
            0x43, 0x00, 0xE0, 0x00, 0xE0, 0x00, 0x80, 0x00, 0x80, 0x00,
            0x80, 0x00, 0x80, 0x00, 0xE0, 0x00, 0xE0,
        ])
    },
    "tetris.chip8": {
        "name": "Mini Tetris",
        "author": "Samsoft",
        "desc": "Tiny Tetris-like. Q/E rotate, A/D move, S drop",
        "data": bytes([
            0x00, 0xE0, 0x6A, 0x1C, 0x6B, 0x00, 0x6C, 0x00, 0xA2, 0x80,
            0xC6, 0x03, 0x26, 0x00, 0xDA, 0xB4, 0x60, 0x07, 0xE0, 0x9E,
            0x12, 0x18, 0x7A, 0xFE, 0x3A, 0x08, 0x6A, 0x08, 0x60, 0x09,
            0xE0, 0x9E, 0x12, 0x24, 0x7A, 0x02, 0x3A, 0x30, 0x6A, 0x2E,
            0x60, 0x08, 0xE0, 0x9E, 0x12, 0x30, 0x7B, 0x02, 0x3B, 0x1C,
            0x6B, 0x1A, 0xDA, 0xB4, 0x3F, 0x00, 0x12, 0x06, 0xDA, 0xB4,
            0x60, 0x05, 0xF0, 0x15, 0xF0, 0x07, 0x30, 0x00, 0x12, 0x3E,
            0xDA, 0xB4, 0x7B, 0x02, 0x3B, 0x1C, 0x12, 0x56, 0xDA, 0xB4,
            0x3F, 0x00, 0x12, 0x06, 0xDA, 0xB4, 0x7B, 0xFE, 0x12, 0x06,
            0x12, 0x06,
            0xF0, 0xF0, 0x00, 0x00,
            0x60, 0x60, 0x60, 0x60,
            0xE0, 0x40, 0x00, 0x00,
            0xF0, 0x90, 0x00, 0x00,
        ])
    }
}

# ═══════════════════════════════════════════════════════════════════════════════
# CHIP-8 FONTSET
# ═══════════════════════════════════════════════════════════════════════════════

FONTSET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
]

WIDTH, HEIGHT = 64, 32


# ═══════════════════════════════════════════════════════════════════════════════
# PROJECT64 COLOR SCHEME
# ═══════════════════════════════════════════════════════════════════════════════

class P64:
    BG = (20, 28, 20)
    MENU_BG = (45, 60, 45)
    MENU_HOVER = (60, 85, 60)
    MENU_ACTIVE = (75, 105, 75)
    MENU_BORDER = (30, 42, 30)
    TOOLBAR = (38, 52, 38)
    TOOLBAR_BTN = (52, 72, 52)
    TOOLBAR_HOVER = (68, 95, 68)
    GOLD = (218, 165, 32)
    GOLD_HI = (255, 200, 64)
    GOLD_LO = (160, 120, 32)
    TEXT = (200, 200, 180)
    TEXT_DIM = (130, 130, 110)
    PIXEL_ON = (0, 255, 64)
    PIXEL_OFF = (8, 20, 8)
    BORDER = (48, 68, 48)
    STATUS = (30, 42, 30)
    LIST_BG = (18, 25, 18)
    LIST_SEL = (45, 75, 45)
    LIST_HOVER = (32, 48, 32)


# ═══════════════════════════════════════════════════════════════════════════════
# CHIP-8 EMULATOR
# ═══════════════════════════════════════════════════════════════════════════════

class Chip8:
    def __init__(self):
        self.reset()

    def reset(self):
        self.memory = [0] * 4096
        self.V = [0] * 16
        self.I = 0
        self.pc = 0x200
        self.stack = []
        self.display = [[0] * WIDTH for _ in range(HEIGHT)]
        self.keys = [0] * 16
        self.delay_timer = 0
        self.sound_timer = 0
        self.waiting_key = False
        self.key_reg = 0
        self.paused = False
        self.running = False
        for i, b in enumerate(FONTSET):
            self.memory[i] = b

    def load(self, data):
        self.reset()
        for i, b in enumerate(data):
            if 0x200 + i < 4096:
                self.memory[0x200 + i] = b
        self.running = True

    def cycle(self):
        if self.paused or self.waiting_key or not self.running:
            return
        if self.pc < 0x200 or self.pc > 0xFFE:
            self.pc = 0x200
            return

        op = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2

        x = (op >> 8) & 0xF
        y = (op >> 4) & 0xF
        n = op & 0xF
        nn = op & 0xFF
        nnn = op & 0xFFF
        hi = op & 0xF000

        if op == 0x00E0:
            self.display = [[0] * WIDTH for _ in range(HEIGHT)]
        elif op == 0x00EE:
            if self.stack:
                self.pc = self.stack.pop()
        elif hi == 0x1000:
            self.pc = nnn
        elif hi == 0x2000:
            self.stack.append(self.pc)
            self.pc = nnn
        elif hi == 0x3000:
            if self.V[x] == nn:
                self.pc += 2
        elif hi == 0x4000:
            if self.V[x] != nn:
                self.pc += 2
        elif hi == 0x5000:
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif hi == 0x6000:
            self.V[x] = nn
        elif hi == 0x7000:
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif hi == 0x8000:
            self._alu(x, y, n)
        elif hi == 0x9000:
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif hi == 0xA000:
            self.I = nnn
        elif hi == 0xB000:
            self.pc = (nnn + self.V[0]) & 0xFFF
        elif hi == 0xC000:
            self.V[x] = random.randint(0, 255) & nn
        elif hi == 0xD000:
            self._draw(x, y, n)
        elif hi == 0xE000:
            k = self.V[x] & 0xF
            if nn == 0x9E and self.keys[k]:
                self.pc += 2
            elif nn == 0xA1 and not self.keys[k]:
                self.pc += 2
        elif hi == 0xF000:
            self._misc(x, nn)

    def _alu(self, x, y, n):
        if n == 0:
            self.V[x] = self.V[y]
        elif n == 1:
            self.V[x] |= self.V[y]
        elif n == 2:
            self.V[x] &= self.V[y]
        elif n == 3:
            self.V[x] ^= self.V[y]
        elif n == 4:
            result = self.V[x] + self.V[y]
            self.V[0xF] = 1 if result > 255 else 0
            self.V[x] = result & 0xFF
        elif n == 5:
            self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
            self.V[x] = (self.V[x] - self.V[y]) & 0xFF
        elif n == 6:
            self.V[0xF] = self.V[x] & 1
            self.V[x] >>= 1
        elif n == 7:
            self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
            self.V[x] = (self.V[y] - self.V[x]) & 0xFF
        elif n == 0xE:
            self.V[0xF] = (self.V[x] >> 7) & 1
            self.V[x] = (self.V[x] << 1) & 0xFF

    def _draw(self, x, y, n):
        xpos = self.V[x] % WIDTH
        ypos = self.V[y] % HEIGHT
        self.V[0xF] = 0

        for row in range(n):
            if ypos + row >= HEIGHT:
                break
            sprite_byte = self.memory[self.I + row]
            for col in range(8):
                if xpos + col >= WIDTH:
                    break
                if sprite_byte & (0x80 >> col):
                    px = (xpos + col) % WIDTH
                    py = (ypos + row) % HEIGHT
                    if self.display[py][px]:
                        self.V[0xF] = 1
                    self.display[py][px] ^= 1

    def _misc(self, x, nn):
        if nn == 0x07:
            self.V[x] = self.delay_timer
        elif nn == 0x0A:
            self.waiting_key = True
            self.key_reg = x
        elif nn == 0x15:
            self.delay_timer = self.V[x]
        elif nn == 0x18:
            self.sound_timer = self.V[x]
        elif nn == 0x1E:
            self.I = (self.I + self.V[x]) & 0xFFF
        elif nn == 0x29:
            self.I = (self.V[x] & 0xF) * 5
        elif nn == 0x33:
            val = self.V[x]
            self.memory[self.I] = val // 100
            self.memory[self.I + 1] = (val // 10) % 10
            self.memory[self.I + 2] = val % 10
        elif nn == 0x55:
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]
        elif nn == 0x65:
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]

    def key_down(self, key):
        if 0 <= key <= 15:
            self.keys[key] = 1
            if self.waiting_key:
                self.V[self.key_reg] = key
                self.waiting_key = False

    def key_up(self, key):
        if 0 <= key <= 15:
            self.keys[key] = 0

    def tick_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1


# ═══════════════════════════════════════════════════════════════════════════════
# GUI COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

class Menu:
    def __init__(self, name, items):
        self.name = name
        self.items = items
        self.open = False
        self.hover_idx = -1


class RomList:
    def __init__(self, roms):
        self.roms = list(roms.items())
        self.selected = 0
        self.hover = -1
        self.scroll = 0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class CatChip8:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

        self.screen_w = 800
        self.screen_h = 600
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Cat's CHIP-8 - SAMSOFT RTX ! ON")

        self.clock = pygame.time.Clock()
        self.chip8 = Chip8()

        # Fonts
        self.font = pygame.font.SysFont("Consolas", 14)
        self.font_bold = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_title = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 11)

        # UI State
        self.menu_height = 22
        self.toolbar_height = 32
        self.status_height = 24
        self.rom_list = RomList(ROMS)
        self.current_rom = None
        self.show_rom_browser = True

        # Menus
        self.menus = [
            Menu("File", ["Open ROM...", "─", "Reset", "─", "Exit"]),
            Menu("System", ["Pause/Resume", "Stop", "─", "Speed: Normal", "Speed: Fast", "Speed: Turbo"]),
            Menu("Options", ["Display Scale: 8x", "Display Scale: 10x", "Display Scale: 12x", "─", "Sound On/Off"]),
            Menu("Help", ["Controls", "─", "About Cat's CHIP-8"])
        ]
        self.active_menu = -1

        # Display settings
        self.pixel_scale = 10
        self.sound_on = True
        self.speed = 10  # cycles per frame

        # Generate beep sound
        self.beep = self._generate_beep()

        # Key mapping (QWERTY -> CHIP-8 hex keypad)
        self.keymap = {
            pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
            pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
            pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
            pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
        }

        # Controller support
        self.joysticks = []
        self._init_controllers()

    def _generate_beep(self):
        sample_rate = 44100
        duration = 0.1
        frequency = 440
        samples = int(sample_rate * duration)
        buf = []
        for i in range(samples):
            t = i / sample_rate
            val = int(16000 * (1 if (t * frequency * 2) % 1 < 0.5 else -1))
            buf.append(val)
        arr = bytearray()
        for v in buf:
            arr.extend(v.to_bytes(2, 'little', signed=True))
        return pygame.mixer.Sound(buffer=bytes(arr))

    def _init_controllers(self):
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            self.joysticks.append(joy)

    def run(self):
        running = True
        timer_acc = 0

        while running:
            dt = self.clock.tick(60)
            timer_acc += dt

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self._handle_click(event)
                elif event.type == pygame.MOUSEMOTION:
                    self._handle_motion(event)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self._handle_joy_button(event, True)
                elif event.type == pygame.JOYBUTTONUP:
                    self._handle_joy_button(event, False)

            # Run emulator cycles
            if self.chip8.running and not self.chip8.paused:
                for _ in range(self.speed):
                    self.chip8.cycle()

            # Timer at 60Hz
            if timer_acc >= 16:
                timer_acc = 0
                self.chip8.tick_timers()
                if self.chip8.sound_timer > 0 and self.sound_on:
                    self.beep.play()

            # Render
            self._render()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_keydown(self, event):
        if event.key in self.keymap:
            self.chip8.key_down(self.keymap[event.key])
        elif event.key == pygame.K_ESCAPE:
            if self.active_menu >= 0:
                self.active_menu = -1
            elif self.chip8.running:
                self.show_rom_browser = True
        elif event.key == pygame.K_RETURN:
            if self.show_rom_browser and self.rom_list.roms:
                self._load_selected_rom()
        elif event.key == pygame.K_UP:
            if self.show_rom_browser:
                self.rom_list.selected = max(0, self.rom_list.selected - 1)
        elif event.key == pygame.K_DOWN:
            if self.show_rom_browser:
                self.rom_list.selected = min(len(self.rom_list.roms) - 1, self.rom_list.selected + 1)
        elif event.key == pygame.K_SPACE:
            self.chip8.paused = not self.chip8.paused

    def _handle_keyup(self, event):
        if event.key in self.keymap:
            self.chip8.key_up(self.keymap[event.key])

    def _handle_click(self, event):
        mx, my = event.pos

        # Menu bar click
        if my < self.menu_height:
            x = 10
            for i, menu in enumerate(self.menus):
                w = self.font.size(menu.name)[0] + 20
                if x <= mx < x + w:
                    self.active_menu = i if self.active_menu != i else -1
                    return
                x += w
            self.active_menu = -1
            return

        # Menu dropdown click
        if self.active_menu >= 0:
            menu = self.menus[self.active_menu]
            x = 10 + sum(self.font.size(m.name)[0] + 20 for m in self.menus[:self.active_menu])
            y = self.menu_height
            for idx, item in enumerate(menu.items):
                if item == "─":
                    y += 10
                    continue
                h = 24
                if x <= mx < x + 180 and y <= my < y + h:
                    self._menu_action(self.active_menu, idx)
                    self.active_menu = -1
                    return
                y += h
            self.active_menu = -1
            return

        # ROM list click
        if self.show_rom_browser:
            list_y = self.menu_height + self.toolbar_height + 60
            for i, (_, rom) in enumerate(self.rom_list.roms):
                item_y = list_y + i * 50 - self.rom_list.scroll
                if item_y < list_y - 50 or item_y > self.screen_h - 100:
                    continue
                if 50 <= mx < self.screen_w - 50 and item_y <= my < item_y + 48:
                    self.rom_list.selected = i
                    if event.button == 1:  # Double click simulation via quick re-select
                        self._load_selected_rom()
                    return

    def _handle_motion(self, event):
        mx, my = event.pos
        self.rom_list.hover = -1

        if self.show_rom_browser:
            list_y = self.menu_height + self.toolbar_height + 60
            for i in range(len(self.rom_list.roms)):
                item_y = list_y + i * 50 - self.rom_list.scroll
                if 50 <= mx < self.screen_w - 50 and item_y <= my < item_y + 48:
                    self.rom_list.hover = i
                    return

    def _handle_joy_button(self, event, pressed):
        # Map controller buttons to CHIP-8 keys
        btn_map = {0: 0x5, 1: 0x6, 2: 0x7, 3: 0x8}  # A/B/X/Y -> 5/6/7/8
        if event.button in btn_map:
            if pressed:
                self.chip8.key_down(btn_map[event.button])
            else:
                self.chip8.key_up(btn_map[event.button])

    def _menu_action(self, menu_idx, item_idx):
        if menu_idx == 0:  # File
            if item_idx == 0:
                self.show_rom_browser = True
            elif item_idx == 2:
                if self.current_rom:
                    self.chip8.load(ROMS[self.current_rom]["data"])
            elif item_idx == 4:
                pygame.quit()
                sys.exit()
        elif menu_idx == 1:  # System
            if item_idx == 0:
                self.chip8.paused = not self.chip8.paused
            elif item_idx == 1:
                self.chip8.reset()
                self.show_rom_browser = True
            elif item_idx == 3:
                self.speed = 10
            elif item_idx == 4:
                self.speed = 20
            elif item_idx == 5:
                self.speed = 50
        elif menu_idx == 2:  # Options
            if item_idx == 0:
                self.pixel_scale = 8
            elif item_idx == 1:
                self.pixel_scale = 10
            elif item_idx == 2:
                self.pixel_scale = 12
            elif item_idx == 4:
                self.sound_on = not self.sound_on
        elif menu_idx == 3:  # Help
            if item_idx == 0:
                self._show_controls()
            elif item_idx == 2:
                self._show_about()

    def _load_selected_rom(self):
        if 0 <= self.rom_list.selected < len(self.rom_list.roms):
            key, rom = self.rom_list.roms[self.rom_list.selected]
            self.current_rom = key
            self.chip8.load(rom["data"])
            self.show_rom_browser = False

    def _show_controls(self):
        # Simple in-game display (could be improved)
        pass

    def _show_about(self):
        pass

    def _render(self):
        self.screen.fill(P64.BG)

        if self.show_rom_browser:
            self._render_rom_browser()
        else:
            self._render_game()

        self._render_menubar()
        self._render_toolbar()
        self._render_status()
        self._render_menus()

    def _render_menubar(self):
        pygame.draw.rect(self.screen, P64.MENU_BG, (0, 0, self.screen_w, self.menu_height))
        pygame.draw.line(self.screen, P64.MENU_BORDER, (0, self.menu_height - 1), (self.screen_w, self.menu_height - 1))

        x = 10
        for i, menu in enumerate(self.menus):
            w = self.font.size(menu.name)[0] + 20
            if i == self.active_menu:
                pygame.draw.rect(self.screen, P64.MENU_ACTIVE, (x, 0, w, self.menu_height))
            txt = self.font.render(menu.name, True, P64.TEXT)
            self.screen.blit(txt, (x + 10, 3))
            x += w

    def _render_menus(self):
        if self.active_menu < 0:
            return

        menu = self.menus[self.active_menu]
        x = 10 + sum(self.font.size(m.name)[0] + 20 for m in self.menus[:self.active_menu])
        y = self.menu_height

        # Calculate dropdown height
        h = sum(10 if item == "─" else 24 for item in menu.items) + 4
        pygame.draw.rect(self.screen, P64.MENU_BG, (x, y, 180, h))
        pygame.draw.rect(self.screen, P64.MENU_BORDER, (x, y, 180, h), 1)

        cy = y + 2
        mx, my = pygame.mouse.get_pos()
        for item in menu.items:
            if item == "─":
                pygame.draw.line(self.screen, P64.MENU_BORDER, (x + 5, cy + 5), (x + 175, cy + 5))
                cy += 10
            else:
                if x <= mx < x + 180 and cy <= my < cy + 24:
                    pygame.draw.rect(self.screen, P64.MENU_HOVER, (x + 2, cy, 176, 22))
                txt = self.font.render(item, True, P64.TEXT)
                self.screen.blit(txt, (x + 10, cy + 3))
                cy += 24

    def _render_toolbar(self):
        y = self.menu_height
        pygame.draw.rect(self.screen, P64.TOOLBAR, (0, y, self.screen_w, self.toolbar_height))
        pygame.draw.line(self.screen, P64.MENU_BORDER, (0, y + self.toolbar_height - 1),
                         (self.screen_w, y + self.toolbar_height - 1))

        # Toolbar buttons
        buttons = ["▶ Play", "⏸ Pause", "⏹ Stop", "🔄 Reset"]
        bx = 10
        for btn in buttons:
            w = self.font.size(btn)[0] + 16
            pygame.draw.rect(self.screen, P64.TOOLBAR_BTN, (bx, y + 4, w, 24), border_radius=3)
            txt = self.font.render(btn, True, P64.TEXT)
            self.screen.blit(txt, (bx + 8, y + 8))
            bx += w + 8

    def _render_status(self):
        y = self.screen_h - self.status_height
        pygame.draw.rect(self.screen, P64.STATUS, (0, y, self.screen_w, self.status_height))
        pygame.draw.line(self.screen, P64.MENU_BORDER, (0, y), (self.screen_w, y))

        status = "Ready"
        if self.chip8.running:
            status = f"Running: {self.current_rom}" if self.current_rom else "Running"
            if self.chip8.paused:
                status += " [PAUSED]"

        txt = self.font_small.render(status, True, P64.TEXT_DIM)
        self.screen.blit(txt, (10, y + 5))

        # Speed indicator
        speed_txt = f"Speed: {self.speed}x | Sound: {'ON' if self.sound_on else 'OFF'}"
        stxt = self.font_small.render(speed_txt, True, P64.TEXT_DIM)
        self.screen.blit(stxt, (self.screen_w - stxt.get_width() - 10, y + 5))

    def _render_rom_browser(self):
        y = self.menu_height + self.toolbar_height

        # Title
        title = self.font_title.render("🐱 Cat's CHIP-8 ROM Browser", True, P64.GOLD)
        self.screen.blit(title, (self.screen_w // 2 - title.get_width() // 2, y + 15))

        # ROM list
        list_y = y + 60
        for i, (key, rom) in enumerate(self.rom_list.roms):
            item_y = list_y + i * 50 - self.rom_list.scroll
            if item_y < list_y - 50 or item_y > self.screen_h - 100:
                continue

            # Background
            if i == self.rom_list.selected:
                color = P64.LIST_SEL
            elif i == self.rom_list.hover:
                color = P64.LIST_HOVER
            else:
                color = P64.LIST_BG

            pygame.draw.rect(self.screen, color, (50, item_y, self.screen_w - 100, 48), border_radius=4)
            pygame.draw.rect(self.screen, P64.BORDER, (50, item_y, self.screen_w - 100, 48), 1, border_radius=4)

            # ROM info
            name = self.font_bold.render(rom["name"], True, P64.GOLD if i == self.rom_list.selected else P64.TEXT)
            self.screen.blit(name, (70, item_y + 8))

            author = self.font_small.render(f"by {rom['author']}", True, P64.TEXT_DIM)
            self.screen.blit(author, (70 + name.get_width() + 15, item_y + 10))

            desc = self.font_small.render(rom["desc"], True, P64.TEXT_DIM)
            self.screen.blit(desc, (70, item_y + 28))

        # Instructions
        inst = self.font_small.render("↑↓ Select | Enter/Click to Run | ESC to close", True, P64.TEXT_DIM)
        self.screen.blit(inst, (self.screen_w // 2 - inst.get_width() // 2, self.screen_h - 60))

    def _render_game(self):
        y_offset = self.menu_height + self.toolbar_height + 10

        # Calculate display position (centered)
        disp_w = WIDTH * self.pixel_scale
        disp_h = HEIGHT * self.pixel_scale
        dx = (self.screen_w - disp_w) // 2
        dy = y_offset + (self.screen_h - y_offset - self.status_height - disp_h) // 2

        # Border
        pygame.draw.rect(self.screen, P64.BORDER, (dx - 4, dy - 4, disp_w + 8, disp_h + 8), 2, border_radius=4)

        # Pixels
        for row in range(HEIGHT):
            for col in range(WIDTH):
                color = P64.PIXEL_ON if self.chip8.display[row][col] else P64.PIXEL_OFF
                pygame.draw.rect(self.screen, color,
                                 (dx + col * self.pixel_scale, dy + row * self.pixel_scale,
                                  self.pixel_scale - 1, self.pixel_scale - 1))

        # ROM title
        if self.current_rom:
            rom_name = ROMS[self.current_rom]["name"]
            title = self.font_bold.render(rom_name, True, P64.GOLD)
            self.screen.blit(title, (dx, dy - 25))

        # Controls hint
        hint = self.font_small.render("Keys: 1234 QWER ASDF ZXCV | Space: Pause | ESC: Browser", True, P64.TEXT_DIM)
        self.screen.blit(hint, (self.screen_w // 2 - hint.get_width() // 2, dy + disp_h + 15))


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = CatChip8()
    app.run()
