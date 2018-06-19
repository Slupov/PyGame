# @brief
# @date 17.06.18
# @author Stoyan Lupov
from SpriteEntity import *
from random import randint
from PIL import Image

normalImage = Image.open(RESOURCE_FOLDER + "/zombie/male/idle_(1).png")
nWidth, nHeight = normalImage.size

femaleMobImages = {}
maleMobImages = {}


def load_mob_images():
    for (state, spriteCnt) in MOB_STATES_SPRITE_CNT.items():
        femaleMobImages[state.name] = list()
        maleMobImages[state.name] = list()

        for x in range(1, spriteCnt + 1):
            img = pg.image \
                .load(RESOURCE_FOLDER + "/zombie/male/" + state.name.lower() +
                      "_(" + str(x) + ").png").convert_alpha()

            maleMobImages[state.name].append(img)

            img = pg.image \
                .load(RESOURCE_FOLDER + "/zombie/female/" + state.name.lower() +
                      "_(" + str(x) + ").png").convert_alpha()

            femaleMobImages[state.name].append(img)


class Mob(SpriteEntity):
    genders = ["female", "male"]
    roamRectW = 50
    roamRectH = 50
    imgScaleFactor = nWidth / MOB_IMG_WIDTH

    def __init__(self, game):
        super(Mob, self).__init__(game, 0, 0)
        self.gender = self.genders[randint(0, 1)]

        self.health = MOB_HEALTH
        self.stamina = MOB_STAMINA
        self.staminaLossRate = MOB_RATES[STAMINA_LOSS]
        self.staminaRegenerateRate = MOB_RATES[STAMINA_REGEN]
        self.initImages()
        self.last_shot = 0
        self.spawn()
        self.deathFrames = 0
        self.roamRect = pg.Rect(self.pos, (self.roamRectW, self.roamRectW))
        self.initImages()
        self.setState(SpriteState.IDLE)

    def initImages(self):
        if self.gender == 'female':
            self.images = femaleMobImages
        else:
            self.images = maleMobImages

        self.imageOriginal = self.images[self.state.name][self.frameIdx]
        self.scaledSize = (MOB_IMG_WIDTH, int(nHeight / self.imgScaleFactor))
        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)
        self.mask = pg.mask.from_surface(self.image)

    def setState(self, state):
        self.stateSpritesCount = MOB_STATES_SPRITE_CNT[state]
        super(Mob, self).setState(state)
        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

    def handleState(self):
        super(Mob, self).handleState()

        # check for attack on player
        if self.state == SpriteState.ATTACK:
            playerMobHit = pg.sprite.collide_mask(self.game.player, self)

    def spawn(self):
        x = randint(0, self.game.map_rect.width / TILESIZE)
        y = randint(0, self.game.map_rect.height / TILESIZE)

        # TODO Stoyan Lupov 16-06-2018 Check if this lands on a wall or other object and generate again if so
        self.pos = vec(x, y) * TILESIZE

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt

        # TODO Stoyan Lupov 17-06-2018 Check if player is inside roam rect and do stuff if so, else roam
        # self.roam()

        self.velocity = vec(0, 0)
        self.handleState()

        self.mask = pg.mask.from_surface(self.image)

        # regenerate stamina
        if self.state != SpriteState.RUN:
            self.regenerate_stamina()
            if self.stamina >= MOB_STAMINA:
                self.stamina = MOB_STAMINA


    def roam(self):
        # if self.state != SpriteState.WALK:
        #     self.setState(SpriteState.WALK)

        # uncomment velocity so mobs could walk
        # self.velocity = vec(MOB_SPEED, 0).rotate(-self.rot)

        pass

    def chase_player(self):
        pass

    def take_hit(self, damage):
        super(Mob, self).take_hit(damage)

        # add kickback
        kbVec = self.collision_normal(self.game.player.mask, self.mask, self.game.player.pos, self.pos)
        if kbVec:
            self.velocity = vec(kbVec[0] * 2, kbVec[1] * 2).rotate(-self.rot)

        if self.health == 0:
            self.setState(SpriteState.DEAD)

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

    def draw_stamina(self):
        col = BLUE
        width = int(self.rect.width * self.stamina / MOB_STAMINA)

        self.stamina_bar = pg.Rect(0, 10, width, 7)

        if self.stamina < MOB_STAMINA:
            pg.draw.rect(self.image, col, self.stamina_bar)

    def die(self):
        self.game.mobs.remove(self)
        self.game.all_sprites.remove(self)
