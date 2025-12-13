"""
PVZ REBOOTED — NIGHTLY #003 (FILES=OFF, 600x400 @60FPS)
Replanted-like tempo, original procedural art, sun economy, pea shots, basic zombie AI,
and a minimal seed bank — all in one file, zero external assets.

Controls:
- Left click = place plant   • Right click = shovel
- [1] = Pea (50 sun)         • [2] = Wallnut (75 sun)
"""
import sys, random, pygame
pygame.init()

# --- Config ---
W,H=600,400; FPS=60; TILE=50
ROWS, COLS = 5, 9
LANE_Y=[80+i*60 for i in range(ROWS)]
scr=pygame.display.set_mode((W,H))
clk=pygame.time.Clock()
font=pygame.font.SysFont(None,18)

# --- State ---
GRID=[[None for _ in range(COLS)] for _ in range(ROWS)]
SUN, SELECT=50, 'pea'
proj=[]; zombies=[]
spawn_t=0; wave=1
sun_tick=0

# --- Colors ---
COL_BG=(20,28,36)
COL_GRASS=(36,90,50)
COL_SUN=(255,220,80)

# --- Entities ---
class Plant:
    def __init__(self,r,c,kind):
        self.r,self.c,self.kind=r,c,kind
        self.x=c*TILE+TILE//2; self.y=LANE_Y[r]
        self.cool=0
        self.hp=12 if kind=='wallnut' else 6
    def update(self,dt):
        if self.kind=='pea':
            self.cool-=dt
            if self.cool<=0:
                proj.append([self.x+16,self.y,3.0,1])  # x, y, speed, dmg
                self.cool=36
    def draw(self):
        if self.kind=='pea':
            pygame.draw.rect(scr,(30,170,60),(self.x-18,self.y-18,36,36),border_radius=7)
            pygame.draw.circle(scr,(50,240,90),(self.x-6,self.y-6),4)
        else:
            pygame.draw.rect(scr,(120,90,50),(self.x-20,self.y-22,40,44),border_radius=9)

class Zombie:
    def __init__(self,r):
        self.r=r; self.x=W+20; self.y=LANE_Y[r]
        self.hp=18+wave*2
        self.v=0.25+0.02*wave
        self.bite=0
    def update(self,dt):
        c=int((self.x)//TILE); r=self.r
        target=GRID[r][c] if 0<=c<COLS else None
        if target and abs(target.y-self.y)<10 and target.hp>0 and self.x>target.x:
            self.bite-=dt
            if self.bite<=0:
                target.hp-=1; self.bite=18
        else:
            self.x-=self.v*dt
    def draw(self):
        pygame.draw.rect(scr,(160,120,80),(self.x-18,self.y-22,36,44),0,8)
        pygame.draw.rect(scr,(90,50,35),(self.x-18,self.y-8,36,8))
        # hp bar
        maxhp=18+wave*2
        w=max(0,32*self.hp/maxhp)
        pygame.draw.rect(scr,(200,40,40),(self.x-16,self.y-30,w,4))

# --- Helpers ---
def place(r,c,kind):
    global SUN
    cost=50 if kind=='pea' else 75
    if 0<=r<ROWS and 0<=c<COLS and GRID[r][c] is None and SUN>=cost:
        GRID[r][c]=Plant(r,c,kind); SUN-=cost
def shovel(r,c):
    if 0<=r<ROWS and 0<=c<COLS: GRID[r][c]=None

# --- Loop ---
running=True
while running:
    dt=clk.tick(FPS); spawn_t+=dt; sun_tick+=dt
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_1: SELECT='pea'
            if e.key==pygame.K_2: SELECT='wallnut'
        if e.type==pygame.MOUSEBUTTONDOWN:
            mx,my=e.pos; c=mx//TILE
            r=min(range(ROWS), key=lambda i:abs(LANE_Y[i]-my))
            if e.button==1: place(r,c,SELECT)
            if e.button==3: shovel(r,c)

    # Passive sun income
    if sun_tick>1000:
        SUN+=25; sun_tick=0

    # Spawn zombies by wave tempo
    if spawn_t>max(800,2400-200*wave):
        zombies.append(Zombie(random.randrange(ROWS))); spawn_t=0

    # Update plants
    for r in range(ROWS):
        for c in range(COLS):
            p=GRID[r][c]
            if p:
                p.update(dt)
                if p.hp<=0: GRID[r][c]=None

    # Update zombies
    for z in zombies: z.update(dt)

    # Projectiles
    for b in proj:
        b[0]+=b[2]*dt
        for z in zombies:
            if abs(z.y-b[1])<12 and -10<(z.x-b[0])<10:
                z.hp-=b[3]; b[0]=W+999
    proj=[b for b in proj if b[0]<W+40]
    zombies=[z for z in zombies if z.hp>0 and z.x>-20]

    # Draw
    scr.fill(COL_BG)
    pygame.draw.rect(scr,COL_GRASS,(0,60,W,H-60))
    for i in range(ROWS):
        pygame.draw.line(scr,(40,110,68),(0,LANE_Y[i]),(W,LANE_Y[i]),1)

    for r in range(ROWS):
        for c in range(COLS):
            x=c*TILE+TILE//2; y=LANE_Y[r]
            pygame.draw.rect(scr,(30,70,45),(c*TILE, y-25, TILE, 50),1)
            p=GRID[r][c]
            if p: p.draw()

    for b in proj: pygame.draw.circle(scr,(80,240,120),(int(b[0]),int(b[1])),4)
    for z in zombies: z.draw()

    # HUD
    pygame.draw.rect(scr,(18,20,24),(0,0,W,60))
    pygame.draw.circle(scr,COL_SUN,(26,30),12)
    scr.blit(font.render(f"Sun: {SUN}",True,(255,255,200)),(44,22))
    scr.blit(font.render(f"Seed [1]=Pea(50)  [2]=Wallnut(75)  Selected: {SELECT}",True,(200,220,255)),(140,10))
    scr.blit(font.render("Nightly #003 — Procedural-only, Rebooted tempo",True,(140,170,255)),(140,32))
    pygame.display.flip()

pygame.quit()
