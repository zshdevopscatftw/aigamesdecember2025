# PLATFORMER STARTER — grid tiles • AABB • jump buffer • coyote • look-ahead cam
# Single file • Pygame • FILES=OFF
import pygame, sys, math, itertools
pygame.init()

# ---------- Config ----------
SCALE   = 3
TW, TH  = 16, 16                  # tile size
VW, VH  = 20, 15                  # view tiles (logical)
WIN_W, WIN_H = VW*TW*SCALE, VH*TH*SCALE
FPS     = 60
FIXED_DT = 1/120                  # fixed step for crisp physics
MAX_STEPS = 4                     # clamp spiral of death

# Physics
GRAVITY = 1800
MAX_FALL= 900
ACCEL   = 800
FRICTION= 0.85
RUN_MAX = 160
JUMP_V  = 430
COYOTE  = 0.10                    # seconds after leaving ground
JBUF    = 0.12                    # seconds before landing

# Colors
C_BG=(30,30,40); C_SOLID=(80,90,120); C_PLAYER=(240,90,70); C_ENEMY=(240,200,70)

# ---------- Level (ASCII) ----------
LEVEL = [
    "............................",
    "............................",
    "............###............",
    "....................###....",
    ".............##...........#",
    ".........................##",
    ".....##....................",
    "..................E.......#",
    "#####...........#####......",
    "...........................",
    "...............####........",
    "...........###.............",
    "......................###..",
    "############..#############",
    "############..#############",
]
W, H = len(LEVEL[0]), len(LEVEL)

def is_solid(tx, ty):
    if tx<0 or ty<0 or tx>=W or ty>=H: return True
    return LEVEL[ty][tx] == "#"

