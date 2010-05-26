"""
pyGhost.py
a component of pyGhost.py

Defines the game display and event loop for pyGhost.

Copyright (c) 2010 John Graves
MIT License: see LICENSE.txt
"""

import logging
import video
from voice import *
from gesture import *
from pygame import *
from text import *

def main():
    """Initialization and event loop"""

    print("\n\n   pyGhost. \n\n   F3 to Show webcam. F4 to Recalibrate. \n\n   F5 to Show pixels. Escape to quit.\n\n   Enjoy!\n\n")

    logging.basicConfig(level=logging.DEBUG)
    __version__='0.13d0'
    logging.info(" pyGhost Version: %s" % __version__)

    pygame.init()

    wordList = open("data/113809of.fic").readlines()
    wordList = [word.strip() for word in wordList]

    logging.info(" Word List contains %s words." % str(len(wordList)))

    # Set size of screen and size of margins
    SCREENRECT = rect.Rect(0, 0, 640, 480)

    screen = display.set_mode(SCREENRECT.size)
    background = Surface(SCREENRECT.size).convert()

    margin = 20
    margins = (margin,margin,SCREENRECT.size[0]-margin,SCREENRECT.size[1]-margin)

    # Setup for video capture with green screen
    greenScreen = video.GreenScreen()
    vcp         = video.VideoCapturePlayer(processFunction=greenScreen.process)
    showFlag    = True

    # Setup for display of text
    text        = Text(margins)
    textRegions = text.preRender(text.AZString)

    # Setup for gesture recognition relative to text and initialize signals
    gesture     = Gesture()
    signal      = lastSignal = (0,0)

    # Setup for voice output
    voice       = Voice()

    # Initialize game variables

    # What choice (if any) has been made?
    choice = -1
    gestureLetter = keyboardLetter = ""

    # What choice (if any) has been highlighted by gesture or keyboard?
    highlight= -1

    # When was choice first highlighted by gesture?
    choiceStartTime = 0

    # How much of highlight color should be blended with selected color? in how many steps? with how much time (in ticks) per step?
    colorLevel = colorLevels = 12
    colorLevelStepTime = 100

    # Who's turn is it? 0 = Left, 1 = Right
    turn = 0

    # What is the answer string so far?
    answer = ["    "]

    # Game loop
    quit = False
    while not quit:

        # Sort out who owns choice and highlight
        if turn:
            choiceR = choice
            choiceL = -1
            highlightR = highlight
            highlightL = -1
        else:
            choiceL = choice
            choiceR = -1
            highlightL = highlight
            highlightR = -1

        # Paint A-Z and a-z on left and right sides of screen with appropriate colors
        text.paintText(screen,
           text.lettersAZ,
           highlightL,
           choiceL,
           colorLevel,colorLevels,
           text.boundingRectangle,
           text.font)
        text.paintText(screen,
           text.lettersaz,
           highlightR,
           choiceR,
           colorLevel,colorLevels,
           text.boundingRectangleRight,
           text.font)

        # Paint answer along top of screen
        text.paintText(screen,
           answer,
           -1,
           -1,
           colorLevels,colorLevels,
           text.answerRectangle,
           text.fontLarge)

        display.flip()

        # Evaluate state of play - does adding new letter make a word?
        if gestureLetter or keyboardLetter:
            answer[0] = answer[0] + gestureLetter + keyboardLetter
            choiceMade = 0
            gestureLetter = keyboardLetter = ""

            # Re-paint answer along top of screen
            text.paintText(screen,
               answer,
               -1,
               -1,
               colorLevels,colorLevels,
               text.answerRectangle,
               text.fontLarge)

            display.flip()

            answerString = answer[0].strip().lower()
            if answerString in wordList:
                voice.speak("You have spelled " + answerString)
            else:
                # check if any word begins with answerString
                possibleAnswers = [word.startswith(answerString) for word in wordList]
                possibleAnswerCount = sum(possibleAnswers)
                #print possibleAnswerCount
                if possibleAnswerCount == 0:
                   voice.speak("Sorry.  There are no words which begin with those letters.")
                   voice.speak("Press Space to start again.")
                if possibleAnswerCount == 1:
                   voice.speak("One possible word remains.")
                if possibleAnswerCount > 1:
                    if possibleAnswerCount > 199:
                       voice.speak("Hundreds of possible words remain.")
                    elif possibleAnswerCount < 200 and possibleAnswerCount > 24:
                       voice.speak("Dozens of possible words remain.")
                    elif possibleAnswerCount < 25:
                       voice.speak("There are %s possible words remaining." % str(possibleAnswerCount).strip())

        # get input
        for event in pygame.event.get():
            if event.type == pygame.QUIT   \
               or (event.type == pygame.KEYDOWN and    \
                   event.key == pygame.K_ESCAPE):
                       quit = True
            # Define toggle keys
            elif event.type == pygame.KEYDOWN and \
               event.key == pygame.K_F3:
                    screen.blit(background, (0, 0))
                    pygame.display.update()
                    showFlag = not showFlag
            elif event.type == pygame.KEYDOWN and \
               event.key == pygame.K_F4:
                    greenScreen.calibrated = 0
            elif event.type == pygame.KEYDOWN and \
               event.key == pygame.K_F5:
                    gesture.showPixels = not gesture.showPixels

            elif event.type == pygame.KEYDOWN and \
               event.key == pygame.K_SPACE:
                    # Continue on to next round
                    answer = ["    "]
                    screen.blit(background, (0, 0))
                    pygame.display.update()

            elif event.type == pygame.KEYDOWN and \
               event.key == pygame.K_BACKSPACE:
                    # Remove last letter from answer and restore turn
                    answer = [answer[0][0:len(answer[0])-1]]
                    turn = not turn
                    screen.blit(background, (0, 0))
                    pygame.display.update()

            elif event.type == pygame.KEYDOWN:
                # select letters using keyboard
                abcKeys = [pygame.K_a,
                           pygame.K_b,
                           pygame.K_c,
                           pygame.K_d,
                           pygame.K_e,
                           pygame.K_f,
                           pygame.K_g,
                           pygame.K_h,
                           pygame.K_i,
                           pygame.K_j,
                           pygame.K_k,
                           pygame.K_l,
                           pygame.K_m,
                           pygame.K_n,
                           pygame.K_o,
                           pygame.K_p,
                           pygame.K_q,
                           pygame.K_r,
                           pygame.K_s,
                           pygame.K_t,
                           pygame.K_u,
                           pygame.K_v,
                           pygame.K_w,
                           pygame.K_x,
                           pygame.K_y,
                           pygame.K_z]
                if event.key in abcKeys:
                    choiceMade = 1
                    choice = abcKeys.index(event.key)
                    if turn:
                       keyboardLetter = text.az[choice]
                    else:
                       keyboardLetter = text.AZ[choice]
                    turn = not turn


        # check webcam
        processedImage = vcp.get_and_flip(show=showFlag)
        # Recalibrate at startup
        timeFromStart = pygame.time.get_ticks()
        if timeFromStart > 10000 and timeFromStart < 15000:
            greenScreen.calibrated = 0
        # Ignore signals until camera has time to settle
        if pygame.time.get_ticks() > 20000 and greenScreen.calibrated:
            lastSignal = signal
            if turn:
               signal = gesture.choiceSelected(processedImage,textRegions,margins,boxPlacementList=(-3,-2,-1))
            else:
               signal = gesture.choiceSelected(processedImage,textRegions,margins,boxPlacementList=(0,1,2))
            choice = signal[0]

        #print signal
        #if signal[0] > 0: print text.AZ[signal[0]]

        if showFlag: vcp.display.blit(processedImage, (0,0))

        # adjust highlight and colorLevel
        if not highlight < 0 and highlight == choice:
            # choice was previously highlighted. Find out how long.
            dwellTime = pygame.time.get_ticks() - choiceStartTime

            # lower color level to 0 as time passes
            colorLevel = colorLevels - int(dwellTime/colorLevelStepTime)
            colorLevel = max(0, colorLevel)
            #TODO: provide shortcut to go immediately to colorLevel=0 if choice[1] (number of selected boxes) is big enough

            if colorLevel == 0:
                # choice has been highlighted long enough to actually be the desired selection
                choiceMade = True

                if turn:
##                    voice.speak("You selected " + text.az[choice])
                    gestureLetter = text.az[choice]
                else:
##                    voice.speak("You selected " + text.AZ[choice])
                    gestureLetter = text.AZ[choice]
                turn = not turn
                highlight = -1
            else:
                # block a choice that has not been highlighted long enough
                choice = -1
        else:
            # new choice or no choice
            highlight = choice
            if highlight < 0:
                colorLevel = colorLevels
            else:
                choiceStartTime = pygame.time.get_ticks()



if __name__ == '__main__':
    main()
    pygame.quit()