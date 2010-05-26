"""
gesture.py
a component of pyPong.py

Derive a signal from a processed webcam image

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

class Gesture(object):
    """
    Return the highest significant selected point on each side of the image.

    A webcam image processed with the green screen approach (background subtraction)
    may have white pixels which can be used to extract a signal from a gesture (hand movement).

    This implementation looks along rows of pixels, counting the non-black (white) pixels.
    Any count over 5 (about finger width) is considered a valid selection.

    Due to the imperfect filtering of the green screen approach (artifacts),
    the scan looks down a few additional rows to see if they are also selected
    (since a finger tip is usually connected to a hand below ...).
    """
    def __init__(self):
        pass
    def isWhite(self,x):
        """
        Actually just tests x > 0.  Used in sum(map( function , row of pixels )) with True counting as 1 to count non-black pixels.
        """
        return x > 0
    def countWhitePixels(self,image):
        """
        Steps down from top row of image within 40 pixels from left and right sides.  Checks every other row for over 5 white pixels.
        Sets signal when it finds three selected rows together.
        """
        import pygame
        import logging
        ar = pygame.PixelArray(image)
        rows = topWhiteRowLeft = topWhiteRowRight = image.get_height() - 1
        minTopWhiteRowLeft = minTopWhiteRowRight = rows
        cols = image.get_width() - 1
        fromCol = cols-40

        # Check along left side of image for top row selected
        for i in range(0,rows,3):
          whiteCount = sum(map(self.isWhite,ar[0:10,i]))
          if whiteCount > 5:
              whiteCount1 = sum(map(self.isWhite,ar[0:10,i+1]))
              whiteCount2 = sum(map(self.isWhite,ar[0:10,i+2]))
              if whiteCount1 > 5 and whiteCount2 > 5:
                  topWhiteRowLeft = i
                  break
                  # otherwise an artifact was selected

        # Check along right side of image for top row selected
        for i in range(0,rows,3):
          whiteCount = 0
          for j in range(1,10):
              whiteCount += (ar[-j,i] > 0)
          if whiteCount > 5:
              whiteCount1 = 0
              for j in range(1,10):
                 whiteCount1 += (ar[-j,i+1] > 0)
              whiteCount2 = 0
              for j in range(1,10):
                 whiteCount2 += (ar[-j,i+2] > 0)
              if whiteCount1 > 5 and whiteCount2 > 5:
                  topWhiteRowRight = i
                  break

##        print  topWhiteRowLeft, topWhiteRowRight
        return topWhiteRowLeft, topWhiteRowRight
