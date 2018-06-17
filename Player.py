# @brief
# @date 17.06.18
# @author Stoyan Lupov
from SpriteEntity import *
from PIL import Image

normalImage = Image.open(RESOURCE_FOLDER + "/knight/idle_(1).png")
nWidth, nHeight = normalImage.size


class Player(SpriteEntity):
    imgScaleFactor = nWidth / PLAYER_IMG_WIDTH

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.health = PLAYER_HEALTH
        self.stamina = PLAYER_STAMINA
        self.staminaLossRate = PLAYER_STAMINA_LOSS_RATE
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
        self.scaledSize = (PLAYER_IMG_WIDTH, int(nHeight / self.imgScaleFactor))

        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)
        self.rect = self.image.get_rect()

    def setState(self, state):
        self.stateSpritesCount = PLAYER_STATES_SPRITE_CNT[state]
        self.state = state

    def handleState(self):
        now = pg.time.get_ticks()
        diff = now - self.last_frame_change

        if diff > PLAYER_RATES[self.state]:
            self.last_frame_change = now
            self.frameIdx = (self.frameIdx + 1) % self.stateSpritesCount
            self.setFrame(self.frameIdx)

        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

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
            self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

        if keys[pg.K_q]:
            self.setState(SpriteState.ATTACK)

        if keys[pg.K_r]:
            self.velocity = vec(PLAYER_SPEED + 500, 0).rotate(-self.rot)
            self.setState(SpriteState.RUN)

        if keys[pg.K_z]:
            self.setState(SpriteState.DEAD)

        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if now - self.last_shot > BULLET_RATE:
                self.last_shot = now
                dir = vec(1, 0).rotate(-self.rot)
                pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
                Bullet(self.game, pos, dir)
                self.velocity = vec(-KICKBACK, 0).rotate(-self.rot)

        self.handleState()
        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

    def update(self):
        self.get_keys()
        self.image = pg.transform.rotate(pg.transform.
                                         scale(self.imageOriginal, self.scaledSize), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt
