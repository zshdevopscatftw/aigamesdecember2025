#!/usr/bin/env python3
# ============================================================
# ULTRA MARIO 2D BROS.
# NES-STYLE MAIN MENU — TKINTER
# Pure SMB1 vibe • No parody • No extras • One file
# ============================================================

import tkinter as tk

# ============================================================
# CONFIG
# ============================================================
WIDTH, HEIGHT = 512, 448   # NES 256x224 ×2
BG = "black"
WHITE = "#f8f8f8"
RED = "#d82800"

# ============================================================
# APP
# ============================================================
class SMB1Menu:
    def __init__(self, root):
        self.root = root
        self.root.title("ULTRA MARIO 2D BROS.")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=BG,
            highlightthickness=0
        )
        self.canvas.pack()

        self.selection = 0
        self.options = ["1 PLAYER GAME", "2 PLAYER GAME"]

        self.draw()
        self.bind()

    # ========================================================
    # DRAW
    # ========================================================
    def draw(self):
        self.canvas.delete("all")

        # --- TITLE ---
        self.canvas.create_text(
            WIDTH // 2, 120,
            text="ULTRA MARIO 2D BROS.",
            fill=WHITE,
            font=("Courier", 28, "bold")
        )

        # --- MENU OPTIONS ---
        y_start = 220
        for i, text in enumerate(self.options):
            y = y_start + i * 32

            # Selector (like SMB1 arrow)
            if self.selection == i:
                self.canvas.create_text(
                    WIDTH // 2 - 120, y,
                    text="▶",
                    fill=WHITE,
                    font=("Courier", 18, "bold")
                )

            self.canvas.create_text(
                WIDTH // 2, y,
                text=text,
                fill=WHITE,
                font=("Courier", 18, "bold")
            )

        # --- FOOTER (TOP SCORE STYLE) ---
        self.canvas.create_text(
            WIDTH // 2, HEIGHT - 64,
            text="TOP-000000",
            fill=WHITE,
            font=("Courier", 14)
        )

        self.canvas.create_text(
            WIDTH // 2, HEIGHT - 36,
            text="© 1985 SAMSOFT",
            fill=RED,
            font=("Courier", 12)
        )

    # ========================================================
    # INPUT
    # ========================================================
    def bind(self):
        self.root.bind("<Up>", self.up)
        self.root.bind("<Down>", self.down)
        self.root.bind("<Return>", self.select)
        self.root.bind("<z>", self.select)      # NES A
        self.root.bind("<space>", self.select)  # NES A alt

    def up(self, event=None):
        self.selection = (self.selection - 1) % len(self.options)
        self.draw()

    def down(self, event=None):
        self.selection = (self.selection + 1) % len(self.options)
        self.draw()

    def select(self, event=None):
        choice = self.options[self.selection]
        print("SELECTED:", choice)
        # hook this into your game boot
        # if choice == "1 PLAYER GAME": start_game(1)
        # if choice == "2 PLAYER GAME": start_game(2)

# ============================================================
# BOOT
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    SMB1Menu(root)
    root.mainloop()
