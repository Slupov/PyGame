import pygame as pg
from enum import Enum

vec = pg.math.Vector2


class SpriteState(Enum):
    IDLE = 0,
    WALK = 1,
    RUN = 2,
    ATTACK = 3,
    JUMP = 4,
    JUMPATTACK = 5,
    DEAD = 6


# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)

# Project constants
RESOURCE_FOLDER = "resources"

# Engine settings
WIDTH = 1280  # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player settings
PLAYER_HEALTH = 100
PLAYER_SPEED = 280
PLAYER_ROT_SPEED = 2
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)

PLAYER_RATES = {SpriteState.IDLE: 10,
                SpriteState.WALK: 10,
                SpriteState.RUN: 10,
                SpriteState.ATTACK: 10,
                SpriteState.JUMP: 10,
                SpriteState.JUMPATTACK: 10,
                SpriteState.DEAD: 10, }

# Gun settings
BULLET_IMG = RESOURCE_FOLDER + '/bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 150
KICKBACK = 200
GUN_SPREAD = 5
BULLET_DAMAGE = 10

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEED = 150
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20

MOB_WALK_RATE = 10
MOB_RUN_RATE = 10

MOB_RATES = {SpriteState.IDLE: 10,
             SpriteState.WALK: 20,
             SpriteState.RUN: 10,
             SpriteState.ATTACK: 10,
             SpriteState.JUMP: 10,
             SpriteState.JUMPATTACK: 10,
             SpriteState.DEAD: 10, }
