# @brief
# @date 10.06.18
# @author Stoyan Lupov

from pygame import sprite

SCREENRECT = (0, 0, 640, 480)


class Knight(sprite.Sprite):
    speed = 10
    bounce = 24
    gun_offset = -11
    images = []

    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = self.images[0]

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)

        # The direction the knight faces (< 0 for left, > 0 right)
        self.facing = -1

    def move(self, direction):
        if direction:
            self.facing = direction

        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)

        # TODO Stoyan Lupov 10.6.2018 Flip images
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
