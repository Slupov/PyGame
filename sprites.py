from random import randint
from random import uniform

from settings import *

vec = pg.math.Vector2


class SpriteEntity(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites

        pg.sprite.Sprite.__init__(self, self.groups)

        self.state = SpriteState.IDLE
        self.stateSpritesCount = 0

        self.images = {}
        self.imageOriginal = None
        self.image = None

        # current frame of state animation
        self.frameIdx = 0
        self.last_frame_change = 0  # tick when last frame change happened

        self.rect = None

        self.pos = vec(x, y) * TILESIZE
        self.rot = 0

        self.velocity = vec(0, 0)
        self.health = 100

        # init images matrix - every row corresponds to a sprite state
        for name, member in SpriteState.__members__.items():
            self.images[name] = list()
            for x in range(1, 11):
                img = pg.image \
                    .load(RESOURCE_FOLDER + "/knight/" + name.lower() + "_(" + str(x) + ").png").convert_alpha()
                self.images[name].append(img)

    def setFrame(self, frame):
        frame = frame % self.stateSpritesCount
        self.frameIdx = frame
        self.imageOriginal = self.images[self.state.name][frame]

    def setState(self, state):
        pass

    def get_keys(self):
        pass

    def update(self):
        pass


class Player(SpriteEntity):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.imageOriginal = pg.image.load(RESOURCE_FOLDER + "/knight/idle_(1).png").convert_alpha()
        self.image = pg.transform.scale(self.imageOriginal, (100, 100))
        self.last_shot = 0

    def setState(self, state):
        self.stateSpritesCount = PLAYER_STATES_SPRITE_CNT[state]
        self.state = state

    def get_keys(self):
        self.rot_speed = 0
        self.velocity = vec(0, 0)

        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot = (self.rot + PLAYER_ROT_SPEED) % 360

        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot = (self.rot - PLAYER_ROT_SPEED) % 360

        if keys[pg.K_UP] or keys[pg.K_w]:
            self.setState(SpriteState.WALK)
            self.velocity = vec(PLAYER_SPEED, 0).rotate(-self.rot)
            self.image = pg.transform.scale(self.imageOriginal, (100, 100))

            now = pg.time.get_ticks()
            diff = now - self.last_frame_change

            if diff > PLAYER_RATES[self.state]:
                self.last_frame_change = now
                self.frameIdx = (self.frameIdx + 1) % 10
                self.setFrame(self.frameIdx)
                self.image = self.imageOriginal

        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.velocity = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            self.image = pg.transform.scale(self.imageOriginal, (100, 100))

        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, pos, dir)
                self.velocity = vec(-KICKBACK, 0).rotate(-self.rot)

    def update(self):
        self.get_keys()
        self.image = pg.transform.rotate(pg.transform.scale(self.imageOriginal, (100, 100)), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt


class Mob(SpriteEntity):
    genders = ["female", "male"]

    def __init__(self, game):
        super().__init__(game, 0, 0)

        self.gender = self.genders[randint(0, 1)]
        self.imageOriginal = pg.image.load(RESOURCE_FOLDER + "/zombie/" + self.gender + "/idle_(1).png").convert_alpha()
        self.image = pg.transform.scale(self.imageOriginal, (100, 100))
        self.last_shot = 0
        self.spawn()

    def spawn(self):
        x = randint(0, SCREEN_WIDTH)
        y = randint(0, SCREEN_HEIGHT)

        # TODO Stoyan Lupov 16-06-2018 Check if this lands on a wall or other object and generate again if so
        self.pos = vec(x, y)

    def setState(self, state):
        self.stateSpritesCount = MOB_STATES_SPRITE_CNT[state]
        self.state = state

    def update(self):
        self.velocity = vec(0, 0)
        self.image = pg.transform.rotate(pg.transform.scale(self.imageOriginal, (100, 100)), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt

        pass

    def roam(self):
        pass

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED

        # width = int(self.rect.width * self.health / MOB_HEALTH)
        # self.health_bar = pg.Rect(0, 0, width, 7)
        # if self.health < MOB_HEALTH:
        #     pg.draw.rect(self.image, col, self.health_bar)


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
