import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Game Settings
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
BALL_SIZE = 15
PADDLE_SPEED = 7
BALL_X_SPEED = 5
BALL_Y_SPEED = 5
WINNING_SCORE = 5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)
large_font = pygame.font.SysFont("Arial", 80)

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

    def move_player(self):
        # Use mouse Y position for left player
        mouse_y = pygame.mouse.get_pos()[1]
        self.rect.centery = mouse_y
        # Keep paddle on screen
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def move_ai(self, ball):
        # Simple AI for right paddle
        if self.rect.centery < ball.rect.centery and self.rect.bottom < HEIGHT:
            self.rect.y += PADDLE_SPEED
        elif self.rect.centery > ball.rect.centery and self.rect.top > 0:
            self.rect.y -= PADDLE_SPEED

class Ball:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
        self.reset()

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = BALL_X_SPEED * random.choice([1, -1])
        self.speed_y = BALL_Y_SPEED * random.choice([1, -1])

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1

    def draw(self):
        pygame.draw.ellipse(screen, WHITE, self.rect)

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    screen.blit(img, rect)

def main_menu():
    while True:
        screen.fill(BLACK)
        draw_text("PONG", large_font, WHITE, WIDTH // 2, HEIGHT // 3)
        draw_text("Left Player: Mouse | Right Player: AI", font, WHITE, WIDTH // 2, HEIGHT // 2)
        draw_text("Credits: [ATARI] [Flames co]", font, WHITE, WIDTH // 2, HEIGHT // 2 + 50)
        draw_text("Click Left Mouse to Start", font, WHITE, WIDTH // 2, HEIGHT * 3 // 4)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Mouse
                    return

        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen(winner):
    while True:
        screen.fill(BLACK)
        draw_text(f"{winner} WINS!", large_font, WHITE, WIDTH // 2, HEIGHT // 3)
        draw_text("y/ restaart n = qutit", font, WHITE, WIDTH // 2, HEIGHT // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key == pygame.K_n:
                    return False

        pygame.display.flip()
        clock.tick(FPS)

def play_game():
    left_paddle = Paddle(20, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    right_paddle = Paddle(WIDTH - 20 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2)
    ball = Ball()

    left_score = 0
    right_score = 0

    while True:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Input
        left_paddle.move_player()
        right_paddle.move_ai(ball)
        ball.move()

        # Collisions
        if ball.rect.colliderect(left_paddle.rect) or ball.rect.colliderect(right_paddle.rect):
            ball.speed_x *= -1
            # Prevent ball from getting stuck in paddle
            if ball.speed_x > 0:
                ball.rect.left = left_paddle.rect.right
            else:
                ball.rect.right = right_paddle.rect.left

        # Scoring
        if ball.rect.left <= 0:
            right_score += 1
            ball.reset()
        if ball.rect.right >= WIDTH:
            left_score += 1
            ball.reset()

        # Check Game Over
        if left_score >= WINNING_SCORE or right_score >= WINNING_SCORE:
            winner = "LEFT PLAYER" if left_score >= WINNING_SCORE else "RIGHT PLAYER"
            if game_over_screen(winner):
                return True # Restart
            else:
                pygame.quit()
                sys.exit()

        # Draw
        left_paddle.draw()
        right_paddle.draw()
        ball.draw()
        pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        
        draw_text(str(left_score), font, WHITE, WIDTH // 4, 30)
        draw_text(str(right_score), font, WHITE, WIDTH * 3 // 4, 30)

        pygame.display.flip()
        clock.tick(FPS)

def main():
    while True:
        main_menu()
        if not play_game():
            break

if __name__ == "__main__":
    main()
