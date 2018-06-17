import pytmx
from Settings import *


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


class TiledMap:
    def __init__(self, filename):
        self.game_map = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.game_map.width * self.game_map.tilewidth
        self.height = self.game_map.height * self.game_map.tileheight

    # Draws the map on a surface passed
    def render(self, surface):
        for layer in self.game_map.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.game_map.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, (x * self.game_map.tilewidth, y * self.game_map.tileheight))

    # Creates a SDL surface of the map
    def make_map(self):
        mapSurface = pg.Surface((self.width, self.height))
        self.render(mapSurface)
        return mapSurface


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - SCREEN_WIDTH), x)  # right
        y = max(-(self.height - SCREEN_HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)
