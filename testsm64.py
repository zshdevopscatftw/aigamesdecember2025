#!/usr/bin/env python3
"""
Ultra Mario 3D Bros — Mario Head Test + 1-1-ish Course (Pygame-CE)
No assets. No shaders. Just math.

Controls:
A/D rotate | W/S forward/back | Q/E strafe | Shift run | Space jump | Ctrl ground pound | R reset
"""

import math
from dataclasses import dataclass

import pygame

pygame.init()
W, H = 960, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Ultra Mario 3D Bros — Head Test (1-1-ish)")
clock = pygame.time.Clock()

FPS = 60
FOV = 420
NEAR = 12

GRAVITY = 0.55
FRICTION = 0.86
RUN_ACCEL = 0.18
WALK_ACCEL = 0.10
JUMP = 12.5
POUND = -32
TERM = 22

MARIO_R = 14     # collision radius
MARIO_H = 56     # collision height (feet -> head)

SKY = (100, 149, 237)
GRASS = (95, 195, 95)
DIRT = (130, 85, 45)
BRICK = (180, 60, 60)
STONE = (130, 130, 130)
PIPE = (40, 170, 70)
PIPE_D = (25, 120, 50)

RED = (220, 30, 20)
SKIN = (255, 200, 160)
BROWN = (120, 70, 35)
YELLOW = (255, 215, 0)
BLACK = (15, 15, 15)
WHITE = (235, 240, 255)

def clamp(v,a,b): return a if v<a else b if v>b else v
def dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(v):
    l = math.sqrt(dot(v,v)) or 1.0
    return (v[0]/l,v[1]/l,v[2]/l)
def shade(col, k):
    k = clamp(k, 0.0, 1.15)
    return (int(clamp(col[0]*k,0,255)), int(clamp(col[1]*k,0,255)), int(clamp(col[2]*k,0,255)))

@dataclass
class P3:
    x: float
    y: float
    z: float

@dataclass
class Cam:
    x: float
    y: float
    z: float
    yaw: float  # looks along +Z

def w2c(wx, wy, wz, cam: Cam):
    rx, ry, rz = wx-cam.x, wy-cam.y, wz-cam.z
    ca, sa = math.cos(-cam.yaw), math.sin(-cam.yaw)
    return (rx*ca - rz*sa, ry, rx*sa + rz*ca)

def proj(cx, cy, cz):
    if cz < NEAR: return None
    s = FOV / cz
    return (cx*s + W/2, -cy*s + H/2, cz, s)

class Platform:
    def __init__(self, x,y,z,w,h,d,col):
        self.x,self.y,self.z = x,y,z
        self.w,self.h,self.d = w,h,d
        self.col = col
    def corners(self):
        hw,hh,hd = self.w/2, self.h, self.d/2
        x,y,z = self.x,self.y,self.z
        return [
            (x-hw,y,z-hd),(x+hw,y,z-hd),(x+hw,y,z+hd),(x-hw,y,z+hd),
            (x-hw,y+hh,z-hd),(x+hw,y+hh,z-hd),(x+hw,y+hh,z+hd),(x-hw,y+hh,z+hd),
        ]

class Star:
    def __init__(self, x,y,z):
        self.p = P3(x,y,z)
        self.a = 0.0
        self.collected = False
    def update(self): self.a += 0.06
    def hit(self, mario_pos: P3):
        if self.collected: return False
        dx = mario_pos.x - self.p.x
        dy = (mario_pos.y+30) - self.p.y
        dz = mario_pos.z - self.p.z
        if math.sqrt(dx*dx+dy*dy+dz*dz) < 34:
            self.collected = True
            return True
        return False

