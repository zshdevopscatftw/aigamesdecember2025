#!/usr/bin/env python3
"""
Samsoft Kart - Complete Edition with Beta MKDS-Style Main Menu
A Mode7-style kart racer inspired by Mario Kart DS pre-release builds.
Single-file implementation for Flames / Team Flames / Samsoft.
"""

import math
import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Tuple, List, Dict, Any
import pygame
import numpy as np

# =============================================================================
# SETTINGS
# =============================================================================
INTERNAL_W = 256
INTERNAL_H = 192
SCALE = 4
WINDOW_W = INTERNAL_W * SCALE
WINDOW_H = INTERNAL_H * SCALE
FPS = 60

TRACK_SIZE = 512
HORIZON_Y = 78
CAM_HEIGHT = 60.0
FOV_DEG = 70.0

MAX_SPEED_ROAD = 240.0
MAX_SPEED_OFFROAD = 150.0
ACCEL = 220.0
BRAKE = 260.0
FRICTION = 140.0
OFFROAD_FRICTION = 220.0
REVERSE_MAX = 110.0
STEER_RATE = 2.4
STEER_RATE_DRIFT = 3.2
BOOST_STRENGTH = 340.0

# Menu colors (MKDS beta style - blue/orange theme)
COL_BG_DARK = (16, 24, 48)
COL_BG_LIGHT = (32, 48, 80)
COL_HIGHLIGHT = (255, 180, 60)
COL_HIGHLIGHT_GLOW = (255, 220, 120)
COL_TEXT = (255, 255, 255)
COL_TEXT_DIM = (140, 160, 200)
COL_PANEL = (24, 40, 72)
COL_PANEL_BORDER = (80, 120, 180)
COL_SELECT = (255, 100, 60)


# =============================================================================
# GAME STATES
# =============================================================================
class GameState(Enum):
    TITLE = auto()
    MAIN_MENU = auto()
    CHARACTER_SELECT = auto()
    CUP_SELECT = auto()
    TRACK_SELECT = auto()
    COUNTDOWN = auto()
    RACING = auto()
    RESULTS = auto()
    OPTIONS = auto()


# =============================================================================
# KART PHYSICS
# =============================================================================
def _approach(value: float, target: float, delta: float) -> float:
    if value < target:
        return min(value + delta, target)
    return max(value - delta, target)


@dataclass
class Kart:
    x: float
    y: float
    angle: float
    speed: float = 0.0
    lap: int = 0
    checkpoint: int = 0
    finish_time: float = 0.0

    def update(
        self, dt: float, throttle: float, brake: float, steer: float,
        drifting: bool, on_road: bool, on_boost: bool,
        max_speed_road: float, max_speed_offroad: float,
        accel: float, brake_strength: float, friction: float,
        offroad_friction: float, reverse_max: float, steer_rate: float,
        steer_rate_drift: float, boost_strength: float
    ) -> None:
        max_fwd = max_speed_road if on_road else max_speed_offroad
        fr = friction if on_road else offroad_friction

        # FIX: Only apply friction when NOT accelerating
        if throttle > 0.0:
            self.speed += accel * throttle * dt
        elif brake > 0.0:
            if self.speed > 0:
                self.speed -= brake_strength * brake * dt
            else:
                self.speed -= (accel * 0.65) * brake * dt
        else:
            # Apply friction only when coasting
            self.speed = _approach(self.speed, 0.0, fr * dt)

        if on_boost and self.speed >= 0:
            self.speed += boost_strength * dt

        # Clamp speed
        if self.speed >= 0:
            self.speed = min(self.speed, max_fwd)
        else:
            self.speed = max(self.speed, -reverse_max)

        # Steering
        speed_factor = min(abs(self.speed) / max_speed_road, 1.0)
        turn = (steer_rate_drift if drifting else steer_rate) * speed_factor
        self.angle += steer * turn * dt * (1 if self.speed >= 0 else -1)

        # Position update
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt


# =============================================================================
# TRACK GENERATION
# =============================================================================
@dataclass
class Track:
    name: str
    size: int
    surface: pygame.Surface
    road_mask: np.ndarray
    boost_mask: np.ndarray
    minimap: pygame.Surface
    start_x: float
    start_y: float
    start_angle: float
    checkpoints: List[Tuple[float, float, float]]  # (x, y, radius)

    def is_road(self, x: float, y: float) -> bool:
        ix = int(x) % self.size
        iy = int(y) % self.size
        return bool(self.road_mask[ix, iy])

    def is_boost(self, x: float, y: float) -> bool:
        ix = int(x) % self.size
        iy = int(y) % self.size
        return bool(self.boost_mask[ix, iy])


