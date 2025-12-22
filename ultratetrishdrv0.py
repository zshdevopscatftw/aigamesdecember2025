import pygame
import random

pygame.init()

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE)
pygame.display.set_caption("ULTRA!TETRIS - Team Flames")

NES_BG = (0, 0, 0)
NES_WHITE = (252, 252, 252)
NES_RED = (228, 0, 88)
NES_CYAN = (0, 232, 216)
NES_PURPLE = (104, 68, 252)
NES_GREEN = (0, 168, 0)
NES_BLUE = (0, 88, 248)
NES_YELLOW = (248, 184, 0)
NES_ORANGE = (228, 92, 16)
NES_GRAY = (188, 188, 188)

font_large = pygame.font.Font(None, 32)
font_medium = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 20)
font_tiny = pygame.font.Font(None, 16)

BLOCK_SIZE = 16
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X = 40
GRID_Y = 40

SHAPES = {
    'I': [[1,1,1,1]],
    'O': [[1,1],[1,1]],
    'T': [[0,1,0],[1,1,1]],
    'S': [[0,1,1],[1,1,0]],
    'Z': [[1,1,0],[0,1,1]],
    'J': [[1,0,0],[1,1,1]],
    'L': [[0,0,1],[1,1,1]]
}

COLORS = {
    'I': NES_CYAN, 'O': NES_YELLOW, 'T': NES_PURPLE, 'S': NES_GREEN,
    'Z': NES_RED, 'J': NES_BLUE, 'L': NES_ORANGE
}

class Piece:
    def __init__(self, name):
        self.name = name
        self.shape = [r[:] for r in SHAPES[name]]
        self.color = COLORS[name]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0
    def rotate(self):
        self.shape = [list(r) for r in zip(*self.shape[::-1])]

class Game:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.grid = [[None]*GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.current = self.new_piece()
        self.next = self.new_piece()
        self.held = None
        self.can_hold = True
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.drop_timer = 0
        self.drop_delay = 500
    
    def new_piece(self):
        return Piece(random.choice(list(SHAPES)))
    
    def valid(self, piece, dx=0, dy=0):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    nx, ny = piece.x + x + dx, piece.y + y + dy
                    if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT:
                        return False
                    if ny >= 0 and self.grid[ny][nx]:
                        return False
        return True
    
    def lock(self):
        for y, row in enumerate(self.current.shape):
            for x, cell in enumerate(row):
                if cell:
                    py, px = self.current.y + y, self.current.x + x
                    if py >= 0:
                        self.grid[py][px] = self.current.color
        self.clear_lines()
        self.current = self.next
        self.next = self.new_piece()
        self.can_hold = True
        if not self.valid(self.current):
            self.game_over = True
    
    def clear_lines(self):
        cleared = 0
        y = GRID_HEIGHT - 1
        while y >= 0:
            if all(self.grid[y]):
                del self.grid[y]
                self.grid.insert(0, [None] * GRID_WIDTH)
                cleared += 1
            else:
                y -= 1
        if cleared:
            self.score += [0, 100, 300, 500, 800][cleared] * self.level
            self.lines += cleared
            self.level = self.lines // 10 + 1
            self.drop_delay = max(50, 500 - (self.level - 1) * 40)
    
    def hold(self):
        if not self.can_hold:
            return
        self.can_hold = False
        if self.held:
            self.current, self.held = Piece(self.held), self.current.name
        else:
            self.held = self.current.name
            self.current = self.next
            self.next = self.new_piece()
    
    def hard_drop(self):
        while self.valid(self.current, dy=1):
            self.current.y += 1
            self.score += 2
        self.lock()
    
    def ghost_y(self):
        gy = self.current.y
        while self.valid(self.current, dy=gy - self.current.y + 1):
            gy += 1
        return gy
    
    def update(self, dt):
        if self.game_over:
            return
        self.drop_timer += dt
        if self.drop_timer >= self.drop_delay:
            self.drop_timer = 0
            if self.valid(self.current, dy=1):
                self.current.y += 1
            else:
                self.lock()

def draw_block(x, y, color, size=BLOCK_SIZE):
    pygame.draw.rect(screen, color, (x, y, size-1, size-1))
    light = (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50))
    pygame.draw.rect(screen, light, (x, y, size-1, 2))
    pygame.draw.rect(screen, light, (x, y, 2, size-1))

def draw_preview(name, x, y, label):
    screen.blit(font_small.render(label, True, NES_WHITE), (x, y))
    if name:
        for ry, row in enumerate(SHAPES[name]):
            for rx, cell in enumerate(row):
                if cell:
                    draw_block(x + rx*12, y + 18 + ry*12, COLORS[name], 12)