class Mario:
    def __init__(self):
        self.p = P3(-220, 140, 140)
        self.v = P3(0,0,0)
        self.a = 0.0
        self.ground = False

    def _resolve_walls(self, plats):
        """Cheap AABB wall collisions in XZ (so pipes/bricks feel solid)."""
        feet = self.p.y
        head = self.p.y + MARIO_H
        for pl in plats:
            # vertical overlap with the platform's volume
            if head <= pl.y or feet >= pl.y + pl.h:
                continue

            dx = self.p.x - pl.x
            dz = self.p.z - pl.z
            px = (pl.w/2 + MARIO_R) - abs(dx)
            pz = (pl.d/2 + MARIO_R) - abs(dz)

            if px > 0 and pz > 0:
                # Don't push when standing on top (feet essentially at top)
                if feet >= (pl.y + pl.h - 1):
                    continue
                # Push out along the shallowest penetration axis
                if px < pz:
                    self.p.x += px if dx > 0 else -px
                    self.v.x = 0
                else:
                    self.p.z += pz if dz > 0 else -pz
                    self.v.z = 0

    def update(self, keys, plats):
        acc = RUN_ACCEL if keys[pygame.K_LSHIFT] else WALK_ACCEL
        if keys[pygame.K_a]: self.a += 0.06
        if keys[pygame.K_d]: self.a -= 0.06

        fwd = (-math.sin(self.a), -math.cos(self.a))
        rgt = ( math.cos(self.a), -math.sin(self.a))

        moving = False
        if keys[pygame.K_w]:
            self.v.x += fwd[0]*acc*10; self.v.z += fwd[1]*acc*10; moving=True
        if keys[pygame.K_s]:
            self.v.x -= fwd[0]*acc*7;  self.v.z -= fwd[1]*acc*7;  moving=True
        if keys[pygame.K_q]:
            self.v.x -= rgt[0]*acc*6;  self.v.z -= rgt[1]*acc*6;  moving=True
        if keys[pygame.K_e]:
            self.v.x += rgt[0]*acc*6;  self.v.z += rgt[1]*acc*6;  moving=True

        if not moving:
            self.v.x *= FRICTION; self.v.z *= FRICTION

        if keys[pygame.K_SPACE] and self.ground:
            self.v.y = JUMP; self.ground = False
        if keys[pygame.K_LCTRL] and not self.ground and self.v.y > -TERM:
            self.v.y = POUND

        self.v.y -= GRAVITY
        self.v.y = max(-TERM, self.v.y)

        # integrate
        self.p.x += self.v.x; self.p.y += self.v.y; self.p.z += self.v.z

        # floor collision (land on top)
        self.ground = False
        for pl in plats:
            if (pl.x - pl.w/2 < self.p.x < pl.x + pl.w/2 and
                pl.z - pl.d/2 < self.p.z < pl.z + pl.d/2):
                top = pl.y + pl.h
                if self.p.y <= top and self.v.y <= 0:
                    self.p.y = top
                    self.v.y = 0
                    self.ground = True

        # wall collision (XZ push-out)
        self._resolve_walls(plats)

        if self.p.y < -240:
            self.__init__()

# ─── low-poly unit sphere mesh ───
def unit_sphere(rings=7, seg=10):
    rings = max(3, rings); seg = max(3, seg)
    V, F = [(0,-1,0)], []
    for i in range(1, rings):
        lat = -math.pi/2 + math.pi*i/rings
        y = math.sin(lat); r = math.cos(lat)
        for j in range(seg):
            lon = 2*math.pi*j/seg
            V.append((math.cos(lon)*r, y, math.sin(lon)*r))
    top = len(V); V.append((0,1,0))
    def rid(i,j): return 1 + (i-1)*seg + (j%seg)
    for j in range(seg): F.append((0, rid(1,j), rid(1,j+1)))
    for i in range(1, rings-1):
        for j in range(seg):
            F.append((rid(i,j), rid(i,j+1), rid(i+1,j+1), rid(i+1,j)))
    for j in range(seg): F.append((top, rid(rings-1,j+1), rid(rings-1,j)))
    return V, F

SPV, SPF = unit_sphere()
LIGHT = norm((-0.25, 0.85, -0.55))

def add_poly(draw, pts, z, col, outline=True):
    draw.append((z, "poly", pts, col, outline))

def add_circle(draw, sx, sy, z, r, col):
    draw.append((z, "circ", (sx,sy,r), col, False))

