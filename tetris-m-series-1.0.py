#!/usr/bin/env python3
import pygame
import random
import sys
from enum import Enum, auto
from typing import List, Tuple

pygame.init()

# =========================
# CONFIG
# =========================
SCREEN_WIDTH, SCREEN_HEIGHT = 480, 640
FPS = 60
GRID_WIDTH, GRID_HEIGHT = 10, 20
CELL_SIZE = 28
OFFSET_X, OFFSET_Y = 40, 60

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (64, 64, 64)
COLOR_GRID = (40, 40, 40)

PIECE_COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (200, 50, 255),
    'S': (0, 255, 100),
    'Z': (255, 50, 50),
    'J': (50, 50, 255),
    'L': (255, 165, 0)
}

# =========================
# SHAPES
# =========================
SHAPE_DEFINITIONS = {
    'I': {'blocks': [[(0,1),(1,1),(2,1),(3,1)],[(2,0),(2,1),(2,2),(2,3)]]*2},
    'O': {'blocks': [[(1,0),(2,0),(1,1),(2,1)]]*4},
    'T': {'blocks': [[(1,0),(0,1),(1,1),(2,1)],[(1,0),(1,1),(2,1),(1,2)],
                     [(0,1),(1,1),(2,1),(1,2)],[(1,0),(0,1),(1,1),(1,2)]]},
    'S': {'blocks': [[(1,0),(2,0),(0,1),(1,1)],[(1,0),(1,1),(2,1),(2,2)]]*2},
    'Z': {'blocks': [[(0,0),(1,0),(1,1),(2,1)],[(2,0),(1,1),(2,1),(1,2)]]*2},
    'J': {'blocks': [[(0,0),(0,1),(1,1),(2,1)],[(1,0),(2,0),(1,1),(1,2)],
                     [(0,1),(1,1),(2,1),(2,2)],[(1,0),(1,1),(1,2),(0,2)]]},
    'L': {'blocks': [[(2,0),(0,1),(1,1),(2,1)],[(1,0),(1,1),(1,2),(2,2)],
                     [(0,1),(1,1),(2,1),(0,2)],[(0,0),(1,0),(1,1),(1,2)]]}
}

# =========================
# GAME STATE
# =========================
class GameState(Enum):
    MAIN_MENU = auto()
    HOW_TO_PLAY = auto()
    CREDITS = auto()
    PLAYING = auto()

# =========================
# PIECE
# =========================
class Tetromino:
    def __init__(self, piece_type):
        self.type = piece_type
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 1
        self.y = -2

    @property
    def blocks(self):
        shape = SHAPE_DEFINITIONS[self.type]['blocks'][self.rotation]
        return [(self.x + dx, self.y + dy) for dx, dy in shape]

    def rotate(self, grid):
        old = self.rotation
        self.rotation = (self.rotation + 1) % len(SHAPE_DEFINITIONS[self.type]['blocks'])
        for x, y in self.blocks:
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT or (y >= 0 and grid[y][x]):
                self.rotation = old
                break

# =========================
# GRID
# =========================
class GameGrid:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def lock(self, piece):
        for x, y in piece.blocks:
            if 0 <= y < GRID_HEIGHT:
                self.grid[y][x] = PIECE_COLORS[piece.type]

    def clear_lines(self):
        new = [row for row in self.grid if any(c is None for c in row)]
        cleared = GRID_HEIGHT - len(new)
        while len(new) < GRID_HEIGHT:
            new.insert(0, [None]*GRID_WIDTH)
        self.grid = new
        return cleared

# =========================
# GAME
# =========================
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ULTRA! TETRIS")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 28)
        self.state = GameState.MAIN_MENU
        self.reset()

    def reset(self):
        self.grid = GameGrid()
        self.current = Tetromino(random.choice(list(PIECE_COLORS)))
        self.next_piece = Tetromino(random.choice(list(PIECE_COLORS)))
        self.drop_timer = 0
        self.drop_speed = 0.5
        self.score = 0

    def spawn(self):
        self.current = self.next_piece
        self.next_piece = Tetromino(random.choice(list(PIECE_COLORS)))
        self.current.y = -2

    def handle_input(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if e.type == pygame.KEYDOWN:
                if self.state == GameState.MAIN_MENU:
                    if e.key in (pygame.K_z, pygame.K_SPACE):
                        self.reset()
                        self.state = GameState.PLAYING
                    if e.key == pygame.K_h:
                        self.state = GameState.HOW_TO_PLAY
                    if e.key == pygame.K_c:
                        self.state = GameState.CREDITS

                elif self.state in (GameState.HOW_TO_PLAY, GameState.CREDITS):
                    if e.key == pygame.K_ESCAPE:
                        self.state = GameState.MAIN_MENU

                elif self.state == GameState.PLAYING:
                    if e.key == pygame.K_LEFT: self.current.x -= 1
                    if e.key == pygame.K_RIGHT: self.current.x += 1
                    if e.key == pygame.K_DOWN: self.current.y += 1
                    if e.key == pygame.K_UP: self.current.rotate(self.grid.grid)
                    if e.key == pygame.K_ESCAPE: self.state = GameState.MAIN_MENU

    def update(self, dt):
        if self.state != GameState.PLAYING:
            return
        self.drop_timer += dt
        if self.drop_timer > self.drop_speed:
            self.drop_timer = 0
            self.current.y += 1
            if any(y >= GRID_HEIGHT or (y >= 0 and self.grid.grid[y][x]) for x, y in self.current.blocks):
                self.current.y -= 1
                self.grid.lock(self.current)
                self.score += self.grid.clear_lines()
                self.spawn()

    def draw_text_center(self, text, y, font=None):
        font = font or self.font
        surf = font.render(text, True, COLOR_WHITE)
        self.screen.blit(surf, (SCREEN_WIDTH//2 - surf.get_width()//2, y))

    def draw(self):
        self.screen.fill(COLOR_BLACK)

        if self.state == GameState.MAIN_MENU:
            self.draw_text_center("ULTRA! TETRIS", 140, self.font_big)
            self.draw_text_center("PRESS Z / SPACE TO START", 240)
            self.draw_text_center("H - HOW TO PLAY", 280)
            self.draw_text_center("C - CREDITS", 320)

        elif self.state == GameState.HOW_TO_PLAY:
            self.draw_text_center("HOW TO PLAY", 120, self.font_big)
            self.draw_text_center("ARROWS - MOVE", 240)
            self.draw_text_center("UP - ROTATE", 270)
            self.draw_text_center("DOWN - SOFT DROP", 300)
            self.draw_text_center("ESC - BACK", 360)

        elif self.state == GameState.CREDITS:
            self.draw_text_center("CREDITS", 140, self.font_big)
            self.draw_text_center("Tetris Co.", 260)
            self.draw_text_center("Samsoft", 300)
            self.draw_text_center("ESC - BACK", 360)

        elif self.state == GameState.PLAYING:
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    c = self.grid.grid[y][x]
                    if c:
                        pygame.draw.rect(self.screen, c,
                            (OFFSET_X + x*CELL_SIZE, OFFSET_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            for x, y in self.current.blocks:
                if y >= 0:
                    pygame.draw.rect(self.screen, PIECE_COLORS[self.current.type],
                        (OFFSET_X + x*CELL_SIZE, OFFSET_Y + y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000
            self.handle_input()
            self.update(dt)
            self.draw()

if __name__ == "__main__":
    Game().run()
