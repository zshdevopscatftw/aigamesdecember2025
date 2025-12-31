# kart_demo.py
import pygame, math, sys
W, H = 800, 600
FPS = 60

pygame.init()
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
pygame.display.set_caption("Top‑Down Kart Demo")
font = pygame.font.SysFont(None, 20)

class Kart:
    def __init__(self):
        self.x, self.y = W*0.5, H*0.6
        self.a = -90          # facing up
        self.v = 0.0
        self.maxv = 4.0
        self.acc = 0.12
        self.brake = 0.2
        self.fric = 0.05      # base friction; raises slightly while steering

    def update(self, dt, keys):
        steer = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT])
        th = (keys[pygame.K_UP] - keys[pygame.K_DOWN])   # throttle/brake

        # acceleration (forward/back)
        self.v += self.acc * th * dt
        self.v = max(-2.0, min(self.v, self.maxv))

        # steering scales with speed (tighter at higher speeds)
        if abs(self.v) > 0.01:
            self.a += steer * (0.12 + 0.06*(abs(self.v)/self.maxv)) * dt

        # integrate position
        rad = math.radians(self.a)
        self.x += math.cos(rad) * self.v * dt
        self.y += math.sin(rad) * self.v * dt

        # friction + slight extra slip while steering (drift feel)
        self.v -= self.fric * dt * (1.0 + 0.6 * abs(steer))

        # light brake bias when holding DOWN while moving
        if th < 0:
            self.v += -self.brake * 0.4 * dt * math.copysign(1, self.v)

        # bounds clamp
        self.x = max(40, min(W-40, self.x))
        self.y = max(40, min(H-40, self.y))

    def draw(self, surf):
        # simple triangle "kart"
        pts = [(-16, -10), (18, 0), (-16, 10)]
        rad = math.radians(self.a)
        c, s = math.cos(rad), math.sin(rad)
        t = [(self.x + px*c - py*s, self.y + px*s + py*c) for (px, py) in pts]
        pygame.draw.polygon(surf, (240, 230, 90), t)

# build a simple oval track mask
track = pygame.Surface((W, H))
track.fill((30, 30, 35))
pygame.draw.ellipse(track, (55, 55, 65), pygame.Rect(60, 40, W-120, H-80), 60)
pygame.draw.ellipse(track, (25, 25, 30), pygame.Rect(60, 40, W-120, H-80), 0)
pygame.draw.ellipse(track, (90, 90, 110), pygame.Rect(60, 40, W-120, H-80), 4)

kart = Kart()
running = True

while running:
    # Fixed cap + delta-time (dt) in "frame units" (60fps baseline ≈ 16.67ms)
    dt = clock.tick(FPS) / 16.67

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    kart.update(dt, keys)

    screen.blit(track, (0, 0))
    kart.draw(screen)

    hud = f"speed:{kart.v:0.2f}  angle:{(kart.a%360):0.0f}"
    screen.blit(font.render(hud, True, (230, 240, 240)), (10, 10))
    screen.blit(font.render("Arrows: steer/throttle | Mild drift via steer friction", True, (210, 220, 220)), (10, 32))
    pygame.display.flip()

pygame.quit()
sys.exit(0)