def box_faces(draw, corners, cam, base_col, bottom=False):
    faces = []
    if bottom: faces.append((0,1,2,3))
    faces += [(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)]
    for f in faces:
        cv = [w2c(*corners[i], cam) for i in f]
        if any(v[2] < NEAR for v in cv): continue
        n = cross(sub(cv[1],cv[0]), sub(cv[2],cv[0]))
        c = (sum(v[0] for v in cv)/len(cv), sum(v[1] for v in cv)/len(cv), sum(v[2] for v in cv)/len(cv))
        if dot(n, c) >= 0:  # backface
            continue
        k = clamp(dot(norm(n), LIGHT)*0.85 + 0.25, 0.25, 1.05)
        col = shade(base_col, k)
        pts=[]; zsum=0.0; ok=True
        for x,y,z in cv:
            pr = proj(x,y,z)
            if not pr: ok=False; break
            pts.append((pr[0],pr[1])); zsum += z
        if ok and len(pts)>=3:
            add_poly(draw, pts, zsum/len(pts), col)

def oriented_box(draw, center, w,h,d, yaw, col, cam):
    cx,cy,cz = center
    hw,hd = w/2, d/2
    local = [(-hw,0,-hd),(hw,0,-hd),(hw,0,hd),(-hw,0,hd),(-hw,h,-hd),(hw,h,-hd),(hw,h,hd),(-hw,h,hd)]
    ca,sa = math.cos(yaw), math.sin(yaw)
    world=[]
    for lx,ly,lz in local:
        rx = lx*ca - lz*sa
        rz = lx*sa + lz*ca
        world.append((cx+rx, cy+ly, cz+rz))
    box_faces(draw, world, cam, col)

def sphere(draw, center_w, r, col, cam, top_only=False):
    cxw,cyw,czw = center_w
    center_c = w2c(cxw,cyw,czw,cam)
    cv=[w2c(cxw+vx*r, cyw+vy*r, czw+vz*r, cam) for vx,vy,vz in SPV]
    for f in SPF:
        fv=[cv[i] for i in f]
        if any(v[2] < NEAR for v in fv): continue
        if top_only and (sum(v[1] for v in fv)/len(fv)) < center_c[1]:
            continue
        n = cross(sub(fv[1],fv[0]), sub(fv[2],fv[0]))
        fc = (sum(v[0] for v in fv)/len(fv), sum(v[1] for v in fv)/len(fv), sum(v[2] for v in fv)/len(fv))
        outward = sub(fc, center_c)
        if dot(n, outward) < 0: n = (-n[0],-n[1],-n[2])
        if dot(n, fc) >= 0: continue
        k = clamp(dot(norm(n), LIGHT)*0.9 + 0.22, 0.22, 1.08)
        scol = shade(col, k)
        pts=[]; zsum=0.0; ok=True
        for x,y,z in fv:
            pr=proj(x,y,z)
            if not pr: ok=False; break
            pts.append((pr[0],pr[1])); zsum+=z
        if ok and len(pts)>=3:
            add_poly(draw, pts, zsum/len(pts), scol)

def mario_head(draw, m: Mario, cam: Cam):
    fwd = (-math.sin(m.a), -math.cos(m.a))
    rgt = ( math.cos(m.a), -math.sin(m.a))
    hc = (m.p.x, m.p.y+36, m.p.z)
    sphere(draw, hc, 18, SKIN, cam)                         # head
    sphere(draw, (hc[0],hc[1]+5,hc[2]), 19, RED, cam, True) # cap top
    brim = (hc[0]+fwd[0]*14, hc[1]+8, hc[2]+fwd[1]*14)
    oriented_box(draw, brim, 20, 3.2, 10, m.a, RED, cam)    # brim
    nose = (hc[0]+fwd[0]*18, hc[1]-1, hc[2]+fwd[1]*18)
    sphere(draw, nose, 6.2, SKIN, cam)
    st = (hc[0]+fwd[0]*13, hc[1]-6, hc[2]+fwd[1]*13)
    sphere(draw, (st[0]+rgt[0]*4.5, st[1], st[2]+rgt[1]*4.5), 3.3, BROWN, cam)
    sphere(draw, (st[0]-rgt[0]*4.5, st[1], st[2]-rgt[1]*4.5), 3.3, BROWN, cam)
    # eyes as billboard circles (readable)
    eb = (hc[0]+fwd[0]*14, hc[1]+3.5, hc[2]+fwd[1]*14)
    for sgn in (-1,1):
        ex = eb[0] + rgt[0]*5.3*sgn
        ey = eb[1]
        ez = eb[2] + rgt[1]*5.3*sgn
        pr = proj(*w2c(ex,ey,ez,cam))
        if pr:
            rpx = int(clamp(2.5*pr[3]*1.6, 2, 10))
            add_circle(draw, pr[0], pr[1], pr[2]-0.01, rpx, BLACK)