def rect_vs_level(rect):
    # returns correction vector to resolve AABB vs solid tiles
    # sample tiles overlapped by rect
    min_tx = int(rect.left//TW); max_tx = int((rect.right-1)//TW)
    min_ty = int(rect.top //TH); max_ty = int((rect.bottom-1)//TH)
    dx=dy=0
    r=pygame.Rect(rect)
    for ty in range(min_ty, max_ty+1):
        for tx in range(min_tx, max_tx+1):
            if is_solid(tx,ty):
                tile = pygame.Rect(tx*TW, ty*TH, TW, TH)
                if r.colliderect(tile):
                    # resolve on the shallowest axis
                    overlap_x = (tile.right - r.left) if r.centerx<tile.centerx else -(r.right - tile.left)
                    overlap_y = (tile.bottom- r.top) if r.centery<tile.centery else -(r.bottom- tile.top)
                    if abs(overlap_x) < abs(overlap_y):
                        r.x += overlap_x; dx += overlap_x
                    else:
                        r.y += overlap_y; dy += overlap_y
    return dx, dy

# ---------- Entities ----------
class Actor:
    def __init__(self, x,y,w=12,h=14,color=C_PLAYER):
        self.x,self.y=x,y; self.w,self.h=w,h
        self.vx=self.vy=0
        self.grounded=False
        self.coyote=0.0
        self.jump_buf=0.0
        self.color=color
    @property
    def rect(self): return pygame.Rect(int(self.x-self.w/2), int(self.y-self.h/2), self.w, self.h)

    def move_and_collide(self, dt):
        # integrate
        self.vy += GRAVITY*dt
        if self.vy>MAX_FALL: self.vy=MAX_FALL
        # X
        self.x += self.vx*dt
        dx,dy = rect_vs_level(self.rect)
        if dx: self.x -= dx; self.vx = 0
        # Y
        self.y += self.vy*dt
        dx,dy = rect_vs_level(self.rect)
        if dy:
            self.y -= dy
            if dy<0: # bumped ceiling
                self.vy = 0
            else:    # landed
                self.vy = 0
                self.grounded = True
                self.coyote = COYOTE
            # reset vertical overlap handled
        else:
            self.grounded = False

class Player(Actor):
    def update(self, keys, dt):
        # horizontal input
        ax = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  ax -= ACCEL
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: ax += ACCEL
        self.vx += ax*dt
        self.vx = max(-RUN_MAX, min(RUN_MAX, self.vx))
        if ax==0 and self.grounded:
            self.vx *= FRICTION

        # jump buffering + coyote
        if (keys[pygame.K_z] or keys[pygame.K_SPACE] or keys[pygame.K_UP]):
            self.jump_buf = JBUF
        else:
            self.jump_buf = max(0.0, self.jump_buf - dt)
        if self.grounded: self.coyote = COYOTE
        else: self.coyote = max(0.0, self.coyote - dt)
        if self.jump_buf>0 and self.coyote>0:
            self.vy = -JUMP_V
            self.grounded=False
            self.jump_buf = 0
            self.coyote = 0

        self.move_and_collide(dt)

class Enemy(Actor):
    # Finite‑state: idle → patrol → (optional) chase
    IDLE, PATROL, CHASE = range(3)
    def __init__(self,x,y):
        super().__init__(x,y,12,12,C_ENEMY)
        self.state=self.PATROL
        self.dir=-1
        self.timer=0.0
    def update(self, player, dt):
        if self.state==self.IDLE:
            self.timer+=dt
            if self.timer>1.0: self.state=self.PATROL; self.timer=0
        elif self.state==self.PATROL:
            speed = 60
            # flip at edges or walls
            ahead_x = self.x + self.dir*8
            foot_y  = self.y + self.h/2 + 1
            tx = int(ahead_x//TW); ty = int(foot_y//TH)
            wall = is_solid(int((self.x+self.dir*8)//TW), int(self.y//TH))
            ledge= not is_solid(tx, ty)
            if wall or ledge: self.dir*=-1
            self.vx = self.dir*speed
        # optional chase if close
        if abs(player.x-self.x)<48 and abs(player.y-self.y)<24:
            self.state=self.CHASE
        if self.state==self.CHASE:
            self.vx = 80 if player.x>self.x else -80
            if abs(player.x-self.x)>96: self.state=self.PATROL
        self.move_and_collide(dt)

# ---------- Camera ----------
class Camera:
    def __init__(self):
        self.x=0; self.y=0
    def update(self, target, dt):
        # look‑ahead on X based on player velocity
        look = 0.25 * target.vx
        target_x = target.x + look
        self.x += (target_x - self.x - VW*TW/2)*min(10*dt,1)
        self.y += (target.y - self.y - VH*TH/2)*min(10*dt,1)
        # clamp to level bounds
        self.x = max(0, min(self.x, W*TW - VW*TW))
        self.y = max(0, min(self.y, H*TH - VH*TH))

# ---------- Draw ----------
def draw(screen, cam, player, enemies):
    screen.fill(C_BG)
    # tiles
    min_tx = int(cam.x//TW); max_tx = min(W-1, int((cam.x+VW*TW)//TW)+1)
    min_ty = int(cam.y//TH); max_ty = min(H-1, int((cam.y+VH*TH)//TH)+1)
    for ty in range(min_ty, max_ty+1):
        for tx in range(min_tx, max_tx+1):
            if is_solid(tx,ty):
                rx = tx*TW - cam.x; ry = ty*TH - cam.y
                pygame.draw.rect(screen, C_SOLID, (rx,ry,TW,TH))
    # enemies
    for e in enemies:
        rx, ry = e.x - e.w/2 - cam.x, e.y - e.h/2 - cam.y
        pygame.draw.rect(screen, e.color, (rx,ry,e.w,e.h))
    # player
    px, py = player.x - player.w/2 - cam.x, player.y - player.h/2 - cam.y
    pygame.draw.rect(screen, player.color, (px,py,player.w,player.h))

# ---------- Bootstrap ----------
def spawn_entities():
    p=None; enemies=[]
    for ty,row in enumerate(LEVEL):
        for tx,ch in enumerate(row):
            if ch=='E': enemies.append(Enemy(tx*TW+TW/2, ty*TH+TH/2))
    # player spawn at first walkable column
    p = Player(2*TW+TW/2, 4*TH+TH/2)
    return p,enemies

def main():
    win = pygame.display.set_mode((WIN_W, WIN_H))
    surf = pygame.Surface((VW*TW, VH*TH))
    clock=pygame.time.Clock()

    player,enemies = spawn_entities()
    cam = Camera()

    lag=0.0
    running=True
    while running:
        # --- events ---
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
        keys = pygame.key.get_pressed()

        # --- fixed update ---
        lag += min(0.25, clock.tick(FPS)/1000.0)
        steps=0
        while lag>=FIXED_DT and steps<MAX_STEPS:
            player.update(keys, FIXED_DT)
            for en in enemies: en.update(player, FIXED_DT)
            cam.update(player, FIXED_DT)
            lag -= FIXED_DT; steps+=1

        # --- draw ---
        draw(surf, cam, player, enemies)
        pygame.transform.scale(surf, (WIN_W,WIN_H), win)
        pygame.display.flip()

    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
