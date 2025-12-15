#!/usr/bin/env python3
"""
Cat's CHIP-8 ROM - SAMSOFT RTX ! ON 1999-2025
mGBA-Style GUI | Universal Controller Support (Atari 2600 to PS5)
"""

import pygame
import sys
import random

# Complete Pong ROM (David Winter's public domain version)
PONG_ROM = bytes([
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

FONTSET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,
    0x20, 0x60, 0x20, 0x20, 0x70,
    0xF0, 0x10, 0xF0, 0x80, 0xF0,
    0xF0, 0x10, 0xF0, 0x10, 0xF0,
    0x90, 0x90, 0xF0, 0x10, 0x10,
    0xF0, 0x80, 0xF0, 0x10, 0xF0,
    0xF0, 0x80, 0xF0, 0x90, 0xF0,
    0xF0, 0x10, 0x20, 0x40, 0x40,
    0xF0, 0x90, 0xF0, 0x90, 0xF0,
    0xF0, 0x90, 0xF0, 0x10, 0xF0,
    0xF0, 0x90, 0xF0, 0x90, 0x90,
    0xE0, 0x90, 0xE0, 0x90, 0xE0,
    0xF0, 0x80, 0x80, 0x80, 0xF0,
    0xE0, 0x90, 0x90, 0x90, 0xE0,
    0xF0, 0x80, 0xF0, 0x80, 0xF0,
    0xF0, 0x80, 0xF0, 0x80, 0x80
]

WIDTH, HEIGHT = 64, 32


class Chip8:
    def __init__(self):
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
        for i, b in enumerate(FONTSET):
            self.memory[i] = b

    def load(self, rom):
        for i, b in enumerate(rom):
            if 0x200 + i < 4096:
                self.memory[0x200 + i] = b

    def reset(self):
        self.__init__()

    def cycle(self):
        if self.paused or self.waiting_key:
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
            if n == 0:
                self.V[x] = self.V[y]
            elif n == 1:
                self.V[x] |= self.V[y]
            elif n == 2:
                self.V[x] &= self.V[y]
            elif n == 3:
                self.V[x] ^= self.V[y]
            elif n == 4:
                s = self.V[x] + self.V[y]
                self.V[x] = s & 0xFF
                self.V[0xF] = 1 if s > 255 else 0
            elif n == 5:
                f = 1 if self.V[x] >= self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
                self.V[0xF] = f
            elif n == 6:
                f = self.V[x] & 1
                self.V[x] >>= 1
                self.V[0xF] = f
            elif n == 7:
                f = 1 if self.V[y] >= self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
                self.V[0xF] = f
            elif n == 0xE:
                f = (self.V[x] >> 7) & 1
                self.V[x] = (self.V[x] << 1) & 0xFF
                self.V[0xF] = f
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
            vx, vy = self.V[x] & 63, self.V[y] & 31
            self.V[0xF] = 0
            for row in range(n):
                if self.I + row >= 4096:
                    break
                sprite = self.memory[self.I + row]
                for col in range(8):
                    if sprite & (0x80 >> col):
                        px, py = (vx + col) & 63, (vy + row) & 31
                        if self.display[py][px]:
                            self.V[0xF] = 1
                        self.display[py][px] ^= 1
        elif hi == 0xE000:
            k = self.V[x] & 0xF
            if nn == 0x9E and self.keys[k]:
                self.pc += 2
            elif nn == 0xA1 and not self.keys[k]:
                self.pc += 2
        elif hi == 0xF000:
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
                if self.I < 4094:
                    v = self.V[x]
                    self.memory[self.I] = v // 100
                    self.memory[self.I + 1] = (v // 10) % 10
                    self.memory[self.I + 2] = v % 10
            elif nn == 0x55:
                for i in range(x + 1):
                    if self.I + i < 4096:
                        self.memory[self.I + i] = self.V[i]
            elif nn == 0x65:
                for i in range(x + 1):
                    if self.I + i < 4096:
                        self.V[i] = self.memory[self.I + i]

    def tick_timers(self):
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def press(self, k):
        if 0 <= k <= 15:
            self.keys[k] = 1
            if self.waiting_key:
                self.V[self.key_reg] = k
                self.waiting_key = False

    def release(self, k):
        if 0 <= k <= 15:
            self.keys[k] = 0


class Controller:
    def __init__(self):
        self.joy = None
        self.name = "None"
        self.dz = 0.3

    def init(self):
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
            self.name = self.joy.get_name()[:30]

    def refresh(self):
        pygame.joystick.quit()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joy = pygame.joystick.Joystick(0)
            self.joy.init()
            self.name = self.joy.get_name()[:30]
        else:
            self.joy = None
            self.name = "None"

    def get_dir(self):
        if not self.joy:
            return False, False, False, False
        u = d = l = r = False
        if self.joy.get_numhats() > 0:
            h = self.joy.get_hat(0)
            l, r = h[0] < 0, h[0] > 0
            d, u = h[1] < 0, h[1] > 0
        if self.joy.get_numaxes() >= 2:
            ax, ay = self.joy.get_axis(0), self.joy.get_axis(1)
            if ax < -self.dz: l = True
            if ax > self.dz: r = True
            if ay < -self.dz: u = True
            if ay > self.dz: d = True
        return u, d, l, r

    def btn(self, n):
        if self.joy and n < self.joy.get_numbuttons():
            return self.joy.get_button(n)
        return False


def main():
    pygame.init()
    pygame.mixer.init(22050, -16, 1, 512)

    W, H = 800, 600
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Cat's CHIP-8 ROM - SAMSOFT RTX ! ON 1999-2025")
    clock = pygame.time.Clock()

    try:
        font_title = pygame.font.SysFont("Consolas", 26, bold=True)
        font_small = pygame.font.SysFont("Consolas", 12)
        font_menu = pygame.font.SysFont("Arial", 13)
    except:
        font_title = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 14)
        font_menu = pygame.font.Font(None, 15)

    chip = Chip8()
    chip.load(PONG_ROM)

    ctrl = Controller()
    ctrl.init()

    scale = 11
    dw, dh = WIDTH * scale, HEIGHT * scale
    dx, dy = (W - dw) // 2, 80

    COL_BG = (30, 30, 34)
    COL_BAR = (45, 45, 50)
    COL_BORDER = (70, 70, 78)
    COL_ON = (150, 255, 150)
    COL_OFF = (15, 35, 15)
    COL_ACCENT = (0, 200, 200)
    COL_TEXT = (200, 200, 205)
    COL_DIM = (120, 120, 128)

    keymap = {
        pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
        pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
        pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
        pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
    }

    try:
        beep = pygame.mixer.Sound(buffer=bytes([128 + 50 * ((i // 30) % 2) for i in range(1500)]))
        beep.set_volume(0.15)
    except:
        beep = None

    scanlines = pygame.Surface((dw, dh), pygame.SRCALPHA)
    for y in range(0, dh, 2):
        pygame.draw.line(scanlines, (0, 0, 0, 25), (0, y), (dw, y))

    run = True
    prev_start = False

    while run:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                run = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    run = False
                elif ev.key == pygame.K_p:
                    chip.paused = not chip.paused
                elif ev.key == pygame.K_F5:
                    chip.reset()
                    chip.load(PONG_ROM)
                elif ev.key in keymap:
                    chip.press(keymap[ev.key])
            elif ev.type == pygame.KEYUP:
                if ev.key in keymap:
                    chip.release(keymap[ev.key])
            elif ev.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                ctrl.refresh()

        # Controller
        if ctrl.joy:
            u, d, l, r = ctrl.get_dir()
            chip.keys[0x1] = 1 if u else 0
            chip.keys[0x4] = 1 if d else 0
            
            start = ctrl.btn(7) or ctrl.btn(9) or ctrl.btn(6)
            if start and not prev_start:
                chip.paused = not chip.paused
            prev_start = start

        # Emulate
        if not chip.paused:
            for _ in range(10):
                chip.cycle()
            chip.tick_timers()
            if chip.sound_timer > 0 and beep:
                if not pygame.mixer.get_busy():
                    beep.play(-1)
            elif beep:
                beep.stop()

        # Draw
        screen.fill(COL_BG)

        # Menu bar
        pygame.draw.rect(screen, COL_BAR, (0, 0, W, 26))
        pygame.draw.line(screen, COL_BORDER, (0, 25), (W, 25))
        mx = 12
        for m in ["File", "Emulation", "Video", "Audio", "Help"]:
            t = font_menu.render(m, True, COL_TEXT)
            screen.blit(t, (mx, 5))
            mx += t.get_width() + 18

        # Title
        t = font_title.render("Cat's CHIP-8 ROM", True, COL_ACCENT)
        screen.blit(t, ((W - t.get_width()) // 2, 35))
        t2 = font_small.render("SAMSOFT RTX ! ON 1999-2025", True, COL_DIM)
        screen.blit(t2, ((W - t2.get_width()) // 2, 62))

        # Display bezel
        pygame.draw.rect(screen, (50, 50, 56), (dx - 6, dy - 6, dw + 12, dh + 12), border_radius=3)
        pygame.draw.rect(screen, COL_BORDER, (dx - 2, dy - 2, dw + 4, dh + 4))
        pygame.draw.rect(screen, COL_OFF, (dx, dy, dw, dh))

        # Pixels
        for row in range(HEIGHT):
            for col in range(WIDTH):
                if chip.display[row][col]:
                    pygame.draw.rect(screen, COL_ON,
                        (dx + col * scale, dy + row * scale, scale - 1, scale - 1))

        screen.blit(scanlines, (dx, dy))

        # Status bar
        sy = H - 22
        pygame.draw.rect(screen, COL_BAR, (0, sy, W, 22))
        pygame.draw.line(screen, COL_BORDER, (0, sy), (W, sy))

        st = "PAUSED" if chip.paused else "RUNNING"
        sc = (200, 180, 60) if chip.paused else (60, 200, 60)
        screen.blit(font_small.render("●", True, sc), (10, sy + 4))
        screen.blit(font_small.render(st, True, COL_DIM), (24, sy + 5))

        screen.blit(font_small.render("PONG", True, COL_ACCENT), ((W - 30) // 2, sy + 5))

        ct = font_small.render(f"PAD: {ctrl.name}", True, COL_DIM)
        screen.blit(ct, (W - 280, sy + 5))

        fps = font_small.render(f"{clock.get_fps():.0f} FPS", True, COL_DIM)
        screen.blit(fps, (W - 55, sy + 5))

        # Controls help
        help_txt = font_small.render("1/Q=P1 Up/Down | C/4=P2 | P=Pause | F5=Reset", True, COL_DIM)
        screen.blit(help_txt, ((W - help_txt.get_width()) // 2, H - 45))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
