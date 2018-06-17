# @brief
# @date 17.06.18
# @author Stoyan Lupov
from SpriteEntity import *
from PIL import Image

normalImage = Image.open(RESOURCE_FOLDER + "/knight/idle_(1).png")
nWidth, nHeight = normalImage.size

playerImages = {}


def load_player_images():
    for (state, spriteCnt) in PLAYER_STATES_SPRITE_CNT.items():
        playerImages[state.name] = list()
        for x in range(1, spriteCnt + 1):
            img = pg.image \
                .load(RESOURCE_FOLDER + "/knight/" + state.name.lower() +
                      "_(" + str(x) + ").png").convert_alpha()

            playerImages[state.name].append(img)


class Player(SpriteEntity):
    imgScaleFactor = nWidth / PLAYER_IMG_WIDTH

    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.health = PLAYER_HEALTH
        self.stamina = PLAYER_STAMINA
        self.staminaLossRate = PLAYER_RATES[STAMINA_LOSS]
        self.staminaRegenerateRate = PLAYER_RATES[STAMINA_REGEN]

        self.last_shot = 0
        self.collideRect = pg.rect.Rect((0, 0), (70, 70))
        self.collideRect.center=self.rect.center

    def initImages(self):
        self.images = playerImages
        self.imageOriginal = self.images[self.state.name][self.frameIdx]
        self.scaledSize = (PLAYER_IMG_WIDTH, int(nHeight / self.imgScaleFactor))

        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)
        self.rect = self.image.get_rect()
        self.collideRect = pg.rect.Rect((0, 0), (50, 50))
        self.collideRect.midbottom = self.rect.midbottom

    def setState(self, state):
        super().setState(state)
        self.stateSpritesCount = PLAYER_STATES_SPRITE_CNT[self.state]

    def handleState(self):
        super().handleState()
        now = pg.time.get_ticks()
        diff = now - self.last_frame_change

        # handle state animation
        if diff > PLAYER_RATES[self.state]:
            self.last_frame_change = now
            self.frameIdx = (self.frameIdx + 1) % self.stateSpritesCount
            self.setFrame(self.frameIdx)
            self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

    def wall_collision(self):
        for wall in self.game.walls:
            if self.collideRect.colliderect(wall):
                self.pos -= self.velocity * self.game.dt
                self.rect.center = self.pos
                self.collideRect.midbottom = self.rect.midbottom
                break

    def get_keys(self):
        self.rot_speed = 0
        self.velocity = vec(0, 0)
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot = (self.rot + PLAYER_ROT_SPEED) % 360
            self.collided = False

        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot = (self.rot - PLAYER_ROT_SPEED) % 360
            self.collided = False

        if keys[pg.K_UP] or keys[pg.K_w]:
            self.setState(SpriteState.WALK)
            self.velocity = vec(PLAYER_SPEED, 0).rotate(-self.rot)

        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.setState(SpriteState.WALK)
            self.velocity = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
            # self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

        if keys[pg.K_q]:
            self.setState(SpriteState.ATTACK)

        if keys[pg.K_r]:
            self.setState(SpriteState.RUN)
            if self.state == SpriteState.RUN:
                self.velocity = vec(PLAYER_RUN_SPEED, 0).rotate(-self.rot)

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

        self.pos += self.velocity * self.game.dt

        # regenerate stamina
        if self.state != SpriteState.RUN:
            self.regenerate_stamina()
            if self.stamina >= PLAYER_STAMINA:
                self.stamina = PLAYER_STAMINA

        self.rect.center = self.pos
        self.collideRect.midbottom = self.rect.midbottom
        self.wall_collision()
