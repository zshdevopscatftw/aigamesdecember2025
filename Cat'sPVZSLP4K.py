# pvz_zzz.py — one-file, files=off, 600x400, 60 FPS, "zzz/rebooted" theme
import pygame, random, math, sys
pygame.init()
W,H=600,400; screen=pygame.display.set_mode((W,H)); pygame.display.set_caption("PVZ zzz/rebooted")
CLK=pygame.time.Clock(); FPS=60
FONT=pygame.font.SysFont("consolas",16)

# Grid: 9x5 lanes; calm, sleepy palette
COLS,ROWS=9,5; CELL_W=60; CELL_H=H//ROWS  # 60x80
GRID_OX=(W-COLS*CELL_W)//2; GRID_OY=0

# Colors
BG=(14,16,24); LAWN=(18,26,34); LANE1=(20,30,40); LANE2=(22,34,46)
PLANT=(120,200,255); PEA=(160,255,160); ZMB=(200,160,160); TXT=(220,230,240)
SNOOZE=(120,130,180)

class Pea:
    def __init__(self,x,y):
        self.x=x; self.y=y; self.v=180.0  # px/s
        self.r=5
    def update(self,dt):
        self.x+=self.v*dt
    def draw(self,surf):
        pygame.draw.circle(surf,PEA,(int(self.x),int(self.y)),self.r)
    def rect(self):
        return pygame.Rect(self.x-self.r,self.y-self.r,self.r*2,self.r*2)

class Plant:
    COST=25
    def __init__(self,c,r):
        self.c=c; self.r=r
        self.x=GRID_OX+c*CELL_W+CELL_W//2
        self.y=GRID_OY+r*CELL_H+CELL_H//2
        self.cool=0.0
        self.rate=1.4  # shoot every ~1.4s (dreamy pace)
    def update(self,dt,peas):
        self.cool-=dt
        if self.cool<=0:
            peas.append(Pea(self.x+12,self.y-6))
            self.cool=self.rate
    def draw(self,surf):
        pygame.draw.rect(surf,PLANT,pygame.Rect(self.x-12,self.y-18,24,36),0,border_radius=6)
        pygame.draw.circle(surf,SNOOZE,(self.x-2,self.y-26),4)

class Zombie:
    def __init__(self,row):
        self.row=row
        self.x=W+random.randint(0,80)
        self.y=GRID_OY+row*CELL_H+CELL_H//2
        self.hp=3
        base=12
        self.v=base+random.random()*6  # px/s; deliberately slow, sleepy
    def update(self,dt):
        self.x-=self.v*dt
    def draw(self,surf):
        pygame.draw.rect(surf,ZMB,pygame.Rect(self.x-14,self.y-22,28,44),0,border_radius=5)
    def rect(self):
        return pygame.Rect(self.x-14,self.y-22,28,44)

# State
plants=[[None for _ in range(COLS)] for _ in range(ROWS)]
peas=[]; zombs=[]
sun=75  # starting resource
spawn_t=0.0; spawn_rate=3.8  # seconds between spawns; can tighten nightly
wave=1; time_acc=0.0

running=True
while running:
    dt=CLK.tick(FPS)/1000.0
    for e in pygame.event.get():
        if e.type==pygame.QUIT:
            running=False
        elif e.type==pygame.MOUSEBUTTONDOWN:
            mx,my=e.pos
            if GRID_OX<=mx<GRID_OX+COLS*CELL_W and GRID_OY<=my<GRID_OY+ROWS*CELL_H:
                c=(mx-GRID_OX)//CELL_W; r=(my-GRID_OY)//CELL_H
                if e.button==1:  # place plant
                    if not plants[r][c] and sun>=Plant.COST:
                        plants[r][c]=Plant(c,r); sun-=Plant.COST
                elif e.button==3:  # remove
                    if plants[r][c]:
                        plants[r][c]=None; sun+=Plant.COST//2
        elif e.type==pygame.KEYDOWN:
            if e.key==pygame.K_r:
                # reboot vibe: wipe peas/zombs, soft refund 10 sun
                peas.clear(); zombs.clear(); sun+=10

    # Economy: sleepy drizzle of sun
    time_acc+=dt
    if time_acc>=5.0:
        sun+=15; time_acc=0.0

    # Spawn logic
    spawn_t+=dt
    if spawn_t>=spawn_rate:
        spawn_t=0.0
        zombs.append(Zombie(random.randrange(ROWS)))
        # ramp pressure slightly over time
        spawn_rate=max(1.8, spawn_rate-0.05)
        wave+=1

    # Update
    for r in range(ROWS):
        for c in range(COLS):
            p=plants[r][c]
            if p: p.update(dt,peas)
    for pea in peas: pea.update(dt)
    for zb in zombs: zb.update(dt)

    # Collisions
    for zb in zombs:
        zr=zb.rect()
        for pea in peas[:]:
            if zr.colliderect(pea.rect()):
                peas.remove(pea); zb.hp-=1
                if zb.hp<=0: break
    zombs=[z for z in zombs if z.hp>0 and z.x>-30]
    peas=[p for p in peas if p.x<W+30]

    # Lose condition (zombie reaches left)
    for zb in zombs:
        if zb.x<GRID_OX-10:
            # soft reset into dream again
            plants=[[None for _ in range(COLS)] for _ in range(ROWS)]
            peas.clear(); zombs.clear(); spawn_rate=3.8; wave=1; sun=max(50,sun)
            break

    # Draw
    screen.fill(BG)
    # lawn lanes
    for r in range(ROWS):
        lane_c = LANE1 if r%2==0 else LANE2
        pygame.draw.rect(screen,lane_c,(GRID_OX,GRID_OY+r*CELL_H,COLS*CELL_W,CELL_H))
    # grid lines
    for c in range(COLS+1):
        x=GRID_OX+c*CELL_W
        pygame.draw.line(screen,LAWN,(x,0),(x,H),1)
    # entities
    for r in range(ROWS):
        for c in range(COLS):
            if plants[r][c]: plants[r][c].draw(screen)
    for pea in peas: pea.draw(screen)
    for zb in zombs: zb.draw(screen)

    hud=f"sun:{sun}  wave:{wave}  LMB=plant({Plant.COST}) RMB=remove  R=reboot"
    screen.blit(FONT.render(hud,True,TXT),(8,8))
    pygame.display.flip()

pygame.quit(); sys.exit()