def _make_checker_grass(size: int, c1: Tuple, c2: Tuple) -> pygame.Surface:
    surf = pygame.Surface((size, size))
    tile = 16
    for y in range(0, size, tile):
        for x in range(0, size, tile):
            surf.fill(c1 if ((x // tile + y // tile) % 2 == 0) else c2, (x, y, tile, tile))
    return surf


def generate_oval_track(size: int = 512, name: str = "Samsoft Circuit") -> Track:
    """Generate the default oval track."""
    tex = _make_checker_grass(size, (55, 140, 70), (50, 130, 65))

    road_color = (70, 75, 80)
    kerb_color = (225, 60, 60)
    line_color = (230, 230, 230)
    boost_color = (90, 200, 255)

    center = (size // 2, size // 2)
    rx, ry = int(size * 0.34), int(size * 0.26)
    road_half_width = int(size * 0.06)

    # Road layer
    road_layer = pygame.Surface((size, size), flags=pygame.SRCALPHA)
    outer_rect = pygame.Rect(0, 0, (rx + road_half_width) * 2, (ry + road_half_width) * 2)
    outer_rect.center = center
    inner_rect = pygame.Rect(0, 0, (rx - road_half_width) * 2, (ry - road_half_width) * 2)
    inner_rect.center = center

    pygame.draw.ellipse(road_layer, road_color, outer_rect)
    pygame.draw.ellipse(road_layer, (0, 0, 0, 0), inner_rect)

    # Kerbs
    kerb = pygame.Surface((size, size), flags=pygame.SRCALPHA)
    num_seg = 64
    for i in range(num_seg):
        t0 = (i / num_seg) * math.tau
        t1 = ((i + 1) / num_seg) * math.tau
        if i % 2 == 0:
            pts = []
            for j in range(5):
                t = t0 + (t1 - t0) * (j / 4)
                x = center[0] + (rx + road_half_width) * math.cos(t)
                y = center[1] + (ry + road_half_width) * math.sin(t)
                pts.append((x, y))
            pygame.draw.lines(kerb, kerb_color, False, pts, 6)

    # Lane line
    for i in range(0, 96, 2):
        t0 = (i / 96) * math.tau
        t1 = ((i + 1) / 96) * math.tau
        pts = []
        for j in range(4):
            t = t0 + (t1 - t0) * (j / 3)
            x = center[0] + rx * math.cos(t)
            y = center[1] + ry * math.sin(t)
            pts.append((x, y))
        pygame.draw.lines(road_layer, line_color, False, pts, 2)

    tex.blit(road_layer, (0, 0))
    tex.blit(kerb, (0, 0))

    # Start/finish line
    start = pygame.Surface((size, size), flags=pygame.SRCALPHA)
    sx = center[0] + rx
    sy = center[1]
    pygame.draw.rect(start, (240, 240, 240), pygame.Rect(sx - 6, sy - 36, 12, 72))
    for k in range(7):
        if k % 2 == 0:
            pygame.draw.rect(start, (30, 30, 30), pygame.Rect(sx - 6, sy - 36 + k * 10, 12, 10))
    tex.blit(start, (0, 0))

    # Boost pads
    boost_layer = pygame.Surface((size, size), flags=pygame.SRCALPHA)
    pad_w, pad_h = 26, 10
    for t in (0.25 * math.tau, 0.62 * math.tau, 0.87 * math.tau):
        px = center[0] + rx * math.cos(t)
        py = center[1] + ry * math.sin(t)
        angle = math.degrees(t + math.pi / 2)
        pad = pygame.Surface((pad_w, pad_h), flags=pygame.SRCALPHA)
        pygame.draw.rect(pad, boost_color, pygame.Rect(0, 0, pad_w, pad_h), border_radius=2)
        pygame.draw.rect(pad, (255, 255, 255), pygame.Rect(3, 3, pad_w - 6, pad_h - 6), 1, border_radius=2)
        pad_rot = pygame.transform.rotate(pad, -angle)
        rect = pad_rot.get_rect(center=(px, py))
        boost_layer.blit(pad_rot, rect.topleft)
    tex.blit(boost_layer, (0, 0))

    # Build masks
    tex_rgb = pygame.surfarray.array3d(tex)
    r = tex_rgb[:, :, 0].astype(np.int16)
    g = tex_rgb[:, :, 1].astype(np.int16)
    b = tex_rgb[:, :, 2].astype(np.int16)
    road_mask = (abs(r - road_color[0]) < 25) & (abs(g - road_color[1]) < 25) & (abs(b - road_color[2]) < 25)
    boost_mask = (abs(r - boost_color[0]) < 25) & (abs(g - boost_color[1]) < 25) & (abs(b - boost_color[2]) < 25)

    minimap = pygame.transform.smoothscale(tex, (64, 64))

    # Checkpoints around the track
    checkpoints = []
    for i in range(8):
        t = (i / 8) * math.tau
        cx = center[0] + rx * math.cos(t)
        cy = center[1] + ry * math.sin(t)
        checkpoints.append((cx, cy, 50.0))

    return Track(
        name=name,
        size=size,
        surface=tex.convert(),
        road_mask=road_mask,
        boost_mask=boost_mask,
        minimap=minimap.convert(),
        start_x=center[0] + size * 0.34,
        start_y=center[1],
        start_angle=math.pi,
        checkpoints=checkpoints,
    )


def generate_figure8_track(size: int = 512, name: str = "Figure-8 Cross") -> Track:
    """Generate a figure-8 track with crossing."""
    tex = _make_checker_grass(size, (130, 100, 60), (120, 90, 55))  # Desert theme

    road_color = (90, 85, 75)
    kerb_color = (255, 200, 60)
    boost_color = (90, 200, 255)

    center = (size // 2, size // 2)
    loop_r = int(size * 0.18)
    loop_offset = int(size * 0.16)
    road_width = int(size * 0.05)

    road_layer = pygame.Surface((size, size), flags=pygame.SRCALPHA)

    # Draw two overlapping circles
    for ox in (-loop_offset, loop_offset):
        cx, cy = center[0] + ox, center[1]
        pygame.draw.circle(road_layer, road_color, (cx, cy), loop_r + road_width)
        pygame.draw.circle(road_layer, (0, 0, 0, 0), (cx, cy), loop_r - road_width)

    # Center crossing
    pygame.draw.rect(road_layer, road_color, 
                     pygame.Rect(center[0] - road_width, center[1] - loop_r - road_width,
                                road_width * 2, (loop_r + road_width) * 2))

    tex.blit(road_layer, (0, 0))

    # Build masks
    tex_rgb = pygame.surfarray.array3d(tex)
    r = tex_rgb[:, :, 0].astype(np.int16)
    g = tex_rgb[:, :, 1].astype(np.int16)
    b = tex_rgb[:, :, 2].astype(np.int16)
    road_mask = (abs(r - road_color[0]) < 25) & (abs(g - road_color[1]) < 25) & (abs(b - road_color[2]) < 25)
    boost_mask = np.zeros_like(road_mask)

    minimap = pygame.transform.smoothscale(tex, (64, 64))

    return Track(
        name=name,
        size=size,
        surface=tex.convert(),
        road_mask=road_mask,
        boost_mask=boost_mask,
        minimap=minimap.convert(),
        start_x=center[0] + loop_offset + loop_r,
        start_y=center[1],
        start_angle=math.pi / 2,
        checkpoints=[(center[0], center[1], 40.0)],
    )


# =============================================================================
# MODE7 RENDERER
# =============================================================================
class Mode7Renderer:
    def __init__(self, texture: pygame.Surface, horizon_y: int, cam_height: float,
                 fov_deg: float, screen_w: int, screen_h: int) -> None:
        self.texture = texture
        self.horizon_y = horizon_y
        self.cam_height = float(cam_height)
        self.screen_w = int(screen_w)
        self.screen_h = int(screen_h)

        self.tex_array = pygame.surfarray.array3d(texture)
        self.tw, self.th = self.tex_array.shape[0], self.tex_array.shape[1]

        self.x_lerp = np.linspace(0.0, 1.0, self.screen_w, endpoint=False, dtype=np.float32)
        self.proj = 120.0
        self.fov_scale = float(math.tan(math.radians(fov_deg) / 2.0))

        # Sky gradient
        top = np.array([120, 185, 255], dtype=np.float32)
        bot = np.array([180, 225, 255], dtype=np.float32)
        if self.horizon_y <= 1:
            self.sky_rows = np.tile(bot.astype(np.uint8), (max(self.horizon_y, 1), 1))
        else:
            t = np.linspace(0.0, 1.0, self.horizon_y, dtype=np.float32)[:, None]
            self.sky_rows = (top * (1.0 - t) + bot * t).astype(np.uint8)

    def update_texture(self, texture: pygame.Surface) -> None:
        """Update the texture (for track changes)."""
        self.texture = texture
        self.tex_array = pygame.surfarray.array3d(texture)
        self.tw, self.th = self.tex_array.shape[0], self.tex_array.shape[1]

    def render_ground(self, target: pygame.Surface, cam_x: float, cam_y: float, cam_angle: float) -> None:
        W, H = self.screen_w, self.screen_h
        h0 = self.horizon_y
        cos_a = math.cos(cam_angle)
        sin_a = math.sin(cam_angle)
        dir_x, dir_y = cos_a, sin_a
        right_x, right_y = -sin_a, cos_a

        arr = pygame.surfarray.pixels3d(target)

        if h0 > 0:
            arr[:, :h0, :] = self.sky_rows[None, :, :]

        for y in range(h0, H):
            p = (y - h0) + 1.0
            row_dist = (self.cam_height * self.proj) / p
            half_width = row_dist * self.fov_scale

            start_x = cam_x + dir_x * row_dist - right_x * half_width
            start_y = cam_y + dir_y * row_dist - right_y * half_width
            end_x = cam_x + dir_x * row_dist + right_x * half_width
            end_y = cam_y + dir_y * row_dist + right_y * half_width

            wx = start_x + (end_x - start_x) * self.x_lerp
            wy = start_y + (end_y - start_y) * self.x_lerp

            ix = (wx.astype(np.int32) % self.tw)
            iy = (wy.astype(np.int32) % self.th)

            arr[:, y, :] = self.tex_array[ix, iy, :]

        del arr

    def project_point(self, world_x: float, world_y: float, cam_x: float, cam_y: float, cam_angle: float):
        dx = world_x - cam_x
        dy = world_y - cam_y
        cos_a = math.cos(cam_angle)
        sin_a = math.sin(cam_angle)
        dir_x, dir_y = cos_a, sin_a
        right_x, right_y = -sin_a, cos_a

        forward = dx * dir_x + dy * dir_y
        if forward <= 1.0:
            return None

        side = dx * right_x + dy * right_y
        p = (self.cam_height * self.proj) / forward
        sy = self.horizon_y + p

        if sy < self.horizon_y or sy >= self.screen_h + 20:
            return None

        half_width = forward * self.fov_scale
        nx = side / half_width
        sx = (0.5 + 0.5 * nx) * self.screen_w

        if sx < -40 or sx > self.screen_w + 40:
            return None

        scale = max(0.05, min(2.2, 120.0 / forward))
        return float(sx), float(sy), float(scale), float(forward)


# =============================================================================
# CHARACTER DATA
# =============================================================================
@dataclass
class Character:
    name: str
    color: Tuple[int, int, int]
    outline: Tuple[int, int, int]
    speed_bonus: float = 0.0
    accel_bonus: float = 0.0
    handling_bonus: float = 0.0


CHARACTERS = [
    Character("Mario", (255, 0, 0), (20, 20, 80), 0.0, 0.0, 0.0),          # Red - balanced
    Character("Luigi", (0, 200, 0), (20, 20, 80), -0.05, 0.1, 0.05),       # Green - better accel/handling
    Character("Boo", (240, 240, 255), (100, 100, 120), 0.05, 0.0, 0.1),    # White ghost - fast, good handling
    Character("E. Gadd", (255, 255, 200), (80, 60, 40), -0.1, 0.15, 0.0),  # Yellow lab coat - high accel
    Character("Toad", (255, 80, 80), (255, 255, 255), -0.05, 0.1, 0.1),    # Red spots - nimble
    Character("Wario", (255, 220, 0), (100, 0, 150), 0.15, -0.1, -0.1),    # Yellow/purple - heavy, fast
]


# =============================================================================
# CUP DATA
# =============================================================================
@dataclass
class Cup:
    name: str
    icon_color: Tuple[int, int, int]
    tracks: List[str]


CUPS = [
    Cup("Mushroom Cup", (255, 80, 80), ["Samsoft Circuit", "Figure-8 Cross"]),
    Cup("Flower Cup", (255, 200, 60), ["Samsoft Circuit"]),  # Placeholder
    Cup("Star Cup", (100, 200, 255), ["Samsoft Circuit"]),
    Cup("Special Cup", (200, 100, 255), ["Samsoft Circuit"]),
]


# =============================================================================
# UI HELPERS
# =============================================================================
def draw_panel(surf: pygame.Surface, rect: pygame.Rect, selected: bool = False) -> None:
    """Draw a MKDS-style panel with optional selection highlight."""
    border_col = COL_HIGHLIGHT if selected else COL_PANEL_BORDER
    pygame.draw.rect(surf, COL_PANEL, rect, border_radius=4)
    pygame.draw.rect(surf, border_col, rect, 2, border_radius=4)
    if selected:
        glow = pygame.Surface((rect.width + 4, rect.height + 4), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*COL_HIGHLIGHT, 60), glow.get_rect(), border_radius=6)
        surf.blit(glow, (rect.x - 2, rect.y - 2))


def draw_text_shadow(surf: pygame.Surface, font: pygame.font.Font, text: str,
                     pos: Tuple[int, int], color: Tuple, shadow_color: Tuple = (0, 0, 0)) -> None:
    """Draw text with shadow for MKDS style."""
    shadow = font.render(text, True, shadow_color)
    main = font.render(text, True, color)
    surf.blit(shadow, (pos[0] + 1, pos[1] + 1))
    surf.blit(main, pos)


def make_kart_sprite(size: Tuple[int, int], color: Tuple, outline: Tuple) -> pygame.Surface:
    w, h = size
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.polygon(surf, color,
        [(0, h-1), (3, 2), (w-4, 2), (w-1, h-1), (w-6, h-4), (5, h-4)])
    pygame.draw.polygon(surf, outline,
        [(0, h-1), (3, 2), (w-4, 2), (w-1, h-1), (w-6, h-4), (5, h-4)], 2)
    pygame.draw.rect(surf, (255, 255, 255, 180), pygame.Rect(8, 4, w-16, 4), border_radius=2)
    return surf


# =============================================================================
# MENU SCREENS
# =============================================================================
class TitleScreen:
    """MKDS Beta-style title screen."""
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.t = 0.0
        self.font_title = pygame.font.Font(None, 42)
        self.font_sub = pygame.font.Font(None, 16)
        self.font_press = pygame.font.Font(None, 14)
        
    def update(self, dt: float) -> Optional[GameState]:
        self.t += dt
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            return GameState.MAIN_MENU
        return None

    def draw(self, surf: pygame.Surface) -> None:
        # Gradient background
        for y in range(self.h):
            t = y / self.h
            r = int(COL_BG_DARK[0] * (1 - t) + COL_BG_LIGHT[0] * t)
            g = int(COL_BG_DARK[1] * (1 - t) + COL_BG_LIGHT[1] * t)
            b = int(COL_BG_DARK[2] * (1 - t) + COL_BG_LIGHT[2] * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (self.w, y))

        # Animated logo
        logo_y = 50 + math.sin(self.t * 2) * 3
        title = self.font_title.render("SAMSOFT KART", True, COL_HIGHLIGHT)
        title_shadow = self.font_title.render("SAMSOFT KART", True, (40, 30, 10))
        surf.blit(title_shadow, title_shadow.get_rect(center=(self.w // 2 + 2, logo_y + 2)))
        surf.blit(title, title.get_rect(center=(self.w // 2, logo_y)))

        # Subtitle
        sub = self.font_sub.render("DS-STYLE RACING DEMO", True, COL_TEXT_DIM)
        surf.blit(sub, sub.get_rect(center=(self.w // 2, logo_y + 28)))

        # Flashing "Press Start"
        if int(self.t * 2) % 2 == 0:
            press = self.font_press.render("PRESS START", True, COL_TEXT)
            surf.blit(press, press.get_rect(center=(self.w // 2, self.h - 40)))

        # Copyright
        copy_text = self.font_press.render("© 2025 SAMSOFT / TEAM FLAMES", True, COL_TEXT_DIM)
        surf.blit(copy_text, copy_text.get_rect(center=(self.w // 2, self.h - 16)))

        # Decorative karts
        kart_offset = int((self.t * 30) % 40) - 20
        kart = make_kart_sprite((20, 12), COL_HIGHLIGHT, (40, 30, 10))
        surf.blit(kart, (30 + kart_offset, self.h - 60))
        surf.blit(pygame.transform.flip(kart, True, False), (self.w - 50 - kart_offset, self.h - 60))


class MainMenu:
    """MKDS Beta-style main menu with vertical options."""
    OPTIONS = ["GRAND PRIX", "TIME TRIALS", "VS RACE", "OPTIONS", "RECORDS"]

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.selected = 0
        self.t = 0.0
        self.font = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        self.key_delay = 0.0

    def update(self, dt: float) -> Optional[GameState]:
        self.t += dt
        self.key_delay = max(0, self.key_delay - dt)
        keys = pygame.key.get_pressed()

        if self.key_delay <= 0:
            if keys[pygame.K_UP]:
                self.selected = (self.selected - 1) % len(self.OPTIONS)
                self.key_delay = 0.15
            elif keys[pygame.K_DOWN]:
                self.selected = (self.selected + 1) % len(self.OPTIONS)
                self.key_delay = 0.15
            elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                if self.selected == 0:  # Grand Prix
                    return GameState.CHARACTER_SELECT
                elif self.selected == 1:  # Time Trials
                    return GameState.CHARACTER_SELECT
                elif self.selected == 3:  # Options
                    return GameState.OPTIONS
                self.key_delay = 0.2
            elif keys[pygame.K_ESCAPE]:
                return GameState.TITLE

        return None

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(COL_BG_DARK)

        # Header
        header = self.font.render("MAIN MENU", True, COL_HIGHLIGHT)
        surf.blit(header, header.get_rect(center=(self.w // 2, 20)))

        # Menu panel
        panel_w, panel_h = 140, 120
        panel_rect = pygame.Rect((self.w - panel_w) // 2, 40, panel_w, panel_h)
        draw_panel(surf, panel_rect)

        # Menu options
        for i, opt in enumerate(self.OPTIONS):
            y = 52 + i * 20
            color = COL_HIGHLIGHT if i == self.selected else COL_TEXT
            if i == self.selected:
                # Selection cursor
                cursor_x = panel_rect.x + 10 + math.sin(self.t * 8) * 2
                pygame.draw.polygon(surf, COL_HIGHLIGHT, 
                    [(cursor_x, y + 4), (cursor_x + 6, y + 8), (cursor_x, y + 12)])
            text = self.font_small.render(opt, True, color)
            surf.blit(text, (panel_rect.x + 22, y))

        # Footer hint
        hint = self.font_small.render("↑↓:SELECT  ENTER:OK  ESC:BACK", True, COL_TEXT_DIM)
        surf.blit(hint, hint.get_rect(center=(self.w // 2, self.h - 12)))


class CharacterSelect:
    """MKDS Beta-style character selection grid."""
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.selected = 0
        self.t = 0.0
        self.font = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 12)
        self.font_stats = pygame.font.Font(None, 10)
        self.key_delay = 0.0
        self.confirmed = False

    def update(self, dt: float) -> Optional[Tuple[GameState, int]]:
        self.t += dt
        self.key_delay = max(0, self.key_delay - dt)
        keys = pygame.key.get_pressed()

        cols = 3  # Grid is 3 columns x 2 rows
        num_chars = len(CHARACTERS)

        if self.key_delay <= 0:
            if keys[pygame.K_LEFT]:
                self.selected = (self.selected - 1) % num_chars
                self.key_delay = 0.12
            elif keys[pygame.K_RIGHT]:
                self.selected = (self.selected + 1) % num_chars
                self.key_delay = 0.12
            elif keys[pygame.K_UP]:
                new_sel = self.selected - cols
                if new_sel >= 0:
                    self.selected = new_sel
                self.key_delay = 0.12
            elif keys[pygame.K_DOWN]:
                new_sel = self.selected + cols
                if new_sel < num_chars:
                    self.selected = new_sel
                self.key_delay = 0.12
            elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                return (GameState.CUP_SELECT, self.selected)
            elif keys[pygame.K_ESCAPE]:
                return (GameState.MAIN_MENU, -1)

        return None

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(COL_BG_DARK)

        # Header
        header = self.font.render("SELECT CHARACTER", True, COL_HIGHLIGHT)
        surf.blit(header, header.get_rect(center=(self.w // 2, 14)))

        # Character grid - 6 characters in 2 rows of 3
        cols, rows = 3, 2
        cell_w, cell_h = 70, 52
        grid_w = cols * cell_w
        grid_h = rows * cell_h
        start_x = (self.w - grid_w) // 2 + cell_w // 2
        start_y = 38

        for i, char in enumerate(CHARACTERS):
            col = i % cols
            row = i // cols
            x = start_x + col * cell_w
            y = start_y + row * cell_h
            selected = (i == self.selected)

            # Character box
            box_rect = pygame.Rect(x - 28, y - 5, 56, 46)
            draw_panel(surf, box_rect, selected)

            # Kart preview
            kart = make_kart_sprite((24, 14), char.color, char.outline)
            if selected:
                scale = 1.0 + math.sin(self.t * 6) * 0.1
                kart = pygame.transform.scale(kart, (int(24 * scale), int(14 * scale)))
            surf.blit(kart, kart.get_rect(center=(x, y + 8)))

            # Name
            name_color = COL_HIGHLIGHT if selected else COL_TEXT
            name = self.font_small.render(char.name, True, name_color)
            surf.blit(name, name.get_rect(center=(x, y + 30)))

        # Stats panel for selected character
        char = CHARACTERS[self.selected]
        stats_rect = pygame.Rect(20, 145, self.w - 40, 38)
        draw_panel(surf, stats_rect)

        # Stats bars
        stats = [
            ("SPD", 0.7 + char.speed_bonus),
            ("ACC", 0.7 + char.accel_bonus),
            ("HND", 0.7 + char.handling_bonus),
        ]
        bar_start_x = 28
        for i, (label, val) in enumerate(stats):
            x = bar_start_x + i * 72
            y = 152
            text = self.font_stats.render(label, True, COL_TEXT_DIM)
            surf.blit(text, (x, y))
            # Bar background
            pygame.draw.rect(surf, COL_BG_DARK, pygame.Rect(x + 22, y + 1, 45, 8))
            # Bar fill
            fill_w = int(45 * min(1.0, max(0.0, val)))
            bar_color = COL_HIGHLIGHT if val >= 0.7 else COL_TEXT_DIM
            pygame.draw.rect(surf, bar_color, pygame.Rect(x + 22, y + 1, fill_w, 8))

        # Hint
        hint = self.font_stats.render("ARROWS:SELECT  ENTER:OK  ESC:BACK", True, COL_TEXT_DIM)
        surf.blit(hint, hint.get_rect(center=(self.w // 2, self.h - 6)))


class CupSelect:
    """MKDS Beta-style cup selection."""
    def __init__(self, w: int, h: int, character_idx: int):
        self.w, self.h = w, h
        self.character_idx = character_idx
        self.selected = 0
        self.t = 0.0
        self.font = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 12)
        self.key_delay = 0.0

    def update(self, dt: float) -> Optional[Tuple[GameState, int, int]]:
        self.t += dt
        self.key_delay = max(0, self.key_delay - dt)
        keys = pygame.key.get_pressed()

        if self.key_delay <= 0:
            if keys[pygame.K_LEFT]:
                self.selected = (self.selected - 1) % len(CUPS)
                self.key_delay = 0.12
            elif keys[pygame.K_RIGHT]:
                self.selected = (self.selected + 1) % len(CUPS)
                self.key_delay = 0.12
            elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                return (GameState.COUNTDOWN, self.character_idx, self.selected)
            elif keys[pygame.K_ESCAPE]:
                return (GameState.CHARACTER_SELECT, -1, -1)

        return None

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(COL_BG_DARK)

        # Header
        header = self.font.render("SELECT CUP", True, COL_HIGHLIGHT)
        surf.blit(header, header.get_rect(center=(self.w // 2, 16)))

        # Cup icons
        grid_w = len(CUPS) * 55
        start_x = (self.w - grid_w) // 2 + 27

        for i, cup in enumerate(CUPS):
            x = start_x + i * 55
            y = 60
            selected = (i == self.selected)

            box_rect = pygame.Rect(x - 22, y - 20, 44, 55)
            draw_panel(surf, box_rect, selected)

            # Trophy icon
            trophy_y = y - 8
            if selected:
                trophy_y += math.sin(self.t * 5) * 2
            pygame.draw.polygon(surf, cup.icon_color, [
                (x, trophy_y - 10), (x - 10, trophy_y + 5),
                (x - 6, trophy_y + 12), (x + 6, trophy_y + 12), (x + 10, trophy_y + 5)
            ])
            pygame.draw.rect(surf, cup.icon_color, pygame.Rect(x - 4, trophy_y + 12, 8, 4))

            # Cup name
            name_color = COL_HIGHLIGHT if selected else COL_TEXT
            words = cup.name.split()
            for j, word in enumerate(words):
                text = self.font_small.render(word, True, name_color)
                surf.blit(text, text.get_rect(center=(x, y + 20 + j * 10)))

        # Track list for selected cup
        cup = CUPS[self.selected]
        tracks_rect = pygame.Rect(20, 125, self.w - 40, 45)
        draw_panel(surf, tracks_rect)

        track_label = self.font_small.render("TRACKS:", True, COL_TEXT_DIM)
        surf.blit(track_label, (28, 130))

        for i, track_name in enumerate(cup.tracks[:3]):
            text = self.font_small.render(f"{i+1}. {track_name}", True, COL_TEXT)
            surf.blit(text, (28, 142 + i * 10))

        # Hint
        hint = self.font_small.render("←→:SELECT  ENTER:OK  ESC:BACK", True, COL_TEXT_DIM)
        surf.blit(hint, hint.get_rect(center=(self.w // 2, self.h - 8)))


class Countdown:
    """Pre-race countdown."""
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.t = 0.0
        self.font = pygame.font.Font(None, 48)
        self.done = False

    def update(self, dt: float) -> bool:
        self.t += dt
        if self.t >= 3.5:
            self.done = True
        return self.done

    def draw(self, surf: pygame.Surface) -> None:
        # Draw on top of race view
        if self.t < 1.0:
            text = "3"
            color = (255, 80, 80)
        elif self.t < 2.0:
            text = "2"
            color = (255, 200, 80)
        elif self.t < 3.0:
            text = "1"
            color = (80, 255, 80)
        else:
            text = "GO!"
            color = (80, 255, 255)

        # Pulsing effect
        scale = 1.0 + (1.0 - (self.t % 1.0)) * 0.3
        rendered = self.font.render(text, True, color)
        scaled = pygame.transform.scale(rendered, 
            (int(rendered.get_width() * scale), int(rendered.get_height() * scale)))
        surf.blit(scaled, scaled.get_rect(center=(self.w // 2, self.h // 3)))


class OptionsMenu:
    """Simple options menu."""
    OPTIONS = ["SFX VOLUME", "BGM VOLUME", "CAMERA STYLE", "BACK"]

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.selected = 0
        self.t = 0.0
        self.font = pygame.font.Font(None, 18)
        self.font_small = pygame.font.Font(None, 14)
        self.key_delay = 0.0

    def update(self, dt: float) -> Optional[GameState]:
        self.t += dt
        self.key_delay = max(0, self.key_delay - dt)
        keys = pygame.key.get_pressed()

        if self.key_delay <= 0:
            if keys[pygame.K_UP]:
                self.selected = (self.selected - 1) % len(self.OPTIONS)
                self.key_delay = 0.15
            elif keys[pygame.K_DOWN]:
                self.selected = (self.selected + 1) % len(self.OPTIONS)
                self.key_delay = 0.15
            elif keys[pygame.K_RETURN] or keys[pygame.K_ESCAPE]:
                if self.selected == 3 or keys[pygame.K_ESCAPE]:
                    return GameState.MAIN_MENU
                self.key_delay = 0.2

        return None

    def draw(self, surf: pygame.Surface) -> None:
        surf.fill(COL_BG_DARK)

        header = self.font.render("OPTIONS", True, COL_HIGHLIGHT)
        surf.blit(header, header.get_rect(center=(self.w // 2, 20)))

        panel_rect = pygame.Rect(40, 40, self.w - 80, 120)
        draw_panel(surf, panel_rect)

        for i, opt in enumerate(self.OPTIONS):
            y = 55 + i * 24
            color = COL_HIGHLIGHT if i == self.selected else COL_TEXT
            if i == self.selected:
                cursor_x = panel_rect.x + 12 + math.sin(self.t * 8) * 2
                pygame.draw.polygon(surf, COL_HIGHLIGHT,
                    [(cursor_x, y + 2), (cursor_x + 6, y + 6), (cursor_x, y + 10)])
            text = self.font_small.render(opt, True, color)
            surf.blit(text, (panel_rect.x + 24, y))

            # Value indicators for adjustable options
            if i < 3:
                bar_x = panel_rect.x + 100
                pygame.draw.rect(surf, COL_BG_DARK, pygame.Rect(bar_x, y + 2, 60, 10))
                pygame.draw.rect(surf, COL_HIGHLIGHT, pygame.Rect(bar_x, y + 2, 45, 10))


# =============================================================================
# MAIN GAME CLASS
# =============================================================================
class SamsoftKart:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Samsoft Kart — Beta MKDS Style")
        self.window = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        self.clock = pygame.time.Clock()
        self.frame = pygame.Surface((INTERNAL_W, INTERNAL_H)).convert()

        self.state = GameState.TITLE
        self.running = True

        # Menu screens
        self.title = TitleScreen(INTERNAL_W, INTERNAL_H)
        self.main_menu = MainMenu(INTERNAL_W, INTERNAL_H)
        self.char_select = CharacterSelect(INTERNAL_W, INTERNAL_H)
        self.cup_select: Optional[CupSelect] = None
        self.countdown: Optional[Countdown] = None
        self.options = OptionsMenu(INTERNAL_W, INTERNAL_H)

        # Race state
        self.selected_character = 0
        self.selected_cup = 0
        self.track: Optional[Track] = None
        self.renderer: Optional[Mode7Renderer] = None
        self.player: Optional[Kart] = None
        self.player_sprite: Optional[pygame.Surface] = None
        self.ai_karts: List[Dict] = []
        self.race_time = 0.0
        self.drifting = False
        self.drift_sparks_t = 0.0
        self.show_fps = True

        # Fonts for HUD
        self.font = pygame.font.Font(None, 20)
        self.font_small = pygame.font.Font(None, 16)

    def init_race(self):
        """Initialize a race with current selections."""
        # Generate track based on cup/track selection
        cup = CUPS[self.selected_cup]
        track_name = cup.tracks[0]  # First track in cup

        if track_name == "Figure-8 Cross":
            self.track = generate_figure8_track()
        else:
            self.track = generate_oval_track(name=track_name)

        self.renderer = Mode7Renderer(
            self.track.surface,
            horizon_y=HORIZON_Y,
            cam_height=CAM_HEIGHT,
            fov_deg=FOV_DEG,
            screen_w=INTERNAL_W,
            screen_h=INTERNAL_H,
        )

        # Player
        char = CHARACTERS[self.selected_character]
        self.player = Kart(
            x=self.track.start_x,
            y=self.track.start_y,
            angle=self.track.start_angle,
        )
        self.player_sprite = make_kart_sprite((28, 16), char.color, char.outline)

        # AI karts
        self.ai_karts = []
        ai_chars = [c for i, c in enumerate(CHARACTERS) if i != self.selected_character]
        cx, cy = self.track.size // 2, self.track.size // 2
        rx, ry = self.track.size * 0.34, self.track.size * 0.26
        for i, char in enumerate(ai_chars[:5]):  # Up to 5 AI opponents
            t = random.random() * math.tau
            self.ai_karts.append({
                "t": t,
                "speed": 0.45 + 0.08 * i,
                "sprite": make_kart_sprite((22, 12), char.color, char.outline),
                "x": cx + rx * math.cos(t),  # Initialize position immediately
                "y": cy + ry * math.sin(t),
            })

        self.race_time = 0.0
        self.countdown = Countdown(INTERNAL_W, INTERNAL_H)

    def update_race(self, dt: float):
        """Update race logic."""
        keys = pygame.key.get_pressed()

        # Handle race inputs
        throttle = 1.0 if keys[pygame.K_UP] else 0.0
        brake = 1.0 if keys[pygame.K_DOWN] else 0.0
        steer = (1.0 if keys[pygame.K_RIGHT] else 0.0) - (1.0 if keys[pygame.K_LEFT] else 0.0)
        self.drifting = keys[pygame.K_SPACE]

        on_road = self.track.is_road(self.player.x, self.player.y)
        on_boost = self.track.is_boost(self.player.x, self.player.y)

        # Apply character bonuses
        char = CHARACTERS[self.selected_character]
        speed_mult = 1.0 + char.speed_bonus
        accel_mult = 1.0 + char.accel_bonus

        self.player.update(
            dt, throttle, brake, steer, self.drifting, on_road, on_boost,
            MAX_SPEED_ROAD * speed_mult, MAX_SPEED_OFFROAD * speed_mult,
            ACCEL * accel_mult, BRAKE,
            FRICTION, OFFROAD_FRICTION, REVERSE_MAX,
            STEER_RATE * (1.0 + char.handling_bonus),
            STEER_RATE_DRIFT * (1.0 + char.handling_bonus),
            BOOST_STRENGTH,
        )

        # Update AI
        cx, cy = self.track.size // 2, self.track.size // 2
        rx, ry = self.track.size * 0.34, self.track.size * 0.26
        for bot in self.ai_karts:
            bot["t"] = (bot["t"] + bot["speed"] * dt) % math.tau
            bot["x"] = cx + rx * math.cos(bot["t"])
            bot["y"] = cy + ry * math.sin(bot["t"])

        self.race_time += dt

        # Check for pause/quit
        if keys[pygame.K_ESCAPE]:
            return GameState.MAIN_MENU
        if keys[pygame.K_r]:
            self.player.x = self.track.start_x
            self.player.y = self.track.start_y
            self.player.angle = self.track.start_angle
            self.player.speed = 0.0

        return None

    def draw_race(self):
        """Draw the race view."""
        # Camera
        cam_back = 56.0
        cam_x = self.player.x - math.cos(self.player.angle) * cam_back
        cam_y = self.player.y - math.sin(self.player.angle) * cam_back

        # Ground
        self.renderer.render_ground(self.frame, cam_x, cam_y, self.player.angle)

        # AI karts
        projected = []
        for bot in self.ai_karts:
            pr = self.renderer.project_point(bot["x"], bot["y"], cam_x, cam_y, self.player.angle)
            if pr:
                sx, sy, sc, fwd = pr
                projected.append((fwd, sx, sy, sc, bot["sprite"]))
        projected.sort(reverse=True)

        for fwd, sx, sy, sc, spr in projected:
            w = max(2, int(spr.get_width() * sc))
            h = max(2, int(spr.get_height() * sc))
            spr2 = pygame.transform.smoothscale(spr, (w, h))
            rect = spr2.get_rect(center=(int(sx), int(sy) - int(h * 0.35)))
            self.frame.blit(spr2, rect.topleft)

        # Player kart
        px, py = INTERNAL_W // 2, INTERNAL_H - 28
        self.frame.blit(self.player_sprite, self.player_sprite.get_rect(center=(px, py)))

        # Drift sparks
        keys = pygame.key.get_pressed()
        steer = (1.0 if keys[pygame.K_RIGHT] else 0.0) - (1.0 if keys[pygame.K_LEFT] else 0.0)
        if self.drifting and abs(steer) > 0.1 and abs(self.player.speed) > 90:
            self.drift_sparks_t += 1/60
            if self.drift_sparks_t > 0.03:
                self.drift_sparks_t = 0.0
                for side in (-1, 1):
                    sx = px + side * 12 + random.randint(-1, 1)
                    sy = py + 8 + random.randint(-1, 1)
                    pygame.draw.circle(self.frame, (255, 240, 160), (sx, sy), 1)
        else:
            self.drift_sparks_t = 0.0

        # HUD
        on_road = self.track.is_road(self.player.x, self.player.y)
        speed_kmh = max(0.0, self.player.speed) * 0.18
        
        # Speed panel (MKDS style)
        hud_rect = pygame.Rect(4, 4, 85, 22)
        pygame.draw.rect(self.frame, (0, 0, 0, 128), hud_rect, border_radius=3)
        pygame.draw.rect(self.frame, COL_PANEL_BORDER, hud_rect, 1, border_radius=3)
        
        speed_text = self.font.render(f"{speed_kmh:05.1f}", True, COL_HIGHLIGHT)
        self.frame.blit(speed_text, (10, 8))
        kmh_text = self.font_small.render("km/h", True, COL_TEXT_DIM)
        self.frame.blit(kmh_text, (58, 10))

        # Time
        mins = int(self.race_time // 60)
        secs = self.race_time % 60
        time_text = self.font.render(f"{mins:02d}:{secs:05.2f}", True, COL_TEXT)
        self.frame.blit(time_text, (INTERNAL_W // 2 - 30, 6))

        # Minimap
        self.frame.blit(self.track.minimap, (INTERNAL_W - 72, 8))
        mx, my = INTERNAL_W - 72, 8
        dot_x = int(mx + (self.player.x % self.track.size) / self.track.size * 64)
        dot_y = int(my + (self.player.y % self.track.size) / self.track.size * 64)
        pygame.draw.circle(self.frame, (255, 60, 60), (dot_x, dot_y), 2)

        # Controls hint
        hint = self.font_small.render("↑↓←→:DRIVE  SPACE:DRIFT  R:RESET  ESC:MENU", True, (60, 60, 60))
        self.frame.blit(hint, (4, INTERNAL_H - 14))

        # FPS
        if self.show_fps:
            fps_text = self.font_small.render(f"{self.clock.get_fps():.0f}FPS", True, (60, 60, 60))
            self.frame.blit(fps_text, (INTERNAL_W - 40, INTERNAL_H - 14))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            # Events
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_F1:
                        self.show_fps = not self.show_fps

            # State machine
            if self.state == GameState.TITLE:
                result = self.title.update(dt)
                self.title.draw(self.frame)
                if result:
                    self.state = result

            elif self.state == GameState.MAIN_MENU:
                result = self.main_menu.update(dt)
                self.main_menu.draw(self.frame)
                if result:
                    self.state = result

            elif self.state == GameState.CHARACTER_SELECT:
                result = self.char_select.update(dt)
                self.char_select.draw(self.frame)
                if result:
                    next_state, char_idx = result
                    if char_idx >= 0:
                        self.selected_character = char_idx
                        self.cup_select = CupSelect(INTERNAL_W, INTERNAL_H, char_idx)
                    self.state = next_state

            elif self.state == GameState.CUP_SELECT:
                result = self.cup_select.update(dt)
                self.cup_select.draw(self.frame)
                if result:
                    next_state, char_idx, cup_idx = result
                    if cup_idx >= 0:
                        self.selected_cup = cup_idx
                        self.init_race()
                    self.state = next_state

            elif self.state == GameState.COUNTDOWN:
                # Draw race behind countdown
                self.draw_race()
                done = self.countdown.update(dt)
                self.countdown.draw(self.frame)
                if done:
                    self.state = GameState.RACING

            elif self.state == GameState.RACING:
                result = self.update_race(dt)
                self.draw_race()
                if result:
                    self.state = result

            elif self.state == GameState.OPTIONS:
                result = self.options.update(dt)
                self.options.draw(self.frame)
                if result:
                    self.state = result

            # Scale and flip
            if SCALE == 1:
                self.window.blit(self.frame, (0, 0))
            else:
                self.window.blit(pygame.transform.scale(self.frame, (WINDOW_W, WINDOW_H)), (0, 0))
            pygame.display.flip()

        pygame.quit()


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    game = SamsoftKart()
    game.run()
