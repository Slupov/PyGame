from random import randint
from random import uniform

from settings import *
from pytmx import pytmx

vec = pg.math.Vector2


class SpriteEntity(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites

        pg.sprite.Sprite.__init__(self, self.groups)

        self.stateSpritesCount = 0

        self.state = None
        self.setState(SpriteState.IDLE)

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

        self.initImages()

    def setFrame(self, frame):
        frame = frame % self.stateSpritesCount
        self.frameIdx = frame
        self.imageOriginal = self.images[self.state.name][frame]
        self.image = self.imageOriginal

    #     one has to call a scaling function after setFrame

    def setState(self, state):
        pass

    def get_keys(self):
        pass

    def updateVelocity(self):
        pass

    def initImages(self):
        pass

    def handleState(self):
        now = pg.time.get_ticks()
        diff = now - self.last_frame_change

        if diff > PLAYER_RATES[self.state]:
            self.last_frame_change = now
            self.frameIdx = (self.frameIdx + 1) % self.stateSpritesCount

            self.setFrame(self.frameIdx)

    def update(self):
        pass


class Player(SpriteEntity):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.last_shot = 0

    def initImages(self):
        # init images matrix - every row corresponds to a sprite state
        for (state, spriteCnt) in PLAYER_STATES_SPRITE_CNT.items():
            self.images[state.name] = list()
            for x in range(1, spriteCnt + 1):
                img = pg.image \
                    .load(RESOURCE_FOLDER + "/knight/" + state.name.lower() + "_(" + str(x) + ").png").convert_alpha()
                self.images[state.name].append(img)

        self.imageOriginal = self.images[self.state.name][self.frameIdx]
        self.image = pg.transform.scale(self.imageOriginal, (100, 100))

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

        self.handleState()
        self.image = pg.transform.scale(self.imageOriginal, (100, 100))

    def update(self):
        self.get_keys()
        self.image = pg.transform.rotate(pg.transform.
                                         scale(self.imageOriginal, (100, 100)), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt
        self.handleState()


class Mob(SpriteEntity):
    genders = ["female", "male"]
    roamRectW = 50
    roamRectH = 50

    def __init__(self, game):
        self.gender = self.genders[randint(0, 1)]

        super().__init__(game, 0, 0)
        self.initImages()
        self.last_shot = 0
        self.spawn()
        self.roamRect = pg.Rect(self.pos, (self.roamRectW, self.roamRectW))

    def initImages(self):
        # init images matrix - every row corresponds to a sprite state
        for (state, spriteCnt) in MOB_STATES_SPRITE_CNT.items():
            self.images[state.name] = list()
            for x in range(1, spriteCnt + 1):
                img = pg.image \
                    .load(RESOURCE_FOLDER + "/zombie/" +
                          self.gender + "/" +
                          state.name.lower() +
                          "_(" +
                          str(x) +
                          ").png").convert_alpha()
                self.images[state.name].append(img)

        self.imageOriginal = self.images[self.state.name][self.frameIdx]
        self.image = pg.transform.scale(self.imageOriginal, (100, 100))

    def spawn(self):
        x = randint(0, self.game.map_rect.width / TILESIZE)
        y = randint(0, self.game.map_rect.height / TILESIZE)

        # TODO Stoyan Lupov 16-06-2018 Check if this lands on a wall or other object and generate again if so
        self.pos = vec(x, y) * TILESIZE

    def setState(self, state):
        self.stateSpritesCount = MOB_STATES_SPRITE_CNT[state]
        self.state = state

    def handleState(self):
        super().handleState()

        # if self.state == SpriteState.IDLE:
        #     self.roam()
        # elif self.state == SpriteState.WALK:
        #     pass
        # elif self.state == SpriteState.RUN:
        #     pass
        # elif self.state == SpriteState.ATTACK:
        #     pass
        # elif self.state == SpriteState.DEAD:
        #     pass

    def updateVelocity(self):
        if self.state == SpriteState.WALK:
            self.velocity = vec(PLAYER_SPEED, 0).rotate(-self.rot)

    def update(self):
        self.updateVelocity()
        self.image = pg.transform.rotate(pg.transform.scale(self.imageOriginal, (100, 100)), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt

        self.handleState()
        self.image = pg.transform.scale(self.imageOriginal, (100, 100))

    def roam(self):
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
