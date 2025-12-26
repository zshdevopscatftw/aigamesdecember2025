import pygame
import numpy as np
import math

# --- CONFIGURATION ---
WIDTH, HEIGHT = 600, 400
FPS = 60
TITLE = "FAMICON BREAKOUT - 600x400"

# NES-like Palette
BLACK = (10, 10, 20)
WHITE = (220, 220, 220)
RED = (200, 50, 50)
ORANGE = (220, 120, 20)
YELLOW = (220, 200, 20)
GREEN = (50, 180, 50)
BLUE = (50, 100, 220)
PADDLE_COLOR = (180, 180, 200)

# --- AUDIO ENGINE (Famicon Synth) ---
def generate_tone(frequency, duration, volume=0.5, wave_type="square"):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)

    if wave_type == "square":
        wave = np.sign(np.sin(2 * np.pi * frequency * t))
    elif wave_type == "sawtooth":
        wave = 2 * (t * frequency - np.floor(t * frequency + 0.5))
    elif wave_type == "noise":
        wave = np.random.uniform(-1, 1, n_samples)
    else:
        wave = np.sin(2 * np.pi * frequency * t)

    envelope = np.linspace(1, 0, n_samples)
    wave = wave * envelope * volume

    audio = (wave * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=2)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20, bold=True)

        # Sounds
        self.snd_hit_paddle = generate_tone(440, 0.1, 0.3, "square")
        self.snd_hit_brick = generate_tone(880, 0.05, 0.2, "square")
        self.snd_wall = generate_tone(220, 0.05, 0.2, "square")
        self.snd_die = generate_tone(110, 0.5, 0.4, "sawtooth")
        self.snd_win = generate_tone(660, 0.2, 0.3, "square")

        self.reset_game()

    def reset_game(self):
        # Paddle
        self.paddle_w = 80
        self.paddle_h = 12
        self.paddle_rect = pygame.Rect(
            WIDTH // 2 - self.paddle_w // 2,
            HEIGHT - 30,
            self.paddle_w,
            self.paddle_h,
        )

        # Ball
        self.ball_radius = 6
        self.reset_ball()

        # Bricks
        self.bricks = []
        rows, cols = 5, 8
        brick_w, brick_h = 60, 20
        padding = 10
        offset_top = 50
        offset_left = (WIDTH - (cols * (brick_w + padding))) // 2

        colors = [RED, ORANGE, YELLOW, GREEN, BLUE]

        for row in range(rows):
            for col in range(cols):
                bx = offset_left + col * (brick_w + padding)
                by = offset_top + row * (brick_h + padding)
                color = colors[row % len(colors)]

                # ✅ FIXED: tuple append
                self.bricks.append(
                    (pygame.Rect(bx, by, brick_w, brick_h), color)
                )

        self.state = "MENU"
        self.score = 0
        self.lives = 3

    def reset_ball(self):
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2 + 50
        self.ball_dx = 4 * (1 if np.random.rand() > 0.5 else -1)
        self.ball_dy = -4

    def play_sound(self, snd):
        snd.play()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state in ("MENU", "GAMEOVER", "WIN"):
                    self.reset_game()
                    self.state = "PLAYING"

        if self.state == "PLAYING":
            mx, _ = pygame.mouse.get_pos()
            self.paddle_rect.centerx = mx
            self.paddle_rect.clamp_ip(self.screen.get_rect())

        return True

    def update(self):
        if self.state != "PLAYING":
            return

        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Walls
        if self.ball_x - self.ball_radius <= 0 or self.ball_x + self.ball_radius >= WIDTH:
            self.ball_dx *= -1
            self.play_sound(self.snd_wall)

        if self.ball_y - self.ball_radius <= 0:
            self.ball_dy *= -1
            self.play_sound(self.snd_wall)

        # Floor
        if self.ball_y + self.ball_radius >= HEIGHT:
            self.lives -= 1
            self.play_sound(self.snd_die)
            if self.lives <= 0:
                self.state = "GAMEOVER"
            else:
                self.reset_ball()

        ball_rect = pygame.Rect(
            self.ball_x - self.ball_radius,
            self.ball_y - self.ball_radius,
            self.ball_radius * 2,
            self.ball_radius * 2,
        )

        # Paddle
        if self.paddle_rect.colliderect(ball_rect) and self.ball_dy > 0:
            offset = (self.ball_x - self.paddle_rect.centerx) / (self.paddle_w / 2)
            self.ball_dx = offset * 6
            self.ball_dy *= -1
            self.play_sound(self.snd_hit_paddle)

        # Bricks
        brick_rects = [b[0] for b in self.bricks]
        hit = ball_rect.collidelist(brick_rects)

        if hit != -1:
            brick_rect, _ = self.bricks[hit]
            if abs(self.ball_y - brick_rect.centery) > abs(self.ball_x - brick_rect.centerx):
                self.ball_dy *= -1
            else:
                self.ball_dx *= -1

            del self.bricks[hit]
            self.score += 10
            self.ball_dx *= 1.02
            self.ball_dy *= 1.02
            self.play_sound(self.snd_hit_brick)

            if not self.bricks:
                self.state = "WIN"
                self.play_sound(self.snd_win)

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "MENU":
            self.draw_center("FAMICON BREAKOUT", -30, WHITE, 40)
            self.draw_center("CLICK TO START", 30, GREEN)

        elif self.state == "PLAYING":
            for rect, color in self.bricks:
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

            pygame.draw.rect(self.screen, PADDLE_COLOR, self.paddle_rect)
            pygame.draw.circle(
                self.screen, WHITE,
                (int(self.ball_x), int(self.ball_y)),
                self.ball_radius
            )

            self.screen.blit(self.font.render(f"SCORE: {self.score}", True, WHITE), (10, 10))
            self.screen.blit(self.font.render(f"LIVES: {self.lives}", True, WHITE), (WIDTH - 100, 10))

        elif self.state == "GAMEOVER":
            self.draw_center("GAME OVER", -20, RED, 40)
            self.draw_center("CLICK TO RESTART", 40, GREEN)

        elif self.state == "WIN":
            self.draw_center("YOU WIN!", -20, YELLOW, 40)
            self.draw_center("CLICK TO RESTART", 40, GREEN)

        pygame.display.flip()

    def draw_center(self, text, y, color, size=20):
        font = pygame.font.SysFont("arial", size, bold=True)
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + y))
        self.screen.blit(surf, rect)

    def run(self):
        running = True
        while running:
            pygame.mouse.set_visible(self.state != "PLAYING")
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    Game().run()
