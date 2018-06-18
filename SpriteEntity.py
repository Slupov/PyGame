from random import uniform

from Settings import *

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
        self.health = 0
        self.stamina = 0
        self.staminaLossRate = 0
        self.staminaRegenerateRate = 0
        self.last_stamina_reg = 0

        self.scaledSize = (0, 0)
        self.initImages()

    # one has to call a scaling function after setFrame
    def setFrame(self, frame):
        frame = frame % self.stateSpritesCount
        self.frameIdx = frame
        self.imageOriginal = self.images[self.state.name][frame]
        self.image = self.imageOriginal

    def setState(self, state):
        if state == SpriteState.RUN and self.stamina < self.staminaLossRate:
            state = SpriteState.WALK

        self.state = state

    def get_keys(self):
        pass

    def updateVelocity(self):
        pass

    def initImages(self):
        pass

    def handleState(self):
        if self.state == SpriteState.RUN:
            self.stamina -= self.staminaLossRate

    def handleEvent(self, event):
        pass

    def update(self):
        pass

    def regenerate_stamina(self):
        now = pg.time.get_ticks()
        if now - self.last_stamina_reg > self.staminaRegenerateRate:
            self.last_stamina_reg = now
            self.stamina += 1

    def wall_collision(self):
        pass

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


class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()

        self.image = img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x*TILESIZE
        self.rect.y = y*TILESIZE
        self.mask = pg.mask.from_surface(self.image)