def build_level():
    plats=[]
    gy=0; gh=40
    # ground segments (with gaps)
    plats += [Platform(0,gy,-250,720,gh,1100,GRASS), Platform(0,gy-40,-250,720,40,1100,DIRT)]
    plats += [Platform(0,gy,-1350,720,gh,900,GRASS), Platform(0,gy-40,-1350,720,40,900,DIRT)]
    plats += [Platform(0,gy,-2450,720,gh,1200,GRASS), Platform(0,gy-40,-2450,720,40,1200,DIRT)]
    # bricks row
    by=90
    for x in (-120,-60,0,60,120):
        plats.append(Platform(x,by,-220,44,20,44,BRICK))
    # small stair of bricks
    for i in range(4):
        plats.append(Platform(-220+i*55, by+i*25, -520, 50, 20, 50, BRICK))
    # pipe (now actually blocks you)
    plats += [Platform(180,gy,-640,64,80,64,PIPE), Platform(180,gy+80,-640,86,22,86,PIPE_D)]
    # gap helpers
    plats += [Platform(-140,by+30,-900,140,20,140,STONE), Platform(140,by+55,-980,140,20,140,STONE)]
    plats += [Platform(0,by+40,-1900,220,20,220,STONE)]
    # end staircase along Z
    step_w, step_d, step_h = 300, 90, 22
    start_z = -2680
    for i in range(7):
        base_y = gy + gh + i*step_h
        plats.append(Platform(0, base_y, start_z - i*step_d, step_w, step_h, step_d, STONE))
    # flag pole-ish + topper
    pole_y = gy+gh
    plats += [Platform(260,pole_y,-3000,18,260,18,STONE), Platform(260,pole_y+260,-3000,40,14,40,WHITE)]
    star = Star(0, pole_y + 7*step_h + 60, -3000)
    return plats, star

m = Mario()
plats, star = build_level()
font = pygame.font.SysFont("Arial", 22)
small = pygame.font.SysFont("Arial", 16)
stars = 0

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        m = Mario(); plats, star = build_level(); stars = 0

    m.update(keys, plats)
    star.update()
    if star.hit(m.p): stars += 1

    cam = Cam(
        m.p.x + math.sin(m.a)*320,
        m.p.y + 160,
        m.p.z + math.cos(m.a)*320,
        m.a + math.pi,  # IMPORTANT: look along mario forward (-sin,-cos)
    )

    screen.fill(SKY)
    for (x,y,r) in [(140,90,28),(170,80,34),(205,92,26),(820,110,26),(850,100,32),(885,112,24)]:
        pygame.draw.circle(screen, WHITE, (x,y), r)

    draw=[]
    for pl in plats:
        box_faces(draw, pl.corners(), cam, pl.col)

    if not star.collected:
        sx,sy,sz = star.p.x, star.p.y + 18*math.sin(star.a), star.p.z
        pr = proj(*w2c(sx,sy,sz,cam))
        if pr:
            rpx = int(clamp(14*pr[3], 3, 30))
            add_circle(draw, pr[0], pr[1], pr[2], rpx, YELLOW)

    mario_head(draw, m, cam)

    draw.sort(key=lambda it: it[0], reverse=True)
    for _,kind,payload,col,outline in draw:
        if kind=="poly":
            pygame.draw.polygon(screen, col, payload)
            if outline: pygame.draw.polygon(screen, (0,0,0), payload, 1)
        else:
            sx,sy,r = payload
            pygame.draw.circle(screen, col, (int(sx),int(sy)), int(r))

    screen.blit(font.render(f"STARS: {stars}   (1-1-ish test course)", True, (255,255,0)), (18,16))
    screen.blit(small.render("A/D rotate  W/S move  Q/E strafe  Shift run  Space jump  Ctrl pound  R reset", True, (10,10,10)), (18, H-26))
    if stars>=1:
        msg = font.render("COURSE CLEAR! (R to reset)", True, (255,255,255))
        screen.blit(msg, (W//2 - msg.get_width()//2, 52))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
