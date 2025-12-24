import pygame
import math
import random

pygame.init()

# Screen
WIDTH, HEIGHT = 960, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultra! Mario 3D Bros")

# Colors
C_BG = (0, 0, 50)
C_STAR = (255, 255, 200)
C_TITLE = (255, 255, 0)
C_TEXT = (255, 255, 255)
C_MARIO = (255, 0, 0)
C_MARIO_EYE = (255, 255, 255)

# Stars (twinkle)
stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "size": random.randint(1, 3), "alpha": random.randint(100, 255)} for _ in range(150)]

# Menu
menu_options = ["START GAME", "OPTIONS", "QUIT"]
selected = 0
menu_y = HEIGHT // 2 + 50

# Mario head rotation
mario_angle = 0
mario_angle_speed = 0.5

# Title warp timer
warp_time = 0
warp_active = False

clock = pygame.time.Clock()
font_big = pygame.font.SysFont("monospace", 72, bold=True)
font_med = pygame.font.SysFont("monospace", 36)

running = True
while running:
    dt = clock.tick(60) / 1000.0
    warp_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected = (selected - 1) % len(menu_options)
            if event.key == pygame.K_DOWN:
                selected = (selected + 1) % len(menu_options)
            if event.key == pygame.K_RETURN:
                if selected == 0:
                    print("START GAME - loading level...")
                    # Hook your game loop here
                elif selected == 1:
                    print("OPTIONS - not implemented")
                elif selected == 2:
                    running = False
            if event.key == pygame.K_SPACE:  # Press SPACE to warp title
                warp_active = True
                warp_time = 0

    # Update
    mario_angle += mario_angle_speed
    if warp_active and warp_time > 2:
        warp_active = False

    # Draw
    screen.fill(C_BG)

    # Starfield
    for s in stars:
        s["alpha"] += random.randint(-20, 20)
        s["alpha"] = max(100, min(255, s["alpha"]))
        pygame.draw.circle(screen, (*C_STAR, s["alpha"]), (s["x"], s["y"]), s["size"])

    # Fake fog gradient (N64 style)
    for i in range(HEIGHT):
        alpha = (i / HEIGHT) * 0.6
        fog = (int(0 * alpha), int(0 * alpha), int(50 * alpha))
        pygame.draw.line(screen, fog, (0, i), (WIDTH, i))

    # Title "Ultra! Mario 3D Bros" with warp effect
    title_text = "Ultra! Mario 3D Bros"
    warp_scale = 1.0 + math.sin(warp_time * 8) * 0.3 if warp_active else 1.0
    title_surf = font_big.render(title_text, True, C_TITLE)
    title_surf = pygame.transform.scale(title_surf, (int(title_surf.get_width() * warp_scale), int(title_surf.get_height() * warp_scale)))
    title_rect = title_surf.get_rect(center=(WIDTH//2, 150))
    screen.blit(title_surf, title_rect)

    # Mario head billboard
    head_x = WIDTH // 2
    head_y = 300
    head_size = 120
    # Simple rotation effect
    head_surf = pygame.Surface((head_size, head_size), pygame.SRCALPHA)
    pygame.draw.circle(head_surf, C_MARIO, (head_size//2, head_size//2), head_size//2)
    # Eyes
    eye_offset = 30 * math.cos(math.radians(mario_angle))
    eye_y = 40 * math.sin(math.radians(mario_angle))
    pygame.draw.circle(head_surf, C_MARIO_EYE, (head_size//2 - 20 + int(eye_offset), head_size//2 - 20 + int(eye_y)), 15)
    pygame.draw.circle(head_surf, C_MARIO_EYE, (head_size//2 + 20 + int(eye_offset), head_size//2 - 20 + int(eye_y)), 15)
    # Nose
    pygame.draw.circle(head_surf, (255, 165, 0), (head_size//2, head_size//2 + 10), 12)
    screen.blit(head_surf, (head_x - head_size//2, head_y - head_size//2))

    # Menu options
    for i, opt in enumerate(menu_options):
        color = (255, 215, 0) if i == selected else C_TEXT
        text = font_med.render(opt, True, color)
        rect = text.get_rect(center=(WIDTH//2, menu_y + i*60))
        screen.blit(text, rect)

    pygame.display.flip()

pygame.quit()
