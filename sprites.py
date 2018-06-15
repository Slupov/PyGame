import pygame as pg
from random import uniform
from settings import *
from enum import Enum

vec = pg.math.Vector2


class SpriteState(Enum):
    IDLE = 0,
    WALK = 1,
    RUN = 2,
    ATTACK = 3,
    JUMP = 4,
    JUMP_ATTACK = 5,
    DEAD = 6


class SpriteEntity(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites

        pg.sprite.Sprite.__init__(self, self.groups)

        self.state = SpriteState.IDLE

        self.images = {}
        self.imageOriginal = pg.image.load(RESOURCE_FOLDER + "/knight/Idle (1).png").convert_alpha()
        self.image = None

        self.rect = None

        self.pos = vec(x, y) * TILESIZE
        self.rot = 0

        self.velocity = vec(0, 0)
        self.health = 100

        # init images matrix - every row corresponds to a sprite state
        for name, member in SpriteState.__members__.items():
            self.images[name] = list()

    def setFrame(self, frame):
        self.image = self.images[self.state.name][frame]

    def setState(self, state):
        self.state = state

    def get_keys(self):
        pass

    def update(self):
        pass


class Player(SpriteEntity):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.image = pg.transform.scale(self.imageOriginal, (100, 100))
        self.last_shot = 0

    def get_keys(self):
        self.rot_speed = 0
        self.vel = vec(0, 0)

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot = (self.rot - PLAYER_ROT_SPEED) % 360

        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot = (self.rot + PLAYER_ROT_SPEED) % 360

        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot)
            self.image = pg.transform.scale(self.imageOriginal, (100, 100))

        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            self.image = pg.transform.scale(self.imageOriginal, (100, 100))

        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, pos, dir)
                self.vel = vec(-KICKBACK, 0).rotate(-self.rot)

    def update(self):
        self.get_keys()
        self.image = pg.transform.rotate(pg.transform.scale(self.imageOriginal,(100,100)), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt


class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = game.mob_img

    def update(self):
       pass

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED

        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, engine, pos, dir):
        self.groups = engine.all_sprites, engine.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = engine
        self.image = pg.image.load(RESOURCE_FOLDER + "/bullet.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir.rotate(spread) * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos

        if pg.time.get_ticks() - self.spawn_time > BULLET_LIFETIME:
            self.kill()
