"""
text.py
a component of pyGhost.py

Collection of functions for rendering text

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

class Text(object):

    def __init__(self,margins):
        import pygame
        pygame.font.init()
        self.font = pygame.font.SysFont("default", 24)
        self.fontLarge = pygame.font.SysFont("default", 40)

        self.boundingRectangle = pygame.Rect(margins)

        rightHandMargins = (margins[2]-40,margins[1],margins[2],margins[3])
        self.boundingRectangleRight = pygame.Rect(rightHandMargins)

        self.answerRectangle = pygame.Rect(margins)

        # name colors
        self.black = (0,0,0)
        self.gray  = (200,200,200)
        self.white = (255,255,255)
        self.red   = (255,0,0)
        self.blue  = (0,255,0)
        self.green = (0,0,255)
        self.yellow= (255,255,0)
        self.purple= (255,0,255)

        # put colors on things
        # TODO: put these in parameter file
        self.displayColor   = self.white
        self.selectedColor  = self.red
        self.highlightColor = self.yellow

        # Create list of A-Z, string of A\nB\nC\n ... and list of incremental strings A, A\nB, A\nB\nC, ...
        self.AZ = [chr(x) for x in range(65,91)]
        self.AZString = "\n".join(self.AZ)
        self.lettersAZ = range(0,26)
        for index,letter in enumerate(self.AZ): self.lettersAZ[index]="\n".join(self.AZ[:index+1])

        # Create list of a-z, string of a\nb\nc\n ... and list of incremental strings a, a\nb, a\nb\nc, ...
        self.az = [chr(x) for x in range(97,123)]
        self.azString = "\n".join(self.az)
        self.lettersaz = range(0,26)
        for index,letter in enumerate(self.az): self.lettersaz[index]="\n".join(self.az[:index+1])

    def writewrap(self,s,font,rect,color,text):
     """write wrapped text

     Copied from PyGame Utilities
     """
     r,c,txt = rect,color,text
     txt = txt.replace("\t","        ")
     i = font.render(" ",1,c)
     sw,sh = i.get_width(),i.get_height()
     y = r.top
     for sentence in txt.split("\n"):
         x = r.left
         for word in sentence.split(" "):
             i = font.render(word,1,c)
             iw,ih = i.get_width(),i.get_height()
             if x+iw > r.right: x,y = r.left,y+sh
             s.blit(i,(x,y))
             x += iw+sw
         y += sh

    def preRender(self,questionText,screenWidth=640,rightMargin=20):
        """
        Pre-render text to find regions where it will be placed within screen with **screenWidth** and right margin of **rightMargin**
        """
        space = self.font.render(" ",1,self.black)
        sw,sh = space.get_width(),space.get_height()
        del space

        rightHandLimit = screenWidth - rightMargin

        # choices collects (upper left x y, lower right x y) coordinates of question (choice 0) and answers (choice 1, 2, ...)
        choices = []

        # starting x, y track upper left corner
        starting_x = starting_y = 0

        # x, y track lower right corner
        x = y = 0

        for sentence in questionText.split("\n"):
            for word in sentence.split(" "):
                rendered_word = self.font.render(word,1,self.black)
                rww,rwh = rendered_word.get_width(),rendered_word.get_height()
                if x+rww > rightHandLimit: x,y = 0,y+sh
                x += rww+sw
            y += sh
            #print rendered_word, x, y
            x = 0
            choices.append((starting_x,starting_y,screenWidth-1,y))
            starting_y = y + 1

        return choices

    def paintText(self,screen,textStrings,highlight,choice,colorLevel,colorLevels,inRectangle,font):
        """
Paint using text from list **textStrings** within **inRectangle** using **font** on **screen** with appropriate colors.

What is appropriate depends on

* whether a **choice** has been selected
* if touched by **highlight**, the dwellTime-based **colorLevel** (out of  **colorLevels**)
        """

        # Start by painting longest string (last in list) using display color
        self.writewrap(screen,font,inRectangle,self.displayColor,textStrings[-1])

        # If choice made, paint it selectedColor, but everything before it displayColor
        if not choice < 0:
           self.writewrap(screen,font,inRectangle,self.selectedColor,textStrings[choice])
           if choice > 0: self.writewrap(screen,font,inRectangle,self.displayColor,textStrings[choice-1])
        else:
            # If choice highlighted, paint it highlightColor (or blend with selectedColor), but paint everything before it displayColor
            if not highlight < 0:
               # Sort out how much highlightColor to mix with selectedColor based on colorLevel
               highlightPercent = float(colorLevel)/float(colorLevels)
               highlightPart    = [x*highlightPercent for x in self.highlightColor]
               selectedPercent  = 1 - highlightPercent
               selectedPart     = [x*selectedPercent for x in self.selectedColor]
               blendedColor = [int(selectedPart[i] + highlightPart[i]) for i in [0,1,2]]
               self.writewrap(screen,font,inRectangle,blendedColor,textStrings[highlight])
               if highlight > 0: self.writewrap(screen,font,inRectangle,self.displayColor,textStrings[highlight-1])


