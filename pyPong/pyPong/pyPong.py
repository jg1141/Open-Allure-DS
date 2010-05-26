#!/usr/bin/env python
"""
pyPong.py

Implement game like Pong(R) using webcam to control paddles

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""
__version__ = '0.1d0dev'

import logging
import game
import pygame

def main():
    """Initialization and event loop"""

    print("\n\n   pyPong. B for Ball(s). S to Show webcam. R to Recalibrate. Escape to quit.\n\n   Enjoy!\n\n")

    logging.basicConfig(level=logging.DEBUG)
    logging.info("PyPong Version: %s" % __version__)

    game.Game()

    pygame.quit()

if __name__ == '__main__':
    main()
