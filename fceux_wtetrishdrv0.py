import tkinter as tk
import random

# Cat's FCEUX 0.1 - Now with built-in Tetris!
# 600x400 Tkinter - No external dependencies

# Tetris constants
COLS = 10
ROWS = 20
CELL = 25
BOARD_X = 50
BOARD_Y = 50

# Tetromino shapes (each rotation)
SHAPES = {
    'I': [[(0,1),(1,1),(2,1),(3,1)], [(1,0),(1,1),(1,2),(1,3)]],
    'O': [[(0,0),(0,1),(1,0),(1,1)]],
    'T': [[(0,1),(1,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(1,2)], [(1,0),(1,1),(1,2),(2,1)], [(1,0),(0,1),(1,1),(1,2)]],
    'S': [[(0,1),(0,2),(1,0),(1,1)], [(0,0),(1,0),(1,1),(2,1)]],
    'Z': [[(0,0),(0,1),(1,1),(1,2)], [(0,1),(1,0),(1,1),(2,0)]],
    'J': [[(0,0),(1,0),(1,1),(1,2)], [(0,1),(0,2),(1,1),(2,1)], [(1,0),(1,1),(1,2),(2,2)], [(0,1),(1,1),(2,0),(2,1)]],
    'L': [[(0,2),(1,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(2,2)], [(1,0),(1,1),(1,2),(2,0)], [(0,0),(0,1),(1,1),(2,1)]]
}

COLORS = {'I':'#00ffff','O':'#ffff00','T':'#aa00ff','S':'#00ff00','Z':'#ff0000','J':'#0000ff','L':'#ff8800'}

class Tetris:
    def __init__(self, canvas):
        self.canvas = canvas
        self.board = [[None]*COLS for _ in range(ROWS)]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        self.current = None
        self.current_x = 0
        self.current_y = 0
        self.current_rot = 0
        self.current_type = ''
        self.spawn_piece()
        
    def spawn_piece(self):
        self.current_type = random.choice(list(SHAPES.keys()))
        self.current_rot = 0
        self.current = SHAPES[self.current_type][0]
        self.current_x = COLS // 2 - 2
        self.current_y = 0
        if self.collision(self.current_x, self.current_y, self.current):
            self.game_over = True
            
    def collision(self, px, py, piece):
        for (r, c) in piece:
            nx, ny = px + c, py + r
            if nx < 0 or nx >= COLS or ny >= ROWS:
                return True
            if ny >= 0 and self.board[ny][nx]:
                return True
        return False
        
    def lock_piece(self):
        color = COLORS[self.current_type]
        for (r, c) in self.current:
            nx, ny = self.current_x + c, self.current_y + r
            if 0 <= ny < ROWS and 0 <= nx < COLS:
                self.board[ny][nx] = color
        self.clear_lines()
        self.spawn_piece()
        
    def clear_lines(self):
        cleared = 0
        new_board = []
        for row in self.board:
            if all(row):
                cleared += 1
            else:
                new_board.append(row)
        for _ in range(cleared):
            new_board.insert(0, [None]*COLS)
        self.board = new_board
        self.lines += cleared
        self.score += [0, 100, 300, 500, 800][cleared] * self.level
        self.level = 1 + self.lines // 10
        
    def move(self, dx, dy):
        if not self.collision(self.current_x + dx, self.current_y + dy, self.current):
            self.current_x += dx
            self.current_y += dy
            return True
        return False
        
    def rotate(self):
        rotations = SHAPES[self.current_type]
        new_rot = (self.current_rot + 1) % len(rotations)
        new_piece = rotations[new_rot]
        if not self.collision(self.current_x, self.current_y, new_piece):
            self.current = new_piece
            self.current_rot = new_rot
            
    def drop(self):
        if not self.move(0, 1):
            self.lock_piece()
            
    def hard_drop(self):
        while self.move(0, 1):
            self.score += 2
        self.lock_piece()
        
    def draw(self):
        self.canvas.delete("game")
        # Board background
        self.canvas.create_rectangle(BOARD_X, BOARD_Y, BOARD_X + COLS*CELL, BOARD_Y + ROWS*CELL, fill="#111122", outline="#4444ff", width=3, tags="game")
        # Grid
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = BOARD_X + c*CELL, BOARD_Y + r*CELL
                self.canvas.create_rectangle(x1, y1, x1+CELL, y1+CELL, outline="#222244", tags="game")
                if self.board[r][c]:
                    self.canvas.create_rectangle(x1+2, y1+2, x1+CELL-2, y1+CELL-2, fill=self.board[r][c], outline="#ffffff", tags="game")
        # Current piece
        if self.current and not self.game_over:
            color = COLORS[self.current_type]
            for (r, c) in self.current:
                nx, ny = self.current_x + c, self.current_y + r
                if ny >= 0:
                    x1, y1 = BOARD_X + nx*CELL, BOARD_Y + ny*CELL
                    self.canvas.create_rectangle(x1+2, y1+2, x1+CELL-2, y1+CELL-2, fill=color, outline="#ffffff", width=2, tags="game")
        # UI panel
        px = BOARD_X + COLS*CELL + 30
        self.canvas.create_text(px, 60, text="Cat's Tetris", font=("Arial", 16, "bold"), fill="#ff99ff", anchor="nw", tags="game")
        self.canvas.create_text(px, 100, text=f"Score: {self.score}", font=("Arial", 14), fill="#ffffff", anchor="nw", tags="game")
        self.canvas.create_text(px, 130, text=f"Level: {self.level}", font=("Arial", 14), fill="#ffffff", anchor="nw", tags="game")
        self.canvas.create_text(px, 160, text=f"Lines: {self.lines}", font=("Arial", 14), fill="#ffffff", anchor="nw", tags="game")
        # Cat
        cat = "  /\\_/\\\n ( o.o )\n  > ^ <"
        self.canvas.create_text(px, 220, text=cat, font=("Courier", 14), fill="#ff99ff", anchor="nw", tags="game")
        self.canvas.create_text(px, 300, text="Meow~", font=("Arial", 12), fill="#aaaaaa", anchor="nw", tags="game")
        # Controls
        self.canvas.create_text(px, 340, text="←→ Move\n↑ Rotate\n↓ Soft\nSpace Hard\nP Pause", font=("Arial", 10), fill="#888888", anchor="nw", tags="game")
        # Game over / Pause
        if self.game_over:
            self.canvas.create_text(BOARD_X + COLS*CELL//2, BOARD_Y + ROWS*CELL//2, text="GAME OVER\nPress R", font=("Arial", 20, "bold"), fill="#ff0000", tags="game")
        elif self.paused:
            self.canvas.create_text(BOARD_X + COLS*CELL//2, BOARD_Y + ROWS*CELL//2, text="PAUSED", font=("Arial", 20, "bold"), fill="#ffff00", tags="game")

# Main window
root = tk.Tk()
root.title("Cat's FCEUX 0.1 - Tetris")
root.configure(bg="#000011")
root.resizable(False, False)

canvas = tk.Canvas(root, width=600, height=400, bg="#000011", highlightthickness=0)
canvas.pack()

game = Tetris(canvas)

def tick():
    if not game.game_over and not game.paused:
        game.drop()
    game.draw()
    delay = max(100, 500 - (game.level - 1) * 40)
    root.after(delay, tick)

def key_press(e):
    if e.keysym == 'r' or e.keysym == 'R':
        game.__init__(canvas)
        return
    if game.game_over:
        return
    if e.keysym == 'p' or e.keysym == 'P':
        game.paused = not game.paused
    if game.paused:
        return
    if e.keysym == 'Left':
        game.move(-1, 0)
    elif e.keysym == 'Right':
        game.move(1, 0)
    elif e.keysym == 'Down':
        game.move(0, 1)
        game.score += 1
    elif e.keysym == 'Up':
        game.rotate()
    elif e.keysym == 'space':
        game.hard_drop()
    game.draw()

root.bind("<KeyPress>", key_press)
root.focus_set()

tick()
root.mainloop()
