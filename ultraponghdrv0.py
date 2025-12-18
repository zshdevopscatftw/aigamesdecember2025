#!/usr/bin/env python3
"""
Ultra!Pong - Retro NES/Famicom Style Pong
Pure Tkinter implementation with 8-bit aesthetics
"""

import tkinter as tk
import random
import sys
import platform

# Try to use winsound for Windows, fallback to print for other OS
try:
    import winsound
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False

class UltraPong:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultra!Pong - Famicom Edition")
        
        # NES/Famicom Color Palette
        self.COLORS = {
            "bg": "#000000",
            "paddle": "#00ffff",      # Bright cyan
            "ball": "#ff00ff",        # Magenta
            "text": "#ffffff",        # White
            "accent": "#ff0000",      # Red
            "net": "#404040",         # Gray for dashed line
        }
        
        # Game Constants
        self.CANVAS_WIDTH = 800
        self.CANVAS_HEIGHT = 600
        self.PADDLE_WIDTH = 15
        self.PADDLE_HEIGHT = 100
        self.BALL_SIZE = 20
        self.BALL_SPEED = 10
        self.AI_SPEED = 7
        self.WIN_SCORE = 5
        
        # Game State
        self.ball_x = self.CANVAS_WIDTH // 2
        self.ball_y = self.CANVAS_HEIGHT // 2
        self.ball_dx = random.choice([-self.BALL_SPEED, self.BALL_SPEED])
        self.ball_dy = random.choice([-self.BALL_SPEED // 2, self.BALL_SPEED // 2])
        
        self.left_paddle_y = self.CANVAS_HEIGHT // 2 - self.PADDLE_HEIGHT // 2
        self.right_paddle_y = self.CANVAS_HEIGHT // 2 - self.PADDLE_HEIGHT // 2
        
        self.ai_score = 0
        self.player_score = 0
        self.hit_count = 0
        self.game_active = True
        self.game_ended = False
        
        # Setup Canvas
        self.canvas = tk.Canvas(
            root,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg=self.COLORS["bg"],
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Draw initial game elements
        self.draw_net()
        self.draw_paddles()
        self.draw_ball()
        self.draw_scores()
        self.draw_title()
        
        # Bindings
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.root.bind("<KeyPress>", self.on_key_press)
        self.canvas.bind("<Enter>", lambda e: self.canvas.focus_set())
        
        # Start game loop
        self.game_loop()
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.CANVAS_WIDTH // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.CANVAS_HEIGHT // 2)
        self.root.geometry(f"{self.CANVAS_WIDTH}x{self.CANVAS_HEIGHT}+{x}+{y}")
    
    def draw_net(self):
        """Draw dashed line in center like classic Pong"""
        dash_length = 20
        gap_length = 15
        y = dash_length
        
        while y < self.CANVAS_HEIGHT:
            self.canvas.create_line(
                self.CANVAS_WIDTH // 2,
                y,
                self.CANVAS_WIDTH // 2,
                y + dash_length,
                fill=self.COLORS["net"],
                width=2
            )
            y += dash_length + gap_length
    
    def draw_paddles(self):
        """Draw both paddles with pixelated look"""
        # Left paddle (AI)
        self.left_paddle = self.canvas.create_rectangle(
            20,
            self.left_paddle_y,
            20 + self.PADDLE_WIDTH,
            self.left_paddle_y + self.PADDLE_HEIGHT,
            fill=self.COLORS["paddle"],
            outline=self.COLORS["paddle"],
            width=0
        )
        
        # Right paddle (Player)
        self.right_paddle = self.canvas.create_rectangle(
            self.CANVAS_WIDTH - 20 - self.PADDLE_WIDTH,
            self.right_paddle_y,
            self.CANVAS_WIDTH - 20,
            self.right_paddle_y + self.PADDLE_HEIGHT,
            fill=self.COLORS["paddle"],
            outline=self.COLORS["paddle"],
            width=0
        )
    
    def draw_ball(self):
        """Draw ball as thick rectangle for pixelated look"""
        self.ball = self.canvas.create_rectangle(
            self.ball_x - self.BALL_SIZE // 2,
            self.ball_y - self.BALL_SIZE // 2,
            self.ball_x + self.BALL_SIZE // 2,
            self.ball_y + self.BALL_SIZE // 2,
            fill=self.COLORS["ball"],
            outline=self.COLORS["ball"],
            width=0
        )
    
    def draw_scores(self):
        """Draw score display in retro font style"""
        self.score_text = self.canvas.create_text(
            self.CANVAS_WIDTH // 2,
            40,
            text=f"AI: {self.ai_score}    PLAYER: {self.player_score}",
            fill=self.COLORS["text"],
            font=("Courier", 32, "bold")
        )
    
    def draw_title(self):
        """Draw game title at top"""
        self.title_text = self.canvas.create_text(
            self.CANVAS_WIDTH // 2,
            20,
            text="Ultra!Pong",
            fill=self.COLORS["ball"],  # Magenta like the ball
            font=("Courier", 24, "bold")
        )
    
    def update_scores(self):
        """Update score display"""
        self.canvas.itemconfig(
            self.score_text,
            text=f"AI: {self.ai_score}    PLAYER: {self.player_score}"
        )
    
    def play_sound(self, frequency, duration):
        """Play beep sound or print for non-Windows"""
        if SOUND_ENABLED and platform.system() == "Windows":
            winsound.Beep(frequency, duration)
        else:
            # Fallback: print sound event
            print(f"BEEP {frequency}Hz {duration}ms")
    
    def move_ai_paddle(self):
        """AI paddle smoothly tracks ball with slight delay"""
        target_y = self.ball_y - self.PADDLE_HEIGHT // 2
        
        # Smooth movement with delay
        if self.left_paddle_y < target_y:
            self.left_paddle_y += min(self.AI_SPEED, target_y - self.left_paddle_y)
        elif self.left_paddle_y > target_y:
            self.left_paddle_y -= min(self.AI_SPEED, self.left_paddle_y - target_y)
        
        # Keep paddle in bounds
        self.left_paddle_y = max(0, min(self.CANVAS_HEIGHT - self.PADDLE_HEIGHT, self.left_paddle_y))
        
        # Update paddle position
        self.canvas.coords(
            self.left_paddle,
            20,
            self.left_paddle_y,
            20 + self.PADDLE_WIDTH,
            self.left_paddle_y + self.PADDLE_HEIGHT
        )
    
    def on_mouse_move(self, event):
        """Move player paddle with mouse"""
        if not self.game_ended:
            # Constrain to canvas
            y = max(0, min(event.y - self.PADDLE_HEIGHT // 2, self.CANVAS_HEIGHT - self.PADDLE_HEIGHT))
            self.right_paddle_y = y
            
            # Update paddle position
            self.canvas.coords(
                self.right_paddle,
                self.CANVAS_WIDTH - 20 - self.PADDLE_WIDTH,
                self.right_paddle_y,
                self.CANVAS_WIDTH - 20,
                self.right_paddle_y + self.PADDLE_HEIGHT
            )
    
    def check_collisions(self):
        """Check ball collisions with walls and paddles"""
        ball_left = self.ball_x - self.BALL_SIZE // 2
        ball_right = self.ball_x + self.BALL_SIZE // 2
        ball_top = self.ball_y - self.BALL_SIZE // 2
        ball_bottom = self.ball_y + self.BALL_SIZE // 2
        
        # Top and bottom walls
        if ball_top <= 0 or ball_bottom >= self.CANVAS_HEIGHT:
            self.ball_dy = -self.ball_dy
            self.play_sound(800, 50)
        
        # Left paddle collision
        if (ball_left <= 20 + self.PADDLE_WIDTH and 
            ball_left >= 20 and
            ball_bottom >= self.left_paddle_y and
            ball_top <= self.left_paddle_y + self.PADDLE_HEIGHT):
            
            # Angle variation based on where ball hits paddle
            hit_pos = (self.ball_y - self.left_paddle_y) / self.PADDLE_HEIGHT
            angle = (hit_pos - 0.5) * 1.5  # -0.75 to 0.75
            
            self.ball_dx = abs(self.ball_dx)  # Ensure moving right
            self.ball_dy = angle * self.BALL_SPEED * 2
            
            self.hit_count += 1
            self.play_sound(1000, 50)
            
            # Increase speed every 4 hits
            if self.hit_count % 4 == 0:
                self.ball_dx *= 1.1
                self.ball_dy *= 1.1
        
        # Right paddle collision
        if (ball_right >= self.CANVAS_WIDTH - 20 - self.PADDLE_WIDTH and
            ball_right <= self.CANVAS_WIDTH - 20 and
            ball_bottom >= self.right_paddle_y and
            ball_top <= self.right_paddle_y + self.PADDLE_HEIGHT):
            
            # Angle variation based on where ball hits paddle
            hit_pos = (self.ball_y - self.right_paddle_y) / self.PADDLE_HEIGHT
            angle = (hit_pos - 0.5) * 1.5  # -0.75 to 0.75
            
            self.ball_dx = -abs(self.ball_dx)  # Ensure moving left
            self.ball_dy = angle * self.BALL_SPEED * 2
            
            self.hit_count += 1
            self.play_sound(1000, 50)
            
            # Increase speed every 4 hits
            if self.hit_count % 4 == 0:
                self.ball_dx *= 1.1
                self.ball_dy *= 1.1
        
        # Scoring
        if ball_left <= 0:
            self.player_score += 1
            self.reset_ball()
            self.play_sound(500, 200)
        
        if ball_right >= self.CANVAS_WIDTH:
            self.ai_score += 1
            self.reset_ball()
            self.play_sound(300, 200)
        
        # Update scores if changed
        if self.ai_score != self.old_ai_score or self.player_score != self.old_player_score:
            self.update_scores()
            self.old_ai_score = self.ai_score
            self.old_player_score = self.player_score
        
        # Check for win condition
        if self.ai_score >= self.WIN_SCORE or self.player_score >= self.WIN_SCORE:
            self.end_game()
    
    def reset_ball(self):
        """Reset ball to center with random direction"""
        self.ball_x = self.CANVAS_WIDTH // 2
        self.ball_y = self.CANVAS_HEIGHT // 2
        self.ball_dx = random.choice([-self.BALL_SPEED, self.BALL_SPEED])
        self.ball_dy = random.choice([-self.BALL_SPEED // 2, self.BALL_SPEED // 2])
        self.hit_count = 0
    
    def end_game(self):
        """Handle end game conditions"""
        self.game_active = False
        self.game_ended = True
        
        # Determine winner
        winner = "AI" if self.ai_score >= self.WIN_SCORE else "PLAYER"
        
        # Draw winner text
        self.winner_text = self.canvas.create_text(
            self.CANVAS_WIDTH // 2,
            self.CANVAS_HEIGHT // 2 - 50,
            text=f"{winner} WINS!",
            fill=self.COLORS["accent"],
            font=("Courier", 48, "bold")
        )
        
        # Draw restart prompt
        self.restart_text = self.canvas.create_text(
            self.CANVAS_WIDTH // 2,
            self.CANVAS_HEIGHT // 2 + 30,
            text="Play again? (Y/N)",
            fill=self.COLORS["text"],
            font=("Courier", 24, "bold")
        )
        
        self.play_sound(200, 500)
    
    def reset_game(self):
        """Reset game to initial state"""
        self.ai_score = 0
        self.player_score = 0
        self.old_ai_score = 0
        self.old_player_score = 0
        self.hit_count = 0
        self.game_active = True
        self.game_ended = False
        
        # Remove winner text if exists
        if hasattr(self, 'winner_text'):
            self.canvas.delete(self.winner_text)
        if hasattr(self, 'restart_text'):
            self.canvas.delete(self.restart_text)
        
        self.reset_ball()
        self.update_scores()
        
        # Reset paddle positions
        self.left_paddle_y = self.CANVAS_HEIGHT // 2 - self.PADDLE_HEIGHT // 2
        self.right_paddle_y = self.CANVAS_HEIGHT // 2 - self.PADDLE_HEIGHT // 2
        
        self.canvas.coords(
            self.left_paddle,
            20,
            self.left_paddle_y,
            20 + self.PADDLE_WIDTH,
            self.left_paddle_y + self.PADDLE_HEIGHT
        )
    
    def on_key_press(self, event):
        """Handle keyboard input"""
        if self.game_ended:
            if event.char.lower() == 'y':
                self.reset_game()
            elif event.char.lower() == 'n':
                self.root.quit()
    
    def game_loop(self):
        """Main game loop running at ~60 FPS"""
        if self.game_active:
            # Move ball
            self.ball_x += self.ball_dx
            self.ball_y += self.ball_dy
            
            # Move AI paddle
            self.move_ai_paddle()
            
            # Check collisions
            self.check_collisions()
            
            # Update ball position
            self.canvas.coords(
                self.ball,
                self.ball_x - self.BALL_SIZE // 2,
                self.ball_y - self.BALL_SIZE // 2,
                self.ball_x + self.BALL_SIZE // 2,
                self.ball_y + self.BALL_SIZE // 2
            )
        
        # Schedule next frame (approximately 60 FPS)
        self.root.after(16, self.game_loop)

def main():
    """Main entry point"""
    root = tk.Tk()
    game = UltraPong(root)
    
    # Initialize old scores for change detection
    game.old_ai_score = 0
    game.old_player_score = 0
    
    # Center window on screen
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = game.CANVAS_WIDTH
    window_height = game.CANVAS_HEIGHT
    
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.resizable(False, False)
    
    # Start the game
    root.mainloop()

if __name__ == "__main__":
    main()
