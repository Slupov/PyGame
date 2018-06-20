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
    roamRectW = 300
    roamRectH = 300
    imgScaleFactor = nWidth / MOB_IMG_WIDTH

    def __init__(self, game):
        super(Mob, self).__init__(game, 0, 0)
        self.gender = self.genders[randint(0, 1)]
        self.rates = MOB_RATES

        self.health = MOB_HEALTH
        self.stamina = MOB_STAMINA
        self.staminaLossRate = self.rates[STAMINA_LOSS]
        self.staminaRegenerateRate = self.rates[STAMINA_REGEN]
        self.initImages()
        self.last_shot = 0
        self.roamRect = None
        self.spawn()
        self.deathFrames = 0
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
        self.rect = self.image.get_rect()
        self.mask = pg.mask.from_surface(self.image)

    def spawn(self):
        rightPos = False

        x = None
        y = None

        while not rightPos:
            x = randint(0, self.game.map_rect.width / TILESIZE)
            y = randint(0, self.game.map_rect.height / TILESIZE)

            self.pos = vec(x, y) * TILESIZE
            self.rect.center = self.pos

            if not pg.sprite.spritecollide(self, self.game.walls, False, pg.sprite.collide_rect):
                rightPos = True

        self.roamRect = pg.Rect(
            (x * TILESIZE - self.roamRectW / 2, y * TILESIZE - self.roamRectH / 2),
            (self.roamRectW, self.roamRectW))

    def setState(self, state):
        if self.state == SpriteState.DEAD:
            return

        self.stateSpritesCount = MOB_STATES_SPRITE_CNT[state]
        super(Mob, self).setState(state)

        self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)

        if self.state == SpriteState.WALK:
            self.velocity = vec(MOB_SPEED, 0).rotate(-self.rot)

        elif self.state == SpriteState.RUN:
            self.velocity = vec(MOB_RUN_SPEED, 0).rotate(-self.rot)

    def handleState(self):
        super(Mob, self).handleState()

        if (self.state == SpriteState.WALK or self.state == SpriteState.IDLE) and abs(
                self.pos.x - self.game.player.pos.x) > 5:
            if self.walkDirection == -1:
                self.image = pg.transform.flip(self.image, True, False)
                self.mask = pg.mask.from_surface(self.image)

        # check for attack on player
        if self.state == SpriteState.ATTACK:
            playerMobHit = pg.sprite.collide_mask(self.game.player, self)

            if playerMobHit:
                if self.game.player.health <= 0:
                    return
                self.game.player.take_hit(MOB_ATTACK_DAMAGE, self)

    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.velocity * self.game.dt

        if self.state != SpriteState.DEAD:
            self.roam()

        self.handleState()

        # regenerate stamina
        if self.state != SpriteState.RUN:
            self.regenerate_stamina()
            if self.stamina >= MOB_STAMINA:
                self.stamina = MOB_STAMINA

    def roam(self):
        if self.roamRect.colliderect(self.game.player.rect):
            if pg.sprite.spritecollide(self, self.game.walls, False, pg.sprite.collide_rect):
                self.velocity = vec(0, 0)
            else:
                self.chase_and_attack_player()
        else:
            self.setState(SpriteState.WALK)

            collide = pg.sprite.spritecollideany(self, self.game.walls)
            if collide:
                if collide.rect.x < self.pos.x:
                    self.walkDirection = 1
                    self.roamRect.x = collide.rect.x + TILESIZE
                else:
                    self.walkDirection = -1
                    self.roamRect.x = self.roamRect.x - (self.roamRect.width - (collide.rect.x - self.roamRect.x))

            if self.rect.x > self.roamRect.x + self.roamRect.width:
                self.walkDirection = -1
            elif self.rect.x <= self.roamRect.x:
                self.walkDirection = 1

        self.velocity *= self.walkDirection

    def chase_and_attack_player(self):
        if pg.sprite.collide_mask(self, self.game.player):
            self.setState(SpriteState.ATTACK)
        else:
            self.setState(SpriteState.WALK)

            if self.pos.x > self.game.player.pos.x:
                self.pos.x -= 1
                self.walkDirection = -1

            elif self.pos.x < self.game.player.pos.x:
                self.pos.x += 1
                self.walkDirection = 1

            if self.pos.y < self.game.player.pos.y:
                self.pos.y += 1
            elif self.pos.y > self.game.player.pos.y:
                self.pos.y -= 1

            self.roamRect.center = self.pos
            self.rect.center = self.pos
            # self.mask = pg.mask.from_surface(self.image)

    def take_hit(self, damage, hitting_sprite):
        super(Mob, self).take_hit(damage, hitting_sprite)

        # add kickback
        kbVec = self.collision_normal(hitting_sprite.mask, self.mask, hitting_sprite.pos, self.pos)
        if kbVec:
            self.velocity = vec(kbVec[0] * 2, kbVec[1] * 2).rotate(-self.rot)

        if self.health <= 0:
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
