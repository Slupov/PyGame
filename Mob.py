# @brief
# @date 17.06.18
# @author Stoyan Lupov
from SpriteEntity import *
from random import randint


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
