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
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)

# Project constants
RESOURCE_FOLDER = "resources"

# Engine settings
SCREEN_WIDTH = 1280  # 16 * 64 or 32 * 32 or 64 * 16
SCREEN_HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Zombie Kill v1.0"

TILESIZE = 64
GRIDWIDTH = SCREEN_WIDTH / TILESIZE
GRIDHEIGHT = SCREEN_HEIGHT / TILESIZE

# Map settings
WALLS_IMAGE_LAYER_INDEX = 1
ITEMS_IMAGE_LAYER_INDEX = 2

# Player settings
PLAYER_HEALTH = 100
PLAYER_STAMINA = 100
PLAYER_SPEED = 280
PLAYER_ATTACK_DAMAGE = 5
PLAYER_RUN_SPEED = 500
PLAYER_ROT_SPEED = 2
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
PLAYER_POINTS_PER_MOB_KILLED = 10
BARREL_OFFSET = vec(30, 10)

STAMINA_REGEN = "STAMINA_REGEN"
STAMINA_LOSS = "STAMINA_LOSS"

PLAYER_RATES = {SpriteState.IDLE: 50,
                SpriteState.WALK: 50,
                SpriteState.RUN: 10,
                SpriteState.ATTACK: 20,
                SpriteState.JUMP: 10,
                SpriteState.JUMPATTACK: 10,
                SpriteState.DEAD: 70,
                STAMINA_REGEN: 200,
                STAMINA_LOSS: 1}

PLAYER_STATES_SPRITE_CNT = {SpriteState.IDLE: 10,
                            SpriteState.WALK: 10,
                            SpriteState.RUN: 10,
                            SpriteState.ATTACK: 10,
                            SpriteState.JUMP: 10,
                            SpriteState.JUMPATTACK: 10,
                            SpriteState.DEAD: 10, }

PLAYER_IMG_HEIGHT = 120

# Gun settings
BULLET_IMG = RESOURCE_FOLDER + '/bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 1000
BULLET_RATE = 150
KICKBACK = 200
GUN_SPREAD = 5
BULLET_DAMAGE = 10

# Mob settings
MOB_SPEED = 100
MOB_RUN_SPEED = 300
MOB_ROT_SPEED = 2
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_ATTACK_DAMAGE = 0.5
MOB_STAMINA = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20

MOB_WALK_RATE = 10
MOB_RUN_RATE = 10

MOB_RATES = {SpriteState.IDLE: 50,
             SpriteState.WALK: 50,
             SpriteState.RUN: 10,
             SpriteState.ATTACK: 150,
             SpriteState.DEAD: 100,
             STAMINA_REGEN: 100,
             STAMINA_LOSS: 5}

MOB_STATES_SPRITE_CNT = {SpriteState.IDLE: 15,
                         SpriteState.WALK: 10,
                         SpriteState.RUN: 0,
                         SpriteState.ATTACK: 8,
                         SpriteState.DEAD: 12}

MOB_IMG_WIDTH = 100
