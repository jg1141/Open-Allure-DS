"""
game.py
a component of pyPong.py

Defines the ball and paddle sprites, arena and event loop for pyPong.

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""
# Adapted from http://wiki.showmedo.com/index.php/PythonArellanoPyGameSeries
#
# scriptedfun.com
#
# Screencast #4
# Arinoid - The Ball
#

import pygame

import os
import math

GAME_SIZE = (GAME_WIDTH, GAME_HEIGHT) = (640, 480)

class Arena:
    """
    Defines the playing area of the game.
    """
    topx = GAME_WIDTH
    topy = GAME_HEIGHT
    rect = pygame.rect.Rect(0, 0, topx, topy)

    def __init__(self):
        self.background = pygame.Surface(self.rect.size).convert()

class Spritesheet:
    """
    Gets a small image from a larger bitmap containing an inventory of images.
    """
    def __init__(self, filename):
        self.sheet = pygame.image.load(os.path.join('data', filename)).convert()

    def imgat(self, rect, colorkey=None):
        """
        Returns an image at the location and size specified by a rectangle (top x1, left y1, x2 width, y2 height).
        """
        rect = pygame.rect.Rect(rect)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey is - 1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def imgsat(self, rects, colorkey=None):
        """
        Returns image sequence at the locations and sizes specified by a list of rectangles (top x1, left y1, x2 width, y2 height).
        """
        return [self.imgat(rect, colorkey) for rect in rects]

class Paddle(pygame.sprite.Sprite):
        """
        A paddle object type.
        """
        def __init__(self, image, center_x, signal):
            '''Create a paddle instance.
            Params:
            center_x: the center of the x coordinate where this paddle is.
            signal: which webcam signal to get the y cood from
            '''
            super(Paddle, self).__init__(self.containers)
            self.image = image
            self.rect = self.image.get_rect()
            self.center_x = center_x
            self.signal = signal

        def update(self):
            """
            Move the paddle to the correct row (determined by a signal from the webcam)
            """
            self.rect.centerx = self.center_x
            self.rect.centery = signal[self.signal]
            self.rect.clamp_ip(self.arena.rect)

class Ball(pygame.sprite.Sprite):
    """
    Defines the ball
    """
    speed = 6
    angleup = 45
    angledown = -45

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.update = self.start

    def start(self):
        """
        Starts the ball adjacent to the center of the left paddle
        """
        #TODO: Start a different place depending on which side serves next
        self.rect.centery = self.paddle.rect.centery
        self.rect.left = self.paddle.rect.right
        self.setfp()
        self.dx = 6
        self.dy = 0
        self.update = self.move

    def setfp(self):
        """
        Set floating point location
        """
        self.fpx = float(self.rect.centerx)
        self.fpy = float(self.rect.centery)

    def setint(self):
        """
        Set integer location
        """
        self.rect.centerx = int(self.fpx)
        self.rect.centery = int(self.fpy)

    def move(self):
        """
        Calculate movement of ball, based on collisions with paddles and sides of arena.
        """

        '''
        # Ball-Paddle Physics
        # - there are 2 extreme ball-paddle
        #   collision scenarios:
        #
        #
        # Scenario 1 - right edge
        #
        #            bbb
        #   pppppppppp
        #
        # - in this scenario, the left edge
        #   of the ball is at paddle.rect.right
        #
        #
        # Scenario 2 - left edge
        #
        # bbb
        #   pppppppppp
        #
        # - here, the left edge of the ball is
        #   (ball.rect.width - 1) units away from
        #   the paddle.rect.left, which means that
        #   the left edge of the ball is at
        #   (paddle.rect.left - (ball.rect.width - 1))
        #
        #
        # Hence, we want the linear function that
        # will determine the ball angle to contain
        # (paddle.rect.right, angler) and
        # (paddle.rect.left - (ball.rect.width - 1), anglel).
        '''

        # TODO: Stop the code duplication...
        if self.rect.colliderect(self.paddle.rect): # and self.dx > 0:
            x1 = self.paddle.rect.top
            y1 = self.angleup
            x2 = self.paddle.rect.bottom # - (self.rect.height - 1)
            y2 = self.angledown
            y = self.rect.centery
            offset = self.paddle.rect.centery - y
            m = float(y1 - y2) / (x2 - x1) # degrees per pixel of paddle
            x = m * offset
            #print self.__dict__.items()
            #print "hit1", self.paddle.rect, self.rect
            angle = math.radians(x)
            #print m, offset, x, angle, math.cos(angle), math.sin(angle)
            self.dx = self.speed * math.cos(angle)
            self.dy = -self.speed * math.sin(angle)
            #print self.dx, self.dy
            # TODO: Add sound effect here

        if self.rect.colliderect(self.paddle2.rect): # and self.dx > 0:
            x1 = self.paddle2.rect.top
            y1 = self.angleup
            x2 = self.paddle2.rect.bottom # - (self.rect.height - 1)
            y2 = self.angledown
            y = self.rect.centery
            offset = self.paddle2.rect.centery - y
            m = float(y1 - y2) / (x2 - x1) # degrees per pixel of paddle
            x = m * offset
            #print self.__dict__.items()
            #print "hit2", self.paddle2.rect, self.rect
            angle = math.radians(x)
            #print m, offset, x, angle, math.cos(angle), math.sin(angle)
            self.dx = -self.speed * math.cos(angle)
            self.dy = -self.speed * math.sin(angle)
            #print self.dx, self.dy
            # TODO: Add sound effect here

        self.fpx = self.fpx + self.dx
        self.fpy = self.fpy + self.dy
        self.setint()

        if not self.arena.rect.contains(self.rect):
            if self.rect.left < self.arena.rect.left or \
               self.rect.right > self.arena.rect.right:
                #print "die", self.paddle.rect, self.paddle2.rect, self.rect
                self.kill()
                # TODO: Add score keeping and change of serve here
            else:
                if self.rect.top < self.arena.rect.top:
                    self.dy = -self.dy
                    # TODO: Add sound effect here
                if self.rect.bottom > self.arena.rect.bottom:
                    self.dy = -self.dy
                    # TODO: Add sound effect here
                self.rect.clamp_ip(self.arena.rect)
                self.setfp()

class Game(object):
    """
    This class encapsulates the functionality of a game like Pong(R)
    with two paddles bouncing a ball from one side to the other.

    TODO: Scoring and sound
    """

    def __init__(self):
        '''Initialise the game'''
        import video
        import gesture

        global signal

        SCREENRECT = pygame.rect.Rect(0, 0, 640, 480)

        pygame.init()

        screen = pygame.display.set_mode(SCREENRECT.size)

        spritesheet = Spritesheet('arinoid_master.bmp')

        def get_paddle_image(spritesheet):
            paddle = pygame.Surface((12, 61)).convert()
            paddle.blit(spritesheet.imgat((312, 413, 12, 61)), (0, 0))
            paddle.set_colorkey(paddle.get_at((0, 0)), pygame.RLEACCEL)
            return paddle

        paddle_image = get_paddle_image(spritesheet)
        Ball.image = spritesheet.imgat((483, 420, 27, 25), -1)


        # make background
        self.arena = Arena()

        # you may change the background colour here
        screen.blit(self.arena.background, (0, 0))
        pygame.display.update()

        Paddle.arena = self.arena
        Ball.arena = self.arena

        # keep track of sprites
        balls = pygame.sprite.Group()
        all = pygame.sprite.RenderUpdates()

        Paddle.containers = all
        Ball.containers = all, balls

        # keep track of the time
        clock = pygame.time.Clock()

        # Create the paddle instances
        self.left_paddle = Paddle(paddle_image, 7, 0)
        self.right_paddle = Paddle(paddle_image, self.arena.rect.right - paddle_image.get_width(), 1)

        # The Ball class needs a reference of the paddles...
        Ball.paddle = self.left_paddle
        Ball.paddle2 = self.right_paddle

        greenScreen = video.GreenScreen()
        vcp = video.VideoCapturePlayer(processFunction=greenScreen.process)
        gesture = gesture.Gesture()
        showFlag = True
        signal = lastSignal = (0, 0)

        # game loop
        while 1:

            # get input
            for event in pygame.event.get():
                if event.type == pygame.QUIT   \
                   or (event.type == pygame.KEYDOWN and    \
                       event.key == pygame.K_ESCAPE):
                    return
                if event.type == pygame.KEYDOWN and \
                   event.key == pygame.K_b: Ball()
                if event.type == pygame.KEYDOWN and \
                   event.key == pygame.K_s:
                        screen.blit(self.arena.background, (0, 0))
                        pygame.display.update()
                        showFlag = not showFlag
                if event.type == pygame.KEYDOWN and \
                   event.key == pygame.K_r:
                        greenScreen.calibrated = False

            # check webcam
            processedImage = vcp.get_and_flip(show=showFlag)
            lastSignal = signal
            signal = gesture.countWhitePixels(processedImage)

            # clear sprites
            all.clear(screen, self.arena.background)

            # update sprites
            all.update()

            #if not balls:
            #    Ball()

            # redraw sprites
            dirty = all.draw(screen)
            pygame.display.update(dirty)

            # maintain frame rate
            clock.tick(60)

#    if __name__ == '__main__': main()
