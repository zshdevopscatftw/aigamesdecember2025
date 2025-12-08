import pygame, sys, random, math, array, copy
from pygame.locals import *

pygame.init()
pygame.mixer.quit()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)

# ================================================================
# SCREEN + CONSTANTS
# ================================================================
SW, SH = 480, 640
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("ULTRA!TETRIS GB+ (AC EDITION)")

FPS = 60
BLOCK = 24
FW, FH = 10, 20
FX, FY = 60, 40

GB = [(155,188,15),(139,172,15),(48,98,48),(15,56,15)]
BG, GR, BL, BR = GB

# ================================================================
# FONT
# ================================================================
font_big = pygame.font.SysFont("consolas", 48, bold=True)
font_med = pygame.font.SysFont("consolas", 28, bold=True)
font_sml = pygame.font.SysFont("consolas", 20)

# ================================================================
# SIMPLE HYBRID DMG AUDIO ENGINE
# (Pulse lead + pulse harmony + noise percussion)
# ================================================================
sr = 44100
def sq(freq, dur, vol=0.3, duty=0.5):
    if freq <= 0:
        return array.array('h', [0]*int(sr*dur))
    N = int(sr*dur)
    p = max(int(sr/freq),1)
    wave=[]
    for i in range(N):
        env = 1.0
        if i<50: env = i/50
        elif i>N-50: env = (N-i)/50
        v = 1 if (i%p) < p*duty else -1
        wave.append(int(v*32767*vol*env))
    return array.array('h', wave)

def noise(dur, vol=0.2):
    N = int(sr*dur)
    s=1
    out=[]
    for _ in range(N):
        bit = (s ^ (s >> 1)) & 1
        s = (s>>1) | (bit<<14)
        out.append(int((1 if bit else -1)*vol*30000))
    return array.array('h', out)

def mix(a,b):
    L=max(len(a),len(b))
    o=array.array('h',[0]*L)
    for i in range(L):
        v=0
        if i<len(a): v+=a[i]
        if i<len(b): v+=b[i]
        o[i]=max(-32767,min(32767,v))
    return o

# ========== Build music themes ==========
def build_melody(seq):
    out=array.array('h')
    for note,d in seq:
        if note=="R":
            out.extend([0]*int(sr*d))
        elif note=="N":
            out.extend(noise(d,0.25))
        else:
            out.extend(sq(NOTES[note], d, 0.22, 0.25))
    return pygame.mixer.Sound(buffer=out)

NOTES={
"E5":659,"D5":587,"C5":523,"B4":494,"A4":440,
"G4":392,"F4":349,"E4":330,"A5":880
}

def dur(q): return 60/150*q  # Nintendo DS BPM (~150)

# Shortened melodies to fit output size
melA=[("E5",dur(1.5)),("B4",dur(0.5)),("C5",dur(0.5)),("D5",dur(1)),
      ("C5",dur(0.5)),("B4",dur(0.5)),("A4",dur(1)),("R",dur(0.5)),
      ("C5",dur(0.5)),("E5",dur(1.5)),("D5",dur(0.5)),("C5",dur(0.5)),
      ("B4",dur(1.5)),("C5",dur(0.5)),("D5",dur(1)),("E5",dur(1))]

def freq(n): return NOTES[n]

# ================================================================
# SFX
# ================================================================
move_snd=sq(300,0.05,0.2)
move_snd=pygame.mixer.Sound(buffer=move_snd)
rot_snd=pygame.mixer.Sound(buffer=sq(450,0.05,0.2))
drop_snd=pygame.mixer.Sound(buffer=noise(0.15,0.3))
tetris_snd=pygame.mixer.Sound(buffer=sq(1200,0.25,0.35))
hold_snd=pygame.mixer.Sound(buffer=sq(200,0.1,0.25))

musicA = build_melody(melA)

# ================================================================
# TETROMINOES + SRS ROTATION
# ================================================================
TETS = {
"I":[[1,1,1,1]],
"O":[[1,1],[1,1]],
"T":[[0,1,0],[1,1,1]],
"S":[[0,1,1],[1,1,0]],
"Z":[[1,1,0],[0,1,1]],
"J":[[1,0,0],[1,1,1]],
"L":[[0,0,1],[1,1,1]]
}

def rotate(mat):
    return [list(r) for r in zip(*mat[::-1])]

