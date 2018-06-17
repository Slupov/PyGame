# @brief
# @date 17.06.18
# @author Stoyan Lupov
from SpriteEntity import *
from random import randint
from PIL import Image

normalImage = Image.open(RESOURCE_FOLDER + "/zombie/male/idle_(1).png")
nWidth, nHeight = normalImage.size


class Mob(SpriteEntity):
    genders = ["female", "male"]
    roamRectW = 50
    roamRectH = 50
    imgScaleFactor = nWidth / MOB_IMG_WIDTH

    def __init__(self, game):
        self.gender = self.genders[randint(0, 1)]

        super().__init__(game, 0, 0)
        self.health = MOB_HEALTH
        self.stamina = MOB_STAMINA
        self.staminaLossRate = MOB_RATES[STAMINA_LOSS]
        self.staminaRegenerateRate = MOB_RATES[STAMINA_REGEN]

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
        self.scaledSize = (MOB_IMG_WIDTH, int(nHeight / self.imgScaleFactor))

        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

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

        now = pg.time.get_ticks()
        diff = now - self.last_frame_change

        # handle state animation
        if diff > MOB_RATES[self.state]:
            self.last_frame_change = now
            self.frameIdx = (self.frameIdx + 1) % self.stateSpritesCount
            self.setFrame(self.frameIdx)
            self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

    def updateVelocity(self):
        if self.state == SpriteState.WALK:
            self.velocity = vec(PLAYER_SPEED, 0).rotate(-self.rot)

    def update(self):
        self.updateVelocity()
        self.image = pg.transform.rotate(pg.transform.scale(self.imageOriginal, self.scaledSize), self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt

        self.handleState()
        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

        # regenerate stamina
        if self.state != SpriteState.RUN:
            self.regenerate_stamina()
            if self.stamina >= MOB_STAMINA:
                self.stamina = MOB_STAMINA

    def roam(self):
        pass

    def chase_player(self):
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

        # if self.health < MOB_HEALTH:
        #     pg.draw.rect(self.image, col, self.health_bar)

        pg.draw.rect(self.image, col, self.health_bar)

    def draw_stamina(self):
        col = BLUE
        width = int(self.rect.width * self.stamina / MOB_STAMINA)

        self.stamina_bar = pg.Rect(0, 10, width, 7)

        # if self.stamina < MOB_STAMINA:
        #     pg.draw.rect(self.image, col, self.stamina_bar)

        pg.draw.rect(self.image, col, self.stamina_bar)