def draw_game(game):
    screen.fill(NES_BG)
    pygame.draw.rect(screen, NES_WHITE, (GRID_X-2, GRID_Y-2, GRID_WIDTH*BLOCK_SIZE+4, GRID_HEIGHT*BLOCK_SIZE+4), 2)
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if game.grid[y][x]:
                draw_block(GRID_X + x*BLOCK_SIZE, GRID_Y + y*BLOCK_SIZE, game.grid[y][x])
    
    gy = game.ghost_y()
    for y, row in enumerate(game.current.shape):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, game.current.color, (GRID_X + (game.current.x+x)*BLOCK_SIZE, GRID_Y + (gy+y)*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1), 1)
    
    for y, row in enumerate(game.current.shape):
        for x, cell in enumerate(row):
            if cell and game.current.y + y >= 0:
                draw_block(GRID_X + (game.current.x+x)*BLOCK_SIZE, GRID_Y + (game.current.y+y)*BLOCK_SIZE, game.current.color)
    
    px = 240
    screen.blit(font_large.render("ULTRA!TETRIS", True, NES_CYAN), (px, 20))
    screen.blit(font_small.render(f"SCORE: {game.score}", True, NES_YELLOW), (px, 55))
    screen.blit(font_small.render(f"LEVEL: {game.level}", True, NES_GREEN), (px + 120, 55))
    screen.blit(font_small.render(f"LINES: {game.lines}", True, NES_PURPLE), (px + 220, 55))
    
    draw_preview(game.next.name, px, 85, "NEXT")
    draw_preview(game.held, px + 70, 85, "HOLD")
    
    for i, txt in enumerate(["← → MOVE", "↑ ROTATE", "↓ SOFT DROP", "SPACE HARD", "C HOLD", "P PAUSE"]):
        screen.blit(font_tiny.render(txt, True, NES_GRAY), (px, 150 + i*14))
    
    if game.game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        screen.blit(font_large.render("GAME OVER", True, NES_RED), (SCREEN_WIDTH//2 - 70, 160))
        screen.blit(font_medium.render("R TO RESTART", True, NES_WHITE), (SCREEN_WIDTH//2 - 60, 200))

def draw_menu(sel):
    screen.fill(NES_BG)
    screen.blit(font_large.render("ULTRA!TETRIS", True, NES_CYAN), (SCREEN_WIDTH//2 - 80, 100))
    screen.blit(font_medium.render("PYGAME PORT", True, NES_GREEN), (SCREEN_WIDTH//2 - 55, 140))
    opts = ["START GAME", "QUIT"]
    for i, opt in enumerate(opts):
        color = NES_YELLOW if i == sel else NES_WHITE
        txt = font_large.render(opt, True, color)
        screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 200 + i*40))
        if i == sel:
            screen.blit(font_large.render(">", True, NES_YELLOW), (SCREEN_WIDTH//2 - txt.get_width()//2 - 20, 200 + i*40))
    screen.blit(font_tiny.render("© 2025 TEAM FLAMES / SAMSOFT", True, NES_GRAY), (SCREEN_WIDTH//2 - 90, 370))

def draw_pause():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    screen.blit(font_large.render("PAUSED", True, NES_YELLOW), (SCREEN_WIDTH//2 - 45, 180))
    screen.blit(font_medium.render("P TO RESUME", True, NES_WHITE), (SCREEN_WIDTH//2 - 55, 220))

clock = pygame.time.Clock()
game = Game()
state = "menu"
menu_sel = 0
paused = False
running = True

while running:
    dt = clock.tick(60)
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if state == "menu":
                if e.key == pygame.K_UP:
                    menu_sel = (menu_sel - 1) % 2
                elif e.key == pygame.K_DOWN:
                    menu_sel = (menu_sel + 1) % 2
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if menu_sel == 0:
                        game.reset()
                        state = "game"
                    else:
                        running = False
            elif state == "game":
                if e.key == pygame.K_ESCAPE:
                    state = "menu"
                elif e.key == pygame.K_p:
                    paused = not paused
                elif not paused and not game.game_over:
                    if e.key == pygame.K_LEFT and game.valid(game.current, dx=-1):
                        game.current.x -= 1
                    elif e.key == pygame.K_RIGHT and game.valid(game.current, dx=1):
                        game.current.x += 1
                    elif e.key == pygame.K_UP:
                        old = [r[:] for r in game.current.shape]
                        game.current.rotate()
                        if not game.valid(game.current):
                            for kick in [-1, 1, -2, 2]:
                                if game.valid(game.current, dx=kick):
                                    game.current.x += kick
                                    break
                            else:
                                game.current.shape = old
                    elif e.key == pygame.K_DOWN and game.valid(game.current, dy=1):
                        game.current.y += 1
                        game.score += 1
                    elif e.key == pygame.K_SPACE:
                        game.hard_drop()
                    elif e.key == pygame.K_c:
                        game.hold()
                elif game.game_over and e.key == pygame.K_r:
                    game.reset()
    
    if state == "game" and not paused and not game.game_over:
        game.update(dt)
    
    if state == "menu":
        draw_menu(menu_sel)
    elif state == "game":
        draw_game(game)
        if paused:
            draw_pause()
    
    pygame.display.flip()

pygame.quit()
