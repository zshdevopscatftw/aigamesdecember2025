#!/usr/bin/env python3
"""
ULTRA!PONG — Pygame Edition (1990s Core / Game Boy Speed)
---------------------------------------------------------
• Pure pygame (FILES = OFF)
• Left paddle = AI
• Right paddle = Player
• 60 FPS fixed loop
• Main Menu (SPACE)
• First to 5 wins
• Game Over prompt (Y/N)

Samsoft / Team Flames
"""

import sys
import random
import pygame

# =====================================================
# CONFIG
# =====================================================
WIDTH, HEIGHT = 640, 400
PADDLE_W, PADDLE_H = 10, 80
BALL_SIZE = 10
FPS = 60
WIN_SCORE = 5

# "Game Boy" vibes (classic-ish greens)
GB_DARK   = (15, 56, 15)
GB_MID    = (48, 98, 48)
GB_LIGHT  = (155, 188, 15)
GB_LIGHT2 = (139, 172, 15)

# Speed (tuned for that crunchy handheld feel @ 60fps)
PLAYER_SPEED = 320.0   # px/sec
AI_SPEED     = 280.0   # px/sec

BALL_SPEED_X = 260.0   # px/sec
BALL_SPEED_Y = 180.0   # px/sec
BALL_SPIN    = 260.0   # added vy on paddle hit based on impact
BALL_Y_CLAMP = 420.0   # cap vertical speed so it stays fun

# =====================================================
# UTILS
# =====================================================
def clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v

def center_text(screen, font, text, y, color):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH // 2, y))
    screen.blit(surf, rect)

