#!/usr/bin/env python3
"""
ULTRA MARIO 2D BROS - SMB1 Edition
NES-ACCURATE | 60 FPS | Pure Tkinter + Math | Single File
"""
import tkinter as tk
import math

# NES Constants
NES_W, NES_H, SCALE = 256, 240, 2
WIDTH, HEIGHT = NES_W * SCALE, NES_H * SCALE
FPS = 16

# SMB1 Palette
C = {'sky':'#5c94fc','black':'#000000','white':'#fcfcfc','orange':'#c84c0c','brown':'#ac7c00',
     'tan':'#fcbcb0','dark':'#503000','yellow':'#fca044','gold':'#e45c10','red':'#b8131a',
     'skin':'#fcbcb0','hair':'#ac7c00','goomba':'#e45c10','koopa':'#00a800','koopa_l':'#b8f818',
     'pipe':'#00a800','pipe_l':'#b8f818','pipe_d':'#005800','cloud':'#fcfcfc','cloud_l':'#a4e4fc'}

class P:
    WA,RA,MW,MR,FR,SK = 0.037,0.057,1.5,2.5,0.037,0.1
    JW,JR,GJ,GF,TV,GS,SS = -4.0,-5.0,0.125,0.4375,4.0,0.75,4.0

# Sprites
S_MARIO = [[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,0,2,2,2,3,3,2,3,0,0,0,0,0],[0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0],[0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0],[0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0],[0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0],[0,0,0,0,1,1,4,1,1,1,0,0,0,0,0,0],[0,0,0,1,1,1,4,1,1,4,1,1,1,0,0,0],[0,0,1,1,1,1,4,4,4,4,1,1,1,1,0,0],[0,0,3,3,1,4,3,4,4,3,4,1,3,3,0,0],[0,0,3,3,3,4,4,4,4,4,4,3,3,3,0,0],[0,0,3,3,4,4,4,4,4,4,4,4,3,3,0,0],[0,0,0,0,4,4,4,0,0,4,4,4,0,0,0,0],[0,0,0,2,2,2,0,0,0,0,2,2,2,0,0,0],[0,0,2,2,2,2,0,0,0,0,2,2,2,2,0,0]]
S_WALK1 = [[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,0,2,2,2,3,3,2,3,0,0,0,0,0],[0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0],[0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0],[0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0],[0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0],[0,0,0,1,1,1,4,1,1,4,1,0,0,0,0,0],[0,0,1,1,1,1,1,4,4,1,1,1,3,0,0,0],[0,0,3,1,1,4,4,4,4,4,4,3,3,0,0,0],[0,0,3,3,4,4,4,4,4,4,4,3,3,0,0,0],[0,0,0,3,4,4,4,4,4,4,4,0,0,0,0,0],[0,0,0,0,2,2,4,4,4,0,0,0,0,0,0,0],[0,0,0,2,2,2,2,0,0,2,2,0,0,0,0,0],[0,0,2,2,2,2,0,0,0,2,2,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
S_WALK2 = [[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,0,2,2,2,3,3,2,3,0,0,0,0,0],[0,0,0,2,3,2,3,3,3,2,3,3,3,0,0,0],[0,0,0,2,3,2,2,3,3,3,2,3,3,3,0,0],[0,0,0,2,2,3,3,3,3,2,2,2,2,0,0,0],[0,0,0,0,0,3,3,3,3,3,3,3,0,0,0,0],[0,0,0,0,0,1,1,4,1,1,1,1,0,0,0,0],[0,0,0,0,4,1,1,1,4,1,1,1,0,0,0,0],[0,0,0,0,4,4,1,4,4,4,1,1,0,0,0,0],[0,0,0,4,4,4,4,3,4,4,3,0,0,0,0,0],[0,0,0,4,4,4,3,3,3,3,3,0,0,0,0,0],[0,0,0,4,4,4,4,4,3,3,0,0,0,0,0,0],[0,0,0,0,4,4,4,4,2,2,2,0,0,0,0,0],[0,0,0,0,0,0,2,2,2,2,2,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
S_JUMP = [[0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0],[0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,2,2,2,3,3,2,3,0,0,0,0],[0,0,0,0,2,3,2,3,3,3,2,3,3,3,0,0],[0,0,0,0,2,3,2,2,3,3,3,2,3,3,3,0],[0,0,0,0,2,2,3,3,3,3,2,2,2,2,0,0],[0,0,0,0,0,0,3,3,3,3,3,3,3,0,0,0],[0,0,0,3,3,1,1,4,1,1,1,0,0,0,0,0],[0,3,3,3,1,1,1,4,1,1,4,1,1,0,0,0],[0,3,3,4,1,1,1,4,4,4,4,1,1,0,0,0],[0,0,0,4,4,4,4,3,4,4,3,4,0,0,0,0],[0,0,0,0,4,4,4,4,4,4,4,4,4,0,0,0],[0,0,0,0,4,4,4,4,4,4,4,4,0,0,0,0],[0,0,0,4,4,4,4,0,0,0,0,0,0,0,0,0],[0,0,0,2,2,2,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
S_GOOMBA = [[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,1,1,2,2,1,1,1,1,2,2,1,1,0,0],[0,1,1,2,2,3,2,1,1,2,3,2,2,1,1,0],[0,1,1,2,2,3,2,1,1,2,3,2,2,1,1,0],[1,1,1,1,2,2,1,1,1,1,2,2,1,1,1,1],[1,1,1,1,1,1,1,2,2,1,1,1,1,1,1,1],[1,1,1,1,1,1,2,2,2,2,1,1,1,1,1,1],[0,1,1,1,1,1,2,1,1,2,1,1,1,1,1,0],[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],[0,0,0,0,2,2,2,2,2,2,2,2,0,0,0,0],[0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0],[0,0,2,2,2,2,0,0,0,0,2,2,2,2,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]
S_GFLAT = [[0]*16]*10+[[0,0,1,1,2,2,1,1,1,1,2,2,1,1,0,0],[0,1,1,2,3,2,1,1,1,1,2,3,2,1,1,0],[1,1,1,2,2,1,1,2,2,1,1,2,2,1,1,1],[0,0,0,1,1,1,2,2,2,2,1,1,1,0,0,0],[0,0,2,2,2,2,2,2,2,2,2,2,2,2,0,0],[0]*16]
S_KOOPA = [[0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,0,1,2,1,1,1,1,0,0,0,0,0],[0,0,0,0,0,1,2,2,1,1,1,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,1,3,3,3,3,1,0,0,0,0,0,0],[0,0,0,1,3,3,3,3,3,3,1,0,0,0,0,0],[0,0,0,1,3,2,3,3,2,3,1,0,0,0,0,0],[0,0,1,3,3,3,3,3,3,3,3,1,0,0,0,0],[0,0,1,3,3,3,3,3,3,3,3,1,0,0,0,0],[0,0,1,3,3,3,3,3,3,3,3,1,0,0,0,0],[0,0,0,1,3,3,3,3,3,3,1,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0],[0,0,0,1,1,1,0,0,1,1,1,0,0,0,0,0],[0]*16]
S_SHELL = [[0]*16]*4+[[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,1,1,2,2,1,1,2,2,1,1,0,0,0],[0,0,1,1,2,2,2,1,1,2,2,2,1,1,0,0],[0,0,1,1,2,2,2,1,1,2,2,2,1,1,0,0],[0,0,1,1,1,2,2,1,1,2,2,1,1,1,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0]]+[[0]*16]*4
S_QBLK = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],[1,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2],[1,3,3,3,3,3,2,2,2,2,3,3,3,3,2,2],[1,3,3,3,3,2,2,3,3,2,2,3,3,3,2,2],[1,3,3,3,3,2,2,3,3,2,2,3,3,3,2,2],[1,3,3,3,3,3,3,3,2,2,3,3,3,3,2,2],[1,3,3,3,3,3,3,2,2,3,3,3,3,3,2,2],[1,3,3,3,3,3,3,2,2,3,3,3,3,3,2,2],[1,3,3,3,3,3,3,2,2,3,3,3,3,3,2,2],[1,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2],[1,3,3,3,3,3,3,2,2,3,3,3,3,3,2,2],[1,3,3,3,3,3,3,2,2,3,3,3,3,3,2,2],[1,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2],[1,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2],[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]
S_EBLK = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2]]+[[1,3,3,3,3,3,3,3,3,3,3,3,3,3,2,2]]*13+[[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]
S_BRICK = [[1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,2],[1,3,3,3,3,3,3,2,1,3,3,3,3,3,3,2],[1,3,3,3,3,3,3,2,1,3,3,3,3,3,3,2],[1,3,3,3,3,3,3,2,1,3,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,1],[1,3,3,2,1,3,3,3,3,3,3,2,1,3,3,3],[1,3,3,2,1,3,3,3,3,3,3,2,1,3,3,3],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,2],[1,3,3,3,3,3,3,2,1,3,3,3,3,3,3,2],[1,3,3,3,3,3,3,2,1,3,3,3,3,3,3,2],[1,3,3,3,3,3,3,2,1,3,3,3,3,3,3,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,1],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]
S_GND = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,2,2,1,1,1,2,1,1,2,1,1,1,2,2,1],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]+[[3]*16]*13
S_PIPE = [[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],[1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]+[[1,2,3,3,3,3,3,3,3,3,3,3,3,3,3,1]]*14
S_CLOUD = [[0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],[0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],[0,1,1,1,2,2,1,1,1,1,2,2,1,1,1,0],[1,1,1,2,2,3,2,1,1,2,3,2,2,1,1,1],[1,1,1,2,2,3,2,1,1,2,3,2,2,1,1,1],[1,1,1,1,2,2,1,1,1,1,2,2,1,1,1,1],[1]*16,[1]*16,[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],[0]*16,[0]*16]
S_BUSH = [[0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],[0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],[0,1,1,1,2,2,1,1,1,1,2,2,1,1,1,0],[1,1,1,2,2,3,2,1,1,2,3,2,2,1,1,1],[1,1,1,2,2,3,2,1,1,2,3,2,2,1,1,1],[1,1,1,1,2,2,1,1,1,1,2,2,1,1,1,1],[1]*16,[1]*16,[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],[0]*16,[0]*16]
S_HILL = [[0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,1,1,1,1,1,2,1,1,1,1,1,1,0,0],[0,1,1,1,1,1,2,2,2,1,1,1,1,1,1,0],[1,1,1,1,1,2,2,2,2,2,1,1,1,1,1,1],[1,1,1,1,1,2,2,1,2,2,1,1,1,1,1,1],[1,1,1,1,2,2,1,1,1,2,2,1,1,1,1,1],[1,1,1,1,2,1,1,1,1,1,2,1,1,1,1,1],[1,1,1,2,1,1,1,1,1,1,1,2,1,1,1,1]]+[[1]*16]*4
S_COIN = [[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,0,1,1,2,2,1,1,0,0,0,0,0],[0,0,0,0,1,1,2,2,2,2,1,1,0,0,0,0],[0,0,0,0,1,2,2,1,1,2,2,1,0,0,0,0],[0,0,0,1,1,2,2,1,1,2,2,1,1,0,0,0],[0,0,0,1,2,2,1,1,1,1,2,2,1,0,0,0],[0,0,0,1,2,2,1,1,1,1,2,2,1,0,0,0],[0,0,0,1,2,2,1,1,1,1,2,2,1,0,0,0],[0,0,0,1,2,2,1,1,1,1,2,2,1,0,0,0],[0,0,0,1,2,2,1,1,1,1,2,2,1,0,0,0],[0,0,0,1,1,2,2,1,1,2,2,1,1,0,0,0],[0,0,0,0,1,2,2,1,1,2,2,1,0,0,0,0],[0,0,0,0,1,1,2,2,2,2,1,1,0,0,0,0],[0,0,0,0,0,1,1,2,2,1,1,0,0,0,0,0],[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0]*16]
S_MUSH = [[0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0],[0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0],[0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0],[0,0,1,1,2,2,1,1,1,1,2,2,1,1,0,0],[0,1,1,2,2,2,2,1,1,2,2,2,2,1,1,0],[0,1,1,2,2,2,2,1,1,2,2,2,2,1,1,0],[1,1,1,1,2,2,1,1,1,1,2,2,1,1,1,1],[1]*16,[0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],[0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0],[0,0,0,0,3,3,3,3,3,3,3,3,0,0,0,0],[0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,0],[0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,0],[0,0,3,3,3,3,3,3,3,3,3,3,3,3,0,0],[0,0,0,3,3,3,3,3,3,3,3,3,3,0,0,0],[0]*16]

# Palettes
PM = {1:C['red'],2:C['hair'],3:C['skin'],4:C['orange']}
PG = {1:C['goomba'],2:C['black'],3:C['white']}
PK = {1:C['koopa'],2:C['white'],3:C['koopa_l']}
PQ = {1:C['gold'],2:C['dark'],3:C['yellow']}
PE = {1:C['brown'],2:C['dark'],3:C['orange']}
PB = {1:C['tan'],2:C['dark'],3:C['orange']}
PGR = {1:C['tan'],2:C['orange'],3:C['brown']}
PP = {1:C['pipe_d'],2:C['pipe'],3:C['pipe_l']}
PC = {1:C['cloud'],2:C['black'],3:C['cloud_l']}
PBS = {1:C['pipe_l'],2:C['black'],3:C['pipe']}
PH = {1:C['pipe_l'],2:C['pipe']}
PCN = {1:C['gold'],2:C['yellow']}
PMS = {1:C['red'],2:C['white'],3:C['skin']}

# Level
L = {'w':224,'t':400,'gnd':[(0,69),(71,86),(89,153),(155,224)],
     'brk':[(20,9),(22,9),(23,9),(24,9),(77,9),(78,9),(79,9),(80,5),(81,5),(82,5),(83,5),(84,5),(85,5),(86,5),(87,5),(91,9),(92,9),(93,9),(94,9),(100,5),(118,9),(119,9),(120,9),(128,9),(129,9),(130,5),(131,5),(132,5),(168,9),(169,9),(170,9),(171,9)],
     'qb':[(16,9,'c'),(21,9,'m'),(22,5,'c'),(23,9,'c'),(78,9,'m'),(94,5,'c'),(106,9,'c'),(109,9,'m'),(109,5,'c'),(112,9,'c'),(129,9,'c'),(130,9,'c'),(170,5,'c')],
     'pip':[(28,11,2),(38,10,3),(46,9,4),(57,9,4),(163,11,2),(179,11,2)],
     'gmb':[(22,12),(40,12),(51,12),(52,12),(80,4),(82,4),(97,12),(98,12),(114,12),(115,12),(124,12),(125,12),(128,12),(129,12),(174,12),(175,12)],
     'kpa':[(107,12),(181,12)],'str':[(134,'u',4),(140,'d',4),(148,'u',4),(155,'u',4),(182,'u',8)],
     'cld':[(8,3,1),(19,2,1),(27,3,2),(36,2,1),(56,3,2),(67,2,1),(83,3,1),(100,2,2),(119,3,1),(128,2,1),(150,3,2),(170,2,1)],
     'bsh':[(11,2),(23,1),(41,3),(59,2),(69,1),(90,3),(118,2),(136,1),(157,3)],'hil':[(0,2),(16,1),(48,2),(64,1),(96,2),(112,1),(144,2),(160,1)]}

class R:
    def __init__(s,c):s.c=c;s.sc=SCALE
    def px(s,x,y,cl):sx,sy=x*s.sc,y*s.sc;s.c.create_rectangle(sx,sy,sx+s.sc,sy+s.sc,fill=cl,outline='')
    def sp(s,x,y,d,p,f=False):
        for ri,rw in enumerate(d):
            for ci,cv in enumerate(rw):
                if cv==0:continue
                cl=p.get(cv,C['white']);px=x+(len(rw)-1-ci if f else ci)
                s.px(px,y+ri,cl)

class Game:
    def __init__(s,rt):
        s.rt=rt;rt.title("ULTRA MARIO 2D BROS");rt.geometry(f"{WIDTH}x{HEIGHT}");rt.resizable(0,0)
        s.cv=tk.Canvas(rt,width=WIDTH,height=HEIGHT,bg=C['sky'],highlightthickness=0);s.cv.pack()
        s.r=R(s.cv);s.st='m';s.ms=0;s.k=set();s.jh=False;s.rh=False;s.jp=False;s.fr=0
        s.pl=None;s.cx=0.0;s.lv=None;s.bk=[];s.en=[];s.it=[];s.pt=[];s.sc=0;s.cn=0;s.lf=3;s.tm=400
        rt.bind('<KeyPress>',s.kd);rt.bind('<KeyRelease>',s.ku);s.dm();s.up()
    
    def kd(s,e):
        k=e.keysym.lower()
        if k not in s.k:s.k.add(k)
        if k in ('z','space'):s.jp=True;s.jh=True
        if k=='x':s.rh=True
    
    def ku(s,e):
        k=e.keysym.lower();s.k.discard(k)
        if k in ('z','space'):s.jh=False
        if k=='x':s.rh=False
    
    def up(s):
        if s.st=='m':s.um()
        elif s.st=='p':s.ug()
        s.jp=False;s.fr+=1;s.rt.after(FPS,s.up)
    
    def um(s):
        if 'up' in s.k:s.k.discard('up');s.ms=(s.ms-1)%2;s.dm()
        if 'down' in s.k:s.k.discard('down');s.ms=(s.ms+1)%2;s.dm()
        if s.jp or 'return' in s.k:s.k.discard('return');s.sg()
    
    def dm(s):
        s.cv.delete('all')
        for x in range(0,NES_W,16):s.r.sp(x,NES_H-32,S_GND,PGR);s.r.sp(x,NES_H-16,S_GND,PGR)
        s.cv.create_text(WIDTH//2,60*SCALE,text="SUPER MARIO BROS.",fill=C['white'],font=('Courier',20*SCALE,'bold'))
        s.cv.create_text(WIDTH//2,80*SCALE,text="ULTRA MARIO 2D",fill=C['red'],font=('Courier',8*SCALE,'bold'))
        for i,o in enumerate(['1 PLAYER GAME','2 PLAYER GAME']):
            y=(100+i*16)*SCALE
            if i==s.ms:s.r.sp(80,100+i*16-8,S_MUSH,PMS)
            s.cv.create_text(WIDTH//2+20*SCALE,y,text=o,fill=C['white'],font=('Courier',8*SCALE))
        s.r.sp(200,30,S_CLOUD,PC);s.r.sp(40,50,S_CLOUD,PC)
    
    def sg(s):s.st='p';s.sc=0;s.cn=0;s.lf=3;s.ll()
    
    def ll(s):
        s.lv=L;s.pl={'x':40.0,'y':192.0,'vx':0.0,'vy':0.0,'f':1,'g':True,'j':False,'sk':False,'st':'s','a':0,'at':0,'i':0}
        s.cx=0.0;s.bk=[];s.en=[];s.it=[];s.pt=[];s.tm=s.lv['t']
        for bx,by in s.lv['brk']:s.bk.append({'t':'b','x':bx*16,'y':by*16,'h':False,'b':0})
        for bx,by,c in s.lv['qb']:s.bk.append({'t':'q','x':bx*16,'y':by*16,'h':False,'c':c,'b':0})
        for gx,gy in s.lv['gmb']:s.en.append({'t':'g','x':float(gx*16),'y':float(gy*16),'vx':-P.GS,'a':True,'s':False,'st':0})
        for kx,ky in s.lv['kpa']:s.en.append({'t':'k','x':float(kx*16),'y':float(ky*16),'vx':-P.GS,'a':True,'s':False,'st':0,'sh':False,'sm':False})
    
    def ug(s):s.up_pl();s.up_en();s.up_it();s.up_cm();s.dg();(s.fr%24==0 and s.tm>0) and setattr(s,'tm',s.tm-1)
    
    def up_pl(s):
        p=s.pl;d=(1 if 'right' in s.k else 0)-(1 if 'left' in s.k else 0)
        if p['g']:
            if d!=0:
                md=1 if p['vx']>0 else(-1 if p['vx']<0 else 0);p['sk']=d!=md and p['vx']!=0
                ac=P.SK if p['sk'] else(P.RA if s.rh else P.WA);p['vx']+=d*ac
                if not p['sk']:p['f']=d
            else:p['sk']=False;p['vx']=p['vx']-(1 if p['vx']>0 else -1)*P.FR if abs(p['vx'])>P.FR else 0.0
            mx=P.MR if s.rh else P.MW;p['vx']=(1 if p['vx']>0 else -1)*mx if abs(p['vx'])>mx else p['vx']
        else:
            if d!=0:p['vx']+=d*P.WA*0.5;mx=P.MR if s.rh else P.MW;p['vx']=(1 if p['vx']>0 else -1)*mx if abs(p['vx'])>mx else p['vx']
        if s.jp and p['g']:sr=abs(p['vx'])/P.MR;p['vy']=P.JW+(P.JR-P.JW)*sr;p['g']=False;p['j']=True
        if not p['g']:gv=P.GJ if s.jh and p['vy']<0 else P.GF;p['vy']+=gv;p['vy']=P.TV if p['vy']>P.TV else p['vy']
        p['x']+=p['vx'];p['y']+=p['vy'];s.cw();s.cb();s.ce()
        if p['x']<s.cx:p['x']=s.cx;p['vx']=0
        if p['x']>s.lv['w']*16-16:p['x']=s.lv['w']*16-16
        if p['y']>NES_H+32:s.die()
        p['at']+=1
        if p['g'] and abs(p['vx'])>0.1:
            if p['at']>=max(2,int(10-abs(p['vx'])*2)):p['at']=0;p['a']=(p['a']+1)%3
        else:p['a']=0;p['at']=0
    
    def cw(s):
        p=s.pl;p['g']=False
        for st,en in s.lv['gnd']:
            gl,gr,gt=st*16,en*16,13*16
            if p['x']+14>gl and p['x']+2<gr and p['y']+16>=gt and p['vy']>=0 and p['y']+16-p['vy']<=gt+4:
                p['y']=gt-16;p['vy']=0;p['g']=True;p['j']=False;break
        for sx,d,h in s.lv['str']:
            for step in range(h):
                tx=sx+step;ty=(13-step-1)*16 if d=='u' else (13-(h-step-1)-1)*16
                if p['x']+14>tx*16 and p['x']+2<tx*16+16 and p['y']+16>=ty and p['vy']>=0 and p['y']+16-p['vy']<=ty+4:
                    p['y']=ty-16;p['vy']=0;p['g']=True;p['j']=False
        for pip in s.lv['pip']:
            px,py,ph=pip[0]*16,pip[1]*16,pip[2]*16
            if p['x']+14>px and p['x']+2<px+32 and p['y']+16>=py and p['vy']>=0 and p['y']+16-p['vy']<=py+4:
                p['y']=py-16;p['vy']=0;p['g']=True;p['j']=False
            if p['y']+14>py and p['y']+2<py+ph:
                if p['x']+16>px and p['x']<px and p['vx']>0:p['x']=px-16;p['vx']=0
                if p['x']<px+32 and p['x']+16>px+32 and p['vx']<0:p['x']=px+32;p['vx']=0
    
    def cb(s):
        p=s.pl
        for b in s.bk:
            bx,by=b['x'],b['y']
            if abs(bx-p['x'])>32 or abs(by-p['y'])>48:continue
            if p['x']+14>bx and p['x']+2<bx+16:
                if p['y']+16>=by and p['y']+16<=by+8 and p['vy']>=0:p['y']=by-16;p['vy']=0;p['g']=True;p['j']=False
                if p['y']<=by+16 and p['y']>=by+8 and p['vy']<0:p['y']=by+16;p['vy']=0;not b['h'] and s.hb(b)
            if p['y']+14>by and p['y']+2<by+16:
                if p['x']+16>bx and p['x']+16<bx+8 and p['vx']>0:p['x']=bx-16;p['vx']=0
                if p['x']<bx+16 and p['x']>bx+8 and p['vx']<0:p['x']=bx+16;p['vx']=0
    
    def hb(s,b):
        if b['t']=='q' and not b['h']:
            b['h']=True;b['b']=8
            if b['c']=='c':s.cn+=1;s.sc+=200;s.pt.append({'t':'c','x':b['x'],'y':b['y']-16,'vy':-4,'tm':30})
            elif b['c']=='m':s.it.append({'t':'m','x':float(b['x']),'y':float(b['y']-16),'vx':1.0,'vy':0.0,'e':True,'et':16})
        elif b['t']=='b' and not b['h']:
            if s.pl['st']=='s':b['b']=8
            else:b['h']=True;s.sc+=50;[s.pt.append({'t':'d','x':b['x']+(i%2)*8,'y':b['y']+(i//2)*8,'vx':(1 if i%2 else -1)*2,'vy':-4+(i//2)*2,'tm':60}) for i in range(4)]
    
    def ce(s):
        p=s.pl
        if p['i']>0:p['i']-=1;return
        for e in s.en:
            if not e['a']:continue
            ex,ey=e['x'],e['y']
            if abs(ex-p['x'])>32 or abs(ey-p['y'])>32:continue
            if p['x']+14>ex+2 and p['x']+2<ex+14 and p['y']+16>ey+4 and p['y']+4<ey+16:
                if p['vy']>0 and p['y']+16<ey+10:s.stp(e);p['vy']=-3.0
                else:
                    if p['st']=='s':s.die()
                    else:p['st']='s';p['i']=120
    
    def stp(s,e):
        if e['t']=='g':e['a']=False;e['s']=True;e['st']=30;s.sc+=100
        elif e['t']=='k':
            if not e['sh']:e['sh']=True;e['vx']=0;s.sc+=100
            else:e['sm']=not e['sm'];e['vx']=P.SS*s.pl['f'] if e['sm'] else 0
    
    def die(s):s.lf-=1;s.ll() if s.lf>0 else (setattr(s,'st','m'),s.dm())
    
    def up_en(s):
        for e in s.en[:]:
            if e.get('s'):e['st']-=1;e['st']<=0 and s.en.remove(e);continue
            if not e['a']:continue
            e['x']+=e['vx'];e['y']=12*16;e['x']<s.cx-32 and setattr(e,'a',False)
    
    def up_it(s):
        for it in s.it[:]:
            if it['t']=='m':
                if it['e']:it['et']-=1;it['y']-=1;it['et']<=0 and setattr(it,'e',False)
                else:
                    it['vy']+=P.GF;it['x']+=it['vx'];it['y']+=it['vy'];it['y']>12*16 and (setattr(it,'y',12*16),setattr(it,'vy',0))
                    p=s.pl
                    if p['x']+14>it['x'] and p['x']+2<it['x']+16 and p['y']+16>it['y'] and p['y']<it['y']+16:
                        p['st']=='s' and setattr(p,'st','b');s.sc+=1000;s.it.remove(it)
        for pr in s.pt[:]:
            pr['tm']-=1;pr['tm']<=0 and s.pt.remove(pr);continue
            if pr['t']=='c':pr['vy']+=0.3;pr['y']+=pr['vy']
            elif pr['t']=='d':pr['vy']+=0.4;pr['x']+=pr['vx'];pr['y']+=pr['vy']
    
    def up_cm(s):
        p=s.pl;tg=p['x']-NES_W*0.4;tg>s.cx and setattr(s,'cx',tg)
        mx=s.lv['w']*16-NES_W;s.cx>mx and setattr(s,'cx',mx);s.cx<0 and setattr(s,'cx',0)
    
    def sx(s,wx):return int(wx-s.cx)
    
    def dg(s):
        s.cv.delete('all')
        s.dbg();s.dgr();s.dpp();s.dbk();s.dit();s.den();s.dpl();s.dpt();s.dhu()
    
    def dbg(s):
        for cx,cy,sz in s.lv['cld']:
            x=s.sx(cx*16)
            if -32<x<NES_W+32:[s.r.sp(x+i*16,cy*16,S_CLOUD,PC) for i in range(sz)]
        for hx,sz in s.lv['hil']:
            x=s.sx(hx*16)
            if -48<x<NES_W+48:[s.r.sp(x+i*16,11*16,S_HILL,PH) for i in range(sz*2)]
        for bx,sz in s.lv['bsh']:
            x=s.sx(bx*16)
            if -48<x<NES_W+48:[s.r.sp(x+i*16,12*16,S_BUSH,PBS) for i in range(sz)]
    
    def dgr(s):
        for st,en in s.lv['gnd']:
            for tx in range(st,en):
                x=s.sx(tx*16)
                if -16<x<NES_W+16:s.r.sp(x,13*16,S_GND,PGR);s.r.sp(x,14*16,S_GND,PGR)
        for sx_t,d,h in s.lv['str']:
            for step in range(h):
                tx=sx_t+step
                for row in range(step+1 if d=='u' else h-step):
                    x=s.sx(tx*16)
                    if -16<x<NES_W+16:s.r.sp(x,(12-row)*16,S_GND,PGR)
    
    def dpp(s):
        for pip in s.lv['pip']:
            px,py,ph=pip[0]*16,pip[1]*16,pip[2];x=s.sx(px)
            if -32<x<NES_W+32:[s.r.sp(x,py+r*16,S_PIPE,PP) or s.r.sp(x+16,py+r*16,S_PIPE,PP) for r in range(ph)]
    
    def dbk(s):
        for b in s.bk:
            x=s.sx(b['x'])
            if -16<x<NES_W+16:
                bp=0
                if b['b']>0:bp=-4 if b['b']>4 else -(8-b['b']);b['b']-=1
                if b['t']=='q':sp,pl=(S_EBLK,PE) if b['h'] else (S_QBLK,PQ);s.r.sp(x,b['y']+bp,sp,pl)
                elif b['t']=='b' and not b['h']:s.r.sp(x,b['y']+bp,S_BRICK,PB)
    
    def dit(s):
        for it in s.it:
            x=s.sx(it['x'])
            if -16<x<NES_W+16 and it['t']=='m':s.r.sp(int(x),int(it['y']),S_MUSH,PMS)
    
    def den(s):
        for e in s.en:
            x=s.sx(e['x'])
            if -16<x<NES_W+16:
                if e['t']=='g':sp=S_GFLAT if e.get('s') else S_GOOMBA;(e['a'] or e.get('s')) and s.r.sp(int(x),int(e['y']),sp,PG)
                elif e['t']=='k':
                    if e.get('sh'):s.r.sp(int(x),int(e['y']),S_SHELL,PK)
                    elif e['a']:s.r.sp(int(x),int(e['y']),S_KOOPA,PK,f=e['vx']>0)
    
    def dpl(s):
        p=s.pl;x=s.sx(p['x'])
        if p['i']>0 and (p['i']//4)%2==0:return
        if not p['g']:sp=S_JUMP
        elif p['sk']:sp=S_WALK2
        elif abs(p['vx'])>0.1:sp=[S_MARIO,S_WALK1,S_WALK2][p['a']%3]
        else:sp=S_MARIO
        s.r.sp(int(x),int(p['y']),sp,PM,f=p['f']<0)
    
    def dpt(s):
        for pr in s.pt:
            x=s.sx(pr['x'])
            if -16<x<NES_W+16:
                if pr['t']=='c':s.r.sp(int(x),int(pr['y']),S_COIN,PCN)
                elif pr['t']=='d':s.cv.create_rectangle(x*SCALE,pr['y']*SCALE,(x+8)*SCALE,(pr['y']+8)*SCALE,fill=C['orange'],outline='')
    
    def dhu(s):
        s.cv.create_text(32*SCALE,8*SCALE,text="MARIO",fill=C['white'],font=('Courier',6*SCALE),anchor='nw')
        s.cv.create_text(32*SCALE,16*SCALE,text=f"{s.sc:06d}",fill=C['white'],font=('Courier',6*SCALE),anchor='nw')
        s.cv.create_text(96*SCALE,16*SCALE,text=f"x{s.cn:02d}",fill=C['white'],font=('Courier',6*SCALE),anchor='nw')
        s.cv.create_text(144*SCALE,8*SCALE,text="WORLD",fill=C['white'],font=('Courier',6*SCALE),anchor='nw')
        s.cv.create_text(144*SCALE,16*SCALE,text="1-1",fill=C['white'],font=('Courier',6*SCALE),anchor='nw')
        s.cv.create_text(200*SCALE,8*SCALE,text="TIME",fill=C['white'],font=('Courier',6*SCALE),anchor='nw')
        s.cv.create_text(200*SCALE,16*SCALE,text=f"{s.tm:03d}",fill=C['white'],font=('Courier',6*SCALE),anchor='nw')

if __name__=="__main__":rt=tk.Tk();Game(rt);rt.mainloop()
