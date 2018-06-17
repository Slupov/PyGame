import sys

from Tilemap import *
from Mob import *
from Player import *

# init fonts module
pg.font.init()
myfont = pg.font.SysFont('Comic Sans MS', 20)


# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0

    BAR_LENGTH = 100
    BAR_HEIGHT = 20

    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)

    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED

    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


def draw_player_stamina(surf, x, y, pct):
    if pct < 0:
        pct = 0

    BAR_LENGTH = 100
    BAR_HEIGHT = 20

    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)

    col = BLUE

    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


def draw_fps_counter(surf, x, y, fps):
    textsurface = myfont.render("FPS: {:.2f}".format(fps), False, (0, 0, 0))
    surf.blit(textsurface, (x, y))


def load_images():
    load_mob_images()
    load_player_images()


class Engine:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def load_data(self):
        load_images()
        self.map = TiledMap(RESOURCE_FOLDER + '/maps/level1.tmx')
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        pass

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        # Create walls group and add all walls from their layer
        self.walls = pg.sprite.Group()
        wall_layer = self.map.game_map.get_layer_by_name('walls')
        for x, y, image in wall_layer:
            if image:
                surf_img = self.map.game_map.get_tile_image(x, y, 1)

                wall = Wall(x, y, surf_img)
                print(wall.rect)
                self.walls.add(wall)

        self.mobs = pg.sprite.Group()

        mobsCnt = randint(20, 30)

        # mob = Mob(self)
        # for x in range(0, mobsCnt):
        #     print(mob.pos)
        #     mob = Mob(self)

        self.bullets = pg.sprite.Group()
        self.player = Player(self, 5, 5)
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        # game loop - set self.playing = False to end the game
        self.running = True
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.handleEvent()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def handleEvent(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
            if event.type == pg.KEYUP:
                self.player.setState(SpriteState.IDLE)

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)





        # mobs hit player
        # hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        # for hit in hits:
        #     self.player.health -= MOB_DAMAGE
        #     hit.vel = vec(0, 0)
        #     if self.player.health <= 0:
        #         self.running = False
        #
        # if hits:
        #     self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)

        # bullets hit mobs
        # hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)

        # for hit in hits:
        #     hit.health -= BULLET_DAMAGE
        #     hit.vel = vec(0, 0)

    def draw(self):
        # draw map
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        # draw sprites
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
                sprite.draw_stamina()

            self.screen.blit(sprite.image, self.camera.apply(sprite))

        # draw HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        draw_player_stamina(self.screen, 10, 35, self.player.stamina / PLAYER_STAMINA)
        draw_fps_counter(self.screen, 10, 60, self.clock.get_fps())

        pg.display.flip()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


# create the game object
engine = Engine()
engine.show_start_screen()
while True:
    engine.new()
    engine.run()
    engine.show_go_screen()