# ================================================================
# GAME CLASS
# ================================================================
class Game:
    def __init__(self):
        self.state="menu"
        self.field=[[0]*FW for _ in range(FH)]
        self.bag=[]
        self.current=None
        self.next=None
        self.hold=None
        self.can_hold=True
        self.ghost=True
        self.score=0
        self.level=0
        self.lines=0
        self.music_ch=pygame.mixer.Channel(0)
        self.lockdelay=30
        self.ldc=0
        self.drop_counter=0
        self.gravity=53

    def newbag(self):
        self.bag=list(TETS.keys())
        random.shuffle(self.bag)

    def pick(self):
        if not self.bag: self.newbag()
        t = self.bag.pop()
        shape = [row[:] for row in TETS[t]]
        w=len(shape[0])
        return {"shape":shape,"x":FW//2-w//2,"y":0,"t":t}

    def spawn(self):
        if not self.next: self.next=self.pick()
        self.current=self.next
        self.next=self.pick()
        if self.collide(self.current,0,0):
            self.state="gameover"

    def collide(self,p,dx,dy,shape=None):
        shp = shape if shape else p["shape"]
        for r,row in enumerate(shp):
            for c,v in enumerate(row):
                if v:
                    nx=p["x"]+c+dx
                    ny=p["y"]+r+dy
                    if nx<0 or nx>=FW or ny>=FH: return True
                    if ny>=0 and self.field[ny][nx]: return True
        return False

    def lock(self):
        p=self.current
        for r,row in enumerate(p["shape"]):
            for c,v in enumerate(row):
                if v:
                    self.field[p["y"]+r][p["x"]+c]=1
        self.clear()
        self.spawn()
        self.can_hold=True

    def clear(self):
        new=[]
        cleared=0
        for row in self.field:
            if all(row): cleared+=1
            else: new.append(row)
        for _ in range(cleared):
            new.insert(0,[0]*FW)
        self.field=new
        if cleared>=4: tetris_snd.play()

    def hold_piece(self):
        if not self.can_hold: return
        hold_snd.play()
        if self.hold:
            self.hold, self.current = self.current, self.hold
            self.current["x"]=FW//2-len(self.current["shape"][0])//2
            self.current["y"]=0
        else:
            self.hold=self.current
            self.current=self.next
            self.next=self.pick()
        self.can_hold=False

    def update(self):
        if self.state!="play": return
        self.drop_counter+=1
        if self.drop_counter>=self.gravity:
            self.drop_counter=0
            if not self.collide(self.current,0,1):
                self.current["y"]+=1
            else:
                self.ldc+=1
                if self.ldc>=self.lockdelay:
                    self.lock()
                    self.ldc=0

    def draw_block(self,x,y,col):
        pygame.draw.rect(screen,col,(x,y,BLOCK,BLOCK))
        pygame.draw.rect(screen,BR,(x,y,BLOCK,BLOCK),1)

    def draw_field(self):
        for y in range(FH):
            for x in range(FW):
                if self.field[y][x]:
                    self.draw_block(FX+x*BLOCK,FY+y*BLOCK,BL)
                else:
                    pygame.draw.rect(screen,GR,(FX+x*BLOCK,FY+y*BLOCK,BLOCK,BLOCK),1)

    def draw_piece(self,p,ghost=False):
        col = (80,120,80) if ghost else BL
        for r,row in enumerate(p["shape"]):
            for c,v in enumerate(row):
                if v:
                    self.draw_block(FX+(p["x"]+c)*BLOCK, FY+(p["y"]+r)*BLOCK, col)

    def get_ghost(self):
        g=copy.deepcopy(self.current)
        while not self.collide(g,0,1):
            g["y"]+=1
        return g

    def draw_ui(self):
        scr=font_sml.render(f"SCORE: {self.score}",True,BR)
        screen.blit(scr,(300,60))
        nxt=font_sml.render("NEXT:",True,BR)
        screen.blit(nxt,(300,120))
        hld=font_sml.render("HOLD:",True,BR)
        screen.blit(hld,(300,260))

        # draw next
        p=self.next
        for r,row in enumerate(p["shape"]):
            for c,v in enumerate(row):
                if v: self.draw_block(320+c*16,150+r*16,(60,100,60))

        # draw hold
        if self.hold:
            p=self.hold
            for r,row in enumerate(p["shape"]):
                for c,v in enumerate(row):
                    if v: self.draw_block(320+c*16,300+r*16,(100,60,60))

    def draw(self):
        screen.fill(BG)
        self.draw_field()
        if self.ghost:
            g=self.get_ghost()
            self.draw_piece(g,True)
        self.draw_piece(self.current)
        self.draw_ui()

# ================================================================
# MAIN LOOP
# ================================================================
game=Game()
clock=pygame.time.Clock()

def start_game():
    game.field=[[0]*FW for _ in range(FH)]
    game.score=0
    game.lines=0
    game.hold=None
    game.can_hold=True
    game.ldc=0
    game.drop_counter=0
    game.gravity=53
    game.state="play"
    game.next=None
    game.spawn()
    game.music_ch.play(musicA, loops=-1)

running=True
while running:
    for e in pygame.event.get():
        if e.type==QUIT: running=False
        if e.type==KEYDOWN:
            if game.state=="menu":
                if e.key==K_1:
                    start_game()
                elif e.key==K_2:
                    game.state="howto"
                elif e.key==K_3:
                    game.state="credits"
                elif e.key==K_4:
                    running=False
            elif game.state in ["howto", "credits"]:
                if e.key==K_RETURN:
                    game.state="menu"
            elif game.state=="play":
                if e.key==K_LEFT:
                    if not game.collide(game.current,-1,0):
                        game.current["x"]-=1
                        pygame.mixer.Sound.play(move_snd)
                elif e.key==K_RIGHT:
                    if not game.collide(game.current,1,0):
                        game.current["x"]+=1
                        pygame.mixer.Sound.play(move_snd)
                elif e.key==K_UP:
                    shp=rotate(game.current["shape"])
                    if not game.collide(game.current,0,0,shp):
                        game.current["shape"]=shp
                        pygame.mixer.Sound.play(rot_snd)
                elif e.key==K_DOWN:
                    if not game.collide(game.current,0,1):
                        game.current["y"]+=1
                elif e.key==K_SPACE: # Hard drop
                    while not game.collide(game.current,0,1):
                        game.current["y"]+=1
                    pygame.mixer.Sound.play(drop_snd)
                    game.lock()
                elif e.key==K_c: # Hold
                    game.hold_piece()
                elif e.key==K_ESCAPE:
                    game.state="menu"
                    game.music_ch.stop()
            elif game.state=="gameover":
                if e.key==K_RETURN:
                    game.state="menu"

    if game.state=="menu":
        screen.fill(BG)
        title=font_big.render("ULTRA!TETRIS",True,BR)
        screen.blit(title,(SW//2-title.get_width()//2,100))
        options = [
            "1. Start Game",
            "2. How to Play",
            "3. Credits",
            "4. Exit"
        ]
        for i, opt in enumerate(options):
            text=font_med.render(opt,True,BR)
            screen.blit(text,(SW//2-text.get_width()//2,200 + i*40))
        pygame.display.flip()
        clock.tick(FPS)
        continue
    elif game.state=="howto":
        screen.fill(BG)
        htitle=font_med.render("How to Play",True,BR)
        screen.blit(htitle,(SW//2-htitle.get_width()//2,100))
        instructions = [
            "Arrow Keys: Move left/right, rotate (up), soft drop (down)",
            "SPACE: Hard drop",
            "C: Hold current piece",
            "ESC: Pause/Return to menu",
            "",
            "Clear full lines to score!",
            "Tetris (4 lines): Bonus points & sound!"
        ]
        for i, instr in enumerate(instructions):
            if instr:
                text=font_sml.render(instr,True,BR)
                screen.blit(text,(SW//2-text.get_width()//2,150 + i*25))
        back=font_sml.render("PRESS ENTER TO RETURN",True,BR)
        screen.blit(back,(SW//2-back.get_width()//2,500))
        pygame.display.flip()
        clock.tick(FPS)
        continue
    elif game.state=="credits":
        screen.fill(BG)
        ctitle=font_med.render("Credits",True,BR)
        screen.blit(ctitle,(SW//2-ctitle.get_width()//2,100))
        credits = [
            "Original Tetris (C) 1985-2025",
            "The Tetris Company / Nintendo",
            "",
            "Audio: Custom DMG-style synth",
            "Graphics: Pygame retro render",
            "",
            "(C) 1999-2025 Flames Co.",
            "(C) 1999-2025 Samsoft"
        ]
        for i, cred in enumerate(credits):
            if cred:
                text=font_sml.render(cred,True,BR)
                screen.blit(text,(SW//2-text.get_width()//2,150 + i*25))
        back=font_sml.render("PRESS ENTER TO RETURN",True,BR)
        screen.blit(back,(SW//2-back.get_width()//2,500))
        pygame.display.flip()
        clock.tick(FPS)
        continue

    if game.state=="play":
        game.update()
        game.draw()

    if game.state=="gameover":
        game.draw()
        t=font_big.render("GAME OVER",True,BR)
        screen.blit(t,(SW//2-t.get_width()//2,250))
        r=font_sml.render("PRESS ENTER",True,BR)
        screen.blit(r,(SW//2-r.get_width()//2,320))
        pygame.display.flip()
        if pygame.key.get_pressed()[K_RETURN]:
            game.state="menu"

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