# =====================================================
# GAME
# =====================================================
class UltraPong:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ULTRA!PONG — 60 FPS — GAME BOY SPEED")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts (no external files)
        self.f_big = pygame.font.SysFont("Courier", 48, bold=True)
        self.f_mid = pygame.font.SysFont("Courier", 20, bold=True)
        self.f_sml = pygame.font.SysFont("Courier", 16, bold=False)

        self.state = "menu"  # menu | play | gameover
        self.running = True

        self.ai_score = 0
        self.player_score = 0
        self.winner = None

        self._setup_objects()
        self._reset_round(serving_to="player")

    def _setup_objects(self):
        self.ai_paddle = pygame.Rect(20, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
        self.player_paddle = pygame.Rect(WIDTH - 30, HEIGHT // 2 - PADDLE_H // 2, PADDLE_W, PADDLE_H)
        self.ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

        # float positions for smooth dt movement (Rect stays int)
        self.ball_fx = float(self.ball.x)
        self.ball_fy = float(self.ball.y)

        self.ball_vx = 0.0
        self.ball_vy = 0.0

    def _reset_game(self):
        self.ai_score = 0
        self.player_score = 0
        self.winner = None

        self.ai_paddle.y = HEIGHT // 2 - PADDLE_H // 2
        self.player_paddle.y = HEIGHT // 2 - PADDLE_H // 2

        self._reset_round(serving_to="player")

    def _reset_round(self, serving_to="player"):
        # Center ball
        self.ball_fx = float(WIDTH // 2 - BALL_SIZE // 2)
        self.ball_fy = float(HEIGHT // 2 - BALL_SIZE // 2)
        self.ball.x = int(self.ball_fx)
        self.ball.y = int(self.ball_fy)

        # Serve direction
        if serving_to == "player":
            self.ball_vx = +BALL_SPEED_X
        elif serving_to == "ai":
            self.ball_vx = -BALL_SPEED_X
        else:
            self.ball_vx = random.choice([-BALL_SPEED_X, +BALL_SPEED_X])

        # Vertical component (never zero)
        vy = random.choice([-BALL_SPEED_Y, +BALL_SPEED_Y])
        vy += random.uniform(-40.0, 40.0)
        if abs(vy) < 60.0:
            vy = 120.0 if vy >= 0 else -120.0
        self.ball_vy = vy

    # ================= INPUT =================
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_SPACE:
                        self._reset_game()
                        self.state = "play"

                elif self.state == "gameover":
                    if event.key == pygame.K_y:
                        self._reset_game()
                        self.state = "play"
                    elif event.key in (pygame.K_n, pygame.K_ESCAPE):
                        self.running = False

                elif self.state == "play":
                    if event.key == pygame.K_ESCAPE:
                        # Back to menu (optional, feels right)
                        self.state = "menu"

    def _update_player(self, dt):
        keys = pygame.key.get_pressed()
        dy = 0.0

        if keys[pygame.K_UP]:
            dy -= PLAYER_SPEED * dt
        if keys[pygame.K_DOWN]:
            dy += PLAYER_SPEED * dt

        if dy != 0.0:
            self.player_paddle.y += int(round(dy))
            self.player_paddle.y = clamp(self.player_paddle.y, 0, HEIGHT - PADDLE_H)

    def _update_ai(self, dt):
        # AI: follow ball when it's coming left; otherwise drift toward center
        target_y = (HEIGHT // 2 - PADDLE_H // 2)

        if self.ball_vx < 0:
            target_y = self.ball.centery - PADDLE_H // 2

        # Move toward target with capped speed
        diff = target_y - self.ai_paddle.y
        step = AI_SPEED * dt
        if diff > step:
            self.ai_paddle.y += int(round(step))
        elif diff < -step:
            self.ai_paddle.y -= int(round(step))
        else:
            self.ai_paddle.y = int(round(target_y))

        self.ai_paddle.y = clamp(self.ai_paddle.y, 0, HEIGHT - PADDLE_H)

    # ================= BALL =================
    def _paddle_bounce(self, paddle_rect, going_right):
        """
        going_right: True if ball was moving right (player side),
                     False if ball was moving left (AI side)
        """
        # Place ball flush with paddle to prevent "sticking"
        if going_right:
            self.ball.right = paddle_rect.left
        else:
            self.ball.left = paddle_rect.right

        # Mirror X velocity with fixed magnitude
        self.ball_vx = -BALL_SPEED_X if going_right else +BALL_SPEED_X

        # Add spin based on hit position
        offset = (self.ball.centery - paddle_rect.centery) / (PADDLE_H / 2.0)
        offset = clamp(offset, -1.0, 1.0)
        self.ball_vy += offset * BALL_SPIN

        # Clamp vy so it doesn't go totally unhinged
        self.ball_vy = clamp(self.ball_vy, -BALL_Y_CLAMP, BALL_Y_CLAMP)

        # Sync float pos to rect
        self.ball_fx = float(self.ball.x)
        self.ball_fy = float(self.ball.y)

    def _update_ball(self, dt):
        # Move with float precision
        self.ball_fx += self.ball_vx * dt
        self.ball_fy += self.ball_vy * dt

        self.ball.x = int(round(self.ball_fx))
        self.ball.y = int(round(self.ball_fy))

        # Wall bounce
        if self.ball.top <= 0:
            self.ball.top = 0
            self.ball_vy *= -1.0
            self.ball_fy = float(self.ball.y)

        if self.ball.bottom >= HEIGHT:
            self.ball.bottom = HEIGHT
            self.ball_vy *= -1.0
            self.ball_fy = float(self.ball.y)

        # Paddle collisions (only if moving toward that paddle)
        if self.ball_vx > 0 and self.ball.colliderect(self.player_paddle):
            self._paddle_bounce(self.player_paddle, going_right=True)

        elif self.ball_vx < 0 and self.ball.colliderect(self.ai_paddle):
            self._paddle_bounce(self.ai_paddle, going_right=False)

        # Score
        if self.ball.right < 0:
            # Ball went past AI side => player scores
            self.player_score += 1
            self._reset_round(serving_to="ai")

        elif self.ball.left > WIDTH:
            # Ball went past player side => AI scores
            self.ai_score += 1
            self._reset_round(serving_to="player")

    # ================= GAME OVER =================
    def _check_game_over(self):
        if self.ai_score >= WIN_SCORE or self.player_score >= WIN_SCORE:
            self.winner = "PLAYER" if self.player_score >= WIN_SCORE else "AI"
            self.state = "gameover"

    # ================= DRAW =================
    def _draw_center_line(self):
        # Dashed center line, chunky retro
        x = WIDTH // 2
        seg_h = 10
        gap = 8
        y = 0
        while y < HEIGHT:
            pygame.draw.rect(self.screen, GB_MID, (x - 2, y, 4, seg_h))
            y += seg_h + gap

    def _draw_hud(self):
        score = f"{self.ai_score} : {self.player_score}"
        surf = self.f_mid.render(score, True, GB_LIGHT)
        rect = surf.get_rect(center=(WIDTH // 2, 20))
        self.screen.blit(surf, rect)

    def _draw_menu(self):
        self.screen.fill(GB_DARK)
        self._draw_center_line()

        center_text(self.screen, self.f_big, "ULTRA!PONG", HEIGHT // 2 - 40, GB_LIGHT)
        center_text(self.screen, self.f_mid, "PRESS SPACE TO START", HEIGHT // 2 + 15, GB_LIGHT2)
        center_text(self.screen, self.f_sml, "ARROWS = MOVE | ESC = MENU", HEIGHT - 25, GB_MID)

    def _draw_play(self):
        self.screen.fill(GB_DARK)
        self._draw_center_line()

        pygame.draw.rect(self.screen, GB_LIGHT, self.ai_paddle)
        pygame.draw.rect(self.screen, GB_LIGHT, self.player_paddle)
        pygame.draw.rect(self.screen, GB_LIGHT, self.ball)  # square ball = extra retro

        self._draw_hud()

    def _draw_gameover(self):
        self.screen.fill(GB_DARK)
        self._draw_center_line()

        center_text(self.screen, self.f_big, f"{self.winner} WINS", HEIGHT // 2 - 40, GB_LIGHT)
        center_text(self.screen, self.f_mid, "PLAY AGAIN? (Y/N)", HEIGHT // 2 + 20, GB_LIGHT2)

        final = f"FINAL: {self.ai_score} : {self.player_score}"
        center_text(self.screen, self.f_sml, final, HEIGHT // 2 + 55, GB_MID)

    # ================= MAIN LOOP =================
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self._handle_events()

            if self.state == "play":
                self._update_player(dt)
                self._update_ai(dt)
                self._update_ball(dt)
                self._check_game_over()
                self._draw_play()

            elif self.state == "menu":
                self._draw_menu()

            elif self.state == "gameover":
                self._draw_gameover()

            pygame.display.flip()

        pygame.quit()
        sys.exit(0)

# =====================================================
# BOOT
# =====================================================
if __name__ == "__main__":
    UltraPong().run()
