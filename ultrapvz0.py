# filename: pvz_zzz_engine.py
import pygame, sys, random, math
W,H=600,400; UI=56; ROWS,COLS=5,9; CW,CH=W//COLS,(H-UI)//ROWS
pygame.init(); screen=pygame.display.set_mode((W,H)); pygame.display.set_caption("pvz its about zzz — engine")
font=pygame.font.SysFont(None,20); clock=pygame.time.Clock()
# --- Game State ---
sun=150; plants={}  # (r,c)->dict
peas=[]; zombies=[]
wave_left=12; spawn_cd=0.5; game_over=None; paused=False
# --- Tunables ---
PLANT_COST=100; SHOOT_CD=1.35; PEA_SPD=250; PEA_DMG=20; Z_HP=120; Z_SPD=22
sun_tick=0.0; SUN_RATE=25; SUN_EVERY=6.0
# Helpers
cell=lambda r,c:(c*CW,UI+r*CH,CW,CH)
center=lambda r,c:(c*CW+CW//2,UI+r*CH+CH//2)
rx=lambda x,y,w,h:(pygame.Rect(x,y,w,h))
# --- Core Loop ---
while True:
    dt=clock.tick(60)/1000
    for e in pygame.event.get():
        if e.type==pygame.QUIT: pygame.quit(); sys.exit()
        if e.type==pygame.KEYDOWN:
            if e.key==pygame.K_p: paused=not paused
            if e.key==pygame.K_r and game_over: # quick restart
                sun,plants,peas,zombies,wave_left,spawn_cd,game_over,sun_tick=150,{},[],[],12,0.5,None,0.0
        if e.type==pygame.MOUSEBUTTONDOWN and not game_over and not paused:
            mx,my=pygame.mouse.get_pos()
            if my>=UI:
                r=(my-UI)//CH; c=mx//CW
                if e.button==1 and (r,c) not in plants and sun>=PLANT_COST:
                    plants[(r,c)]={"hp":100,"cd":0.0}
                    sun-=PLANT_COST
                elif e.button==3 and (r,c) in plants:
                    del plants[(r,c)]
    if paused or game_over:
        pass
    else:
        # economy
        sun_tick+=dt
        if sun_tick>=SUN_EVERY:
            sun+=SUN_RATE; sun_tick%=SUN_EVERY
        # plant fire
        for (r,c),p in list(plants.items()):
            p["cd"]=max(0.0,p["cd"]-dt)
            if p["cd"]<=0:
                # fire if any zombie ahead in lane
                if any(z["r"]==r and z["x"]>c*CW for z in zombies):
                    x,y=center(r,c)
                    peas.append({"x":x+8,"y":y-6,"vx":PEA_SPD,"d":PEA_DMG,"lane":r})
                    p["cd"]=SHOOT_CD
        # peas move
        for pe in list(peas):
            pe["x"]+=pe["vx"]*dt
            if pe["x"]>W: peas.remove(pe); continue
            # hit test
            for z in list(zombies):
                if z["r"]==pe["lane"] and z["x"]-12<pe["x"]<z["x"]+12:
                    z["hp"]-=pe["d"]; 
                    if pe in peas: peas.remove(pe)
                    if z["hp"]<=0: zombies.remove(z)
                    break
        # zombies spawn & advance
        spawn_cd-=dt
        if spawn_cd<=0 and wave_left>0:
            r=random.randrange(ROWS)
            zombies.append({"r":r,"x":W+18,"hp":Z_HP,"eat":0.0})
            wave_left-=1; spawn_cd=random.uniform(0.8,1.8)
        # advance or eat
        for z in list(zombies):
            c=int((z["x"])//CW); r=z["r"]
            target=plants.get((r,c))
            if target and (c*CW)<=z["x"]<((c+1)*CW):
                z["eat"]+=dt
                if z["eat"]>0.5:
                    target["hp"]-=15; z["eat"]=0.0
                    if target["hp"]<=0: del plants[(r,c)]
            else:
                z["x"]-=Z_SPD*dt
            if z["x"]<0: game_over="Zombies ate your brains!"
        if wave_left==0 and not zombies and not game_over: game_over="You win!"
    # --- Draw ---
    screen.fill((44,105,44))
    pygame.draw.rect(screen,(30,30,30),(0,0,W,UI))
    # grid
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen,(70,150,70),cell(r,c),0)
            pygame.draw.rect(screen,(22,90,22),cell(r,c),1)
    # entities
    for (r,c),p in plants.items():
        x,y,w,h=cell(r,c)
        pygame.draw.rect(screen,(28,180,28),(x+8,y+6,w-16,h-12))
        # muzzle
        pygame.draw.circle(screen,(180,255,180),(x+w-10,y+h//2),4)
    for pe in peas:
        pygame.draw.circle(screen,(80,200,60),(int(pe["x"]),int(pe["y"])),4)
    for z in zombies:
        y=UI+z["r"]*CH+CH//2
        pygame.draw.rect(screen,(170,130,90),(int(z["x"])-12,y-18,24,36))
    # UI text
    t=f"Sun: {sun}  Plants: L-click place ({PLANT_COST}), R-click remove | P pause | R restart | left {wave_left}"
    screen.blit(font.render(t,True,(230,230,230)),(8,8))
    if paused: screen.blit(font.render("Paused",True,(255,230,0)),(W-80,8))
    if game_over:
        msg=font.render(game_over+"  (R to restart)",True,(255,230,0))
        screen.blit(msg,(W//2-msg.get_width()//2, 28))
    pygame.display.flip()
