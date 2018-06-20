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


def draw_player_points(surf, points):
    pointsString = "POINTS: {0}".format(points)
    text_width, text_height = myfont.size(pointsString)

    textsurface = myfont.render(pointsString, False, (0, 0, 0))
    surf.blit(textsurface, (SCREEN_WIDTH - text_width - 10, 0))


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
        self.mobs = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.player_obs=pg.sprite.Group()

    def load_data(self):
        load_images()
        self.map = TiledMap(RESOURCE_FOLDER + '/maps/level1.tmx')
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        # Create walls group and add all walls from their layer

        wall_layer = self.map.game_map.get_layer_by_name('walls')
        items_layer = self.map.game_map.get_layer_by_name('items')

        for x, y, image in wall_layer:
            if image:
                surf_img = self.map.game_map.get_tile_image(x, y, WALLS_IMAGE_LAYER_INDEX)
                wall = Wall(x, y, surf_img)
                self.walls.add(wall)
                self.player_obs.add(wall)
        for x, y, image in items_layer:
            if image:
                surf_img = self.map.game_map.get_tile_image(x, y, ITEMS_IMAGE_LAYER_INDEX)
                wall = Wall(x, y, surf_img)
                self.items.add(wall)
                self.player_obs.add(wall)

        mobsCnt = randint(20, 30)

        for x in range(0, mobsCnt):
            mob = Mob(self)
            self.mobs.add(mob)

        self.bullets = pg.sprite.Group()
        self.player = Player(self, 5, 5)
        self.camera = Camera(self.map.width, self.map.height)

    def run(self):
        # game loop - set self.running = False to end the game
        self.running = True
        while self.running:
            # update the clock once per engine cycle
            # delays to keep the game running slower than the given ticks per second in order to limit the runtime speed
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

        if self.player.health <= 0:
            if self.player.frameIdx == PLAYER_STATES_SPRITE_CNT[self.player.state] - 2:
                self.running = False

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
        draw_player_points(self.screen, self.player.points)
        draw_fps_counter(self.screen, 10, 60, self.clock.get_fps())

        pg.display.flip()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.draw()

        youDiedStr = "You died with {0} points".format(self.player.points)
        messageStr = "Press space bar to play again"

        goScreenFont = pg.font.SysFont('Comic Sans MS', 50)

        text_width, text_height = goScreenFont.size(youDiedStr)
        text_width2, text_height2 = goScreenFont.size(messageStr)

        text_surface = goScreenFont.render(youDiedStr, True, WHITE)
        text_surface2 = goScreenFont.render(messageStr, True, WHITE)

        y = (SCREEN_HEIGHT - text_height) / 2
        self.screen.blit(text_surface, ((SCREEN_WIDTH - text_width) / 2, y))
        self.screen.blit(text_surface2, ((SCREEN_WIDTH - text_width2) / 2, y + text_height + 10))

        pg.display.flip()

        done = False
        while not done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    done = True

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        done = True
                        self.running = True

            self.clock.tick(FPS)

        return self.running


# create the game object
engine = Engine()
engine.show_start_screen()

while True:
    engine.new()
    engine.run()
    if not engine.show_go_screen():
        break
