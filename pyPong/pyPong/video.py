"""
video.py
a component of pyPong.py

Implement webcam image capture and processing

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

class VideoCapturePlayer(object):
    """
    A VideoCapturePlayer object is an encapsulation of
    the processing and display of a video stream.

    A process can be given (as a function) that is run
    on every frame between capture and display.

    For example a filter function that takes and returns a
    surface can be given. This player will take the webcam image,
    pass it through the filter then display the result.

    If the function takes significant computation time (>1second)
    The VideoCapturePlayer takes 3 images between each, this flushes
    the buffer, ensuring an updated picture is used in the next computation.

    This class uses the pygame.camera module.
    """

    def __init__(self, processFunction=None,
                       display        =None,
                       show           =True, **argd):
        import logging
        import pygame
        import utils

        logging.debug("Initializing Video Capture Class")
        logging.debug("Pygame Version: %s" % pygame.__version__)

        processRuns = 0

        #set display size in pixels = width,height
        size                        =   640,480

        utils.initFromArgs(self)

        #print self.__dict__.items()

        #super(VideoCapturePlayer, self).__init__(**argd)

        if self.display is None:
            if self.show is True:
                # create a display surface. standard pygame stuff
                self.display = pygame.display.set_mode( self.size, 0 )
            else:
                pygame.display.init()
                self.display = pygame.surface.Surface(self.size)

        import pygame.camera as camera
        camera.init()

        # get a list of available cameras.
        self.cameraList = camera.list_cameras()
        if not self.cameraList:
            raise ValueError("Sorry, no cameras detected.")

        logging.info(" Opening device %s, with video size (%s,%s)" % (self.cameraList[0],self.size[0],self.size[1]))

        # create and start the camera of the specified size in RGB colorspace
        self.camera = camera.Camera(self.cameraList[0], self.size, "RGB")
        self.camera.start()

        self.processClock = self.clock = pygame.time.Clock()

        # create a surface to capture to.  for performance purposes, you want the
        # bit depth to be the same as that of the display surface.
        self.snapshot = pygame.surface.Surface(self.size, 0, self.display)

        # Explore namespace now:

        #print dir()
        """
          ['argd', 'camera', 'display', 'logging', 'processFunction', 'processRuns', 'pygame', 'self', 'show', 'size', 'utils']
        """

        #print dir(self)
        """
          ['__class__', '__delattr__', '__dict__', '__doc__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__',
          '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__str__', '__weakref__',
          'argd', 'camera', 'cameraList', 'clock', 'display', 'get_and_flip', 'logging', 'main', 'processClock', 'processFunction',
          'processRuns', 'pygame', 'show', 'size', 'snapshot', 'utils']
        """

        #print self.__dict__.items()
        """
          [('argd', {}),

           ('logging', <module 'logging' from 'C:\python25\Lib\logging\__init__.pyc'>),
           ('pygame',  <module 'pygame'  from 'C:\python25\lib\site-packages\pygame\__init__.pyc'>),
           ('utils',   <module 'utils'   from 'C:\Python25\pyPong\Scripts\pyPong\pyPong\utils.pyc'>),

           ('processFunction', <bound method GreenScreen.process of <video.GreenScreen instance at 0x00B54580>>),

           ('camera', <pygame._camera_vidcapture.Camera instance at 0x01690468>),

           ('cameraList', [0]),

           ('display',  <Surface(640x480x32 SW)>),
           ('snapshot', <Surface(640x480x32 SW)>),

           ('clock',        <Clock(fps=0.00)>),
           ('processClock', <Clock(fps=0.00)>),

           ('processRuns', 0),
           ('show', True),
           ('size', (640, 480)),
        """

    def get_and_flip(self, show=True):
        """
        Use webcam to take a snapshot, flip it right-to-left, subtract the background (green screen) and then display it.
        """
        import pygame

        # Capture an image
        self.snapshot = self.camera.get_image(self.snapshot)

        # Flip array version of image around the y axis.
        ar = pygame.PixelArray(self.snapshot)
        ar[:] = ar[::-1,:]
        del ar

        if self.processFunction:
            self.processClock.tick()
            if self.processRuns > 5 and self.processClock.get_fps() < 2:
                # If function is really slow, take a few frames.
                # Flush the camera buffer to get a new image...
                for i in range(5):
                    # Capture an image
                    self.snapshot = self.camera.get_image(self.snapshot)

                # Flip array version of image around the y axis.
                ar = pygame.PixelArray(self.snapshot)
                ar[:] = ar[::-1,:]
                del ar

            #apply green screen process
            processedShot = self.processFunction(self.snapshot)

            if isinstance(processedShot,pygame.Surface):
                self.snapshot = processedShot

            self.processRuns += 1

        if show is True:
            # blit it to the display surface.  simple!
            self.display.blit(self.snapshot, (0,0))
            pygame.display.flip()

        return self.snapshot

class GreenScreen():
    """Process to capture average background image and subtract from snapshot image"""
    def __init__(self):
        self.calibrated  = False
        self.backgrounds = []

    def calibration(self, snapshot):
        """Capture 30 background images and average them out."""
        import pygame
        if len(self.backgrounds) < 30:
            self.backgrounds.append(snapshot)
        else:
            # Average them out to remove noise, and save as background
            self.background = pygame.transform.average_surfaces(self.backgrounds)
            self.calibrated = True
            return self.background

    def threshold(self, snapshot):
        """
        Finds which pixels are beyond a threshold of the average background and makes them white.

        pygame.transform.threshold(DestSurface,               \
                                   Surface,                   \
                                   color,                     \
                                   threshold  = (0,0,0,0),    \
                                   diff_color = (0,0,0,0),    \
                                   change_return = 1,         \
                                   Surface = None,            \
                                   inverse = False): return num_threshold_pixels

        Finds which, and how many pixels in a surface are within a threshold of a color.

        It can set the destination surface where all of the pixels not within the threshold are changed to diff_color.
        If inverse is optionally set to True, the pixels that are within the threshold are instead changed to diff_color.

        If the optional second surface is given, it is used to threshold against rather than the specified color.
        That is, it will find each pixel in the first Surface that is within the threshold of the pixel at the same coordinates of the second Surface.

        If change_return is set to 0, it can be used to just count the number of pixels within the threshold if you set.
        If change_return is set to 1, the pixels set in DestSurface will be those from the color.
        If change_return is set to 2, the pixels set in DestSurface will be those from the first Surface.

        You can use a threshold of (r,g,b,a) where the r,g,b can have different thresholds. So you could use an r threshold of 40 and a blue threshold of 2 if you like.

        New in pygame 1.8

        Comments:

        November 11, 2009 3:11pm - Anonymous
        This documentation does not seem to match what is currently in 1.8.1.
        Instead: pygame.transform.threshold(DestSurface,              \
                                            Surface,                  \
                                            color,                    \
                                            threshold  = (0,0,0,0),   \
                                            diff_color = (0,0,0,0),   \
                                            change_return = True,     \
                                            Surface =None): return num_threshold_pixels

        January 15, 2009 11:36am - Anonymous
        The target surface is first filled with diff_color.
        A pixel is matched if it's distance from the color-argument (or the corresponding pixel from the optional third surface)
        is less than threshold_color (for every color component).
        If a pixel is matched, it will be set to color.
        The number of matched pixels is returned.

        So, if color = (255,0,0), and threshold_color = (10,10,10), any pixel with value (r>245, g<10, b<10) will be matched.

        From http://www.pygame.org/docs/ref/transform.html#pygame.transform.threshold
        """
        import pygame
        snapshotMinusBackground = snapshot.copy()
        threshold_value = 40        # How close to the existing colour must each point be?
        pygame.transform.threshold(snapshotMinusBackground,
                                   snapshot,
                                   (0,0,0),
                                   [threshold_value]*3 ,
                                   (255,255,255),
                                   1,
                                   self.background)
        # Median filter would be good here to remove salt + pepper noise...
        return snapshotMinusBackground

    def process(self, snapshot):
        """
        Toggles between returning calibration image and processed (green screen) image.
        """
        if not self.calibrated:
            return self.calibration(snapshot)
        else:
            return self.threshold(snapshot)
