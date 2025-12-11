# onefile_rpg_battle.py
# Pygame 2.x — 600x400, 60 FPS, one-file, asset-free demo
import pygame, sys, random, math
pygame.init()
W,H = 600,400
screen = pygame.display.set_mode((W,H))
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 18)
BIG  = pygame.font.SysFont(None, 28)

# ------------- Core Data -------------
class Entity:
    def __init__(self, name, maxhp, atk, df, speed, color, is_player=False):
        self.name=name; self.maxhp=maxhp; self.hp=maxhp
        self.atk=atk; self.df=df; self.spd=speed; self.color=color
        self.is_player=is_player
        self.energy=3; self.status={}     # e.g., {'poison':2}
        self.badges=set()                 # e.g., {'POWER_PLUS','GUARD_PLUS'}
        self.alive=True
        self.flip=0.0                     # paper-flip tween 0..1

    def eff_atk(self):
        a=self.atk + (1 if 'POWER_PLUS' in self.badges else 0)
        if 'WEAK' in self.status: a-=1
        return max(0,a)

    def eff_df(self):
        d=self.df + (1 if 'GUARD_PLUS' in self.badges else 0)
        if 'DEF_DOWN' in self.status: d-=1
        return max(0,d)

    def take(self, dmg):
        self.hp=max(0, self.hp-dmg)
        if self.hp==0: self.alive=False

# ------------- Party & Foes -------------
player = Entity("Hero", 20, 4, 1, 6, (30,180,255), True)
player.badges.update({"POWER_PLUS"})       # demo
partner= Entity("Partner",16, 3, 0, 5, (120,220,120), True)

def gen_enemy():
    base = random.choice([
        ("Goomba",12,3,0,4,(255,150,80)),
        ("Spiky", 14,4,1,3,(240,90,90)),
        ("Shy",   10,2,0,7,(250,120,200)),
    ])
    e=Entity(*base); 
    if random.random()<0.3: e.status['DEF_DOWN']=2
    return e

