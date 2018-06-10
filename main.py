# @brief
# @date 10.06.18
# @author Stoyan Lupov

import pygame
import sys
import Knight

# Constants
SIZE = width, height = 800, 600
FPS = 60
SPEED = [10, 10]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

ball = pygame.image.load("resources/ball.png")
ballRect = ball.get_rect()

CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode(SIZE)

# Global variables
shouldEnd = False
color = BLACK

players = pygame.sprite.Group()
enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

player = Knight


def init():
    players.add(player)
    all_sprites.add(player)


def draw():
    global ballRect

    SCREEN.fill(color)
    all_sprites.draw(SCREEN)

    # Draw ball to surface
    SCREEN.blit(ball, ballRect)


def quit_game():
    pygame.quit()
    sys.exit()


def update():
    global ballRect

    ballRect = ballRect.move(SPEED)
    if ballRect.left < 0 or ballRect.right > width:
        SPEED[0] = -SPEED[0]
    if ballRect.top < 0 or ballRect.bottom > height:
        SPEED[1] = -SPEED[1]

    # Update the entire surface
    pygame.display.update()


def handle_event():
    # Get any event that happened per frame
    for event in pygame.event.get():
        # Check if user wants to quit app
        if event.type == pygame.QUIT:
            quit_game()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                return
            elif event.key == pygame.K_RIGHT:
                return

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                return


def main():
    global shouldEnd

    pygame.init()
    pygame.display.set_caption('Our PyGame')

    while not shouldEnd:
        handle_event()
        update()
        draw()

        # Set game max fps in order not to put much weight onto the CPU
        CLOCK.tick(FPS)

    # Deinit game
    quit_game()


# call the "main" function if running this script
if __name__ == '__main__':
    main()
