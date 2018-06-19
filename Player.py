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
    maskScaleFactor = nWidth / 70

    def __init__(self, game, x, y):
        super(Player, self).__init__(game, x, y)
        self.health = PLAYER_HEALTH
        self.stamina = PLAYER_STAMINA
        self.staminaLossRate = PLAYER_RATES[STAMINA_LOSS]
        self.staminaRegenerateRate = PLAYER_RATES[STAMINA_REGEN]
        self.last_shot = 0
        self.hit_rect = None
        self.initImages()
        self.setState(SpriteState.IDLE)

    def initImages(self):
        self.images = playerImages
        self.imageOriginal = self.images[self.state.name][self.frameIdx]
        self.scaledSize = (PLAYER_IMG_WIDTH, int(nHeight / self.imgScaleFactor))
        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.mask = pg.mask.from_surface(self.image)

    def setState(self, state):
        self.stateSpritesCount = PLAYER_STATES_SPRITE_CNT[state]
        super(Player, self).setState(state)
        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

    def handleState(self):
        super(Player, self).handleState()

        if self.state == SpriteState.WALK:
            if self.walkDirection == 1:
                self.velocity = vec(PLAYER_SPEED, 0).rotate(-self.rot)
            else:
                self.velocity = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)
        elif self.state == SpriteState.RUN:
            self.velocity = vec(PLAYER_RUN_SPEED, 0).rotate(-self.rot)

        # check for attack on mob
        if self.state == SpriteState.ATTACK:
            for mob in self.game.mobs:
                playerMobHit = pg.sprite.collide_mask(self, mob)

                # if no hits were blown on that mob
                if playerMobHit:
                    mob.take_hit(5)

    def get_keys(self):
        self.velocity = vec(0, 0)
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot = (self.rot + PLAYER_ROT_SPEED) % 360

        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot = (self.rot - PLAYER_ROT_SPEED) % 360

        if keys[pg.K_UP] or keys[pg.K_w]:
            self.walkDirection = 1

            if keys[pg.K_LSHIFT]:
                if self.stamina > 0:
                    self.setState(SpriteState.RUN)
                else:
                    self.setState(SpriteState.WALK)
            else:
                self.setState(SpriteState.WALK)

        elif keys[pg.K_DOWN] or keys[pg.K_s]:
            self.walkDirection = -1

            self.setState(SpriteState.WALK)
            self.velocity = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot)

        elif keys[pg.K_q]:
            self.setState(SpriteState.ATTACK)

        elif keys[pg.K_z]:
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

    def update(self):
        self.get_keys()
        self.image = pg.transform.rotate(pg.transform.
                                         scale(self.imageOriginal, self.scaledSize), self.rot)
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt
        self.hit_rect.centerx = self.pos.x
        self.collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center
        # regenerate stamina
        if self.state != SpriteState.RUN:
            self.regenerate_stamina()
            if self.stamina >= PLAYER_STAMINA:
                self.stamina = PLAYER_STAMINA

    def die(self):
        self.game.all_sprites.remove(self)