# ------------- Overworld -------------
class Overworld:
    def __init__(self):
        self.player_rect = pygame.Rect(280, 180, 16, 16)
        self.walls=[pygame.Rect(120,120,360,8), pygame.Rect(120,272,360,8)]
        self.encounter_zone = pygame.Rect(220,140,160,80)
        self.in_battle=False
        self.enemies=[]

    def step(self, keys, dt):
        spd=120*dt
        dx=(keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*spd
        dy=(keys[pygame.K_DOWN]-keys[pygame.K_UP])*spd
        self.player_rect.x+=int(dx); self._collide('x')
        self.player_rect.y+=int(dy); self._collide('y')
        if self.player_rect.colliderect(self.encounter_zone) and random.random()<0.01:
            self.in_battle=True
            self.enemies=[gen_enemy() for _ in range(random.choice([1,2,3]))]

    def _collide(self,axis):
        for w in self.walls:
            if self.player_rect.colliderect(w):
                if axis=='x':
                    if self.player_rect.centerx<w.centerx: self.player_rect.right=w.left
                    else: self.player_rect.left=w.right
                else:
                    if self.player_rect.centery<w.centery: self.player_rect.bottom=w.top
                    else: self.player_rect.top=w.bottom

    def draw(self):
        screen.fill((20,20,24))
        # room
        pygame.draw.rect(screen,(40,40,48),(100,100,400,200),0,8)
        for w in self.walls: pygame.draw.rect(screen,(80,80,96),w)
        pygame.draw.rect(screen,(60,80,120),self.encounter_zone,1)
        # player (paper-flip wobble)
        t=pygame.time.get_ticks()*0.005
        w=16*abs(math.cos(t)); r=self.player_rect.copy(); r.width=max(2,int(w))
        r.center=self.player_rect.center
        pygame.draw.rect(screen,(240,230,120),r)
        label(BIG,"Overworld — walk to trigger battle", (W//2,20),center=True)

# ------------- Battle -------------
class ActionCommand:
    """Timed input window mini-checks: press Z within the window to succeed."""
    def __init__(self, ms_window=350):
        self.active=False; self.success=False
        self.start=0; self.ms=ms_window

    def start_now(self):
        self.active=True; self.success=False
        self.start=pygame.time.get_ticks()

    def handle(self, ev):
        if self.active and ev.type==pygame.KEYDOWN and ev.key==pygame.K_z:
            t=pygame.time.get_ticks()-self.start
            self.success = (50<=t<=self.ms)
            self.active=False

    def draw(self, y=330):
        if not self.active: return
        t=pygame.time.get_ticks()-self.start
        pct=min(1,max(0,t/self.ms))
        pygame.draw.rect(screen,(50,50,60),(150,y,300,12),1,4)
        pygame.draw.rect(screen,(120,220,120),(150,y,int(300*pct),12),0,4)
        label(FONT,"Press Z near end!", (300,y-10),center=True)

class Battle:
    def __init__(self, party, foes):
        self.party=[p for p in party if p.alive]
        self.foes=[f for f in foes if f.alive]
        self.turn_order = sorted(self.party+self.foes, key=lambda e:(-e.spd, e.is_player))
        self.turn_idx=0
        self.phase='select'      # select -> windup -> resolve -> enemy -> end
        self.menu_idx=0
        self.target_idx=0
        self.cmd=ActionCommand()
        self.msg=""
        self.anim_t=0.0

    def all_dead(self, group): return all(not e.alive for e in group)

    def step(self, dt, events):
        if self.phase=='end': return
        # lifecycles
        if self.all_dead(self.foes): self.msg="Victory!"; self.phase='end'
        elif self.all_dead(self.party): self.msg="Defeat..."; self.phase='end'
        if self.phase=='end': return

        cur=self.turn_order[self.turn_idx]
        # flip tween
        cur.flip=min(1.0, cur.flip + dt*4)

        # player turn
        for ev in events:
            self.cmd.handle(ev)
            if self.phase=='select' and cur.is_player:
                if ev.type==pygame.KEYDOWN:
                    if ev.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.menu_idx^=1
                    if ev.key in (pygame.K_UP, pygame.K_DOWN):
                        self.target_idx = (self.target_idx + (1 if ev.key==pygame.K_DOWN else -1)) % len(self.foes)
                    if ev.key==pygame.K_RETURN:
                        self.phase='windup'; self.anim_t=0; self.cmd.start_now()
            # enemy turn auto—no input

        # progress phases
        if self.phase=='windup':
            self.anim_t+=dt
            if self.anim_t>0.5:
                self.phase='resolve'
        elif self.phase=='resolve':
            atk=cur
            if cur.is_player:
                target=self.foes[self.target_idx]
                mult=1.0+(0.5 if self.cmd.success else 0.0)
                dmg=max(0, int((atk.eff_atk()*mult) - target.eff_df()))
                target.take(max(1,dmg))
                self.msg=f"{atk.name} hits {target.name} for {max(1,dmg)}! ({'Nice!' if self.cmd.success else '...meh'})"
            else:
                target=random.choice([p for p in self.party if p.alive])
                dmg=max(1, atk.eff_atk()-target.eff_df())
                # simple guard AC: give player a quick chance to reduce
                self.cmd.start_now();  # quick popup
                # simulate instant resolution (no wait for input in enemy phase)
                self.cmd.active=False
                if random.random()<0.2 or 'GUARD_PLUS' in target.badges:
                    dmg=max(1,dmg-1)
                target.take(dmg)
                self.msg=f"{atk.name} bonks {target.name} for {dmg}."

            self._end_turn()
        elif self.phase=='enemy':
            # instantly transfer to resolve for simplicity
            self.phase='resolve'

    def _end_turn(self):
        # tick statuses
        for e in self.turn_order:
            if 'poison' in e.status:
                e.take(1)
                e.status['poison']-=1
                if e.status['poison']<=0: del e.status['poison']
        # next alive entity
        n=len(self.turn_order)
        for _ in range(n):
            self.turn_idx=(self.turn_idx+1)%n
            if self.turn_order[self.turn_idx].alive:
                break
        cur=self.turn_order[self.turn_idx]
        self.phase = 'select' if cur.is_player else 'enemy'
        self.menu_idx=0; self.anim_t=0; self.cmd.active=False
        cur.flip=0.0

    def draw(self):
        # stage
        screen.fill((18,16,22))
        pygame.draw.rect(screen,(36,34,48),(20,60,560,240),0,12)
        # entities
        self._draw_side(self.party, (80, 240), True)
        self._draw_side(self.foes,  (520, 120), False)
        # UI
        cur=self.turn_order[self.turn_idx]
        label(BIG, f"Turn: {cur.name}", (W//2, 24), center=True)
        self._draw_ui(cur)
        self.cmd.draw()
        if self.msg: label(FONT, self.msg, (W//2, 370), center=True)

    def _draw_side(self, ents, origin, left):
        x0,y0 = origin
        step=60 if left else -60
        for i,e in enumerate(ents):
            if not e.alive: continue
            # paper flip: shrink width as flip<0.5
            w = 30*(0.2+abs(math.cos(e.flip*math.pi)))
            h = 38
            r = pygame.Rect(0,0,max(6,int(w)),h)
            r.center = (x0+step*i, y0 - i*8)
            pygame.draw.rect(screen,e.color,r,0,6)
            label(FONT,f"{e.name} {e.hp}/{e.maxhp}", (r.centerx, r.bottom+10), center=True)

    def _draw_ui(self, cur):
        pygame.draw.rect(screen,(28,28,36),(0,300,W,100))
        if cur.is_player and self.phase=='select':
            # simple two-option menu
            opts=["Strike","Skill(-1E)"]
            for i,txt in enumerate(opts):
                col=(220,240,255) if i==self.menu_idx else (160,170,190)
                label(BIG, txt, (80+i*160, 320))
            # targets
            tx=360; label(BIG,"Target", (tx, 320))
            for i,f in enumerate(self.foes):
                col=(255,240,180) if i==self.target_idx else (170,170,170)
                label(FONT, f"{f.name} HP {f.hp}", (tx, 350+i*18))
        # party energy
        e_sum=sum(p.energy for p in self.party if p.alive)
        label(FONT,f"Energy: {e_sum}", (12, 312))
        # badges preview
        label(FONT,"Badges: " + ",".join(sorted(player.badges)) or "None", (12, 332))

def label(font, text, pos, center=False):
    surf=font.render(text, True, (235,235,245))
    r=surf.get_rect()
    if center: r.center=pos
    else: r.topleft=pos
    screen.blit(surf,r)

# ------------- Game Loop -------------
ow = Overworld()
battle=None

while True:
    dt = clock.tick(60)/1000.0
    events = [ev for ev in pygame.event.get()]
    for ev in events:
        if ev.type==pygame.QUIT: pygame.quit(); sys.exit()

    keys=pygame.key.get_pressed()

    # state switch
    if not ow.in_battle:
        ow.step(keys, dt)
        if ow.in_battle:
            # (re)spawn enemy wave; reset party a bit
            player.hp=player.maxhp; partner.hp=partner.maxhp
            player.alive=partner.alive=True
            party=[player,partner]
            battle=Battle(party, ow.enemies)
    else:
        battle.step(dt, events)

    # draw
    if not ow.in_battle:
        ow.draw()
        label(FONT,"Arrows to move • Encounters are random in the highlighted zone", (W//2, H-18), center=True)
    else:
        battle.draw()
        if battle.phase=='end':
            label(BIG,"Press ENTER to return", (W//2, 350), center=True)
            for ev in events:
                if ev.type==pygame.KEYDOWN and ev.key==pygame.K_RETURN:
                    ow=Overworld()

    pygame.display.flip()
