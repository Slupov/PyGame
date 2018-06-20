from random import uniform
from Settings import *
from Tilemap import collide_hit_rect

vec = pg.math.Vector2


class SpriteEntity(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        """
            Constructs a sprite entity object and initializes it with starting values
            :param game: a reference to the engine through which sprite groups are obtained
            (for collision detection)
        """

        self.game = game
        self.groups = game.all_sprites

        pg.sprite.Sprite.__init__(self, self.groups)

        # sprite variables
        self.stateSpritesCount = 0
        self.state = SpriteState.IDLE

        self.rates = {}

        # image variables
        self.images = {}
        self.imageOriginal = None
        self.image = None

        self.rect = None
        self.mask = None

        # current frame of state animation
        self.frameIdx = 0

        # tick when last frame change happened
        self.last_frame_change = 0

        # physics variables
        self.pos = vec(x, y) * TILESIZE
        self.rot = 0
        self.velocity = vec(0, 0)

        # statistics variables
        self.health = 0
        self.stamina = 0

        self.staminaLossRate = 0
        self.staminaRegenerateRate = 0
        self.last_stamina_reg = 0

        # 1 when walking forwards and -1 when backwards
        self.walkDirection = 1
        self.scaledSize = (0, 0)

    def setFrame(self, frame):
        """
            Changes the image of the sprite by a given frame index. Takes into account
            the state the object is currently in
            :param frame: the next frame animation index
        """

        frame = frame % self.stateSpritesCount
        self.frameIdx = frame
        self.imageOriginal = self.images[self.state.name][frame]
        self.image = self.imageOriginal

    def setState(self, state):
        """
            Sets the state of the sprite
        """
        if self.state != state:
            self.setFrame(0)
            self.state = state

            if state == SpriteState.IDLE:
                self.velocity = vec(0, 0).rotate(-self.rot)

    def handleState(self):
        """
            Applies certain logic depending on the sprite's state
        """
        if self.state == SpriteState.RUN:
            self.stamina -= self.staminaLossRate

        now = pg.time.get_ticks()
        diff = now - self.last_frame_change

        # handle state animation
        if diff > self.rates[self.state]:
            self.last_frame_change = now

            if self.state != SpriteState.DEAD:
                self.frameIdx = (self.frameIdx + 1) % self.stateSpritesCount
            else:
                self.velocity = vec(0, 0)
                self.frameIdx += 1

                # reached last death frame idx
                if self.frameIdx == self.stateSpritesCount - 1:
                    self.setFrame(self.frameIdx)
                    self.die()
                    return

            self.setFrame(self.frameIdx)
            self.image = pg.transform.scale(self.imageOriginal, self.scaledSize)
            self.mask = pg.mask.from_surface(self.image)

    def collision_normal(self, left_mask, right_mask, left_pos, right_pos):
        """
            Calculates the direction of the kickback after a collision
        """

        def vadd(x, y):
            return [x[0] + y[0], x[1] + y[1]]

        def vsub(x, y):
            return [x[0] - y[0], x[1] - y[1]]

        def vdot(x, y):
            return x[0] * y[0] + x[1] * y[1]

        offset = list(map(int, vsub(left_pos, right_pos)))

        overlap = left_mask.overlap_area(right_mask, offset)

        if overlap == 0:
            return

        """Calculate collision normal"""

        nx = (left_mask.overlap_area(right_mask, (offset[0] + 1, offset[1])) -
              left_mask.overlap_area(right_mask, (offset[0] - 1, offset[1])))
        ny = (left_mask.overlap_area(right_mask, (offset[0], offset[1] + 1)) -
              left_mask.overlap_area(right_mask, (offset[0], offset[1] - 1)))
        if nx == 0 and ny == 0:
            """One sprite is inside another"""
            return

        n = [nx, ny]
        return n

    def regenerate_stamina(self):
        """
            Regenerates stamina after a certain rate (in ticks) has passed
        """
        now = pg.time.get_ticks()
        if now - self.last_stamina_reg > self.staminaRegenerateRate:
            self.last_stamina_reg = now
            self.stamina += 1

    def collide_with_walls(self, sprite, group, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centerx > sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
                if hits[0].rect.centerx < sprite.hit_rect.centerx:
                    sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
                sprite.velocity.x = 0
                sprite.hit_rect.centerx = sprite.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
            if hits:
                if hits[0].rect.centery > sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
                if hits[0].rect.centery < sprite.hit_rect.centery:
                    sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
                sprite.velocity.y = 0
                sprite.hit_rect.centery = sprite.pos.y

    def take_hit(self, damage, hitting_sprite):
        """
            Lowers a sprites health
            :param damage: the amount of HP taken from the hit
            :param hitting_sprite - the sprite that hit self
        """
        if self.state != SpriteState.DEAD:
            self.health -= damage

    # ----------------- "abstract" functions -----------------
    def initImages(self):
        """
            Sets images dictionary to a previously loaded with resources dictionary
        """
        pass

    def update(self):
        """
            Update internals based on current state
        """
        pass

    def die(self):
        """
            Removes object from sprite groups
        """
        pass


class Bullet(pg.sprite.Sprite):
    def __init__(self, engine, pos, dir):
        self.groups = engine.all_sprites, engine.bullets
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = engine
        self.image = pg.image.load(RESOURCE_FOLDER + "/bullet.png").convert_alpha()
        self.mask = pg.mask.from_surface(self.image)

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

        # check if hits a zombie
        mobs_hits = pg.sprite.spritecollide(self, self.game.mobs, False, pg.sprite.collide_mask)

        if mobs_hits:
            self.game.all_sprites.remove(self)
            self.game.bullets.remove(self)

        for hitMob in mobs_hits:
            hitMob.take_hit(BULLET_DAMAGE, self)

            if hitMob.health <= 0:
                self.game.player.points += PLAYER_POINTS_PER_MOB_KILLED_BULLET

        # check if hits wall
        if pg.sprite.spritecollide(self, self.game.player_obs, False, pg.sprite.collide_rect):
            self.game.all_sprites.remove(self)
            self.game.bullets.remove(self)


class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, img):
        super().__init__()

        self.image = img
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE
