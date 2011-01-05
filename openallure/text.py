# -*- coding: utf-8 -*-
"""
text.py
a component of openallure.py

Collection of functions for rendering text

Copyright (c) 2011 John Graves

MIT License: see LICENSE.txt
"""

import sys

from configobj import ConfigObj
import pygame
pygame.font.init()

class OpenAllureText(object):
    """Text rendered to screen in Open Allure"""

    def __init__( self, margins ):

        self.boundingRectangle = pygame.Rect( margins )

        # put colors on things
        config = ConfigObj(r'openallure.cfg' )
        self.unreadColor = eval(config['Colors']['unreadText'])
        self.readColor = eval(config['Colors']['readText'])
        self.selectedColor = eval(config['Colors']['selectedText'])
        self.highlightColor = eval(config['Colors']['highlightedText'])
        self.fadeColor = (255, 255, 255)

        self.fadeTime = eval(config['Options']['fadeTime'])

        # set font
        self.fontName = config['Font']['font']
        self.fontSize = eval(config['Font']['size'])
        if sys.platform == 'darwin':
            self.font = pygame.font.Font( '/Library/Fonts/Arial.ttf', self.fontSize )
            # For Korean
            #self.font = pygame.font.Font( '/Library/Fonts/HeadlineA.ttf', self.fontSize )
        else:
            #self.font = pygame.font.SysFont( self.fontName, self.fontSize )
            self.font = pygame.font.Font('freesansbold.ttf', self.fontSize )


    def buildQuestionText( self, question ):
        """
Prepare text of question and answers for display and reading aloud::

   questionText[0] is question
   questionText[1] is question + answer 1
   questionText[2] is question + answer 1 + answer 2
   etc.

   justQuestionText[0] is first (perhaps only) part of question
   justQuestionText[1] is next part of question
   etc.

   choiceCount tells how may answers there are

        """
        questionText = [""]
        questionText[0] = " ".join( question[0] ) + "\n"
        choiceCount = 0
        for text in question[1]:
            questionText.append( questionText[choiceCount] + "\n" + text )
            choiceCount += 1
        #   speak(str(choiceCount) + " found")

        # build just question in pieces (if any)
        justQuestionText = [""]
        textCount = 0
        for text in question[0]:
            justQuestionText.append( justQuestionText[textCount] + text + " " )
            textCount += 1
        justQuestionText = justQuestionText[1:]

        return choiceCount, questionText, justQuestionText

    def writewrap( self, s, font, rect, color, text ):
        """write wrapped text or return regions for choices"""
        # choices collects the coordinates (top left x y, bottom right x y) of the regions
        # in which the text is displayed. choice[0] is the question, choice[1], ... are answers
        choices = []

        r, c, txt = rect, color, text
        # starting x, y track upper left corner
        starting_x = r.left
        starting_y = r.top
        txt = txt.replace( "\t", "        " )
        i = font.render( " ", 1, c )
        sw, sh = i.get_width(), i.get_height()
        y = r.top
        for sentence in txt.split( "\n" ):
            x = r.left
            for word in sentence.split( " " ):
                i = font.render( word, 1, c )
                iw = i.get_width()
                if x + iw > r.right: x, y = r.left, y + sh
                if s:
                    s.blit( i, ( x, y ) )
                x += iw + sw
            y += sh
            # don't make a choice out of a blank line
            if not sentence == "":
                choices.append((starting_x, starting_y, r.right, y))
                starting_y = y + 1
        return choices

    def paintText( self, screen, justQuestionText, onText, questionText, onAnswer, highlight, stated, choice, colorLevel, colorLevels ):
        """
Paint words of **justQuestionText** and **questionText** on **screen** with appropriate colors.

What is appropriate depends on

* whether the question is **stated** (everything has been read aloud)
* how far along (**onText**) in the **justQuestionText** the reading of the question is
* how far along (**onAnswer**) in the **questionText** the reading of the answers is
* whether a **choice** has been selected
* if touched by **highlight**, the dwellTime-based **colorLevel** (out of  **colorLevels**)
        """
        # If not stated, start with all unreadColor
        if not stated:
            self.writewrap( screen, self.font, self.boundingRectangle, self.unreadColor, questionText[-1] )

            if onAnswer == 0:
               # paint as much readColor as needed on question
               onText = min( onText, len( justQuestionText ) - 1 )
               priorOnText = min( onText - 1, len( justQuestionText ) - 1 )
               for color in range(255, -1, -8):
                   color = max(color, 0)
                   self.fadeColor = (color, color, color)
                   if onText > -1 and onText < len(justQuestionText):
                       self.writewrap( screen, self.font, self.boundingRectangle, self.fadeColor, justQuestionText[onText] )
                   self.fadeColor = [item - 8 for item in self.fadeColor]
                   if onText > 0 and onText < len(justQuestionText):
                       self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, justQuestionText[priorOnText] )
                   pygame.display.flip()
                   pygame.time.wait( self.fadeTime )

            else:
               # or paint as much readColor as needed on answers
               # print "on answer" + str( on_answer )
               onAnswer = min( onAnswer, len( questionText ) - 1 )
               priorOnAnswer = min( onAnswer - 1, len( questionText ) - 1 )
               for color in range(255, -1, -8):
                   color = max(color, 0)
                   self.fadeColor = (color, color, color)
                   self.writewrap( screen, self.font, self.boundingRectangle, self.fadeColor, questionText[onAnswer] )
                   if onAnswer > 1:
                       self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, questionText[priorOnAnswer] )
                   self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, justQuestionText[-1] )
                   pygame.display.flip()
                   pygame.time.wait( self.fadeTime )

        # else start with all readColor
        else:
            self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, questionText[-1] )

            # If choice made,  paint it selectedColor,  but everything before it readColor
            if choice[ 0 ] > 0 and choice[ 0 ] <= len( questionText ) - 1:
               self.writewrap( screen, self.font, self.boundingRectangle, self.selectedColor, questionText[ choice[ 0 ] ] )
               self.writewrap( screen, self.font, self.boundingRectangle, self.readColor,     questionText[ choice[ 0 ] - 1 ] )
            else:
                # If choice highlighted,  paint it yellow,  but everything before it gray
                if highlight > 0:
                   #self.writewrap( screen, self.font, self.boundingRectangle, self.yellow, questionText[highlight] )
                   #print highlight,  len( questionText )
                   highlightPercent = float( colorLevel ) / float( colorLevels )
                   highlightPart    = [ x * highlightPercent for x in self.highlightColor ]
                   selectedPercent  = 1 - highlightPercent
                   selectedPart     = [ x * selectedPercent for x in self.selectedColor ]
                   blendedColor = [ int( selectedPart[ i ] + highlightPart[ i ] ) for i in [0, 1, 2] ]
##                   print highlight, stated, choice, colorLevel, colorLevels, blendedColor
##                   print highlightPercent,  highlightPart
##                   print selectedPercent,  selectedPart
##                   print blendedColor,  highlight
                   self.writewrap( screen, self.font, self.boundingRectangle, blendedColor, questionText[highlight] )
                   self.writewrap( screen, self.font, self.boundingRectangle, self.readColor, questionText[highlight-1] )

        pygame.display.flip()


